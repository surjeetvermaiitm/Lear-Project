#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 15:31:59 2020

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
pattern = r"!button"
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
res = []
res2 = []
availability_hrly = []
quality_hrly = []
OEE_hrly = []
performance_hrly = []  
ok_hrly = []
ng_hrly = []
nameslst = ['Availability','Quality','Performance','OEE','Ok','No Go']
calcflag = 0
dir_path = os.path.dirname(os.path.realpath(__file__))
backend_ = "Qt5Agg"
line1 = 1
line2 = 2
Shift1_start = dt.time(7,0,0)
Shift1_end = dt.time(15,30,0)
Shift2_start = dt.time(15,30,0)
Shift2_end = dt.time(23,59,59)
Shift3_start = dt.time(0,0,0)
Shift3_end = dt.time(7,0,0)
#%%

class table:
    
    def listform(self, root, lst, buttonflag):
        self.rows = len(lst)
        self.columns = len(lst[0])
        style = Style() 
        style.configure('W.TButton', font = ('Times New Roman', 10,'bold'), foreground = 'black', background = '#ffffff') 
        
        self.fr1 = tkt.Frame(root, relief = FLAT, bg = '#ffffff')
        self.fr1.pack(side = TOP)
        self.fr2 = tkt.Frame(root, relief = FLAT, bg = '#ffffff')
        self.fr2.pack(side = TOP)
        
        if buttonflag == 'True':
            self.b0 = Button(self.fr1, width = 12, text = 'Availability', style = 'W.TButton', command = lambda : RunCharts(plotflag = 0))
            self.b0.pack(side = LEFT, padx = 5)
            self.b1 = Button(self.fr1, width = 12, text = 'Quality', style = 'W.TButton', command = lambda : RunCharts(plotflag = 1))
            self.b1.pack(side = LEFT, padx = 5)
            self.b2 = Button(self.fr1, width = 12, text = 'Performance', style = 'W.TButton', command = lambda : RunCharts(plotflag = 2))
            self.b2.pack(side = LEFT, padx = 5)
            self.b3 = Button(self.fr1, width = 12, text = 'OEE', style = 'W.TButton', command = lambda : RunCharts(plotflag = 3))
            self.b3.pack(side = LEFT, padx = 5)
            self.b4 = Button(self.fr1, width = 12, text = 'OK', style = 'W.TButton', command = lambda : RunCharts(plotflag = 4))
            self.b4.pack(side = LEFT, padx = 5)
            self.b5 = Button(self.fr1, width = 12, text = 'No GO', style = 'W.TButton', command = lambda : RunCharts(plotflag = 5))
            self.b5.pack(side = LEFT, padx = 5)
        
        for i in range(self.rows):           
            for j in range(self.columns):
                if buttonflag == 'False' and i==0:
                    self.e = Label(self.fr1, width = 15, text = str(lst[i][j]), font = ('Times New Roman', 10), relief = FLAT, foreground = 'black', background= '#ffffff')
                    self.e.pack(side = LEFT, padx = 5)                    
                if i==1:
                    self.e = Label(self.fr2, width = 15, text = str(lst[i][j]), font = ('Times New Roman', 10), relief = FLAT, foreground = 'black', background= '#ffffff')
                    self.e.pack(side = LEFT, padx = 5)
                    
    def tableform(self, root, lst):
         self.rows = len(lst)
         self.columns = len(lst[0])
         for i in range(self.rows):
            self.fr = Frame(root)
            self.fr.pack(side = TOP)
            for j in range(self.columns):
                self.e = Label(self.fr, width = 20, text = str(lst[i][j]), font = ('Arial Bold',18), relief = RAISED, foreground = 'black', background= 'white', borderwidth = 1)
                self.e.pack(side = LEFT)       
    
    def __init__(self, root, lst, buttonflag = 'False', testflag = 0):
        if testflag == 0 :
            self.listform(root, lst, buttonflag)
        if testflag == 1:
            self.tableform(root, lst)

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
        no_ok = 0
        no_ng = 0
    
    res = [availability, quality, OEE, performance, no_ok, no_ng]
       
    #if(l == 'A'):
      # resA = res
     #  return resA
    
    #if(l == 'B'):
       # resB = res
      #  return resB
    
    return res

#%%
def htmp_calc():
    'This cell prepares the data for calculation of hourly quantities'
    global p_table
    data = dataset

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

def rcplot(plotflag, plflag = 0, l = None):
    
    if plotflag == 0:
        hrplt = availability_hrly
    if plotflag == 1:
        hrplt = quality_hrly
    if plotflag == 2:
        hrplt = performance_hrly
    if plotflag == 3:
        hrplt = OEE_hrly
    if plotflag == 4:
        hrplt = ok_hrly
    if plotflag == 5:
        hrplt = ng_hrly
        
    avg = hrplt.mean()*np.ones(int(no_hrs/runhrs))
    std = hrplt.std()*np.ones(int(no_hrs/runhrs))
    
    upper_1 = avg + std*1
    upper_2 = avg + std*2
    upper_3 = avg + std*3
    lower_1 = avg - std*1
    lower_2 = avg - std*2
    lower_3 = avg - std*3
    
    title = str(nameslst[plotflag]) + ' Run Chart'

    if(plflag == 0):
        f = Figure(figsize=(10,10))
        a = f.add_subplot(111)  
        #if(plot_flag['PerPlot'] == 0):
        a.plot(hours, hrplt, 'b-')
        a.plot(hours, upper_1 , 'r--')
        a.plot(hours, upper_2 , 'r--')
        a.plot(hours, upper_3 , 'r--')
        a.plot(hours, avg, 'g-')
        a.plot(hours, lower_1 , 'r--')
        a.plot(hours, lower_2 , 'r--')
        a.plot(hours, lower_3 , 'r--')
        a.set_title(title, fontsize = 16)
        a.set_xlabel('Hours')
        a.set_ylabel(str(nameslst[plotflag]))
        
        if l == 'P':
            f.savefig(dir_path + '/temp/'+str(nameslst[plotflag])+'.png')           
        else: 
            rc_plot_win = tk.ThemedTk()
            rc_plot_win.get_themes()
            rc_plot_win.set_theme('clearlooks')
            rc_plot_win.geometry('1200x1200')
            rc_plot_win.title(title)           
    
            canvas = FigureCanvasTkAgg(f,rc_plot_win)
            canvas.draw()
            canvas.get_tk_widget().pack(side = TOP, fill= BOTH, expand=True)       
            toolbar = NavigationToolbar2Tk(canvas,rc_plot_win)
            toolbar.update()
            canvas._tkcanvas.pack(side = TOP, fill= BOTH, expand=True)           
            rc_plot_win.mainloop()             
            return 

    else:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x = hours, y = hrplt, mode = 'markers+lines', line = dict(color = 'blue'), name = 'performance'))
        fig1.add_trace(go.Scatter(x = hours, y = upper_1, line  = dict(color = 'red', dash = 'dash'), name = 'Upper limit 1'))
        fig1.add_trace(go.Scatter(x = hours, y = upper_2, line  = dict(color = 'red', dash = 'dash'), name = 'Upper limit 2'))
        fig1.add_trace(go.Scatter(x = hours, y = upper_3, line  = dict(color = 'red', dash = 'dash'), name = 'Upper limit 3'))
        fig1.add_trace(go.Scatter(x = hours, y = avg, line  = dict(color = 'green', dash = 'dash'), name = 'Mean value'))
        fig1.add_trace(go.Scatter(x = hours, y = lower_1, line  = dict(color = 'red', dash = 'dash'), name = 'Lower limit 1'))
        fig1.add_trace(go.Scatter(x = hours, y = lower_2, line  = dict(color = 'red', dash = 'dash'), name = 'Lower limit 2'))
        fig1.add_trace(go.Scatter(x = hours, y = lower_3, line  = dict(color = 'red', dash = 'dash'), name = 'Lower limit 3'))
        fig1.update_layout(title = dict(text = title, x = 0.5, y = 0.95, xanchor = 'center', yanchor = 'top'), xaxis_title = 'Hours', yaxis_title = str(nameslst[plotflag]), font = dict(family = 'Courier New, monospace', size = 18, color = '#7f7f7f'))
        fig1 = fig1.to_plotly_json() 
        plotly.offline.plot(fig1)


#%%
def PieChartDraw(results, fr):
    
    global PD_hrs, st_planned, end_planned, Shift1_PD, Shift2_PD, Shift3_PD
    OEE = results[2]
    no_hrs = int((end_time-st_time).seconds/3600)+24*(end_time-st_time).days
     #[availability, quality, OEE, performance]
 #   AVailability = (1-Unplanned/Total)
    UPD_hrs = (1-results[0])*no_hrs
 
    with open("data.txt") as f:
        dicts = eval(f.read())
        Shift1_PD = float(dicts['Shift 1'])/60
        Shift2_PD = float(dicts['Shift 2'])/60
        Shift3_PD = float(dicts['Shift 3'])/60
    f.close()
    PD_hrs = 0 
    if Shift1_start < st_time.time()<= Shift1_end:
        PD_hrs = ((dt.datetime.combine(dt.datetime.today(),Shift1_end)-dt.datetime.combine(dt.datetime.today(),st_time.time())).seconds/((dt.datetime.combine(dt.datetime.today(),Shift1_end)-dt.datetime.combine(dt.datetime.today(),Shift1_start)).seconds))*Shift1_PD
        st_planned = dt.datetime.combine(st_time.date(),Shift1_end)
    elif Shift2_start< st_time.time()<= Shift2_end:
        PD_hrs = ((dt.datetime.combine(dt.datetime.today(),Shift2_end)-dt.datetime.combine(dt.datetime.today(),st_time.time())).seconds/((dt.datetime.combine(dt.datetime.today(),Shift2_end)-dt.datetime.combine(dt.datetime.today(),Shift2_start)).seconds))*Shift2_PD
        st_planned = dt.datetime.combine(st_time.date()+timedelta(days=1),dt.time(0,0))
    elif Shift3_start<= st_time.time()<= Shift3_end:
        PD_hrs = ((dt.datetime.combine(dt.datetime.today(),Shift3_end)-dt.datetime.combine(dt.datetime.today(),st_time.time())).seconds/((dt.datetime.combine(dt.datetime.today(),Shift3_end)-dt.datetime.combine(dt.datetime.today(),Shift3_start)).seconds))*Shift3_PD
        st_planned = dt.datetime.combine(st_time.date(),Shift3_end)

    if Shift1_start < end_time.time()<= Shift1_end:
        PD_hrs = PD_hrs+ ((dt.datetime.combine(dt.datetime.today(),end_time.time())-(dt.datetime.combine(dt.datetime.today(),Shift1_start))).seconds/((dt.datetime.combine(dt.datetime.today(),Shift1_end)-dt.datetime.combine(dt.datetime.today(),Shift1_start)).seconds))*Shift1_PD
        end_planned = dt.datetime.combine(end_time.date(),Shift1_start)
    elif Shift2_start< end_time.time()<= Shift2_end:
        PD_hrs = PD_hrs+ ((dt.datetime.combine(dt.datetime.today(),end_time.time())-(dt.datetime.combine(dt.datetime.today(),Shift2_start))).seconds/((dt.datetime.combine(dt.datetime.today(),Shift2_end)-dt.datetime.combine(dt.datetime.today(),Shift2_start)).seconds))*Shift2_PD
        end_planned = dt.datetime.combine(end_time.date(),Shift2_start)
    elif Shift3_start<= end_time.time()<= Shift3_end:
        PD_hrs = PD_hrs+ ((dt.datetime.combine(dt.datetime.today(),end_time.time())-(dt.datetime.combine(dt.datetime.today(),Shift3_start))).seconds/((dt.datetime.combine(dt.datetime.today(),Shift3_end)-dt.datetime.combine(dt.datetime.today(),Shift3_start)).seconds))*Shift3_PD
        end_planned = dt.datetime.combine(end_time.date(),Shift3_start)

    while(st_planned< end_planned):
        if st_planned.time() == Shift1_start:
            PD_hrs = PD_hrs+Shift1_PD
            st_planned = st_planned+ pd.to_timedelta('08:30:00')
        elif st_planned.time() == Shift2_start:
            PD_hrs = PD_hrs+Shift2_PD
            st_planned = st_planned+ pd.to_timedelta('08:30:00')
        elif st_planned.time() == Shift3_start:
            PD_hrs = PD_hrs+Shift3_PD
            st_planned = st_planned+ pd.to_timedelta('07:00:00')
    
    if PD_hrs<UPD_hrs:
        UPD_hrs = UPD_hrs-PD_hrs
    elif PD_hrs>= UPD_hrs:
        PD_hrs = UPD_hrs
        UPD_hrs = 0
    # Availability removing Planned Downtime
    Avail_PD = 1 - np.divide(PD_hrs,(end_time-st_time).seconds/3600)
    Avail_UPD = 1 - np.divide(UPD_hrs,(end_time-st_time).seconds/3600)
    # Planned Downtime: All shifts have different planned downtime hours. 
    Quality = results[1]
    OEE= results[2]
    Performance = results[3]    
    
    PD_loss = (1-Avail_PD)*(1-OEE)/(4-Avail_PD-Avail_UPD-Quality-Performance)
    UD_loss = (1-Avail_UPD)*(1-OEE)/(4-Avail_PD-Avail_UPD-Quality-Performance)
    P_loss = (1-Performance)*(1-OEE)/(4-Avail_PD-Avail_UPD-Quality-Performance)
    Q_loss = (1-Quality)*(1-OEE)/(4-Avail_PD-Avail_UPD-Quality-Performance)
    
    backend_ =  mlb.get_backend() 
    mlb.use("Agg") 
    
    labels = ["OEE", 'PD_Loss','UD_Loss', 'P_Loss','Q_Loss']
    values = [OEE*360, PD_loss*360,UD_loss*360, P_loss*360, Q_loss*360]

    colors = ['Green','#33F3FF','Yellow', 'Red', 'DarkRed'] 
    explode =(0,0,0.1,0,0.1)
    
    f = plt.figure(figsize=(10,10))
    a = f.add_subplot(111)
    a.pie(values, explode = explode, colors=colors, startangle=90, autopct='%.1f%%', shadow = True) 
    a.legend(labels, loc = 'upper right')
    f.savefig(dir_path+'/temp/pie.png')
    mlb.use(backend_)
    
    canvas = FigureCanvasTkAgg(f,fr)
    canvas.draw()
    canvas.get_tk_widget().pack(fill= BOTH, expand=True)
    
#%%
def printout(fr, res_rd, wf, testflag = 0):

    if testflag == 0:
        lst = [('Availability','Quality','Performance','OEE','Ok','No Go'),(res_rd[0],res_rd[1],res_rd[3],res_rd[2],res_rd[4],res_rd[5])]
    
        if wf == 1:
            table(fr, lst, buttonflag = 'True')
        if wf == 2:
            table(fr, lst)
            
    if testflag == 1:
        lst = np.transpose([('Availability','Quality','Performance','OEE','Ok','No Go'),(res_rd[0],res_rd[1],res_rd[3],res_rd[2],res_rd[4],res_rd[5])])
        table(fr, lst, testflag = 1)

    
#%%
def RunCharts(plotflag, interactive = 0, l = None):
        
    global calcflag
    
    if calcflag == 0:
        global availability_hrly, quality_hrly, OEE_hrly, performance_hrly, ok_hrly, ng_hrly, hours, no_hrs
        st = st_time
        et = end_time
        hours = pd.date_range(start = st + dt.timedelta(hours = runhrs), end = et, freq = dt.timedelta(hours=runhrs))
        no_hrs = int((et - st).seconds/3600) + 24*(end_time-st_time).days
    
        for i in range(int(no_hrs)):
            hr_res = calc_duration_parameters(st, st+dt.timedelta(hours = runhrs))
            availability_hrly.append(hr_res[0])
            quality_hrly.append(hr_res[1])
            OEE_hrly.append(hr_res[2])
            performance_hrly.append(hr_res[3])
            ok_hrly.append(hr_res[4])
            ng_hrly.append(hr_res[5])
            st = st+dt.timedelta(hours = runhrs)
                
        availability_hrly = np.array(availability_hrly)
        quality_hrly = np.array(quality_hrly)
        OEE_hrly = np.array(OEE_hrly)
        performance_hrly = np.array(performance_hrly)
        ok_hrly = np.array(ok_hrly)
        ng_hrly = np.array(ng_hrly)
    
        calcflag = 1
    
    rcplot(plotflag, plflag = interactive, l = l)
    
#%%
'Defining the GUI'
def main():
    window1 = tk.ThemedTk()
    window1.get_themes()
    window1.set_theme('breeze')
    window1.configure(background= '#1a1410')
    window1.title('Lear Remote Internship')
    window1.geometry('500x300')
    fr1 = tkt.Frame(window1, relief = FLAT, height = 300, bg = '#1a1410')
    fr1.pack(pady = 50)
    wel_lb1 = tkt.Label(fr1, text = 'Welcome', font = ('latin modern roman',30), foreground = '#ffffff', bg = '#1a1410')
    wel_lb1.pack(side = TOP, pady = 20)
    ch_lbl1 = tkt.Label(fr1, text = 'Choose the input data file', font = ('latin modern roman',15), foreground = '#ffffff', bg = '#1a1410')
    ch_lbl1.pack(side = LEFT, padx = 20, pady = 10)
    style = Style() 
    style.configure('W.TButton', font =
       ('Times New Roman', 12, 'bold'), 
        foreground = '#ea1313', background = '#ffffff')
    
    def clicked1():
        global line1, dataset
        
        file = filedialog.askopenfilename(filetypes = (("Comma Separated Variables","*.csv"),("all files","*.*")))
        if re.search(r"HSL1.csv",file):
            line1 = 1
        if re.search(r"HSL2.csv",file):
            line1 = 2       

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
    window2.configure(background= '#ffffff')
    window2.geometry('850x100')
    fr1 = tkt.Frame(window2, relief = RAISED,borderwidth = 1, bg = '#ffffff')
    fr1.pack(side = TOP, fill = X)
    fr2 = tkt.Frame(window2, bg = '#ffffff')
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
       ('Times New Roman', 10, 'bold'), 
        foreground = 'black', background = '#ffffff')
 
    
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
            window3(1)
        
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
def window3(t = None):
    
    '''
    t is another flag used to instruct the function window3 to call the appropriate function.
    If t = 1, the comp_lin function is called, which enables comparison of two lines
    If t = None, the regular operations are carried out
    '''
    
    if t == None: 
        s_st = (st_date + dt.timedelta(0))
        s_et = (st_date + dt.timedelta(hours=23))
        e_st = (end_date + dt.timedelta(0))
        e_et = dt.datetime.strptime(dt.datetime.strftime(dt.datetime.strptime(str(end_date + dt.timedelta(hours =23)),'%Y-%m-%d %H:%M:%S'),'%d-%m-%Y %H:%M:%S'),'%d-%m-%Y %H:%M:%S')
        s_dtip = tuple(pd.date_range(start = s_st, end = s_et, freq = '1H'))
        s_dti = tuple(np.asarray([str(dt.datetime.strftime(dt.datetime.strptime(str(s_dtip[i]),'%Y-%m-%d %H:%M:%S'),'%d-%m-%Y %H:%M:%S')) for i in range(len(s_dtip))]))
    
        window3 = tk.ThemedTk()
        window3.get_themes()
        window3.set_theme('breeze')
        window3.geometry('1650x1200')
        window3.configure(background= '#ffffff')
        global frame1, f1l, f1r, f1b, framel, frame2, frame3, f3l, f3r, frameh, frame4, f4l, f4r, f1h, f2h, f3h, f4h
        framet = tkt.Frame(window3, relief = RAISED, bg = '#1a1410', height = 80)
        framet.pack(side = TOP, fill = X)
        framet.pack_propagate(0)
        Lbt = Label(framet, text = 'TIME SELECTION AND RESULTS', foreground = 'white', background = '#1a1410', font = ('Arial Bold',18))
        Lbt.pack(anchor = 'center')
        Lbt.pack_propagate(0)
        frame1 = tkt.Frame(window3, relief = FLAT, bg = '#ffffff')
        frame1.pack(fill = X)
        f1l = tkt.Frame(frame1, relief = FLAT, width = 600, bg = '#ffffff')
        f1l.pack(fill = Y, side= LEFT, padx = 10)
        f1r = tkt.Frame(frame1, relief = FLAT, width = 600, bg = '#ffffff')
        #f1r.pack(fill = Y, side = LEFT, expand = True, padx = 10)
        f1h = tkt.Frame(frame1, relief = RAISED, width = 100, borderwidth = 2, bg = '#ffffff')
        f1b = tkt.Frame(frame1, relief = FLAT, bg = '#ffffff')
        f1b.pack(side = RIGHT, padx = 10)
        window3.title('Time selection') 
        stime_lbl3 = Label(f1l, text = 'Choose starting time:', width = 20)
        stime_lbl3.pack(side = LEFT, padx = 5, pady = 5)
        stime_cmb3 = Combobox(f1l)
        etime_cmb3 = Combobox(f1l, state = 'disabled')
    
        def chosen(a):
            global st_time
            print(a)
            print(str(e_et))
            st_time = dt.datetime.strptime(a,'%d-%m-%Y %H:%M:%S')
            etime_cmb3.configure(state = 'normal')
            pdi = pd.date_range(start = st_time, end = e_et, freq = '1H')
            print(pdi)
            pdi = tuple(pdi[np.where(pdi >= pd.to_datetime(end_date))])
            print(pdi)
            edi = tuple(np.asarray([str(dt.datetime.strftime(dt.datetime.strptime(str(pdi[i]),'%Y-%m-%d %H:%M:%S'),'%d-%m-%Y %H:%M:%S')) for i in range(len(pdi))]))
            etime_cmb3['values'] = edi
            etime_cmb3.current(0)       
            
        stime_cmb3.pack(side = LEFT, padx = 5, pady = 5)
        stime_cmb3['values'] =s_dti
        stime_cmb3.current(0)
        stime_cmb3.bind("<<ComboboxSelected>>", lambda x: chosen(stime_cmb3.get()))
        etime_lbl3 = Label(f1l, text = 'Choose ending time:').pack(side = LEFT, padx = 5, pady = 5)
        etime_cmb3.pack(side = LEFT, padx = 5, pady = 5)
        frame2= tkt.Frame(window3, relief = FLAT, bg = '#ffffff')
        frame2.pack(side = TOP, fill = X)     
        framel= tkt.Frame(window3, relief = RAISED, borderwidth = 2, bg = '#ffffff', width = 825)
        framel.pack(side = LEFT, fill = Y)   
        framel.pack_propagate(0)
        framer = tkt.Frame(window3, relief = FLAT, bg = '#ffffff')
        framer.pack(side = RIGHT, fill = Y)
        #frame3 = Frame(window3, relief = FLAT)
        #frame3.pack(fill = X)
        f3l = tkt.Frame(framel, relief = FLAT, bg = '#ffffff')
        f3l.pack(fill = X, side = TOP)
        f3r = tkt.Frame(framer, relief = FLAT, bg = '#ffffff')
        #f3r.pack(fill = Y, side = RIGHT, padx = 10)
        frameh = tkt.Frame(framel, relief = FLAT, bg = '#ffffff')
        frameh.pack(side = TOP, fill = X)
        #frame4 = Frame(window3, relief = FLAT, borderwidth = 2)
        #frame4.pack(fill = X, pady = 10)
        f4l = tkt.Frame(framel, relief = FLAT, bg = '#ffffff')
        f4l.pack(fill = X, side = TOP)
        f4r = tkt.Frame(framer, relief = FLAT, bg = '#ffffff')
        #f4h = Frame(frame4, relief = RAISED, width = 100, borderwidth = 2)
        #f4r.pack(fill = Y, side = RIGHT, padx = 10)
        #sres_lbl = Label(frame3, text = '', font = ('Arial Bold', 18), foreground ='blue')
        #sres_lbl.pack(side= BOTTOM, fill=X, padx = 5, pady = 5)
        style = Style() 
        style.configure('W.TButton', font =
           ('Times New Roman', 10,'bold'), 
            foreground = 'black', background = '#ffffff') 
     
        him = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Heat Map.png'))
        rcim = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Run Charts.png')) 
        ipim = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/View Interactive Plot in Browser.png'))
        
        
        def quitfun():
            if mb.askyesno("Quit", "Do you really wish to quit?"):
                window3.destroy()
                for x in globals():
                    del x
                
        window3.protocol("WM_DELETE_WINDOW", quitfun)

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
        for widget in frameh.winfo_children():
            widget.destroy()
        hm = tkt.Button(frameh, image = him, borderwidth = 0, command = plotinmap)
        hm.photo = him
        av = Button(frameh, text = 'Availability', style = 'W.TButton', command = lambda : RunCharts(0, 1))
        pr = Button(frameh, text = 'Quality', style = 'W.TButton', command = lambda : RunCharts(1, 1))
        ql = Button(frameh, text = 'Performance', style = 'W.TButton', command = lambda : RunCharts(2, 1))
        oe = Button(frameh, text = 'OEE', style = 'W.TButton', command = lambda : RunCharts(3, 1))
        ob = Button(frameh, text = 'OK', style = 'W.TButton', command = lambda : RunCharts(4, 1))
        nb = Button(frameh, text = 'No GO', style = 'W.TButton', command = lambda : RunCharts(5, 1))
        
        hm.pack(side = LEFT,padx = 5, pady = 5)
        av.pack(side = LEFT,padx = 5, pady = 5)
        pr.pack(side = LEFT,padx = 5, pady = 5)
        ql.pack(side = LEFT,padx = 5, pady = 5)
        oe.pack(side = LEFT,padx = 5, pady = 5)
        ob.pack(side = LEFT,padx = 5, pady = 5)
        nb.pack(side = LEFT,padx = 5, pady = 5)
        
    def plotmap(p_table, l = None):
        #global plot_flag
        no_hrs = int((end_time-st_time).seconds/3600)+24*(end_time-st_time).days
        if(no_hrs>48):
            Msg = mb.askyesno(title='Warning', message= 'The selected time range is very large \nHeatmap would not be clear \nDo you still want to continue?') 
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
                dissct = eval(f.read())
                Hmapxt = int(dissct['Hmapxt'])
                parttime = int(dissct['parttime'])
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
                    Dictionary = {'Hmapxt':str(Hmapxt),'parttime':str(parttime), 'Shift 1':str(60*Shift1_PD), 'Shift 2': str(60*Shift2_PD), 'Shift 3':str(60*Shift3_PD)}
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


    def comp_lin(l):
        
        if(l=='C'):
            global dataset2, line2
            file2 = filedialog.askopenfilename(filetypes = (("Comma Separated Variables","*.csv"),("all files","*.*")))
            
            if re.search(r"HSL1.csv", file2):
                line2 = 1
            if re.search(r"HSL2.csv", file2):
                line2 = 2
                
            dataset2 = pd.read_csv(file2, encoding = 'latin')
            
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
                
            dataset2['Date time'] = pd.Series([dt.datetime.strptime((dataset2['Date'][i] + ' ' + dataset2['Time'][i]),'%d-%m-%Y %H:%M:%S') for i in dataset2.index])
            dataset2 = dataset2.sort_values(by = 'Date time')
            dataset2.index = np.arange(len(dataset2))
            window2(wf = 2)
               
        if l == 'T':
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
               ('Times New Roman', 10,'bold'), 
                foreground = 'black', background = '#ffffff') 
            resA = calc_duration_parameters(st_time, end_time, l ='A', wf = 1)
            resB = calc_duration_parameters(st_time, end_time, l ='B', wf = 1)
            resA_rd = [str(round(100*resA[i],2))+'%' for i in range(len(resA)-2)]
            resA_rd.append(str(resA[4]))
            resA_rd.append(str(resA[5]))
            resB_rd = [str(round(100*resB[i],2))+'%' for i in range(len(resB)-2)]
            resB_rd.append(str(resB[4]))
            resB_rd.append(str(resB[5]))
            printout(fr2_1, resA_rd, wf = 2, testflag = 1)
            printout(fr2_2, resB_rd, wf = 2, testflag = 1)
            PieChartDraw(resA, fr3_1)
            PieChartDraw(resB, fr3_2)            
            lb1 = Label(fr2_1, text = 'Line A', font = ('Arial Bold', 16)).pack()
            lb2 = Label(fr2_2, text = 'Line B', font = ('Arial Bold', 16)).pack()
            comp.mainloop()
        
        if l == 'R': 
                
            global f1l, f1r, frame2, f3l, f3r, f4l, f4r
            f1l.pack(side = LEFT, fill = Y)
            #f1h.pack(side = LEFT, fill = Y)
            f1r.pack(side = RIGHT, fill = Y)
            f3l.pack(side = TOP, fill = X)
            #f3h.pack(side = TOP, fill = X)
            f3r.pack(side = TOP, fill = X)
            f4l.pack(side = TOP, fill = X)
            #f4h.pack(side = TOP, fill = X)
            f4r.pack(side = TOP, fill = X)
            
            for widget in frame2.winfo_children():
                if re.search(pattern, widget.winfo_name()):
                    widget.config(state = 'disabled')
                    
            for widget in f1b.winfo_children():
                widget.destroy()
                
            s_st = (sd2 + dt.timedelta(0))
            s_et = (sd2 + dt.timedelta(hours=23))
            e_st = (ed2 + dt.timedelta(0))
            e_et = (ed2 + dt.timedelta(hours =23))
            s_dtip = pd.date_range(start = s_st, end = s_et, freq = '1H')
            s_dti = tuple(np.asarray([str(dt.datetime.strftime(dt.datetime.strptime(str(s_dtip[i]),'%Y-%m-%d %H:%M:%S'),'%d-%m-%Y %H:%M:%S')) for i in range(len(s_dtip))]))    
            
            stime_lblc = Label(f1r, text = 'Choose starting time:', width = 20)
            stime_lblc.pack(side = LEFT, padx = 5, pady = 5)
            stime_cmbc = Combobox(f1r)
            etime_cmbc = Combobox(f1r, state = 'disabled')
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
            etime_lblc = Label(f1r, text = 'Choose ending time:').pack(side = LEFT, padx = 5, pady = 5)
            etime_cmbc.pack(side = LEFT, padx = 5, pady = 5)
            
            def clickc():
                
                for widget in f3l.winfo_children():
                    widget.destroy()
                for widget in f3r.winfo_children():
                    widget.destroy()
                for widget in f4l.winfo_children():
                    widget.destroy()
                for widget in f4r.winfo_children():
                    widget.destroy()
                    
                nonlocal et2
                et2 = etime_cmbc.get()
                et2 = dt.datetime.strptime(str(end_time),'%Y-%m-%d %H:%M:%S')
                res2 = calc_duration_parameters(st2, et2, wf = 2)
                res_rd = [str(round(100*res[i],2))+'%' for i in range(len(res)-2)]
                res_rd.append(str(res[4]))
                res_rd.append(str(res[5]))
                res2_rd = [str(round(100*res2[i],2))+'%' for i in range(len(res2)-2)]
                res2_rd.append(str(res2[4]))
                res2_rd.append(str(res2[5]))
                printout(f3l, res_rd, wf = 2)
                printout(f3r, res2_rd, wf = 2)
                PieChartDraw(res, f4l)
                PieChartDraw(res2, f4r)
                lb1 = Label(f3l, text = 'Line ' + str(line1), font = ('Arial Bold', 16)).pack()
                lb2 = Label(f3r, text = 'Line ' + str(line2), font = ('Arial Bold', 16)).pack()
                
            def back():
                for widget in f1r.winfo_children():
                    widget.destroy()
                for widget in f3l.winfo_children():
                    widget.destroy()
                for widget in f3r.winfo_children():
                    widget.destroy()
                for widget in f4r.winfo_children():
                    widget.destroy()
                for widget in frame2.winfo_children():
                    if re.search(r"button",widget.winfo_name()):
                        widget.config(state = 'normal')
                f1l.pack()
                f3l.pack(side = TOP, padx = 15)
                res_rd = np.asarray([str(round(100*res[i],2))+'%' for i in range(len(res))])
                printout(f3l, res_rd, wf = 1)
                lb1 = Label(f3l, text = 'Line ' + str(line1), font = ('Arial Bold', 16)).pack()
                f4l.pack()
                dataset2 = None
            
            bgim = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Accept.png')) 
            bim = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Back.png'))
            ac_bt = tkt.Button(f1b, image = bgim, borderwidth = 0, command = clickc)
            ac_bt.photo = bgim
            ac_bt.pack(side = LEFT)
            bk_bt = tkt.Button(f1b, image = bim, borderwidth = 0, command = back)
            bk_bt.photo = bim
            bk_bt.pack(side = LEFT)
            
        if l == 'X':
            dataset2 = None
        
    
    def PieChart():
        for widget in f4l.winfo_children():
            widget.destroy()
        
        if f4r in locals():
            for widget in f4r.winfo_children():
                widget.destroy()

        ttk.Label(f4l, text = 'Pie Chart').pack()
        
        PieChartDraw(res, f4l)
    
    def begin():
        global flag, res, p_table, Hmapxt, parttime
        
        try:
            with open("data.txt") as f:
                dicts = eval(f.read())
                Hmapxt = int(dicts['Hmapxt'])
                parttime = int(dicts['parttime'])
            f.close()
        except FileNotFoundError:
            Hmapxt = 5
            parttime = 60
            
        res = calc_duration_parameters(st_time, end_time, wf = 1)
        res_rd = [str(round(100*res[i],2))+'%' for i in range(len(res)-2)]
        res_rd.append(str(res[4]))
        res_rd.append(str(res[5]))
         
        for widget in frame2.winfo_children():
            widget.destroy()        
        for widget in f3l.winfo_children():
            widget.destroy()
        for widget in f4l.winfo_children():
            widget.destroy()
        for widget in frameh.winfo_children():
            widget.destroy()
            
        p_table = htmp_calc()
        printout(f3l, res_rd, wf = 1)
        PieChart()
        
        lb1 = Label(f3l, text = 'Line ' + str(line1), font = ('Arial Bold', 16)).pack()
        
        image3 = Image.open(dir_path+'/Internship buttons/gear.png')
        image3 = image3.resize((30,30),Image.ANTIALIAS)
        Set_image=ImageTk.PhotoImage(image3)
        Set_bt = tkt.Button(frame2, image = Set_image,borderwidth=0,command = Settings)
        Set_bt.photo = Set_image
        clim = Image.open(dir_path+'/Internship buttons/Compare High Speed Test Lines.png')
        clim = ImageTk.PhotoImage(clim)
        com_lin = tkt.Button(frame2, image = clim, borderwidth = 0, command = lambda : comp_lin('C'))
        com_lin.photo = clim
        ctim = Image.open(dir_path+'/Internship buttons/Compare Test Lines.png')
        ctim = ImageTk.PhotoImage(ctim)
        #begin_A.photo = lA
        com_test = tkt.Button(frame2, image = ctim, borderwidth = 0, command = lambda: comp_lin('T'))
        com_test.photo = ctim
        #begin_B.photo = lB
        Gpdf = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Generate PDF Report.png'))
        begin_rep= tkt.Button(frame2, image = Gpdf, borderwidth = 0, command = lambda: gen_pdf(res_rd))
        begin_rep.photo = Gpdf
        hm = tkt.Button(frame2, image = him, borderwidth = 0, command = lambda : plotmap(p_table))
        hm.photo = him
        ip = tkt.Button(frame2, image = ipim, borderwidth = 0, command = inplot)
        ip.photo = ipim
            
        hm.pack(side = LEFT, padx = 10)
        ip.pack(side = LEFT, padx = 10)
        Set_bt.pack(side = RIGHT, padx=(10,20))
        com_lin.pack(side = RIGHT, padx = 10)
        com_test.pack(side = RIGHT, padx = 10)
        begin_rep.pack(side = RIGHT, padx = 10)



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
            
            #RunChartParameters(window3, 0, 'P')
            RunCharts(0,l = 'P')
            RunCharts(1,l = 'P')
            RunCharts(2,l = 'P')
            RunCharts(3,l = 'P')
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
        mbx.after(5000, checkwrite)
        mbx.lift()
        mbx.call('wm', 'attributes', '.', '-topmost', True)
        mbx.mainloop()
                
    def clicked3():
        global end_time, calcflag
        end_time = etime_cmb3.get()
        end_time = dt.datetime.strptime(end_time,'%d-%m-%Y %H:%M:%S')
        calcflag = 0
        begin()
        
    def bkclick():
        window3.destroy()
        window2()
        
           
    if t == 1:
        comp_lin('R')
        
    if t == None:
        bim = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Back.png'))
        back_bt = tkt.Button(f1b,image = bim, borderwidth = 0,command = bkclick)
        #back_bt = tkt.Button(frame1, image = bim, borderwidth = 0, command = bkclick)
        #back_bt.photo = bim
        back_bt.pack(side = RIGHT, padx = 10)
        bgim = ImageTk.PhotoImage(Image.open(dir_path+'/Internship buttons/Go.png'))    
        begin_O = tkt.Button(f1b, image = bgim, borderwidth = 0, command = clicked3)
        begin_O.photo = bgim
        begin_O.pack(side = RIGHT, padx = 10)    
        window3.mainloop()
    
#%%
if __name__ =='__main__':
    main()
