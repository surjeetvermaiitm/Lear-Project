# sed q#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 29 14:21:52 2020
@author: syshain
"""

#%%
from tkinter import *
from tkinter.ttk import *
from tkinter import ttk
from ttkthemes import themed_tk as tk
from tkinter import filedialog
from collections import Counter
import tkinter as tkt
import time
import re
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib as mlb
import seaborn as sns
import plotly
import plotly.graph_objs as go
import plotly.figure_factory as ff
from tkinter import messagebox as mb
# from ScrollableImage import ScrollableImage   
pattern = r"Unnamed"
dataset = []
dataA = []
dataB = []
cycle_time = 0
dt_relevant = []
i_bn = 0
i_end = 0
chosen = " "
st_date = dt.datetime.now()
end_date = dt.datetime.now()
st_time = dt.datetime.now()
end_time = dt.datetime.now()
p_table = []  
flag = 0
res = []
#Get Images
# Performance_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Performance.png')
# OEE_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\OEE.png')
# Quality_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Quality.png')
# Availability_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Availability.png')
# Back_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Back.png')
# Go_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Go.png')
# LineA_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Line A.png')
# LineB_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Line B.png')
# HeatMap_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Heat Map.png')
# RunCharts_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Run Charts.png')
# ViewInteractive_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\View Interactive Plot in Browser.png')
# ProdQuan_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Production Quantities.png')
# ProceedtoTime_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Proceed to Time Range Selection.png')


#%%
def calc_cycle_time():
    global dataA, dataB, cycle_time
    line = dataset['Line ID']
    Ain = np.where(line == 'A')[0]
    Bin = np.where(line == 'B')[0]
    dataA = dataset.iloc[Ain]
    dataA.index = np.arange(len(Ain))
    dataB = dataset.iloc[Bin]
    dataB.index = np.arange(len(Bin))
    tdA = np.asarray([abs(dataA['Date time'][i+1]-dataA['Date time'][i]) for i in dataA.index[:-1]])
    tdB = np.asarray([abs(dataB['Date time'][i+1]-dataB['Date time'][i]) for i in dataB.index[:-1]])
    td = np.concatenate((tdA, tdB), axis = 0)
    max_rep = Counter(td).most_common(4)
    cycle_time = max_rep[1][0].total_seconds()/4

#%%
def calc_duration_parameters(st, et, l = None):
    no_hrs = int((et-st).seconds/3600)+24*(et-st).days
    global dt_relevant, i_bn, i_end, unplanned_dt
    
    if(l == None):
        data = dataset
         
    if(l == 'A'):
        data = dataA
        
    if(l=='B'):
        data = dataB
        
    dates = data['Date']
    time = data['Time']
    result = data['Result']
    DT_column = data['Date time']
    
    i_bn = np.where(DT_column > st)[0][0]
    i_end = np.where(DT_column > et)[0][0]
    dt_relevant = DT_column[i_bn:i_end]
    result_relevant = result[i_bn:i_end]
    
    if(len(dt_relevant)>0):
        time_differences = np.asarray([dt_relevant[i+1]-dt_relevant[i] for i in (dt_relevant.index[0] + np.arange(len(dt_relevant)-1))])
        unplanned_dt = time_differences.sum(initial = pd.to_timedelta('00:00:00'), where = (time_differences > pd.to_timedelta('00:01:00')))
        no_ok = Counter(result_relevant)['OK']
        no_ng = Counter(result_relevant)['NG']
        
        total_possibility = no_hrs*3600/cycle_time
        availability = 1 - np.divide(unplanned_dt,dt.timedelta(hours = no_hrs))
        quality = np.divide(no_ok,(no_ok + no_ng))
        OEE = np.divide(no_ok,total_possibility)
        performance = OEE/(availability*quality)
    else: 
        availability = 0
        quality = 0
        OEE  = 0 
        performance = 0
    return availability, quality, OEE, performance

#%%
def htmp_calc(l = None):
    'This cell prepares the data for calculation of hourly quantities'
    global p_table
    
    if(l == None):
        data = dataset
    if(l == 'A'):
        data = dataA
    if(l == 'B'):
        data = dataB
        
    timear = data['Date time']
    result = data['Result']
    hourly_distribution = []
    result_hrly = []
    onehr = pd.to_timedelta('1:00:00')
    starttime = st_time
    req_time = pd.to_timedelta(end_time-st_time)
    rel_rge = int(req_time.seconds/3600)+(req_time.days)*24
    
    for i in range(int(rel_rge)):
        hourly_distribution.append(timear[np.where(timear > starttime+i*(onehr))[0][0]:(np.where(timear > starttime+(i+1)*(onehr))[0][0])-1])
        result_hrly.append(result[np.where(timear > starttime+i*(onehr))[0][0]:(np.where(timear > starttime+(i+1)*(onehr))[0][0])-1])
        
    'This part prepares the respective quantities for the generation of a heat map'
    result_minutely = []
    fivemin = pd.to_timedelta('00:05:00')
    'This cell contains a loop to continue quantity preparation and converts them to appropriate types'
    for i in range(len(hourly_distribution)*12):
        result_minutely.append(result[np.where(timear > starttime+i*(fivemin))[0][0]:(np.where(timear > starttime+(i+1)*(fivemin))[0][0])-1])
        
    'This cell calculates the most important quantities relating to the final calculations'    
    ok_minutely = np.array([Counter(result_minutely[i])['OK'] for i in range(len(result_minutely))])
    st2 = st_time + dt.timedelta(hours = 1)
    et2 = end_time - dt.timedelta(hours = 1)
    h1 = np.array([[str(i)]*12 for i in pd.date_range(st_time, et2, freq = '1H')]).flatten()
    h2 = np.array([[str(i)]*12 for i in pd.date_range(st2, end_time, freq = '1H')]).flatten()
    m1 = np.arange(5,65,5)
    m2 = m1-5
    hString = np.array(["{0} - {1}".format(v1,v2) for v1,v2 in zip(h1,h2)])
    mString = np.array(["{1} - {0}".format(v1,v2) for v1, v2 in zip(m1,m2)]*len(hourly_distribution))
    df = pd.DataFrame({'hours': hString, 'minutes': mString, 'OK': ok_minutely}, index = np.arange(12*len(hourly_distribution)))
    p_table = pd.pivot_table(df, values ='OK', index ='hours' ,columns ='minutes')
    in1 = [hString[i*12] for i in np.arange(len(hourly_distribution))]
    in2 = mString[0:12]
    p_table = p_table.reindex(in1)
    p_table.columns = p_table.columns.reindex(in2)[0]
    return p_table        

#%%    
def availability_plot(plflag):
    avg = availability_hrly.mean()* np.ones(no_hrs)
    std = availability_hrly.std()* np.ones(no_hrs)
    
    upper_1 = avg + std*1
    upper_2 = avg + std*2
    upper_3 = avg + std*3
    lower_1 = avg - std*1
    lower_2 = avg - std*2
    lower_3 = avg - std*3
    
    if(plflag == 0):
           availability_plot = tk.ThemedTk()
           availability_plot.get_themes()
           availability_plot.set_theme('breeze')
           availability_plot.geometry('1200x1200')
           availability_plot.title('Availability Run Chart')
           f = Figure(figsize=(10,10))
           a = f.add_subplot(111)
           a.plot(hours, availability_hrly, 'b-')
           a.plot(hours, upper_1 , 'r--')
           a.plot(hours, upper_2 , 'r--')
           a.plot(hours, upper_3 , 'r--')
           a.plot(hours, avg, 'g-')
           a.plot(hours, lower_1 , 'r--')
           a.plot(hours, lower_2 , 'r--')
           a.plot(hours, lower_3 , 'r--')
           a.set_title('Availability Run Chart', fontsize = 16)
           a.set_xlabel('Hours')
           a.set_ylabel('Availability')
           canvas = FigureCanvasTkAgg(f,availability_plot)
           canvas.draw()
           canvas.get_tk_widget().pack(side = TOP, fill= BOTH, expand=True)
           toolbar = NavigationToolbar2Tk(canvas,availability_plot)
           toolbar.update()
           canvas._tkcanvas.pack(side = TOP, fill= X, expand=True)
           availability_plot.mainloop()
           
    else:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x = hours, y  = availability_hrly, mode = 'markers+lines', line = dict(color = 'blue'), name = 'Avaiability'))
        fig1.add_trace(go.Scatter(x = hours, y = upper_1, mode = 'lines', line  = dict(color = 'red', dash = 'dash'), name = 'Upper limit 1'))
        fig1.add_trace(go.Scatter(x = hours, y = upper_2, mode = 'lines', line  = dict(color = 'red', dash = 'dash'), name = 'Upper limit 2'))
        fig1.add_trace(go.Scatter(x = hours, y = upper_3, mode = 'lines', line  = dict(color = 'red', dash = 'dash'), name = 'Upper limit 3'))
        fig1.add_trace(go.Scatter(x = hours, y = avg, mode = 'lines', line  = dict(color = 'green', dash = 'dash'), name = 'Mean value'))
        fig1.add_trace(go.Scatter(x = hours, y = lower_1, mode = 'lines', line  = dict(color = 'red', dash = 'dash'), name = 'Lower limit 1'))
        fig1.add_trace(go.Scatter(x = hours, y = lower_2, mode = 'lines', line  = dict(color = 'red', dash = 'dash'), name = 'Lower limit 2'))
        fig1.add_trace(go.Scatter(x = hours, y = lower_3, mode = 'lines', line  = dict(color = 'red', dash = 'dash'), name = 'Lower limit 3'))
        fig1.update_layout(title = {'text':'Hourly Availability Plot', 'x':0.5, 'y':0.95, 'xanchor':'center', 'yanchor':'top'}, yaxis_title = 'Availability', xaxis_title = 'Hours',font = dict(family = 'Courier New, monospace', size = 18, color = '#7f7f7f'))
        fig1 = fig1.to_plotly_json() 
        plotly.offline.plot(fig1)
    
#%%

def quality_plot(plflag):
    avg = quality_hrly.mean()* np.ones(no_hrs)
    std = quality_hrly.std()* np.ones(no_hrs)
    
    upper_1 = avg + std*1
    upper_2 = avg + std*2
    upper_3 = avg + std*3
    lower_1 = avg - std*1
    lower_2 = avg - std*2
    lower_3 = avg - std*3
   
    if(plflag == 0):
     quality_plot = tk.ThemedTk()
     quality_plot.get_themes()
     quality_plot.set_theme('breeze')
     quality_plot.geometry('1200x1200')
     quality_plot.title('Quality Run Chart')
     f = Figure(figsize=(10,10))
     a = f.add_subplot(111)
     a.plot(hours, quality_hrly, 'b-')
     a.plot(hours, upper_1 , 'r--')
     a.plot(hours, upper_2 , 'r--')
     a.plot(hours, upper_3 , 'r--')
     a.plot(hours, avg, 'g-')
     a.plot(hours, lower_1 , 'r--')
     a.plot(hours, lower_2 , 'r--')
     a.plot(hours, lower_3 , 'r--')
     a.set_title('Quality Run Chart', fontsize = 16)
     a.set_xlabel('Hours')
     a.set_ylabel('Quality')
     canvas = FigureCanvasTkAgg(f,quality_plot)
     canvas.draw()
     canvas.get_tk_widget().pack(side = TOP, fill= BOTH, expand=True)   
     toolbar = NavigationToolbar2Tk(canvas,quality_plot)
     toolbar.update()
     canvas._tkcanvas.pack(side = TOP, fill= BOTH, expand=True)
     quality_plot.mainloop()
    
    else:
     fig1 = go.Figure()
     fig1.add_trace(go.Scatter(x = hours, y  = quality_hrly, mode = 'markers+lines', line = dict(color = 'blue'), name = 'Quality'))
     fig1.add_trace(go.Scatter(x = hours, y = upper_1, line  = dict(color = 'red', dash = 'dash'), name = 'Upper limit 1'))
     fig1.add_trace(go.Scatter(x = hours, y = upper_2, line  = dict(color = 'red', dash = 'dash'), name = 'Upper limit 2'))
     fig1.add_trace(go.Scatter(x = hours, y = upper_3, line  = dict(color = 'red', dash = 'dash'), name = 'Upper limit 3'))
     fig1.add_trace(go.Scatter(x = hours, y = avg, line  = dict(color = 'green', dash = 'dash'), name = 'Mean value'))
     fig1.add_trace(go.Scatter(x = hours, y = lower_1, line  = dict(color = 'red', dash = 'dash'), name = 'Lower limit 1'))
     fig1.add_trace(go.Scatter(x = hours, y = lower_2, line  = dict(color = 'red', dash = 'dash'), name = 'Lower limit 2'))
     fig1.add_trace(go.Scatter(x = hours, y = lower_3, line  = dict(color = 'red', dash = 'dash'), name = 'Lower limit 3'))
     fig1.update_layout(title = dict(text = 'Hourly Quality Plot', x = 0.5, y = 0.95, xanchor = 'center', yanchor = 'top'), xaxis_title = 'Hours', yaxis_title = 'Quality', font = dict(family = 'Courier New, monospace', size = 18, color = '#7f7f7f'))
     fig1 = fig1.to_plotly_json() 
     plotly.offline.plot(fig1)

#%%

def OEE_plot(plflag):
    avg = OEE_hrly.mean()* np.ones(no_hrs)
    std = OEE_hrly.std()* np.ones(no_hrs)
    
    upper_1 = avg + std*1
    upper_2 = avg + std*2
    upper_3 = avg + std*3
    lower_1 = avg - std*1
    lower_2 = avg - std*2
    lower_3 = avg - std*3

    if(plflag == 0):
        OEE_plot = tk.ThemedTk()
        OEE_plot.get_themes()
        OEE_plot.set_theme('breeze')
        OEE_plot.geometry('1200x1200')
        OEE_plot.title('OEE Run Chart')    
        f = Figure(figsize=(10,10))
        a = f.add_subplot(111)   
        a.plot(hours, OEE_hrly, 'b-')
        a.plot(hours, upper_1 , 'r--')
        a.plot(hours, upper_2 , 'r--')
        a.plot(hours, upper_3 , 'r--')
        a.plot(hours, avg, 'g-')
        a.plot(hours, lower_1 , 'r--')
        a.plot(hours, lower_2 , 'r--')
        a.plot(hours, lower_3 , 'r--')
        a.set_title('OEE Run Chart', fontsize = 16)
        a.set_xlabel('Hours')
        a.set_ylabel('OEE')       
        canvas = FigureCanvasTkAgg(f,OEE_plot)
        canvas.draw()
        canvas.get_tk_widget().pack(side = TOP, fill= BOTH, expand=True)       
        toolbar = NavigationToolbar2Tk(canvas,OEE_plot)
        toolbar.update()
        canvas._tkcanvas.pack(side = TOP, fill= BOTH, expand=True)
        OEE_plot.mainloop()
        
    else:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x = hours, y  = OEE_hrly, mode = 'markers+lines', line = dict(color = 'blue'), name = 'OEE'))
        fig1.add_trace(go.Scatter(x = hours, y = upper_1, line  = dict(color = 'red', dash = 'dash'), name = 'Upper limit 1'))
        fig1.add_trace(go.Scatter(x = hours, y = upper_2, line  = dict(color = 'red', dash = 'dash'), name = 'Upper limit 2'))
        fig1.add_trace(go.Scatter(x = hours, y = upper_3, line  = dict(color = 'red', dash = 'dash'), name = 'Upper limit 3'))
        fig1.add_trace(go.Scatter(x = hours, y = avg, line  = dict(color = 'green', dash = 'dash'), name = 'Mean value'))
        fig1.add_trace(go.Scatter(x = hours, y = lower_1, line  = dict(color = 'red', dash = 'dash'), name = 'Lower limit 1'))
        fig1.add_trace(go.Scatter(x = hours, y = lower_2, line  = dict(color = 'red', dash = 'dash'), name = 'Lower limit 2'))
        fig1.add_trace(go.Scatter(x = hours, y = lower_3, line  = dict(color = 'red', dash = 'dash'), name = 'Lower limit 3'))
        fig1.update_layout(title = {'text':"Hourly OEE plot", 'x':0.5, 'y':0.95,'xanchor':'center', 'yanchor':'top'}, xaxis_title = 'Hours', yaxis_title = 'Availability', font = dict(family = 'Courier New, monospace', color = '#7f7f7f', size = 20))
        fig1 = fig1.to_plotly_json() 
        plotly.offline.plot(fig1)

#%%

def performance_plot(plflag):
    avg = performance_hrly.mean()* np.ones(no_hrs)
    std = performance_hrly.std()* np.ones(no_hrs)
    
    upper_1 = avg + std*1
    upper_2 = avg + std*2
    upper_3 = avg + std*3
    lower_1 = avg - std*1
    lower_2 = avg - std*2
    lower_3 = avg - std*3

    if(plflag == 0):
        performance_plot = tk.ThemedTk()
        performance_plot.get_themes()
        performance_plot.set_theme('breeze')
        performance_plot.geometry('1200x1200')
        performance_plot.title('OEE Run Chart')
        f = Figure(figsize=(10,10))
        a = f.add_subplot(111)    
        a.plot(hours, performance_hrly, 'b-')
        a.plot(hours, upper_1 , 'r--')
        a.plot(hours, upper_2 , 'r--')
        a.plot(hours, upper_3 , 'r--')
        a.plot(hours, avg, 'g-')
        a.plot(hours, lower_1 , 'r--')
        a.plot(hours, lower_2 , 'r--')
        a.plot(hours, lower_3 , 'r--')
        a.set_title('Performance Run Chart', fontsize = 16)
        a.set_xlabel('Hours')
        a.set_ylabel('Performance')       
        canvas = FigureCanvasTkAgg(f,performance_plot)
        canvas.draw()
        canvas.get_tk_widget().pack(side = TOP, fill= BOTH, expand=True)       
        toolbar = NavigationToolbar2Tk(canvas,performance_plot)
        toolbar.update()
        canvas._tkcanvas.pack(side = TOP, fill= BOTH, expand=True)
        performance_plot.mainloop()
        
    else:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x = hours, y  = performance_hrly, mode = 'markers+lines', line = dict(color = 'blue'), name = 'performance'))
        fig1.add_trace(go.Scatter(x = hours, y = upper_1, line  = dict(color = 'red', dash = 'dash'), name = 'Upper limit 1'))
        fig1.add_trace(go.Scatter(x = hours, y = upper_2, line  = dict(color = 'red', dash = 'dash'), name = 'Upper limit 2'))
        fig1.add_trace(go.Scatter(x = hours, y = upper_3, line  = dict(color = 'red', dash = 'dash'), name = 'Upper limit 3'))
        fig1.add_trace(go.Scatter(x = hours, y = avg, line  = dict(color = 'green', dash = 'dash'), name = 'Mean value'))
        fig1.add_trace(go.Scatter(x = hours, y = lower_1, line  = dict(color = 'red', dash = 'dash'), name = 'Lower limit 1'))
        fig1.add_trace(go.Scatter(x = hours, y = lower_2, line  = dict(color = 'red', dash = 'dash'), name = 'Lower limit 2'))
        fig1.add_trace(go.Scatter(x = hours, y = lower_3, line  = dict(color = 'red', dash = 'dash'), name = 'Lower limit 3'))
        fig1.update_layout(title = dict(text = 'Hourly Performance Plot', x = 0.5, y = 0.95, xanchor = 'center', yanchor = 'top'), xaxis_title = 'Hours', yaxis_title = 'Performance', font = dict(family = 'Courier New, monospace', size = 18, color = '#7f7f7f'))
        fig1 = fig1.to_plotly_json() 
        plotly.offline.plot(fig1)

#%%
'Defining the GUI'
def main():
    
   
    window1 = tk.ThemedTk()
    window1.get_themes()
    window1.set_theme('breeze')
    window1.configure(background= '#ffc3a0')
    window1.title('Lear Remote Internship')
    window1.geometry('500x300')
    fr1 = Frame(window1, relief = RAISED, borderwidth = 1, height = 300)
    fr1.pack(pady = 50)
    wel_lb1 = ttk.Label(fr1, text = 'Welcome', font = ('latin modern roman',20))
    wel_lb1.pack(side = TOP, pady = 20)
    ch_lbl1 = ttk.Label(fr1, text = 'Choose the input data file', font = ('latin modern roman',15))
    ch_lbl1.pack(side = LEFT, padx = 20, pady = 10)
    def clicked1():
        file = filedialog.askopenfilename(filetypes = (("Comma Separated Variables","*.csv"),("all files","*.*")))
        global dataset 
        dataset = pd.read_csv(file,usecols=[1,2,13,15])
        #dataset = pd.read_csv(file)
        if {'Date','Time','Result','Line ID'}.issubset(dataset.columns):
            print('')
        elif{' Date'}.issubset(dataset.columns):
            mb.showerror("Data error", "Please remove space before 'Date' in column heading of the selected file")
            window1.mainloop()
        elif{' Time'}.issubset(dataset.columns):
            mb.showerror("Data error", "Please remove space before 'Time' in column heading of the selected file")
            window1.mainloop()
        elif{' Result'}.issubset(dataset.columns):
            mb.showerror("Data error", "Please remove space before 'Result' in column heading of the selected file")
            window1.mainloop()
        elif{' Date'}.issubset(dataset.columns):
            mb.showerror("Data error", "Please remove space before 'Line ID' in column heading of the selected file")
            window1.mainloop()
        else:
            mb.showerror("Data error", "Selected file does not contain required data set")
            window1.mainloop()
        # pb = ttk.Progressbar(window1, orient='horizontal', mode='determinate')
        # pb.pack(expand=True, fill=BOTH, side=TOP)
        # pb.start(50)
        dataset['Date time'] = pd.Series([dt.datetime.strptime((dataset['Date'][i]+' '+dataset['Time'][i]),'%d-%m-%Y %H:%M:%S') for i in dataset.index])
        dataset = dataset.sort_values(by = 'Date time')
        dataset.index = np.arange(len(dataset))
        calc_cycle_time()
        window1.destroy()
        window2()
    ChooseFile_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Choose File.png')    
    ch_bt1 = tkt.Button(fr1, image = ChooseFile_img ,borderwidth=0, command = clicked1)
    ch_bt1.pack(side = LEFT, padx = 10, pady = 10)
    window1.mainloop()
    
#%%
def window2():
    global date
    date = dataset['Date']
    date = [dt.datetime.strptime(str(date[i]), '%d-%m-%Y').date() for i in range(len(date))]
    window2 = tk.ThemedTk()
    window2.get_themes()
    window2.set_theme('breeze')
    window2.configure(background= '#ffc3a0')
    window2.geometry('850x300')
    fr1 = Frame(window2, relief = RAISED,borderwidth = 1)
    fr1.pack(side = TOP, fill = X)
    fr2 = Frame(window2)
    fr2.pack(side = TOP, fill = X)
    window2.title('Date selection')
    sdate_lbl2 = Label(fr1, text = 'Choose starting date')
    sdate_lbl2.pack(side = LEFT, pady = 5)
    strt_cmb2 = Combobox(fr1)
    strt_cmb2.pack(side = LEFT, padx = 5)
    strt_cmb2['values'] =tuple(np.unique(date))
    strt_cmb2.current(0)
    edate_lbl2 = Label(fr1, text = 'Choose ending date').pack(side = LEFT, pady = 5, padx = 5)
    end_cmb2 = Combobox(fr1)
    end_cmb2.pack(side = LEFT, padx = 5)
    end_cmb2['values'] = tuple(np.unique(date))
    end_cmb2.current(0)

    
    def clicked2():
        global st_date, end_date
        st_date = pd.to_datetime(strt_cmb2.get())
        end_date = pd.to_datetime(end_cmb2.get())
        if st_date>end_date:
            mb.showerror("Date Error", "End date must be greater than start date")
            window2.mainloop()
        #sdate_lbl3.configure(text = st_date)
        window2.destroy()
        window3()
        
    def bkclick():
        window2.destroy()
        main()        
    Back_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Back.png')
    ProceedtoTime_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Proceed to Time Range Selection.png')    
    back_bt = tkt.Button(fr2, image = Back_img,borderwidth=0, command = bkclick) 
    back_bt.pack(side = LEFT, padx = 10)
    time_bt = tkt.Button(fr2, image = ProceedtoTime_img,borderwidth=0, command = clicked2)
    time_bt.pack(side = BOTTOM, pady = 5)
    window2.mainloop()
        
#%%
def window3():
    global flag
    flag = 0
    s_st = (st_date + dt.timedelta(0))
    s_et = (st_date + dt.timedelta(hours=23))
    e_st = (end_date + dt.timedelta(0))
    e_et = (end_date + dt.timedelta(hours =23))
    s_dti = tuple(pd.date_range(start = s_st, end = s_et, freq = '1H'))  
    e_dti = tuple(pd.date_range(start = e_st, end = e_et, freq = '1H'))
    window3 = tk.ThemedTk()
    window3.get_themes()
    window3.set_theme('breeze')
    window3.geometry('1000x1200')
    window3.configure(background= '#ffc3a0')
    frame1 = Frame(window3, relief = RAISED)
    frame1.pack(fill = X)
    window3.title('Time selection') 
    stime_lbl3 = Label(frame1, text = 'Choose starting time:', width = 20)
    stime_lbl3.pack(side = LEFT, padx = 5, pady = 5)
    stime_cmb3 = Combobox(frame1)
    stime_cmb3.pack(side = LEFT, padx = 5, pady = 5)
    stime_cmb3['values'] =s_dti
    stime_cmb3.current(0)
    etime_lbl3 = Label(frame1, text = 'Choose ending time:').pack(side = LEFT, padx = 5, pady = 5)
    etime_cmb3 = Combobox(frame1)
    etime_cmb3.pack(side = LEFT, padx = 5, pady = 5)
    etime_cmb3['values'] = e_dti
    etime_cmb3.current(0)
    frb = Frame(window3, relief = FLAT)
    frb.pack(fill = X)    
    frame2= Frame(window3, relief = RAISED, borderwidth = 2, height = 20)
    frame2.pack(fill = X)
    frame1_1= Frame(window3, relief = RAISED, borderwidth = 2, height = 10)
    frame1_1.pack(fill = X)
    sres_lbl = Label(frame2, text = '', font = ('Arial Bold', 18), foreground ='blue')
    sres_lbl.pack(side= BOTTOM,fill=X, padx = 5, pady = 5)
    frame3= Frame(window3, relief = RAISED, borderwidth = 2, height = 10)
    frame3.pack(fill = X)
    frame4= Frame(window3, relief = RAISED, borderwidth = 2, height = 10)
    frame4.pack(fill = X)
    

    def plotinmap():
        no_hrs = int((end_time-st_time).seconds/3600)+24*(end_time-st_time).days
        if(no_hrs>48):
            Msg = mb.askyesno(title='Warning', message= 'The selected time range is very large \nHeatmap would not be clear \nWould you still want to continue?') 
        elif(no_hrs<=48):
            Msg = True
        
        if Msg==True: 
            fig= go.Figure()
            fc = ['black','white']
            annot_text = np.array([str(p_table.values[i][j]) for i in range(np.shape(p_table.values)[0]) for j in range(np.shape(p_table.values)[1])]).reshape(np.shape(p_table.values))
            fig = ff.create_annotated_heatmap(z = p_table.values, x = list(p_table.columns), y = list(p_table.index.values), annotation_text = annot_text, colorscale= 'rdylgn', font_colors = fc)
            fig.update_layout(title = dict(text = 'Heat Map depicting produced quantites every 5 minutes', x = 0.5, y = 0.05, xanchor = 'center', yanchor = 'top'), xaxis_title = 'Minutes', yaxis_title = 'Hours', font = dict(family = 'Courier New, monospace', size = 18, color = '#7f7f7f'))        
            fig = fig.to_plotly_json()
            plotly.offline.plot(fig)
    
        
    def inplot():
        for widget in frame3.winfo_children():
            widget.destroy()
        for widget in frame1_1.winfo_children():
            widget.destroy()
        
        HeatMap_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Heat Map.png')
        RunCharts_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Run Charts.png')
        
        hm = tkt.Button(frame1_1, image= HeatMap_img ,borderwidth=0, command = plotinmap)
        RC = tkt.Button(frame1_1, image= RunCharts_img ,borderwidth=0, command = lambda : RunChartParameters(window3, 1))    
        hm.photo = HeatMap_img
        RC.photo = RunCharts_img
        hm.pack(side = LEFT,padx = 5, pady = 5)
        RC.pack(side = LEFT,padx = 5, pady = 5)
        
    def plotmap(p_table):
        
        no_hrs = int((end_time-st_time).seconds/3600)+24*(end_time-st_time).days
        if(no_hrs>48):
            Msg = mb.askyesno(title='Warning', message= 'The selected time range is very large \nHeatmap would not be clear \nWould you still want to continue?') 
        elif(no_hrs<=48):
            Msg = True
        
        if(Msg == True): 
            plwindow = tk.ThemedTk()
            plwindow.get_themes()
            plwindow.set_theme('breeze')
            plwindow.geometry('1000x1000') 
            plwindow.configure(background= '#ffc3a0')
            plwindow.title('Heat Map')
                    
            f = Figure(figsize = (10,10))
            f.clf()
            f.suptitle('Heatmap for 5 minutes')
            canvas = FigureCanvasTkAgg(f, master = plwindow)
            canvas.get_tk_widget().pack(fill = BOTH, expand = True)
    
            canvas._tkcanvas.pack(side = TOP, fill = BOTH, expand = True)
            a = f.add_subplot(111)
            Heatmap = sns.heatmap(p_table, cmap = 'RdYlGn', annot = p_table.values, ax=a).set_yticklabels(labels = p_table.index, rotation = 0)
            
            plwindow.mainloop()
    
    def PieChart(win):
        for widget in frame4.winfo_children():
            widget.destroy()

        ttk.Label(frame4, text = 'Pie Chart').pack()
     
        OEE = res[2]
        UD_loss = (1-res[0])*(1-res[2])/(3-res[0]-res[1]-res[3])
        P_loss = (1-res[3])*(1-res[2])/(3-res[0]-res[1]-res[3])
        Q_loss = (1-res[1])*(1-res[2])/(3-res[0]-res[1]-res[3])
        
        backend_ =  mlb.get_backend() 
        mlb.use("Agg") 
        
        labels = ["OEE", 'UD_Loss', 'P_Loss','Q_Loss']
        values = [OEE*360, UD_loss*360, P_loss*360, Q_loss*360]
    
        colors = ['Green', 'Yellow', 'Red', 'DarkRed'] 
        explode =(0,0.1,0,0.1)
        
        f = plt.figure(figsize=(24,12))
        a = f.add_subplot(111)
        a.pie(values, explode = explode, colors=colors, startangle=90, autopct='%.1f%%', shadow = True) 
        a.legend(labels, loc = 'upper right')
        
        mlb.use(backend_)
        
        canvas = FigureCanvasTkAgg(f,frame4)
        canvas.draw()
        canvas.get_tk_widget().pack(side = TOP, fill= BOTH, expand=True)
   
        
    def RunChartParameters(win,plflag, l = None):
        for widget in frame3.winfo_children():
            widget.destroy()
        for widget in frame1_1.winfo_children():
            widget.destroy()
        global availability_hrly, quality_hrly, OEE_hrly, performance_hrly, hours, st, et, no_hrs
        # st = dt.datetime.strptime(st_time, '%Y-%m-%d %H:%M:%S') 
        # et = dt.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S') 
        st = st_time
        et = end_time
        hours = pd.date_range(start = st + dt.timedelta(hours = 1), end = et, freq = dt.timedelta(hours=1) )
        no_hrs = int((et - st).seconds/3600)+24*(et-st).days
        
        availability_hrly = []
        quality_hrly = []
        OEE_hrly = []
        performance_hrly = []   
        
        for i in range(int(no_hrs)):
            hr_res = calc_duration_parameters(st, st+dt.timedelta(hours = 1),l)
            availability_hrly.append(hr_res[0])
            quality_hrly.append(hr_res[1])
            OEE_hrly.append(hr_res[2])
            performance_hrly.append(hr_res[3])
            st = st+dt.timedelta(hours = 1)
         
        Performance_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Performance.png')
        OEE_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\OEE.png')
        Quality_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Quality.png')
        Availability_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Availability.png')
        
        availability_hrly = np.array(availability_hrly)
        quality_hrly = np.array(quality_hrly)
        OEE_hrly = np.array(OEE_hrly)
        performance_hrly = np.array(performance_hrly)
        sres_lbl = ttk.Label(frame3, text = 'Please select required parameter:', font = ('Arial Bold', 18))
        sres_lbl.pack(fill = BOTH, padx = 5, pady = 5)

        av = tkt.Button(frame3, image = Availability_img ,borderwidth=0,command = lambda : availability_plot(plflag))
        av.photo = Availability_img
        av.pack(side = LEFT, padx = 5, pady = 5)
        ql = tkt.Button(frame3, image = Quality_img ,borderwidth=0, command = lambda : quality_plot(plflag))
        ql.photo = Quality_img
        ql.pack(side = LEFT, padx = 5, pady = 5)
        oee =  tkt.Button(frame3, image = OEE_img,borderwidth=0, command = lambda : OEE_plot(plflag))
        oee.photo = OEE_img
        oee.pack(side = LEFT, padx = 5, pady = 5)
        perf = tkt.Button(frame3, image = Performance_img ,borderwidth=0, command = lambda : performance_plot(plflag))
        perf.photo = Performance_img
        perf.pack(side = LEFT, padx = 5, pady = 5) 
        
    def printout(l):
        res = calc_duration_parameters(st_time, end_time,l)
        txt = 'The production parameters are given by :' +'\n' + 'Availability : ' + str(res[0]) + '\n' + 'Quality : ' + str(res[1]) + '\n' + 'Performance : ' + str(res[3]) + '\n' + 'OEE : '  + str(res[2]) #AQOP
        sres_lbl.configure(text = txt)
        
    def begin(l = None):
        global flag, res, p_table
        res = calc_duration_parameters(st_time, end_time,l)
        sres_lbl.configure(text = '')
        
        for widget in frame1_1.winfo_children():
            widget.destroy()
        for widget in frame3.winfo_children():
            widget.destroy()
        for widget in frame4.winfo_children():
            widget.destroy()
            
        PieChart(window3)
        p_table = htmp_calc(l)
        
        HeatMap_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Heat Map.png')
        RunCharts_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Run Charts.png')
        ViewInteractive_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\View Interactive Plot in Browser.png')
        ProdQuan_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Production Quantities.png')

        params = tkt.Button(frame2, image = ProdQuan_img ,borderwidth=0, command = lambda: printout(l))
        params.photo = ProdQuan_img
        hm = tkt.Button(frame2, image = HeatMap_img ,borderwidth=0, command = lambda : plotmap(p_table))
        hm.photo = HeatMap_img
        RC = tkt.Button(frame2, image = RunCharts_img,borderwidth=0, command = lambda : RunChartParameters(window3,0,l))
        RC.photo = RunCharts_img
        ip = tkt.Button(frame2, image = ViewInteractive_img,borderwidth=0, command = inplot)
        ip.photo = ViewInteractive_img
        
        if(flag == 0):
            params.pack(side = LEFT, padx = 10)
            hm.pack(side = LEFT, padx = 10)
            RC.pack(side = LEFT, padx = 10)
            ip.pack(side = LEFT, padx = 10)
            flag = l
        
    def clicked3(l = None):
        global st_time ,end_time
        st_time = stime_cmb3.get()
        st_time = dt.datetime.strptime(st_time,'%Y-%m-%d %H:%M:%S')
        end_time = etime_cmb3.get()
        end_time = dt.datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S')
        timear = dataset['Date time']
        if st_time>end_time:
            mb.showerror("Date Error", "End time must be greater than start time")
        elif st_time < timear[0] - pd.to_timedelta('01:00:00'):
            mb.showerror("Date Error", "Start time is out of range")
            window3.mainloop()
        elif end_time> timear.iloc[-1]:
            mb.showerror("Date Error", "End time is out of range")
            window3.mainloop()
        begin(l)
        
    def bkclick():
        window3.destroy()
        window2()
    Go_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Go.png')
    LineA_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Line A.png')
    LineB_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Line B.png')
    Back_img = PhotoImage(file = r'C:\Users\KAUSHIK S CHETTIAR\Pictures\Internship buttons\Back.png')
    back_bt = tkt.Button(frb, image = Back_img ,borderwidth=0, command = bkclick)
    back_bt.pack(side = LEFT, padx = 10)
    begin_A = tkt.Button(frb, image = LineA_img ,borderwidth=0,command = lambda: clicked3('A'))
    begin_A.pack(side = RIGHT, padx = 10)
    begin_B = tkt.Button(frb, image = LineB_img ,borderwidth=0,command = lambda: clicked3('B'))
    begin_B.pack(side = RIGHT, padx = 10)    
    begin_O = tkt.Button(frb, image = Go_img, borderwidth=0,command = clicked3)
    begin_O.pack(side = RIGHT, padx = 10)    
    window3.mainloop()
        
#%%
if __name__ =='__main__':
    main()

