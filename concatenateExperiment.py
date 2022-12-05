import pandas as pd
import tkinter as tk
from tkinter import filedialog
from os import listdir
from os.path import isfile, join
from pprint import pprint


# Create Tk root
tk_root = tk.Tk()
# Hide the main window
tk_root.withdraw()
tk_root.call('wm', 'attributes', '.', '-topmost', True)
file_dir = filedialog.askdirectory(initialdir='./')
file_list =  [f for f in listdir(file_dir) if isfile(join(file_dir, f)) and f.endswith('.xlsx')]


data = []
for f in file_list:
    data.append(pd.read_excel(file_dir + '/' + f))
    break
pprint(data[])

# #TODO New script: concatenate double and single norm from whole FRAP experiment, first colum frame time
    
#     results = {'Area(all)':area_total,
#                'Mean_intensity(all)': mean_intensity_whole_area,
#                'Area(bleached)': area_bleached,
#                'Mean_intensity(bleached)': mean_intensity_bleached_area,
#                'Area(unbleached)': area_unbleached,
#                'Mean_intensity(unbleached)': mean_intensity_unbleached_area,
#                'Cumulative Frame Time / s': frametimes,
#                'Double Normalization': doubleNorm,
#                'Single Normalization': singleNorm}
    
#     results = pd.DataFrame(data=results)
#     excel_path = file_path[:-4]+'.xlsx'
#     print('wrote results to' + excel_path)
#     results.to_excel(excel_path)   
#     return