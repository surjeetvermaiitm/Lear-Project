#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 29 14:21:52 2020

@author: syshain
"""
#%%
from tkinter import *
import tkinter
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
    date = [dt.datetime.strptime(str(date[i]), '%d-%m-%Y') for i in range(len(date))]
    window2 = Tk()
    window2.geometry('850x300')
    window2.title('Date selection')
    sdate_lbl2 = Label(window2, text = 'Choose starting date')
    sdate_lbl2.grid(column = 1, row = 6)
    strt_cmb2 = Combobox(window2)
    strt_cmb2.grid(column = 2,row = 6)
    strt_cmb2['values'] =tuple(np.unique(date))
    strt_cmb2.current(0)
    edate_lbl2 = Label(window2, text = 'Choose ending date').grid(column = 3, row = 6)
    end_cmb2 = Combobox(window2)
    end_cmb2.grid(column = 4, row = 6)
    end_cmb2['values'] = tuple(np.unique(date))
    end_cmb2.current(0)
    
    def clicked2():
        global st_date, end_date
        st_date = dt.datetime.strptime(strt_cmb2.get(), '%Y-%m-%d %H:%M:%S')
        end_date = pd.to_datetime(end_cmb2.get())
        #sdate_lbl3.configure(text = st_date)
        window2.destroy()
        window3()
        
    time_bt = Button(window2, text = 'Proceed to time range selection', command = clicked2).grid(column = 4,row = 7)
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
    window3.title('Time selection')
    stime_lbl3 = Label(window3, text = 'Choose starting time on')
    stime_lbl3.grid(column = 1, row =8)
    stime_cmb3 = Combobox(window3)
    stime_cmb3.grid(column = 2, row = 8)
    stime_cmb3['values'] =s_dti
    stime_cmb3.current(0)
    etime_lbl3 = Label(window3, text = 'Choose ending time on').grid(column = 3, row =8)
    etime_cmb3 = Combobox(window3)
    etime_cmb3.grid(column = 4, row = 8)
    etime_cmb3['values'] = e_dti
    etime_cmb3.current(0)
    
    def begin():
        res_win = Tk()
        res_win.title('HeatMap Visualization')
        txt = calc_duration_parameters()
        sres_lbl = Label(window3, text = txt).grid()
        p_table = htmp_calc()
        f = Figure(figsize = (10,10))
        f.suptitle('Heatmap for 5 minutes')
        a = f.add_subplot(111)
        sns.heatmap(p_table, cmap = 'RdYlGn', annot = p_table.values, ax=a).set_yticklabels(labels = p_table.index, rotation = 0)
        canvas = FigureCanvasTkAgg(f, master = res_win)
        canvas.draw()
        canvas.get_tk_widget().pack(side = BOTTOM, fill = BOTH, expand = True)
        toolbar = NavigationToolbar2Tk(canvas, res_win)
        toolbar.update()
        canvas._tkcanvas.pack(side = TOP, fill = BOTH, expand = True)
        res_win.mainloop()
        
    def clicked3():
        global st_time ,end_time
        #stime_lbl4.configure(text = type(stime_cmb4.get))
        st_time = stime_cmb3.get()
        end_time = etime_cmb3.get()
        begin()
        
    begin_bt = Button(window3, text = 'Begin Calculation', command = clicked3).grid(column = 4, row = 9)
    window3.mainloop()
        
#%%

def calc_duration_parameters():
    global dt_relevant, i_bn, i_end
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
    hrly_diff = []
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
'Defining the GUI'
window1 = Tk()
window1.title('Lear Remote Internship')
window1.geometry('500x300')
wel_lb1 = Label(window1, text = 'Welcome', font = ('Arial Bold',20))
wel_lb1.grid(column = 3, row = 0)
ch_lbl1 = Label(window1, text = 'Choose the input data file').grid(column = 2, row = 2)
ch_bt1 = Button(window1, text = 'Choose File', command = clicked1)
ch_bt1.grid(column = 3, row =2)
window1.mainloop()

#%%
'This cell prepares the data for calculation of hourly quantities'
timear = pd.to_datetime(dataset['Date'] + ' ' + dataset['Time'])
hourly_distribution = []
result_hrly = []
hrly_diff = []
blank = 0
onehr = pd.to_timedelta('1:00:00')
starttime = pd.to_datetime('15-10-2019'+' ' + '7:00:00')
