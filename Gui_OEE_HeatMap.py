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
import re
import pandas as pd
import numpy as np
pattern = r"Unnamed"
dataset = []
chosen = ""
st_date = ""
end_date = ""
st_time = ""
end_time = ""
#%%
def clicked1():
    file = filedialog.askopenfilename(filetypes = (("Comma Separated Variables","*.csv"),("all files","*.*")))
    global dataset 
    dataset = pd.read_csv(file)
    var_list = np.asarray([i for i in dataset.columns.values if(i!=' ' and not(re.search(pattern,i)))])
    window2(tuple(var_list))

#%%
def window2(var_list):
    window1.destroy()
    window2 = Tk()
    window2.title('Variable selection')
    window2.geometry('500x300')
    'The variable selection combobox, label and button'
    ch_lbl2 = Label(window2, text = 'Choose the required variable')
    ch_lbl2.grid(column = 3,row = 4)
    var_cmb2 = Combobox(window2)
    var_cmb2.grid(column = 4,row = 4)
    var_cmb2['values'] = var_list
    var_cmb2.current(0)
    
    def clicked2():
        global chosen 
        chosen = var_cmb2.get()
        window2.destroy()
        window3()
        
    sub_bt2 = Button(window2, text = 'Submit', command = clicked2)
    sub_bt2.grid(column = 3, row = 5)
    window2.mainloop()
    
#%%
def window3():
    date = dataset['Date'].values
    window3 = Tk()
    window3.geometry('500x300')
    window3.title('Date selection')
    sdate_lbl3 = Label(window3, text = 'Choose starting date')
    sdate_lbl3.grid(column = 1, row = 6)
    strt_cmb3 = Combobox(window3)
    strt_cmb3.grid(column = 2,row = 6)
    strt_cmb3['values'] =tuple(np.unique(date))
    strt_cmb3.current(0)
    edate_lbl3 = Label(window3, text = 'Choose ending date').grid(column = 3, row = 6)
    end_cmb3 = Combobox(window3)
    end_cmb3.grid(column = 4, row = 6)
    end_cmb3['values'] = tuple(np.unique(date))
    end_cmb3.current(0)
    
    def clicked3():
        st_date = pd.to_datetime(strt_cmb3.get())
        print(pd.to_datetime(st_date))
        end_date = pd.to_datetime(end_cmb3.get())
        #sdate_lbl3.configure(text = st_date)
        window3.destroy()
        window4()
        
    time_bt = Button(window3, text = 'Proceed to time range selection', command = clicked3).grid(column = 4,row = 7)
    window3.mainloop()
        
#%%
def window4():
    s_st = str(st_date + pd.to_timedelta('00:00:00'))
    s_et = str(st_date + pd.to_timedelta('23:00:00'))
    e_st = str(end_date + pd.to_timedelta('00:00:00'))
    e_et = str(end_date + pd.to_timedelta('23:00:00'))
    s_dti = tuple(pd.date_range(start = s_st, end = s_et, freq = '1H'))
    e_dti = tuple(pd.date_range(start = e_st, end = e_et, freq = '1H'))
    window4 = Tk()
    window4.geometry('500x300')
    window4.title('Time selection')
    stime_lbl4 = Label(window4, text = 'Choose starting time on')
    stime_lbl4.grid(column = 1, row =8)
    stime_cmb4 = Combobox(window4)
    stime_cmb4.grid(column = 2, row = 8)
    stime_cmb4['values'] =s_dti
    stime_cmb4.current(0)
    etime_lbl4 = Label(window4, text = 'Choose ending time on').grid(column = 3, row =8)
    etime_cmb4 = Combobox(window4)
    etime_cmb4.grid(column = 4, row = 8)
    etime_cmb4['values'] = e_dti
    etime_cmb4.current(0)
    
    def clicked4():
        global st_time ,end_time
        #stime_lbl4.configure(text = type(stime_cmb4.get))
        st_time = pd.to_datetime(st_date + stime_cmb4.get())
        end_time = pd.to_datetime(end_date + etime_cmb4.get())
        window4.destroy()
        window5()
        
    begin_bt = Button(window4, text = 'Begin Calculation', command = clicked4).grid(column = 4, row = 9)
    window4.mainloop()
        
#%%
def window5():
    window5 = Tk()
    window5.geometry('500x300')
    window5.title('View Results')
    sres_lbl = Label(window5, text = st_time).grid()
    eres_lbl = Label(window5, text = end_time).grid(column = 0, row =1)
    window5.mainloop()
    
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