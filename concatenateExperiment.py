import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
from os import listdir
from os.path import isfile, join
from pprint import pprint
from pandas import ExcelWriter


# Create Tk root
tk_root = tk.Tk()
# Hide the main window
tk_root.withdraw()
tk_root.call('wm', 'attributes', '.', '-topmost', True)
file_dir = filedialog.askdirectory(initialdir='./')
file_list =  [f for f in listdir(file_dir) if isfile(join(file_dir, f)) and f.endswith('.xlsx') and 'FRAP' in f]

i = 0
for f in file_list:    
    data = pd.read_excel(file_dir + '/' + f, header=0)
    if i == 0:
        single = pd.DataFrame(data= data['Cumulative Frame Time / s'])
        double = pd.DataFrame(data= data['Cumulative Frame Time / s'])
        column_name = ['Cumulative Frame Time / s']
    single_rename = data.rename(columns={'Single Normalization': f[:-5]})
    double_rename = data.rename(columns={'Double Normalization': f[:-5]})
    single = pd.concat([single,single_rename[f[:-5]]], axis=1)
    double = pd.concat([single,double_rename[f[:-5]]], axis=1)
    i += 1

excel_path = file_dir + '/' + 'concatenatedResults.xlsx'


with ExcelWriter(excel_path) as writer:        
    single.to_excel(writer,sheet_name='Single Normalized')  
    double.to_excel(writer,sheet_name='Double Normalized')   


print('wrote results to ' + excel_path)
#pprint(single_dict)