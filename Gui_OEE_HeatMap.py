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
import tkinter as tkt
from ttkthemes import themed_tk as tk
from tkinter import filedialog
from collections import Counter
import re
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.image as mpim
import matplotlib as mlb
import seaborn as sns
import plotly
import plotly.graph_objs as go
import plotly.figure_factory as ff
from PIL import ImageTk, Image
from tkinter import messagebox as mb
from fpdf import FPDF
import os
import time
pattern = r"Unnamed"
dataset = []
dataset2 = []
dataA = []
dataB = []
cycle_time = 0
dt_relevant = []
i_bn = 0
i_end = 0
runhrs = 1
chosen = " "
st_date = dt.datetime.now()
sd2 = dt.datetime.now()
end_date = dt.datetime.now()
ed2 = dt.datetime.now()
st_time = dt.datetime.now()
st2 = dt.datetime.now()
end_time = dt.datetime.now()
et2 = dt.datetime.now()
p_table = []
flag = 0
plot_flag = {'AvPlot':0,'QPlot':0,'PerPlot':0,'OPlot':0,'HeatMap':0,'Pie':0}
'Dictionary that stores 1 if the relevant plot has been plotted as an image and 0 otherwise'
cm_flag = 0
'Flag that stores 1 if the start time has been chosen, 0 if not. End time combobox is activated if flag is true'
res = []
res2 = []
#res_rd = []
dir_path = os.path.dirname(os.path.realpath(__file__))
backend_ = "Qt5Agg"

#%%

class table:
    def __init__(self, root, lst):
        self.rows = len(lst)
        self.columns = len(lst[0])
        for i in range(self.rows):
            self.fr = Frame(root)
            self.fr.pack(side = TOP)
            for j in range(self.columns):
                self.e = Label(self.fr, width = 20, text = str(lst[i][j]), font = ('Arial Bold',18), relief = RAISED, foreground = 'blue', background= 'yellow', borderwidth = 1)
                self.e.pack(side = LEFT)

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
def calc_duration_parameters(st, et, l = None, wf = 1):
    no_hrs = int((pd.to_datetime(et) - pd.to_datetime(st)).seconds/3600)+ 24*(et-st).days
    global dt_relevant, i_bn    
    
    if(wf == 1):
        data = dataset
        
        if(l == 'A'):
            data = dataA
            
        if(l=='B'):
            data = dataB
               
    if(wf == 2):
        data = dataset2
    
    
    dates = data['Date']
    time = data['Time']
    result = data['Result']
    DT_column = data['Date time']
    
    i_bn = np.where(DT_column > st)[0][0]
    i_end = np.where(DT_column > et)[0][0]
    dt_relevant = DT_column[i_bn:i_end]
    result_relevant = result[i_bn:i_end]
    time_part = pd.to_timedelta('00:00:01')*parttime
    
    if(len(dt_relevant)>0):
        time_differences = np.asarray([dt_relevant[i+1]-dt_relevant[i] for i in (dt_relevant.index[0] + np.arange(len(dt_relevant)-1))])
        unplanned_dt = time_differences.sum(initial = pd.to_timedelta('00:00:00'), where = (time_differences > time_part))
        no_ok = Counter(result_relevant)['OK']
        no_ng = Counter(result_relevant)['NG']
        
        total_possibility = no_hrs*3600/cycle_time
        availability = 1 - np.divide(unplanned_dt,dt.timedelta(hours = no_hrs))
        quality = no_ok/(no_ok + no_ng)
        OEE = np.divide(no_ok,total_possibility)
        performance = np.divide(OEE,(availability*quality))
        
    else: 
        availability = 0
        quality = 0
        OEE  = 0 
        performance = 0
    
    res = [availability, quality, OEE, performance]
       
    #if(l == 'A'):
      # resA = res
     #  return resA
    
    #if(l == 'B'):
       # resB = res
      #  return resB
    
    return res

#%%
def htmp_calc(l = None):
    'This cell prepares the data for calculation of hourly quantities'
    global p_table
    
    if(l == None or l == 'P'):
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
    starttime = dt_relevant[i_bn]
    starttime = starttime.replace(second = 0, minute = 0)
    rel_rge = (end_time - st_time).seconds/3600 + (end_time-st_time).days*24
    num = Hmapxt
    
    for i in range(int(rel_rge)):
        hourly_distribution.append(timear[np.where(timear > starttime+i*(onehr))[0][0]:(np.where(timear > starttime+(i+1)*(onehr))[0][0])-1])
        result_hrly.append(result[np.where(timear > starttime+i*(onehr))[0][0]:(np.where(timear > starttime+(i+1)*(onehr))[0][0])-1])
        
    'This part prepares the respective quantities for the generation of a heat map'
    result_minutely = []
    reqmin = pd.to_timedelta('00:01:00')*num
    divn = int(60/num)
    'This cell contains a loop to continue quantity preparation and converts them to appropriate types'
    for i in range(len(hourly_distribution)*divn):
        result_minutely.append(result[np.where(timear > starttime+i*(reqmin))[0][0]:(np.where(timear > starttime+(i+1)*(reqmin))[0][0])-1])
        
    'This cell calculates the most important quantities relating to the final calculations'    
    ok_minutely = np.array([Counter(result_minutely[i])['OK'] for i in range(len(result_minutely))])
    st2 = st_time + dt.timedelta(hours = 1)
    et2 = end_time - dt.timedelta(hours = 1)
    h1 = np.array([[str(i)]*divn for i in pd.date_range(st_time, et2, freq = '1H')]).flatten()
    h2 = np.array([[str(i)]*divn for i in pd.date_range(st2, end_time, freq = '1H')]).flatten()
    m1 = np.arange(num, 60+num ,num)
    m2 = m1-num
    hString = np.array(["{0} - {1}".format(v1,v2) for v1,v2 in zip(h1,h2)])
    mString = np.array(["{1} - {0}".format(v1,v2) for v1, v2 in zip(m1,m2)]*len(hourly_distribution))
    df = pd.DataFrame({'hours': hString, 'minutes': mString, 'OK': ok_minutely}, index = np.arange(divn*len(hourly_distribution)))
    p_table = pd.pivot_table(df, values ='OK', index ='hours' ,columns ='minutes')
    in1 = [hString[i*divn] for i in np.arange(len(hourly_distribution))]
    in2 = mString[0:divn]
    p_table = p_table.reindex(in1)
    p_table.columns = p_table.columns.reindex(in2)[0]
    return p_table        

#%%    
def availability_plot(plflag, l = None):
    global plot_flag
    avg = availability_hrly.mean()* np.ones(int(no_hrs/runhrs))
    std = availability_hrly.std()* np.ones(int(no_hrs/runhrs))
    
    upper_1 = avg + std*1
    upper_2 = avg + std*2
    upper_3 = avg + std*3
    lower_1 = avg - std*1
    lower_2 = avg - std*2
    lower_3 = avg - std*3
    
    if(plflag == 0):
        f = Figure(figsize=(10,10))
        a = f.add_subplot(111)
        
        #if(plot_flag['AvPlot']==0):
    
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
        
        if(l=='P'):
            f.savefig(dir_path + '/temp/availability.png')
        else:
            availability_plot = tk.ThemedTk()
            availability_plot.get_themes()
            availability_plot.set_theme('clearlooks')
            availability_plot.geometry('1200x1200')
            availability_plot.title('Availability Run Chart')
            canvas = FigureCanvasTkAgg(f,availability_plot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = TOP, fill= BOTH, expand=True)
            toolbar = NavigationToolbar2Tk(canvas,availability_plot)
            toolbar.update()
            canvas._tkcanvas.pack(side = TOP, fill= X, expand=True)
            plot_flag['AvPlot'] = 1
            availability_plot.mainloop()    
       # else:
        #    canvas = Canvas(availability_plot)
         #   canvas.pack()
          #  img = ImageTk.PhotoImage(Image.open(dir_path+'/temp/availability.png'))
           # canvas.create_image(20,20, anchor = NW, image = img)


        mlb.use(backend_)   
           
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

def quality_plot(plflag, l = None):
    global plot_flag
    avg = quality_hrly.mean()* np.ones(int(no_hrs/runhrs))
    std = quality_hrly.std()* np.ones(int(no_hrs/runhrs))
    
    upper_1 = avg + std*1
    upper_2 = avg + std*2
    upper_3 = avg + std*3
    lower_1 = avg - std*1
    lower_2 = avg - std*2
    lower_3 = avg - std*3
   
    if(plflag == 0):
     
     f = Figure(figsize=(10,10))
     a = f.add_subplot(111)
     #if(plot_flag['QPlot'] == 0):
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
        
     if l == 'P':
        f.savefig(dir_path + '/temp/quality.png')  
     
     else:
         quality_plot = tk.ThemedTk()
         quality_plot.get_themes()
         quality_plot.set_theme('clearlooks')
         quality_plot.geometry('1200x1200')
         quality_plot.title('Quality Run Chart') 
         canvas = FigureCanvasTkAgg(f,quality_plot)
         canvas.draw()
         canvas.get_tk_widget().pack(side = TOP, fill= BOTH, expand=True)   
         toolbar = NavigationToolbar2Tk(canvas,quality_plot)
         toolbar.update()
         canvas._tkcanvas.pack(side = TOP, fill= BOTH, expand=True)
         plot_flag['QPlot'] = 1
         quality_plot.mainloop()   
     #else:
         #canvas = Canvas(availability_plot)
         #canvas.pack()
         #canvas.create_image(20,20, anchor = NW, image = img)
         #img = ImageTk.PhotoImage(Image.open(dir_path+'/temp/quality.png'))

     mlb.use(backend_)
    
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

def OEE_plot(plflag, l=None):
    global plot_flag
    avg = OEE_hrly.mean()* np.ones(int(no_hrs/runhrs))
    std = OEE_hrly.std()* np.ones(int(no_hrs/runhrs))
    
    upper_1 = avg + std*1
    upper_2 = avg + std*2
    upper_3 = avg + std*3
    lower_1 = avg - std*1
    lower_2 = avg - std*2
    lower_3 = avg - std*3


    if(plflag == 0):
        f = Figure(figsize=(10,10))
        a = f.add_subplot(111)   
        #if(plot_flag['OPlot']==0):
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
        
        if l == 'P':
            f.savefig(dir_path + '/temp/oee.png')            
        else:
            OEE_plot = tk.ThemedTk()
            OEE_plot.get_themes()
            OEE_plot.set_theme('clearlooks')
            OEE_plot.geometry('1200x1200')
            OEE_plot.title('OEE Run Chart')    
            
            canvas = FigureCanvasTkAgg(f,OEE_plot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = TOP, fill= BOTH, expand=True)       
            toolbar = NavigationToolbar2Tk(canvas,OEE_plot)
            toolbar.update()
            canvas._tkcanvas.pack(side = TOP, fill= BOTH, expand=True)
            plot_flag['OPlot'] = 1
            #else:
             #canvas = Canvas(availability_plot)
             #canvas.pack()
             #img = ImageTk.PhotoImage(Image.open(dir_path+'/temp/oee.png'))
             #canvas.create_image(20,20, anchor = NW, image = img)         
            OEE_plot.mainloop() 
            
        mlb.use(backend_)
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

def performance_plot(plflag , l = None):
    global plot_flag
    avg = performance_hrly.mean()* np.ones(int(no_hrs/runhrs))
    std = performance_hrly.std()* np.ones(int(no_hrs/runhrs))
    
    upper_1 = avg + std*1
    upper_2 = avg + std*2
    upper_3 = avg + std*3
    lower_1 = avg - std*1
    lower_2 = avg - std*2
    lower_3 = avg - std*3

    if(plflag == 0):
        f = Figure(figsize=(10,10))
        a = f.add_subplot(111)  
        #if(plot_flag['PerPlot'] == 0):
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
        
        if l == 'P':
            f.savefig(dir_path + '/temp/performance.png')           
        else: 
            performance_plot = tk.ThemedTk()
            performance_plot.get_themes()
            performance_plot.set_theme('clearlooks')
            performance_plot.geometry('1200x1200')
            performance_plot.title('Performance Run Chart')
           
    
            canvas = FigureCanvasTkAgg(f,performance_plot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = TOP, fill= BOTH, expand=True)       
            toolbar = NavigationToolbar2Tk(canvas,performance_plot)
            toolbar.update()
            canvas._tkcanvas.pack(side = TOP, fill= BOTH, expand=True)
            plot_flag['PerPlot'] = 1
            #else:
             #canvas = Canvas(availability_plot)
             #canvas.pack()
             #img = ImageTk.PhotoImage(Image.open(dir_path+'/temp/performance.png'))
             #canvas.create_image(20,20, anchor = NW, image = img)            
            performance_plot.mainloop()
        mlb.use(backend_)
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
    style = Style() 
    style.configure('W.TButton', font =
       ('Times New Roman', 12, 'bold'), 
        foreground = 'red', background = '#0000FF')
    
    def clicked1():
        file = filedialog.askopenfilename(filetypes = (("Comma Separated Variables","*.csv"),("all files","*.*")))
        global dataset 
        dataset = pd.read_csv(file, encoding = 'latin1')
        
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
            
        dataset['Date time'] = pd.Series([dt.datetime.strptime((dataset['Date'][i]+' '+dataset['Time'][i]),'%d-%m-%Y %H:%M:%S') for i in dataset.index])
        dataset = dataset.sort_values(by = 'Date time')
        dataset.index = np.arange(len(dataset))
        calc_cycle_time()
        window1.destroy()
        window2(wf = 1)
        
    cfim = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Choose File.png'))
    ch_bt1 = tkt.Button(fr1, image = cfim, borderwidth = 0,command = clicked1)
    ch_bt1.photo = cfim
    ch_bt1.pack(side = LEFT, padx = 10, pady = 10)
    window1.mainloop()
    
#%%
def window2(wf = 1):
    #global date
    
    if(wf == 1):
        data = dataset
         
    if(wf == 2):
        data = dataset2
        
    date = data['Date']
    #date = [dt.datetime.strptime(str(date[i]), '%d-%m-%Y') for i in range(len(date))]
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
    end_cmb2 = Combobox(fr1, state = 'disabled')
    sd = dt.datetime.now()
    ed = dt.datetime.now()
    
    def dchosen(a):
        nonlocal sd
        sd = dt.datetime.strptime(a + ' 00:00:00','%d-%m-%Y %H:%M:%S')
        end_cmb2.configure(state = 'normal')
        ed = dt.datetime.strptime(str(pd.to_datetime(max(np.unique(date)))),'%Y-%m-%d %H:%M:%S').date()
        ed = dt.datetime.strftime(ed,'%d-%m-%Y')
        pdi = pd.date_range(start = sd.date(), end = ed, freq = '1D')
        edi = tuple(np.asarray([str(dt.datetime.strftime(dt.datetime.strptime(str(pdi[i]),'%Y-%m-%d %H:%M:%S').date(),'%d-%m-%Y')) for i in range(len(pdi))]))
        end_cmb2['values'] = edi
        end_cmb2.current(0)
        
    strt_cmb2.pack(side = LEFT, padx = 5)
    strt_cmb2['values'] =tuple(np.unique(date))
    strt_cmb2.current(0)
    strt_cmb2.bind("<<ComboboxSelected>>",lambda x:dchosen(strt_cmb2.get()))
    edate_lbl2 = Label(fr1, text = 'Choose ending date').pack(side = LEFT, pady = 5, padx = 5)
    end_cmb2.pack(side = LEFT, padx = 5)
    style = Style() 
    style.configure('W.TButton', font =
       ('Times New Roman', 12, 'bold'), 
        foreground = 'red', background = '#0000FF')
 
    
    def clicked2():
        global end_date, st_date, sd2, ed2
        #st_date = pd.to_datetime(strt_cmb2.get())
        ed = dt.datetime.strptime(end_cmb2.get()+' 00:00:00','%d-%m-%Y %H:%M:%S')
        
        if wf == 1:
            st_date = sd
            end_date = ed
        if wf == 2:
            sd2 = sd
            ed2 = ed
            
        window2.destroy()
        
        if wf == 1:
            window3()
        else:
            comp_lin('R')
        
    def bkclick():
        window2.destroy()
        if wf == 1:
            main()        
        if wf == 2:
            comp_lin('X')
        
    if wf == 1:
        bim_ = Image.open(dir_path+'/Internship buttons/Back.png')
        bim = ImageTk.PhotoImage(bim_)
        back_bt = tkt.Button(fr2, image = bim, borderwidth = 0,command = bkclick) 
        back_bt.photo = bim
        back_bt.pack(side = LEFT, padx = 10)
        ptim_ = Image.open(dir_path+'/Internship buttons/Proceed to Time Range Selection.png')
        ptim = ImageTk.PhotoImage(ptim_)
        time_bt = tkt.Button(fr2, image = ptim, borderwidth = 0, command = clicked2)
        time_bt.photo = ptim
        time_bt.pack(side = BOTTOM, pady = 5)
    
    if wf == 2:
        #bim_1 = Image.open(dir_path+'/Internship buttons/Back2.png')
        #bim1 = ImageTk.PhotoImage(bim_1)
        back_bt = Button(fr2, text = 'Back', style = 'W.TButton', command = bkclick) 
        #back_bt.photo = bim1
        back_bt.pack(side = LEFT, padx = 10)
        #ptim_1 = Image.open(dir_path+'/Internship buttons/Proceed to Time Range Selection2.png')
        #ptim1 = ImageTk.PhotoImage(ptim_1)
        time_bt = Button(fr2, text = 'Proceed to Time Range Selection', command = clicked2)
        #time_bt.photo = ptim
        time_bt.pack(side = BOTTOM, pady = 5)  
        
    window2.mainloop()
 
#%%

def printout(fr, res_rd):
    
    for widget in fr.winfo_children():
        widget.destroy()
        
    #txt = 'The production parameters are given by :' 
    #+'\n' + 'Availability : ' + str(res_rd[0]) + '\n' + 'Quality : ' + str(res_rd[1]) + '\n' + 'Performance : ' + str(res_rd[3]) + '\n' + 'OEE : '  + str(res_rd[2]) 
    #sres_lbl.configure(text = txt)
    lst = list({'Availability':res_rd[0],'Quality':res_rd[1],'Performance':res_rd[3],'OEE':res_rd[2]}.items())
    table(fr, lst)

    
#%%
def PieChartDraw(results, fr):
    
    OEE = results[2]
    UD_loss = (1-results[0])*(1-results[2])/(3-results[0]-results[1]-results[3])
    P_loss = (1-results[3])*(1-results[2])/(3-results[0]-results[1]-results[3])
    Q_loss = (1-results[1])*(1-results[2])/(3-results[0]-results[1]-results[3])
    
    backend_ =  mlb.get_backend() 
    mlb.use("Agg") 
    
    labels = ["OEE", 'UD_Loss', 'P_Loss','Q_Loss']
    values = [OEE*360, UD_loss*360, P_loss*360, Q_loss*360]

    colors = ['Green', 'Yellow', 'Red', 'DarkRed'] 
    explode =(0,0.1,0,0.1)
    
    f = plt.figure(figsize=(6,6))
    a = f.add_subplot(111)
    a.pie(values, explode = explode, colors=colors, startangle=90, autopct='%.1f%%', shadow = True) 
    a.legend(labels, loc = 'upper right')
    f.savefig(dir_path+'/temp/pie.png')
    mlb.use(backend_)
    
    canvas = FigureCanvasTkAgg(f,fr)
    canvas.draw()
    canvas.get_tk_widget().pack(fill= BOTH, expand=True)
    plot_flag['Pie'] = 1

#%%
def window3():
    global flag
    flag = 0
    s_st = (st_date + dt.timedelta(0))
    s_et = (st_date + dt.timedelta(hours=23))
    e_st = (end_date + dt.timedelta(0))
    e_et = (end_date + dt.timedelta(hours =23))
    s_dti = tuple(pd.date_range(start = s_st, end = s_et, freq = '1H'))

    window3 = tk.ThemedTk()
    window3.get_themes()
    window3.set_theme('breeze')
    window3.geometry('1650x1200')
    window3.configure(background= '#ffc3a0')
    frame1 = Frame(window3, relief = RAISED)
    frame1.pack(fill = X)
    window3.title('Time selection') 
    stime_lbl3 = Label(frame1, text = 'Choose starting time:', width = 20)
    stime_lbl3.pack(side = LEFT, padx = 5, pady = 5)
    stime_cmb3 = Combobox(frame1)
    etime_cmb3 = Combobox(frame1, state = 'disabled')
    
    def chosen(a):
        global st_time
        st_time = dt.datetime.strptime(a,'%Y-%m-%d %H:%M:%S')
        etime_cmb3.configure(state = 'normal')
        e_dti = pd.date_range(start = a, end = e_et, freq = '1H')
        e_dti = tuple(e_dti[np.where(e_dti >= pd.to_datetime(end_date))])
        etime_cmb3['values'] = e_dti
        etime_cmb3.current(0)       
        
    stime_cmb3.pack(side = LEFT, padx = 5, pady = 5)
    stime_cmb3['values'] =s_dti
    stime_cmb3.current(0)
    stime_cmb3.bind("<<ComboboxSelected>>", lambda x: chosen(stime_cmb3.get()))
    etime_lbl3 = Label(frame1, text = 'Choose ending time:').pack(side = LEFT, padx = 5, pady = 5)
    etime_cmb3.pack(side = LEFT, padx = 5, pady = 5)
    frame2= Frame(window3, relief = RAISED, borderwidth = 2, height = 50)
    frame2.pack(fill = X)
    frame2_2 = Frame(window3, relief = FLAT)
    frame2_2.pack(fill = X)
    frame1_1= Frame(window3, relief = RAISED, borderwidth = 2, height = 10)
    frame1_1.pack(fill = X)
    frame3= Frame(window3, relief = RAISED, borderwidth = 2, height = 10)
    frame3.pack(fill = X)
    sres_lbl = Label(frame2, text = '', font = ('Arial Bold', 18), foreground ='blue')
    sres_lbl.pack(side= BOTTOM, fill=X, padx = 5, pady = 5)
    frame4= Frame(window3, relief = RAISED, borderwidth = 2, height = 10)
    frame4.pack(fill = X)
    style = Style() 
    style.configure('W.TButton', font =
       ('Times New Roman', 12,'bold'), 
        foreground = 'red', background = '#0000FF') 
    
    lA = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Line A.png'))
    lB = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Line B.png'))
    proq = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Production Quantities.png'))
    him = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Heat Map.png'))
    rcim = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Run Charts.png')) 
    ipim = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/View Interactive Plot in Browser.png'))

    def plotinmap():
        no_hrs = int((end_time-st_time).seconds/3600)+24*(end_time-st_time).days
        if(no_hrs>48):
            Msg = mb.askyesno(title='Warning', message= 'The selected time range is very large \nHeatmap would not be clear \nDo you still want to continue?') 
        elif(no_hrs<=48):
            Msg = True
            
        if Msg == True:
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
        hm = tkt.Button(frame1_1, image = him, borderwidth = 0, command = plotinmap)
        hm.photo = him
        RC = tkt.Button(frame1_1, image = rcim, borderwidth = 0, command = lambda : RunChartParameters(window3, 1))
        RC.photo = rcim
        hm.pack(side = LEFT,padx = 5, pady = 5)
        RC.pack(side = LEFT,padx = 5, pady = 5)
        
    def plotmap(p_table, l = None):
        #global plot_flag
        no_hrs = int((end_time-st_time).seconds/3600)+24*(end_time-st_time).days
        if(no_hrs>48):
            Msg = mb.askyesno(title='Warning', message= 'The selected time range is very large \nHeatmap would not be clear \nWould you still want to continue?') 
        elif(no_hrs<=48):
            Msg = True
            
        if Msg == True:
            f = Figure(figsize = (30,10))
            f.clf()
            f.suptitle('Heatmap for 5 minutes')
            a = f.add_subplot(111)
            #val = np.array([str(p_table.values[i][j]) for i in range(len(p_table.values)) for j in range(len(p_table.values[0]))])
            #val = val.reshape(np.shape(p_table.values))
            sns.heatmap(p_table, cmap = 'RdYlGn', annot_kws = {'size':15},annot = p_table.values, fmt = 'd', ax=a).set_yticklabels(labels = p_table.index, rotation = 0)
            
            if l == 'P':
                f.savefig(dir_path + '/temp/heatmap.png')
            else:
                plwindow = tk.ThemedTk()
                plwindow.get_themes()
                plwindow.set_theme('clearlooks')
                plwindow.configure(background= '#ffc3a0')
                canvas = FigureCanvasTkAgg(f, master = plwindow)
                canvas.draw()
                canvas.get_tk_widget().pack(fill = BOTH, expand = True)
                toolbar = NavigationToolbar2Tk(canvas, plwindow)
                toolbar.update()
                canvas._tkcanvas.pack(side = TOP, fill = BOTH, expand = True)
                plwindow.mainloop()
 
    def Settings():
        try:
            with open("data.txt") as f:
                dict = eval(f.read())
                Hmapxt = int(dict['Hmapxt'])
                parttime = int(dict['parttime'])
            f.close()
        except FileNotFoundError:
            Hmapxt = 5
            parttime = 60


        Setwindow = tk.ThemedTk()
        Setwindow.get_themes()
        Setwindow.set_theme('breeze')
        Setwindow.configure(background= '#C0C0C0')
        ws = Setwindow.winfo_screenwidth()
        s = int(ws/2)-500
        Setwindow.geometry('1000x250+%d+0' %(s))
        Setwindow.title('Settings')
        global runhrs
        no_hrs = int((end_time - st_time).seconds/3600)+24*(end_time-st_time).days
        
        def callback(self):
            try:
                if int(nameEntered1.get())!= parttime:
                    Apply.configure(state='normal')
            except ValueError:
                mb.showerror('Invalid Entry', 'Partition Time Difference has to be numerical value')
                
        def nchosen(self):
            if int(timeEntered.get())!= Hmapxt:
                Apply.configure(state='normal')
        
        def hchosen(self):
            global runhrs
            if int(timeEntered2.get())!= runhrs:
                Apply.configure(state='normal')
                
        def applychanges():
            global runhrs
            try:
                Hmapxt= timeEntered.get()
                parttime = int(nameEntered1.get())
                runhrs = int(timeEntered2.get())
                if parttime>1250:
                    mb.showerror("Value Error","Partition Time Difference value Entered is too high")
                    Setwindow.mainloop()
                elif parttime<25:
                    mb.showerror("Value Error","Partition Time Difference value Entered is too low")
                    Setwindow.mainloop()
                
                
                Msg = mb.askyesno(title='Apply Changes', message= 'Are you sure you want to apply the Changes?') 
                if Msg==True:
                    Hmapxt= timeEntered.get()
                    parttime = nameEntered1.get()
                    Dictionary = {'Hmapxt':str(Hmapxt),'parttime':str(parttime)}
                    out = open("data.txt",'w')
                    out.write(str(Dictionary))
                    out.close()
                    Setwindow.destroy()
                    begin()
                else:
                    Setwindow.mainloop()
            except ValueError:
                mb.showerror('Invalid Entry', 'Partition Time Difference has to be numerical value')
                 
               
        def back():
            Setwindow.destroy()
        
        tkt.Label(Setwindow,text='Settings',font=('Century',15,'bold','italic'),bg= 'black',fg='white').place(relx=0.475, rely=0)

        tkt.Label(Setwindow,text='Any Time Difference Greater than this would be taken as Unplanned Down Time: ', font=('Times New Roman',15,'bold'),bg= '#C0C0C0').place(relx=0.1, rely=0.2)
        
        
        name1 = tkt.IntVar(Setwindow,value=parttime)
        nameEntered1 = Entry(Setwindow, width = 7, font=('Times New Roman',15), textvariable = name1)
        nameEntered1.place(relx=0.8, rely=0.2)
        nameEntered1.bind("<Return>", callback)
        tkt.Label(Setwindow,text='sec',font=('Times New Roman',15,'italic','bold'),bg= '#C0C0C0', fg='black').place(relx=0.9,rely=0.2)
        
        
        tkt.Label(Setwindow,text='Each block of Heat Map is for this time duration                                                       :', font=('Times New Roman',15,'bold'),bg= '#C0C0C0').place(relx=0.1, rely=0.35)
        
        
        
        mins = tkt.IntVar(Setwindow,value=Hmapxt)
        timeEntered = Combobox(Setwindow, width = 7, font=('Times New Roman',15), textvariable = mins)
        timeEntered.place(relx=0.8, rely=0.35)
        timeEntered['values']=(5,6,10,15,20,30)
        timeEntered.bind("<<ComboboxSelected>>",nchosen)
        
        tkt.Label(Setwindow,text='Unit number of hours on x axis for plotting Run Charts                                             : ', font=('Times New Roman',15,'bold'),bg= '#C0C0C0').place(relx=0.1, rely=0.5)
        name2 = tkt.IntVar(Setwindow,value=runhrs)
        timeEntered2 = Combobox(Setwindow, width = 7, font=('Times New Roman',15), textvariable = name2)
        timeEntered2.place(relx=0.8, rely=0.5)
        chrs=[i for i in range(1, no_hrs) if no_hrs%i==0]
        timeEntered2['values'] = tuple(chrs)
        timeEntered2.bind("<<ComboboxSelected>>",hchosen)
        tkt.Label(Setwindow,text='hr(s)',font=('Times New Roman',15,'italic','bold'),bg= '#C0C0C0', fg='black').place(relx=0.9,rely=0.5)
        
        
        Apply = tkt.Button(Setwindow,text='Apply Changes',state='disabled', font= ('Times New Roman',15,'italic'),bg='black',fg='white', command = applychanges)
        Apply.place(relx=0.4625,rely=0.65)
        tkt.Label(Setwindow,text='min',font=('Times New Roman',15,'italic','bold'),bg= '#C0C0C0', fg='black').place(relx=0.9,rely=0.35)
        
        Back = tkt.Button( Setwindow,text='Back', font= ('Times New Roman',15,'italic'),bg='black',fg='white', command= back)
        Back.place(relx=0.5, rely=0.85)
        Setwindow.lift()
        Setwindow.call('wm', 'attributes', '.', '-topmost', True)
        Setwindow.mainloop()
    
    def PieChart(win):
        for widget in frame4.winfo_children():
            widget.destroy()

        ttk.Label(frame4, text = 'Pie Chart').pack()
        
        PieChartDraw(res, frame4)
    
    
    def RunChartParameters(win,plflag, l = None):
        for widget in frame3.winfo_children():
            widget.destroy()
        for widget in frame1_1.winfo_children():
            widget.destroy()
            
        global availability_hrly, quality_hrly, OEE_hrly, performance_hrly, hours, no_hrs
        st = st_time
        et = end_time
        hours = pd.date_range(start = st + dt.timedelta(hours = runhrs), end = et, freq = dt.timedelta(hours=runhrs))
        no_hrs = int((et - st).seconds/3600) + 24*(end_time-st_time).days
        
        availability_hrly = []
        quality_hrly = []
        OEE_hrly = []
        performance_hrly = []   
        
        for i in range(int(no_hrs)):
            hr_res = calc_duration_parameters(st, st+dt.timedelta(hours = runhrs))
            availability_hrly.append(hr_res[0])
            quality_hrly.append(hr_res[1])
            OEE_hrly.append(hr_res[2])
            performance_hrly.append(hr_res[3])
            st = st+dt.timedelta(hours = runhrs)
            
        availability_hrly = np.array(availability_hrly)
        quality_hrly = np.array(quality_hrly)
        OEE_hrly = np.array(OEE_hrly)
        performance_hrly = np.array(performance_hrly)
        
    
        Availability_img = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Availability.png'))
        Performance_img = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Performance.png'))
        OEE_img = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/OEE.png'))
        Quality_img = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Quality.png'))
        
        
        if l != 'P':
            sres_lbl = ttk.Label(frame3, text = 'Please select required parameter:', font = ('Arial Bold', 18))
            sres_lbl.pack(fill = BOTH, padx = 5, pady = 5)
            av = ttk.Button(frame3, image = Availability_img,command = lambda : availability_plot(plflag))
            av.photo = Availability_img
            av.pack(side = LEFT, padx = 5, pady = 5)
            ql = ttk.Button(frame3, image = Quality_img, command = lambda : quality_plot(plflag))
            ql.photo = Quality_img
            ql.pack(side = LEFT, padx = 5, pady = 5)
            oee =  ttk.Button(frame3, image = OEE_img, command = lambda : OEE_plot(plflag))
            oee.photo = OEE_img
            oee.pack(side = LEFT, padx = 5, pady = 5)
            perf = ttk.Button(frame3, image = Performance_img , command = lambda : performance_plot(plflag))
            perf.photo = Performance_img
            perf.pack(side = LEFT, padx = 5, pady = 5) 
        
    '''    
    def printout():
        txt = 'The production parameters are given by :' 
        #+'\n' + 'Availability : ' + str(res_rd[0]) + '\n' + 'Quality : ' + str(res_rd[1]) + '\n' + 'Performance : ' + str(res_rd[3]) + '\n' + 'OEE : '  + str(res_rd[2]) 
        sres_lbl.configure(text = txt)
        lst = list({'Availability':res_rd[0],'Quality':res_rd[1],'Performance':res_rd[3],'OEE':res_rd[2]}.items())
        table(frame2_2, lst)
    '''   
    
    def begin(l = None):
        global flag, res, plot_flag, p_table, Hmapxt, parttime
        
        try:
            with open("data.txt") as f:
                dict = eval(f.read())
                Hmapxt = int(dict['Hmapxt'])
                parttime = int(dict['parttime'])
            f.close()
        except FileNotFoundError:
            Hmapxt = 5
            parttime = 60
            
        
        for k in plot_flag.keys():
            plot_flag[k] = 0
            
        res = calc_duration_parameters(st_time, end_time,l, wf = 1)
        res_rd = np.asarray([str(round(100*res[i],2))+'%' for i in range(len(res))])
        sres_lbl.configure(text = '')
        
        for widget in frame1_1.winfo_children():
            widget.destroy()
        for widget in frame2_2.winfo_children():
            widget.destroy()       
        for widget in frame3.winfo_children():
            widget.destroy()
        for widget in frame4.winfo_children():
            widget.destroy()        
            
        p_table = htmp_calc(l)
        PieChart(window3)
        
        image3 = Image.open(dir_path+'/Internship buttons/gear.png')
        image3 = image3.resize((30,30),Image.ANTIALIAS)
        Set_image=ImageTk.PhotoImage(image3)
        Set_bt = tkt.Button(frame2, image = Set_image,borderwidth=0,command = Settings)
        Set_bt.photo = Set_image
        com_lin = Button(frame2, text = 'Compare high speed lines', style = 'W.TButton', command = lambda : comp_lin('C'))
        #begin_A.photo = lA
        com_test = Button(frame2, text = 'Compare test lines', style = 'W.TButton', command = lambda: comp_lin('T'))
        #begin_B.photo = lB
        Gpdf = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Generate PDF Report.png'))
        begin_rep= tkt.Button(frame2, image = Gpdf, borderwidth = 0, command = lambda: gen_pdf(res_rd))
        begin_rep.photo = Gpdf
        params = tkt.Button(frame2, image = proq, borderwidth = 0, command = lambda : printout(frame2_2, res_rd))
        params.photo = proq
        hm = tkt.Button(frame2, image = him, borderwidth = 0, command = lambda : plotmap(p_table))
        hm.photo = him
        RC = tkt.Button(frame2, image = rcim, borderwidth = 0, command = lambda : RunChartParameters(window3,0,l))
        RC.photo = rcim
        ip = tkt.Button(frame2, image = ipim, borderwidth = 0, command = inplot)
        ip.photo = ipim
            
        if(flag == 0):
            params.pack(side = LEFT, padx = 10)
            hm.pack(side = LEFT, padx = 10)
            RC.pack(side = LEFT, padx = 10)
            ip.pack(side = LEFT, padx = 10)
            com_lin.pack(side = RIGHT, padx = 10)
            com_test.pack(side = RIGHT, padx = 10)
            begin_rep.pack(side = RIGHT, padx = 10)
            Set_bt.pack(side = RIGHT, padx=(10,20))
            flag = 1
  

    def gen_pdf(res_rd):           
        mbx = tk.ThemedTk()
        mbx.get_themes()
        mbx.set_theme('breeze')
        mbx.geometry('450x150')
        mbx.title('Please Wait')
        fl = 0
        
        lbx = Label(mbx, text = 'The PDF is being generated. Kindly Wait', font = ('Arial Bold',10))
        btx = Button(mbx, text = 'Proceed', state = 'disabled', command = mbx.destroy)
        lbx.pack()
        btx.pack(pady = 15)
        
        def doit():
            
            RunChartParameters(window3, 0, 'P')
            availability_plot(0,'P')
            quality_plot(0,'P')
            performance_plot(0,'P')
            OEE_plot(0,'P')
            plotmap(p_table,'P')
                
            pdf = FPDF()
            pdf.set_title('Report$'+str(st_time) + ' to ' + str(end_time))
            pdf.add_page()
            pdf.set_font('Arial','B',20)
            pdf.cell(w = 0, txt = 'The Production Parameters for the given time range', align = 'C', border = 2, ln =1)
            pdf.ln(10)
            pdf.cell(w = 0, txt = 'Availability: ' + str(res_rd[0]), align = 'C', border = 2, ln = 1)
            pdf.ln(10)
            pdf.cell(w = 0, txt = 'Quality: ' + str(res_rd[1]), align = 'C', border = 2, ln = 1)
            pdf.ln(10)
            pdf.cell(w = 0, txt = 'Performance: ' + str(res_rd[3]), align = 'C', border = 2, ln = 1)
            pdf.ln(10)
            pdf.cell(w = 0, txt = 'OEE: ' + str(res_rd[2]), align = 'C', border = 2, ln = 1)
            pdf.image(dir_path+'/temp/pie.png', type = 'PNG', x = 5,y = 90, w = 200, h =150)
            pdf.add_page()
            pdf.cell(w = 0, txt = 'The Availability plot for selected time range')
            pdf.image(dir_path+'/temp/availability.png', type = 'PNG', x = 5,y = 50, w = 200, h =150)
            pdf.add_page()
            pdf.cell(w = 0, txt = 'The Quality plot for selected time range')
            pdf.image(dir_path+'/temp/quality.png', type = 'PNG', x = 5,y = 50, w = 200, h =150)
            pdf.add_page()
            pdf.cell(w = 0, txt = 'The Performance plot for selected time range')
            pdf.image(dir_path+'/temp/performance.png', type = 'PNG', x = 5,y = 50, w = 200, h =150)
            pdf.add_page()
            pdf.cell(w = 0, txt = 'The OEE plot for selected time range')
            pdf.image(dir_path+'/temp/oee.png', type = 'PNG', x = 5,y = 50, w = 200, h =150)
            pdf.add_page()
            pdf.cell(w = 0, txt = 'The Heat Map for selected time range')
            pdf.image(dir_path+'/temp/heatmap.png', type = 'PNG', x = 5,y = 50, w = 250, h =150)
            pdf.output('Report$'+str(st_time) + ' to ' + str(end_time)+'.pdf','F')
            
        
        def checkwrite():
            if os.path.isfile('Report$'+str(st_time) + ' to ' + str(end_time)+'.pdf'):
                btx.configure(state = 'normal')
                lbx.configure(text = 'PDF Generated, stored at ' + str(dir_path))
            else:
                checkwrite()
        
                
        mbx.after(500,doit)
        mbx.after(1000, checkwrite)
        mbx.lift()
        mbx.call('wm', 'attributes', '.', '-topmost', True)
        mbx.mainloop()
                
    def clicked3(l = None):
        global end_time
        end_time = etime_cmb3.get()
        end_time = dt.datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S')
        begin(l)
        
    def bkclick():
        window3.destroy()
        window2()

        
    bim = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Back.png'))
    back_bt = tkt.Button(frame1,image = bim, borderwidth = 0,command = bkclick)
    #back_bt = tkt.Button(frame1, image = bim, borderwidth = 0, command = bkclick)
    #back_bt.photo = bim
    back_bt.pack(side = RIGHT, padx = 10)
    bgim = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Go.png'))    
    begin_O = tkt.Button(frame1, image = bgim, borderwidth = 0, command = clicked3)
    begin_O.photo = bgim
    begin_O.pack(side = RIGHT, padx = 10)    
    window3.mainloop()
    
#%%

def comp_lin(l):
    
    if(l=='C'):
        global dataset2
        file2 = filedialog.askopenfilename(filetypes = (("Comma Separated Variables","*.csv"),("all files","*.*")))
        dataset2 = pd.read_csv(file2, encoding = 'latin')
        
        'Write a function to do the data reading. As the dataset has been obtained, the function will sort and create the Date time column'
        
        if {'Date','Time','Result','Line ID'}.issubset(dataset2.columns):
            print('')
        elif{' Date'}.issubset(dataset2.columns):
            mb.showerror("Data error", "Please remove space before 'Date' in column heading of the selected file")
        elif{' Time'}.issubset(dataset2.columns):
            mb.showerror("Data error", "Please remove space before 'Time' in column heading of the selected file")
        elif{' Result'}.issubset(dataset2.columns):
            mb.showerror("Data error", "Please remove space before 'Result' in column heading of the selected file")
        elif{' Date'}.issubset(dataset2.columns):
            mb.showerror("Data error", "Please remove space before 'Line ID' in column heading of the selected file")
        else:
            mb.showerror("Data error", "Selected file does not contain required data set")
            
        dataset2['Date time'] = pd.Series([dt.datetime.strptime(( dataset2['Date'][i] + ' ' + dataset2['Time'][i]),'%d-%m-%Y %H:%M:%S') for i in dataset2.index])
        dataset2 = dataset2.sort_values(by = 'Date time')
        dataset2.index = np.arange(len(dataset2))
        window2(wf = 2)

    if l =='R' or l == 'T':
        comp = tk.ThemedTk()
        comp.get_themes()
        comp.set_theme('breeze')
        comp.geometry('1000x600')
        comp.title('Comparison window')
        
        fr1 = Frame(comp, relief = FLAT, height = 100)
        fr1.pack(fill = X)
        fr2 = Frame(comp, relief = RAISED, height = 100)
        fr2.pack(fill = X)
        fr2_1 = Frame(fr2, relief = RAISED, height = 100, borderwidth = 5)
        fr2_1.pack(side = LEFT, fill = Y)
        fr2_2 = Frame(fr2, relief = RAISED, height = 100, borderwidth = 5)
        fr2_2.pack(side = LEFT, fill = Y)
        fr3 = Frame(comp, relief = RAISED, height = 200)
        fr3.pack(fill = X)
        fr3_1 = Frame(fr3, relief = RAISED, height = 200)
        fr3_1.pack(side = LEFT, fill = Y)
        fr3_2 = Frame(fr3, relief = RAISED, height = 200)
        fr3_2.pack(side = LEFT, fill = Y)    
        style = Style() 
        style.configure('W.TButton', font =
           ('Times New Roman', 12,'bold'), 
            foreground = 'red', background = '#0000FF') 
    
        if l == 'R':
            s_st = (sd2 + dt.timedelta(0))
            s_et = (sd2 + dt.timedelta(hours=23))
            e_st = (ed2 + dt.timedelta(0))
            e_et = (ed2 + dt.timedelta(hours =23))
            s_dtip = pd.date_range(start = s_st, end = s_et, freq = '1H')
            s_dti = tuple(np.asarray([str(dt.datetime.strftime(dt.datetime.strptime(str(s_dtip[i]),'%Y-%m-%d %H:%M:%S'),'%d-%m-%Y %H:%M:%S')) for i in range(len(s_dtip))]))    
            
            stime_lblc = Label(fr1, text = 'Choose starting time:', width = 20)
            stime_lblc.pack(side = LEFT, padx = 5, pady = 5)
            stime_cmbc = Combobox(fr1)
            etime_cmbc = Combobox(fr1, state = 'disabled')
            st2 = dt.datetime.now()
            et2 = dt.datetime.now()
            
            def chosen(a):
                #global st_time
                nonlocal st2
                st2 = dt.datetime.strptime(a,'%d-%m-%Y %H:%M:%S')
                etime_cmbc.configure(state = 'normal')
                pdi = pd.date_range(start = st2, end = e_et, freq = '1H')
                pdi = tuple(pdi[np.where(pdi >= pd.to_datetime(ed2))])
                edi = tuple(np.asarray([str(dt.datetime.strftime(dt.datetime.strptime(str(pdi[i]),'%Y-%m-%d %H:%M:%S'),'%d-%m-%Y %H:%M:%S')) for i in range(len(pdi))]))
                etime_cmbc['values'] = edi
                etime_cmbc.current(0)       
                
            stime_cmbc.pack(side = LEFT, padx = 5, pady = 5)
            stime_cmbc['values'] =s_dti
            stime_cmbc.current(0)
            stime_cmbc.bind("<<ComboboxSelected>>", lambda x: chosen(stime_cmbc.get()))
            etime_lblc = Label(fr1, text = 'Choose ending time:').pack(side = LEFT, padx = 5, pady = 5)
            etime_cmbc.pack(side = LEFT, padx = 5, pady = 5)
            
            def clickc():
                
                for widget in fr2_1.winfo_children():
                    widget.destroy()
                for widget in fr2_2.winfo_children():
                    widget.destroy()
                for widget in fr3_1.winfo_children():
                    widget.destroy()
                for widget in fr3_2.winfo_children():
                    widget.destroy()
                    
                nonlocal et2
                et2 = etime_cmbc.get()
                et2 = dt.datetime.strptime(str(end_time),'%Y-%m-%d %H:%M:%S')
                res2 = calc_duration_parameters(st2, et2, wf = 2)
                res_rd = np.asarray([str(round(100*res[i],2))+'%' for i in range(len(res))])
                res2_rd = np.asarray([str(round(100*res2[i],2))+'%' for i in range(len(res2))])
                printout(fr2_1, res_rd)
                printout(fr2_2, res2_rd)
                PieChartDraw(res, fr3_1)
                PieChartDraw(res2, fr3_2)
                lb1 = Label(fr2_1, text = 'Dataset 1', font = ('Arial Bold', 16)).pack()
                lb2 = Label(fr2_2, text = 'Dataset 2', font = ('Arial Bold', 16)).pack()
                
                ac_bt = Button(fr1, text = 'Accept', style = 'W.TButton', command = clickc)
                ac_bt.pack(side = LEFT)
                
        if l == 'T':
            resA = calc_duration_parameters(st_time, end_time, l ='A', wf = 1)
            resB = calc_duration_parameters(st_time, end_time, l ='B', wf = 1)
            resA_rd = np.asarray([str(round(100*resA[i],2))+'%' for i in range(len(resA))])
            resB_rd = np.asarray([str(round(100*resB[i],2))+'%' for i in range(len(resB))])
            printout(fr2_1, resA_rd)
            printout(fr2_2, resB_rd)
            PieChartDraw(resA, fr3_1)
            PieChartDraw(resB, fr3_2)            
            lb1 = Label(fr2_1, text = 'Line A', font = ('Arial Bold', 16)).pack()
            lb2 = Label(fr2_2, text = 'Line B', font = ('Arial Bold', 16)).pack()
                
        if l == 'X':
            comp.destroy()
        
        comp.mainloop()
        
#%%
if __name__ =='__main__':
    main()
