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
