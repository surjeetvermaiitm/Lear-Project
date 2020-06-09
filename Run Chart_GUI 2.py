# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 23:31:21 2020

@author: M SAI JASWANTH
"""
# Importing libraries
import os
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
from tkinter import filedialog
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import PdfPages
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
plt.style.use('ggplot')

# reading the file containing data
# have to be modified based on the PC being used
path = "C:/Users/M SAI JASWANTH/OneDrive/Desktop/Jassu/Intern/Reference data"

report_1 = os.path.join(path, "hsl1 - 15 Report_20191015 070000~20191016 070000.csv")
report_2 = os.path.join(path, "HSL2 - 15 Report_20191015 070000~20191016 070000.csv")
df1 = pd.read_csv(report_1, low_memory=False)
df2 = pd.read_csv(report_2, low_memory=False)
df1['join']=" || "
df1['d_and_t']=df1['Date'].astype(str)+df1['join'].astype(str)+df1[' Time'].astype(str)

# Creating GUI for HSL-1
window_1 = tk.Tk()
window_1.title("Lear_Project - HSL 1")
window_1.geometry('700x800')
window_1.iconbitmap("D:\\Lear_Corporation_Logo.ico")

# Setting theme
s = ThemedStyle(window_1)
s.set_theme("breeze")
label = ttk.Label(window_1, text="Generation of Run-Chart") 
label.config(font=("Helvetica-Bold", 14))
label.pack(pady=5)
        
# dropdown menu
options = list(df1.columns)
options_start = list(df1['d_and_t'])
options_end = list(df1['d_and_t'])
var = tk.StringVar()
var.set(options[1])
var_s =tk.StringVar()
var.set(options_start[0])
var_e =tk.StringVar()
var.set(options_end[1])
class mclass:

    def __init__(self,  window_1):
        global options, var, options_start, options_end, var_s, var_e
        self.window_1 = window_1
        frame = tk.Frame(self.window_1)
        frame.pack()
        parameter_label = ttk.Label(frame, text="Choose a parameter:")
        parameter_label.config(font=("Helvetica", 10))
        parameter_label.pack(side='left')
        self.drop = ttk.Combobox(frame, width=65, textvariable=var)
        self.drop['values'] = options
        self.drop.pack(side='left', fill='x', expand=True, pady=10)
        self.drop.current(1)
        #Getting start and end times 
        frame_1 = tk.Frame(self.window_1)
        frame_1.pack(padx=10, pady=10)
        start_time_label = ttk.Label(frame_1, text="Choose Start Time:")
        start_time_label.config(font=("Helvetica", 10))
        start_time_label.pack(side='left', fill='x', expand=True)
        self.start_time=ttk.Combobox(frame_1, width=20, textvariable=var_s)
        self.start_time['values'] = options_start
        self.start_time.pack(side='left', fill='x', expand=True, padx=10)
        self.start_time.current(0)
        end_time_label = ttk.Label(frame_1, text="Choose End Time:")
        end_time_label.config(font=("Helvetica", 10))
        end_time_label.pack(side='left', fill='x', expand=True, padx=10)
        self.end_time=ttk.Combobox(frame_1, width=20, textvariable=var_e)
        self.end_time['values'] = options_end
        self.end_time.pack(side='left', fill='x', expand=True)
        self.end_time.current(1)
        # Functionality buttons
        frame_2 = tk.Frame(self.window_1)
        frame_2.pack(pady=10)
        self.button_1 = ttk.Button(frame_2, text="Generate Run-Chart", command=self.plot)
        self.button_1.pack(side='left', fill='x', expand=True, padx=10)
        self.button_2 = ttk.Button(frame_2, text="Clear Plot", width=10, command=self.clr)
        self.button_2.pack(side='left', fill='x', expand=True, padx=60)
        self.button_3 = ttk.Button(frame_2, text="Get Report As PDF", command=self.save_file)
        self.button_3.pack(anchor='nw', side='right', fill='x', expand=True, padx=0)
                   
    def plot (self):
        global var, var_s, var_e, df1
        column_index = df1.columns.get_loc(var.get())
        row_start=int(df1[df1['d_and_t']==var_s.get()].iloc[0,0])-1
        row_end=int(df1[df1['d_and_t']==var_e.get()].iloc[0,0])
        parameter_1 = df1.iloc[row_start:row_end, column_index]
        avg = parameter_1.mean()
        std = parameter_1.std()
        y_label = var.get()
        df = df1.iloc[row_start:row_end].copy()
        df['avg']=avg
        number = df[' Time']
        upper_1 = avg + std*1
        upper_2 = avg + std*2
        upper_3 = avg + std*3
        
        lower_1 = avg - std*1
        lower_2 = avg - std*2
        lower_3 = avg - std*3
        
        df['upper_1'] = upper_1
        df['upper_2'] = upper_2
        df['upper_3'] = upper_3
        
        df['lower_1'] = lower_1
        df['lower_2'] = lower_2
        df['lower_3'] = lower_3

        self.frame_top = tk.Frame(self.window_1)
        self.frame_top.pack(fill='both', expand=True)
        fig_1 = Figure(figsize=(8,4))
        a = fig_1.add_subplot(111)
        a.plot(number,parameter_1, color='b', marker='o')
        a.plot(number, df['avg'], linestyle='solid', linewidth=3, color='g')
        a.plot(number, df['upper_1'], linestyle='dashed', linewidth=3, color='r')
        a.plot(number, df['upper_2'], linestyle='dashed', linewidth=3, color='r')
        a.plot(number, df['upper_3'], linestyle='dashed', linewidth=3, color='r')
        
        a.plot(number, df['lower_1'], linestyle='dashed', linewidth=3, color='r')
        a.plot(number, df['lower_2'], linestyle='dashed', linewidth=3, color='r')
        a.plot(number, df['lower_3'], linestyle='dashed', linewidth=3, color='r')
        a.set_xlabel('Time', fontsize=14)
        a.set_ylabel('{}'.format(y_label), fontsize=14)
        a.set_title('X-Bar Run Chart', fontsize=16)
        for label in a.get_xticklabels():
            label.set_rotation(90)
        self.canvas = FigureCanvasTkAgg(fig_1, master=self.frame_top)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        fig_1.tight_layout()
        self.canvas.draw()
        toolbar = NavigationToolbar2Tk(self.canvas, self.frame_top)
        toolbar.update()
        self.results()
        
    def results(self):
        global var, var_s, var_e
        column_index = df1.columns.get_loc(var.get())
        row_start=int(df1[df1['d_and_t']==var_s.get()].iloc[0,0])
        row_end=int(df1[df1['d_and_t']==var_e.get()].iloc[0,0])
        parameter_1 = df1.iloc[row_start:row_end+1, column_index]
        avg = parameter_1.mean()
        std = parameter_1.std()
        target = avg
        tolerance = std
        # defining the zones and limits
        upper_1 = avg + std*1
        upper_2 = avg + std*2
        upper_3 = avg + std*3
        
        lower_1 = avg - std*1
        lower_2 = avg - std*2
        lower_3 = avg - std*3
        
        # checking for special cause variations
        self.errors=set()
        self.errors.clear
        differentials_to_target = parameter_1 - target
        differentials_to_avg = parameter_1 - avg
        first_differences = np.ediff1d(parameter_1)
        #tolerances
        if np.max(np.absolute(differentials_to_target)) > tolerance:
            self.errors.add("Dimensions are out of tolerance")
        #beyond limit
        absolute_differentials = np.absolute(differentials_to_avg)
        
        if np.max(absolute_differentials) > upper_3:
            self.errors.add("Outliers Exist")
        #outer region or Zone A
        for index, i in enumerate(absolute_differentials):
            if index < 2:
                continue
            count = np.count_nonzero(absolute_differentials[index-2:index+1] > (std*2))
            if count >= 2:
                    self.errors.add("Outer Zone Clusters")
        #middle regions or Zone B
        for index, i in enumerate(absolute_differentials):
            if index < 4:
                continue
            count = np.count_nonzero(absolute_differentials[index-4:index+1] > (std*1))
            if count >= 4:
                    self.errors.add("Middle Zone Clusters")
        #inner region or Zone C
        for index, i in enumerate(absolute_differentials):
            if index < 6:
                continue
            count = np.count_nonzero(differentials_to_avg[index-6:index+1] > 0)
            if count >= 7:
                    self.errors.add("Inner Zone Clusters")
            count = np.count_nonzero(differentials_to_avg[index-6:index+1] < 0)
            if count >= 7:
                    self.errors.add("Inner Zone Clusters")
        #trends
        for index, i in enumerate(first_differences):
            if index < 6:
                continue
            count = np.count_nonzero(first_differences[index-5:index+1] > 0)
            if count >= 7:
                self.errors.add("Trending Data is Present")
            count = np.count_nonzero(first_differences[index-5:index+1] < 0)
            if count >= 7:
                self.errors.add("Trending Data is Present")
        #mixture
        for index, i in enumerate(absolute_differentials):
            if index < 8:
                continue
            count = np.count_nonzero(absolute_differentials[index-8:index+1] > upper_3)
            if count == 0:
              self.errors.add("No Mixture")
            else:
              self.errors.add("Mixture")
        #stratification
        for index, i in enumerate(absolute_differentials):
            if index < 15:
                continue
            count = np.count_nonzero(absolute_differentials[index-15:index+1] > upper_1)
            if count == 0:
              self.errors.add("No Stratification")
        #over control
        def sign_change(x,y):
            if x > 0 and y > 0:
                return 0
            elif x < 0 and y < 0:
                return 0
            else:
                return 1 
        
        changes = []
        
        for index, i in enumerate(first_differences):
            if index == 0:
                continue
            change = sign_change(first_differences[index],first_differences[index-1])
            changes.append(change)
        
        for index, i in enumerate(changes):
            if index < 14:
                continue
            if np.array(changes[index-14:index+1]).sum() >= 15:
                self.errors.add("Over Control")
        self.frame_bottom_1 = tk.Frame(window_1)
        self.frame_bottom_1.pack(fill='x')
        tk.Label(self.frame_bottom_1, text="Errors:").pack(side='left', fill='x')
        entry1=ttk.Entry(self.frame_bottom_1,width=100,font=('Helvetica', 10))
        entry1.pack(side='left', fill='x', expand=True)
        entry1.insert(0,repr(self.errors))
        self.cause()
        
    def cause(self):
        # Possible causes
        self.causes = set() 
        for ele in self.errors:
          if ele == "Dimensions are out of tolerance":
            self.causes.add("Process not proper, leading to dimensional variation")  
          elif ele == "Outliers Exist" or ele == "Outer Zone Clusters":
            self.causes.add("New person doing the job, Wrong setup, Measurement error, Process step skipped, Process step not completed, Power failure, Equipment breakdown")
          elif ele == "Middle Zone Clusters" or ele == "Inner Zone Clusters":
            self.causes.add("Raw material change, Change in work instruction, Different measurement device/calibration, Different shift, Person gains greater skills in doing the job, Change in maintenance program, Change in setup procedure")  
          elif ele == "Trending data is present":
            self.causes.add("Tooling wear or Temperature effects (cooling, heating)") 
          elif ele == "Mixture" or ele == "Stratification":
            self.causes.add("More than one process present (e.g. shifts, machines, raw material.)") 
          elif ele == "Over Control":
            self.causes.add("Tampering by operator or Alternating raw materials")          
        self.frame_bottom_2 = tk.Frame(window_1)
        self.frame_bottom_2.pack(fill='x')
        tk.Label(self.frame_bottom_2, text="Possible\nCauses:").pack(side='left', fill='x')
        entry1=tk.Text(self.frame_bottom_2, height=3, width=5,font=('Helvetica', 10), bg='white', borderwidth=3)
        entry1.pack(side='left', fill='x', expand=True, pady=4)
        lst = repr(self.causes).split("',")
        for ele in lst:
            entry1.insert(tk.END, str(ele)+"\n")
                          
    def save_file(self):
        # create a new PDF with Reportlab
        # have to be modified based on the PC being used
        can = canvas.Canvas("C:\\Users\\M SAI JASWANTH\\OneDrive\\Desktop\\Report.pdf", pagesize=letter)
        # exporting plot as PDF
        global var, var_s, var_e, df1
        column_index = df1.columns.get_loc(var.get())
        row_start=int(df1[df1['d_and_t']==var_s.get()].iloc[0,0])-1
        row_end=int(df1[df1['d_and_t']==var_e.get()].iloc[0,0])
        parameter_1 = df1.iloc[row_start:row_end, column_index]
        avg = parameter_1.mean()
        std = parameter_1.std()
        y_label = var.get()
        df = df1.iloc[row_start:row_end].copy()
        df['avg']=avg
        number = df[' Time']
        upper_1 = avg + std*1
        upper_2 = avg + std*2
        upper_3 = avg + std*3
        
        lower_1 = avg - std*1
        lower_2 = avg - std*2
        lower_3 = avg - std*3
        
        df['upper_1'] = upper_1
        df['upper_2'] = upper_2
        df['upper_3'] = upper_3
        
        df['lower_1'] = lower_1
        df['lower_2'] = lower_2
        df['lower_3'] = lower_3

        #with PdfPages('C:\\Users\\M SAI JASWANTH\\Report.pdf') as export_pdf:
          
        plt.plot(number,parameter_1, color='b', marker='o')
        plt.plot(number, df['avg'], linestyle='solid', linewidth=3, color='g')
        plt.plot(number, df['upper_1'], linestyle='dashed', linewidth=3, color='r')
        plt.plot(number, df['upper_2'], linestyle='dashed', linewidth=3, color='r')
        plt.plot(number, df['upper_3'], linestyle='dashed', linewidth=3, color='r')
            
        plt.plot(number, df['lower_1'], linestyle='dashed', linewidth=3, color='r')
        plt.plot(number, df['lower_2'], linestyle='dashed', linewidth=3, color='r')
        plt.plot(number, df['lower_3'], linestyle='dashed', linewidth=3, color='r')
        plt.xlabel('Time', fontsize=10)
        plt.ylabel('{}'.format(y_label), fontsize=10)
        plt.title('X-Bar Run Chart', fontsize=12)
        plt.xticks(rotation=90)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('plot.png')
        plt.close()
        
        # errors and causes to PDF        
        can.drawImage("Lear_Logo.png", 10, 710, width=200,height=75, mask=None )
        can.drawImage("plot.png", 0, 280, width=600,height=400, mask=None )
        can.drawString(65, 250, "Errors:")
        can.drawString(65,230, repr(self.errors))
        can.drawString(65, 180, "Possible Causes:")  
        lst = repr(self.causes).split("',")
        y = 140
        for i in range(len(lst)):
            ele = str(lst[i])
            print(ele)
            if len(str(ele))>90:
                can.drawString(65, y+15, ele[:90])
                can.drawString(65, y, ele[90:180])
                can.drawString(65, y-15, ele[180:270])
                can.drawString(65, y-30, ele[270:])
            else:    
                can.drawString(65, y-15, ele)
            y-=15
        can.save()

    def clr(self):
        self.frame_top.destroy()
        self.frame_bottom_1.destroy()
        self.frame_bottom_2.destroy()
start= mclass (window_1)
window_1.mainloop()

