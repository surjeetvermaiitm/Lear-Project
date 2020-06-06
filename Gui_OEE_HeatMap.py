#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 29 14:21:52 2020

@author: syshain
"""

#%%
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from os import path
from collections import Counter
import re
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure
import seaborn as sns
pattern = r"Unnamed"
dataset = []
date = []
dt_relevant = []
i_bn = 0
i_end = 0
chosen = " "
st_date = dt.datetime.now()
end_date = dt.datetime.now()
st_time = dt.datetime.now()
end_time = dt.datetime.now()
availabililty_hrly = []
quality_hrly = []
OEE_hrly = []
performance_hrly = []
hours = []

#%%

def calc_duration_parameters():
    global dt_relevant, i_bn, i_end, cycle_time
    dates = dataset['Date']
    time = dataset['Time']
    result = dataset[' Result']
    DT_column = pd.Series([dt.datetime.strptime(dates[i] + ' '+ time[i], '%d-%m-%Y %H:%M:%S') for i in range(len(dates))])
    i_bn = np.where(DT_column > st_time)[0][0]
    i_end = np.where(DT_column > end_time)[0][0]
    dt_relevant = DT_column[i_bn:i_end]
    result_relevant = result[i_bn:i_end]
    time_differences = np.asarray([dt_relevant[i+1]-dt_relevant[i] for i in (dt_relevant.index[0] + np.arange(len(dt_relevant)-1))])
    max_rep = Counter(time_differences).most_common(4)
    'This line finds the most common time difference which can be taken as the ideal time required to produce one set of LH and RH recliners'
    cycle_time = (max_rep[1][0]).total_seconds()/4
    unplanned_dt = time_differences.sum(initial = pd.to_timedelta('00:00:00'), where = (time_differences > pd.to_timedelta('00:01:00')))
    no_ok = Counter(result)['OK']
    no_ng = Counter(result)['NG']
    total_possibility = 24*3600/cycle_time
    availability = 1 - unplanned_dt/pd.to_timedelta('24:00:00')
    quality = no_ok/(no_ok + no_ng)
    OEE = no_ok/total_possibility
    performance = OEE/(availability*quality)
    txt = 'The required results from the calculations are as follow:' + '\n' + 'OEE: ' + str(OEE) + '\n'+ 'Availability: ' + str(availability) + '\n' + 'Performance: ' + str(performance) + '\n' + 'Quality: ' + str(quality)
    return txt
    
#%%
def htmp_calc():
    'This cell prepares the data for calculation of hourly quantities'
    timear = pd.to_datetime(dataset['Date'] + ' ' + dataset['Time'])
    result = dataset[' Result']
    hourly_distribution = []
    result_hrly = []
    onehr = pd.to_timedelta('1:00:00')
    starttime = dt_relevant[i_bn]
    rel_rge = (dt.datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S') - dt.datetime.strptime(st_time,'%Y-%m-%d %H:%M:%S')).seconds/3600
    
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
    st2 = dt.datetime.strptime(st_time, '%Y-%m-%d %H:%M:%S') + dt.timedelta(hours = 1)
    et2 = dt.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S') - dt.timedelta(hours = 1)
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
def RunChartParameters(fr):
    global availability_hrly, quality_hrly, OEE_hrly, performance_hrly, hours
    starttime = pd.to_datetime(st_time)
    endtime = pd.to_datetime(end_time)
    required_time = endtime - starttime
 
    number = int(abs(int(required_time.seconds/3600)+required_time.days*24))
    # sres_lbl = Label(window5, text = st_time).grid(column = 1, row = 0)
    # eres_lbl = Label(window5, text = end_time).grid(column = 0, row =1)
    
    hours = np.arange(0,number)
    hourly_distribution = []
    result_hrly = []
    hrly_diff = []
    blank = 0
    onehr = pd.to_timedelta('01:00:00')
    dates = dataset['Date']
    time = dataset['Time']
    result = dataset[' Result']
    timear = pd.Series([dt.datetime.strptime(dates[i] + ' '+ time[i], '%d-%m-%Y %H:%M:%S') for i in range(len(dates))])
    
    for i in range(number):
        blank = (np.where(timear > starttime+(i)*(onehr))[0][0])
        hourly_distribution.append(timear[np.where(timear > (starttime+i*(onehr)))[0][0]:(np.where(timear > (starttime+(i+1)*(onehr)))[0][0]-1)])
        result_hrly.append(result[np.where(timear > starttime+i*(onehr))[0][0]:(np.where(timear > starttime+(i+1)*(onehr))[0][0])-1])
        hrly_diff.append([hourly_distribution[i][j+1] - hourly_distribution[i][j] for j in range(blank, blank + len(hourly_distribution[i])-1)])
    
    'This cell calculates the most important quantities relating to the final calculations'
    hrly_diff = np.array(hrly_diff)
    hrly_unplanned = []
    for i in range(len(hourly_distribution)):
        hrly_unplanned.append(np.array(hrly_diff[i]).sum(initial = pd.to_timedelta('00:00:00'), where  = (np.array(hrly_diff[i]) > pd.to_timedelta('00:01:00'))))
    ok_hrly = np.array([Counter(result_hrly[i])['OK'] for i in range(len(result_hrly))])
    ng_hrly = np.array([Counter(result_hrly[i])['NG'] for i in range(len(result_hrly))])
    total_possibility = 24*3600/cycle_time
    hrly_possibility = total_possibility/24;
    
    'This cell calculates all the final hourly quantities'
    availability_hrly = 1 - np.divide(hrly_unplanned,pd.to_timedelta('1:00:00'))
    quality_hrly = np.divide(ok_hrly,(ok_hrly + ng_hrly))
    OEE_hrly = ok_hrly / hrly_possibility
    performance_hrly = OEE_hrly/(availability_hrly*quality_hrly)
    
    Radiobutton(fr, text="Availability",command = availability_plot).pack()
    Radiobutton(fr, text="Quality", command = quality_plot).pack()

    Radiobutton(fr, text="OEE", command = OEE_plot).pack()
    
    Radiobutton(fr, text="Performance", command = performance_plot).pack()

#%%    
def availability_plot():
    availability_plot = Tk()
    availability_plot.geometry('1200x1200')
    availability_plot.title('Availability Run Chart')
    avg = availability_hrly.mean()* np.ones(hours.shape)
    std = availability_hrly.std()* np.ones(hours.shape)
    upper_1 = avg + std*1
    upper_2 = avg + std*2
    upper_3 = avg + std*3
    lower_1 = avg - std*1
    lower_2 = avg - std*2
    lower_3 = avg - std*3

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
    
#%%

def quality_plot():
    quality_plot = Tk()
    quality_plot.geometry('1200x1200')
    quality_plot.title('Quality Run Chart')
    avg = quality_hrly.mean()* np.ones(hours.shape)
    std = quality_hrly.std()* np.ones(hours.shape)
    upper_1 = avg + std*1
    upper_2 = avg + std*2
    upper_3 = avg + std*3
    lower_1 = avg - std*1
    lower_2 = avg - std*2
    lower_3 = avg - std*3

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

#%%

def OEE_plot():
    OEE_plot = Tk()
    OEE_plot.geometry('1200x1200')
    OEE_plot.title('OEE Run Chart')
    avg = OEE_hrly.mean()* np.ones(hours.shape)
    std = OEE_hrly.std()* np.ones(hours.shape)
    upper_1 = avg + std*1
    upper_2 = avg + std*2
    upper_3 = avg + std*3
    lower_1 = avg - std*1
    lower_2 = avg - std*2
    lower_3 = avg - std*3

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

#%%

def performance_plot():
    performance_plot = Tk()
    performance_plot.geometry('1200x1200')
    performance_plot.title('OEE Run Chart')
    avg = performance_hrly.mean()* np.ones(hours.shape)
    std = performance_hrly.std()* np.ones(hours.shape)
    upper_1 = avg + std*1
    upper_2 = avg + std*2
    upper_3 = avg + std*3
    lower_1 = avg - std*1
    lower_2 = avg - std*2
    lower_3 = avg - std*3

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
#%%
def clicked1():
    file = filedialog.askopenfilename(filetypes = (("Comma Separated Variables","*.csv"),("all files","*.*")))
    global dataset 
    dataset = pd.read_csv(file)
    "var_list = np.asarray([i for i in dataset.columns.values if(i!=' ' and not(re.search(pattern,i)))])"
    window2()

#%%
def window2():
    global date
    window1.destroy()
    date = dataset['Date']
    #date = [dt.datetime.strptime(str(date[i]), '%d-%m-%Y') for i in range(len(date))]
    window2 = Tk()
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
        #sdate_lbl3.configure(text = st_date)
        window2.destroy()
        window3()
        
    time_bt = Button(fr2, text = 'Proceed to time range selection', command = clicked2)
    time_bt.pack(side = BOTTOM, pady = 5)
    window2.mainloop()
        
#%%
def window3():
    s_st = (st_date + dt.timedelta(0))
    s_et = (st_date + dt.timedelta(hours=23))
    e_st = (end_date + dt.timedelta(0))
    e_et = (end_date + dt.timedelta(hours =23))
    s_dti = tuple(pd.date_range(start = s_st, end = s_et, freq = '1H'))
    e_dti = tuple(pd.date_range(start = e_st, end = e_et, freq = '1H'))
    window3 = Tk()
    window3.geometry('850x300')
    frame1 = Frame(window3, relief = RAISED)
    frame1.pack(fill = X)
    window3.title('Time selection') 
    stime_lbl3 = Label(frame1, text = 'Choose starting time for analysis', width = 20)
    stime_lbl3.pack(side = LEFT, padx = 5, pady = 5)
    stime_cmb3 = Combobox(frame1)
    stime_cmb3.pack(side = LEFT, padx = 5, pady = 5)
    stime_cmb3['values'] =s_dti
    stime_cmb3.current(0)
    etime_lbl3 = Label(frame1, text = 'Choose ending time on').pack(side = LEFT, padx = 5, pady = 5)
    etime_cmb3 = Combobox(frame1)
    etime_cmb3.pack(side = LEFT, padx = 5, pady = 5)
    etime_cmb3['values'] = e_dti
    etime_cmb3.current(0)
    frame2= Frame(window3, relief = RAISED)
    frame2.pack(fill = X)
    sres_lbl = Label(frame2, text = '')
    sres_lbl.pack(fill = BOTH, padx = 5, pady = 5)
    frame3 = Frame(window3, relief = RAISED)
    frame3.pack(fill = BOTH)

    def plotmap(p_table):
        frame3 = Frame(window3, relief = RAISED)
        frame3.pack(fill = BOTH)
        f = Figure(figsize = (10,10))
        f.clf()
        f.suptitle('Heatmap for 5 minutes')
        canvas = FigureCanvasTkAgg(f, master = frame3)
        canvas.draw()
        canvas.get_tk_widget().pack(side = BOTTOM, fill = BOTH, expand = True)
        toolbar = NavigationToolbar2Tk(canvas, frame3)
        toolbar.update()
        canvas._tkcanvas.pack(side = TOP, fill = BOTH, expand = True)
        a = f.add_subplot(111)
        sns.heatmap(p_table, cmap = 'RdYlGn', annot = p_table.values, ax=a).set_yticklabels(labels = p_table.index, rotation = 0)
#%%

    def begin():
        txt = calc_duration_parameters()
        p_table = htmp_calc()
        params = Radiobutton(frame2, text = 'Production Quantities', command = sres_lbl.configure(text = txt))
        params.pack(side = LEFT, padx = 10)
        hm = Radiobutton(frame2, text = 'Heatmap', command = plotmap(p_table))
        hm.pack(side = LEFT, padx = 10)
        RC = Radiobutton(frame2, text = 'Runcharts', command = RunChartParameters(frame2))
        RC.pack(side = LEFT, padx = 10)
        
#%%

    def clicked3():
        frame3.destroy()
        global st_time ,end_time
        #stime_lbl4.configure(text = type(stime_cmb4.get))
        st_time = stime_cmb3.get()
        end_time = etime_cmb3.get()
        begin()
        
#%%
        
    begin_bt = Button(frame1, text = 'Begin Calculation', command = clicked3).pack(side = BOTTOM)
    window3.mainloop()
        

#%%
'Defining the GUI'
window1 = Tk()
window1.title('Lear Remote Internship')
window1.geometry('500x300')
fr1 = Frame(window1, relief = RAISED, borderwidth = 1, height = 300)
fr1.pack(pady = 50)
wel_lb1 = Label(fr1, text = 'Welcome', font = ('latin modern roman',20))
wel_lb1.pack(side = TOP, pady = 20)
ch_lbl1 = Label(fr1, text = 'Choose the input data file', font = ('latin modern roman',15))
ch_lbl1.pack(side = LEFT, padx = 20, pady = 10)
ch_bt1 = Button(fr1, text = 'Choose File', command = clicked1)
ch_bt1.pack(side = LEFT, padx = 10, pady = 10)
window1.mainloop()
