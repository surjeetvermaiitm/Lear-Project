#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 21 17:40:13 2020

@author: syshain
"""
#%%

import numpy as np
import pandas as pd
from collections import Counter
filepath = '/home/syshain/Arshad/Lear_India_Remote_Internship/Task2_OEE/HSL1/'

#%%

dataset = pd.read_csv(filepath + 'HSL1_Report_modified_for_OEE.csv')
date = dataset['Date']
times = dataset['Time']
LineId = dataset[' Line ID']
result = dataset[' Result']

#%%

del_time = pd.to_timedelta(times)
time_differences = np.asarray([del_time[i+1]-del_time[i] for i in range(len(del_time)-1)])
max_rep = Counter(time_differences).most_common(4)
'This line finds the most common time difference which can be taken as the ideal time required to produce one set of LH and RH recliners'
cycle_time = (max_rep[1][0]).total_seconds()/4

#%%
'This cell calculates the relevant intermediate quantities'
unplanned_dt = time_differences.sum(initial = pd.to_timedelta('00:00:00'), where = (time_differences > pd.to_timedelta('00:01:00')))
no_ok = Counter(result)['OK']
no_ng = Counter(result)['NG']
total_possibility = 24*3600/cycle_time

#%%
availability = 1 - unplanned_dt/pd.to_timedelta('24:00:00')
quality = no_ok/(no_ok + no_ng)
OEE = no_ok/total_possibility
performance = OEE/(availability*quality)

#%%
'This cell prints all the results'
print('The required results from the calculations are as follow:' + '\n' + 'OEE: ' + str(OEE) + '\n'+ 'Availability: ' + str(availability) + '\n' + 'Performance: ' + str(performance) + '\n' + 'Quality: ' + str(quality))

#%%
'This cell prepares the data for calculation of hourly quantities'
timear = pd.to_datetime(dataset['Date'] + ' ' + dataset['Time'])
hourly_distribution = []
result_hrly = []
hrly_diff = []
blank = 0
onehr = pd.to_timedelta('1:00:00')
starttime = pd.to_datetime('15-10-2019'+' ' + '7:00:00')

#%%
'This cell contains a loop to continue quantity preparation and converts them to appropriate types'
for i in range(17):
    hourly_distribution.append(timear[np.where(timear > starttime+i*(onehr))[0][0]:(np.where(timear > starttime+(i+1)*(onehr))[0][0])-1])
    result_hrly.append(result[np.where(timear > starttime+i*(onehr))[0][0]:(np.where(timear > starttime+(i+1)*(onehr))[0][0])-1])
    hrly_diff.append([hourly_distribution[i][j+1] - hourly_distribution[i][j] for j in range(blank, blank + len(hourly_distribution[i])-1)])
    blank = (np.where(timear > starttime+(i+1)*(onehr))[0][0])

#%%
'This cell calculates the most important quantities relating to the final calculations'
hrly_diff = np.array(hrly_diff)
hrly_unplanned = []
for i in range(len(hourly_distribution)):
    hrly_unplanned.append(np.array(hrly_diff[i]).sum(initial = pd.to_timedelta('00:00:00'), where  = (np.array(hrly_diff[i]) > pd.to_timedelta('00:01:00'))))
ok_hrly = np.array([Counter(result_hrly[i])['OK'] for i in range(len(result_hrly))])
ng_hrly = np.array([Counter(result_hrly[i])['NG'] for i in range(len(result_hrly))])
hrly_possibility = total_possibility/24;

#%%
'This cell calculates all the final hourly quantities'
availability_hrly = 1 - np.divide(hrly_unplanned,pd.to_timedelta('1:00:00'))
quality_hrly = np.divide(ok_hrly,(ok_hrly + ng_hrly))
OEE_hrly = ok_hrly / hrly_possibility
performance_hrly = OEE_hrly/(availability_hrly*quality_hrly)
#%%
'This cell plots the relevant quantities'
import matplotlib.pyplot as plt
hours = np.arange(8,25,1)
plt.plot(hours, availability_hrly, 'r-')
plt.plot(hours, quality_hrly, 'g--')
plt.plot(hours, OEE_hrly, 'k')
plt.plot(hours, performance_hrly, 'm')
plt.title('Hourly plot of Industry Quantities', fontsize = 16)
plt.legend(('Availability', 'Quality', 'OEE', 'Performance'))
plt.show()

#%%
'This cell prepares the respective quantities for the generation of a heat map'
result_minutely = []
fivemin = pd.to_timedelta('00:05:00')
starttime = pd.to_datetime('15-10-2019'+' ' + '7:00:00')
#%%"
'This cell contains a loop to continue quantity preparation and converts them to appropriate types'
for i in range(len(hourly_distribution)*12):
    result_minutely.append(result[np.where(timear > starttime+i*(fivemin))[0][0]:(np.where(timear > starttime+(i+1)*(fivemin))[0][0])-1])
#%%
'This cell calculates the most important quantities relating to the final calculations'    
ok_minutely = np.array([Counter(result_minutely[i])['OK'] for i in range(len(result_minutely))])
ng_minutely = np.array([Counter(result_minutely[i])['NG'] for i in range(len(result_minutely))])

#%%
'This cell prepares quantities for heat map plotting'
import seaborn as sns
h1 = np.linspace(np.array([8]*12), np.array([24]*12), 17).flatten()
h2 = h1-1
m1 = np.arange(5,65,5)
m2 = m1-5
hString = np.array(["{1} - {0}".format(v1,v2) for v1,v2 in zip(h1,h2)])
mString = np.array(["{1} - {0}".format(v1,v2) for v1, v2 in zip(m1,m2)]*17)
df = pd.DataFrame({'hours': hString, 'minutes': mString, 'OK': ok_minutely}, index = np.arange(204))
p_table = pd.pivot_table(df, values ='OK', index ='hours' ,columns ='minutes')
in1 = [hString[i*12] for i in np.arange(17)]
in2 = mString[0:12]
p_table = p_table.reindex(in1)
p_table.columns = p_table.columns.reindex(in2)[0]

#%%
'Here the final heat map is plotted'
fig, ax = plt.subplots(figsize = (15,8))
plt.title('Hourly Heat Map, every five minutes')
sns.heatmap(p_table, cmap = 'RdYlGn', annot = p_table.values)
#%%