# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 12:15:01 2020

@author: KAUSHIK S CHETTIAR
"""

from tkinter import *
import tkinter as tk
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
from matplotlib.figure import Figure
import seaborn as sns
pattern = r"Unnamed"
dataset = []
date = []
dt_relevant = []
chosen = " "
st_date = dt.datetime.now()
end_date = dt.datetime.now()
st_time = dt.datetime.now()
end_time = dt.datetime.now()

#%%
def calc_duration_parameters():
    global dt_relevant, time_differences, result_relevant, dt_relevant,max_rep,cycle_time
    dates = dataset['Date']
    time = dataset[' Time']
    result = dataset[' Result']
    DT_column = pd.Series([dt.datetime.strptime(dates[i] + ' '+ time[i], '%d-%m-%Y %H:%M:%S') for i in range(len(dates))])
    print(type(DT_column[1]))
    i_bn = np.where(DT_column > st_time)[0][0]
    i_end = np.where(DT_column > end_time)[0][0]
    dt_relevant = DT_column[i_bn:i_end]
    result_relevant = result[i_bn:i_end]
    time_differences = np.asarray([dt_relevant[i+1]-dt_relevant[i] for i in result_relevant.index[0]+np.arange(len(result_relevant)-1)])
    max_rep = Counter(time_differences).most_common(4)
    cycle_time = (max_rep[1][0]).total_seconds()/4
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
    txt = 'The required results from the calculations are as follow:' + '/n' + 'OEE: ' + str(OEE) + '\n'+ 'Availability: ' + str(availability) + '\n' + 'Performance: ' + str(performance) + '\n' + 'Quality: ' + str(quality)
    return txt


#%%


def window2():
    date = dataset['Date'].values
    window2 = Tk()
    window2.geometry('500x700')
    window2.title('Date selection')
    sdate_lbl3 = Label(window2, text = 'Choose starting date')
    sdate_lbl3.grid(column = 1, row = 6)
    strt_cmb3 = Combobox(window2)
    strt_cmb3.grid(column = 2,row = 6)
    strt_cmb3['values'] =tuple(np.unique(date))
    strt_cmb3.current(0)
    edate_lbl3 = Label(window2, text = 'Choose ending date').grid(column = 3, row = 6)
    end_cmb3 = Combobox(window2)
    end_cmb3.grid(column = 4, row = 6)
    end_cmb3['values'] = tuple(np.unique(date))
    end_cmb3.current(0)
    
    def clicked2():
        global st_date, end_date
        print(strt_cmb3.get())
        st_date = pd.to_datetime(strt_cmb3.get())
        #print(pd.to_datetime(st_date))
        print(st_date)
        print(type(st_date), type(end_date))
        end_date = pd.to_datetime(end_cmb3.get())
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
    print(s_st)
    print(s_et)
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
        global txt
        txt = calc_duration_parameters()
        window3.destroy()
        window4()
        
        
    def clicked3():
        global st_time ,end_time
        #stime_lbl4.configure(text = type(stime_cmb4.get))
        st_time = stime_cmb3.get()
        end_time = etime_cmb3.get()
        begin()
        
    begin_bt = Button(window3, text = 'Print Run Chart of Industry Parameters', command = clicked3).grid(column = 4, row = 9)
    window3.mainloop()
        
        
#%%
def window4():
    global availability_hrly, quality_hrly, OEE_hrly, performance_hrly
    window4 = Tk()
    window4.geometry('1000x1000')
    window4.title('Run Chart of Industry Parameters')
    
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
    time = dataset[' Time']
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
    
    
    
    f = Figure(figsize=(10,10), dpi = 100)
    a = f.add_subplot(111)
    a.plot(hours, availability_hrly, 'r-')
    a.plot(hours, quality_hrly, 'g--')
    a.plot(hours, OEE_hrly, 'k')
    a.plot(hours, performance_hrly, 'b')
    a.set_title('Hourly plot of Industry Quantities', fontsize = 16)
    a.legend(('Availability', 'Quality', 'OEE', 'Performance'),loc = 1)
    
    canvas = FigureCanvasTkAgg(f,window4)
    canvas.draw()
    canvas.get_tk_widget().pack(side = tk.TOP, fill= tk.BOTH, expand=False)
    
    window4.mainloop()
    




#%%
    
def clicked1():
    file = filedialog.askopenfilename(filetypes = (("Comma Separated Variables","*.csv"),("all files","*.*")))
    global dataset 
    dataset = pd.read_csv(file)
    # var_list = np.asarray([i for i in dataset.columns.values if(i!=' ' and not(re.search(pattern,i)))])
    # window2(tuple(var_list))
    window1.destroy()
    window2()
    
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
# 'This cell contains a loop to continue quantity preparation and converts them to appropriate types'
# hourly_distribution = []
# result_hrly = []
# hrly_diff = []
# blank = 0

# starttime = pd.to_datetime(st_time)
# endtime = pd.to_datetime(end_time)
# required_time = endtime - starttime

# dates = dataset['Date']
# time = dataset[' Time']
# result = dataset[' Result']
# timear = pd.Series([dt.datetime.strptime(dates[i] + ' '+ time[i], '%d-%m-%Y %H:%M:%S') for i in range(len(dates))])
# number = int(abs(int(required_time.seconds/3600)+required_time.days*24))
# for i in range(number):
#     hourly_distribution.append(timear[np.where(timear > starttime+i*(onehr))[0][0]:(np.where(timear > starttime+(i+1)*(onehr))[0][0])-1])
#     result_hrly.append(result[np.where(timear > starttime+i*(onehr))[0][0]:(np.where(timear > starttime+(i+1)*(onehr))[0][0])-1])
#     hrly_diff.append([hourly_distribution[i][j+1]-hourly_distribution[i][j] for j in range(len(hourly_distribution[i])-1)])
# #%%
# 'This cell calculates the most important quantities relating to the final calculations'
# ok_hrly = np.array([Counter(result_hrly[i])['OK'] for i in range(len(result_hrly))])