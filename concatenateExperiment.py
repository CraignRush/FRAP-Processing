"""
 concatenateExperiment.py

 Author: Johann Brenner
 
Script to concatenate multiple FRAP experiment Excel files into a single results file.
Combines single and double normalization data from each input file into separate sheets.
"""

import pandas as pd
import tkinter as tk
from tkinter import filedialog
from os import listdir
from os.path import isfile, join
from pandas import ExcelWriter

# Set up file selection dialog
tk_root = tk.Tk()
tk_root.withdraw()  # Hide the main window
tk_root.call('wm', 'attributes', '.', '-topmost', True)  # Keep dialog on top

# Open directory selection dialog and get list of FRAP Excel files
file_dir = filedialog.askdirectory(initialdir='./')
file_list = [f for f in listdir(file_dir) 
             if isfile(join(file_dir, f)) and f.endswith('.xlsx') and 'FRAP' in f]

# Initialize dataframes to store combined results
single = None  # For single normalization data
double = None  # For double normalization data

# Process each FRAP file
for i, f in enumerate(file_list):
    # Read Excel file
    data = pd.read_excel(file_dir + '/' + f, header=0)
    
    if i == 0:
        # For first file, initialize dataframes with time column
        single = pd.DataFrame(data['Cumulative Frame Time / s'])
        double = pd.DataFrame(data['Cumulative Frame Time / s'])
    
    # Rename columns to use filename (without extension) as identifier
    file_identifier = f[:-5]
    single_rename = data.rename(columns={'Single Normalization': file_identifier})
    double_rename = data.rename(columns={'Double Normalization': file_identifier})
    
    # Concatenate data columns
    single = pd.concat([single, single_rename[file_identifier]], axis=1)
    double = pd.concat([single, double_rename[file_identifier]], axis=1)

# Define output file path
excel_path = join(file_dir, 'concatenatedResults.xlsx')

# Write results to Excel file with separate sheets
with ExcelWriter(excel_path) as writer:
    single.to_excel(writer, sheet_name='Single Normalized')
    double.to_excel(writer, sheet_name='Double Normalized')

print(f'Wrote combined results to {excel_path}')