# C:/Users/Johann/miniconda3/pip3
# C:/Users/Johann/miniconda3/python3
#!python 3.9.7

import tkinter as tk
from tkinter import filedialog, messagebox
from os import listdir
from os.path import isfile, join
import logging
import sys
from pprint import pprint
import matplotlib.pyplot as plt
from ImageVisualizer import ImageVisualizer
logging.basicConfig(stream=sys.stderr, level=logging.INFO)


def check_file_list_overwrite(fd):
    fl = [f for f in listdir(fd) if isfile(join(fd, f)) and f.endswith('.tif')]
    xlsx_files = [f.removesuffix('.xlsx') for f in listdir(fd) if isfile(join(fd, f)) and f.endswith('.xlsx')]
    result = messagebox.askyesnocancel('Old processing files found!','Would you like to overwrite them?')
    if result:
        return fl
    elif result is False:
        return [t for t in fl if t.removesuffix('.tif') not in xlsx_files]
    else:
        return []

# Create Tk root
if 1:
    tk_root = tk.Tk()
    # Hide the main window
    tk_root.withdraw()
    tk_root.call('wm', 'attributes', '.', '-topmost', True)
    file_dir = filedialog.askdirectory(initialdir='./')
else:
    file_dir = r'/app_home/data/'
file_list = check_file_list_overwrite(file_dir)
pprint(file_list)

for f in file_list:
    file_path = file_dir + '/' + f
    print(file_path)
    try:
        vis = ImageVisualizer(file_path)
        plt.show(block=True)
        #t1 = Thread(target = vis.get_canvas().start_event_loop(), name='ImageVisualizer')
        #t1.daemon = True
        #t1.start()        
    except Exception as e:
       logging.info('error during execution of ImageVisualizer')
       logging.info('{}'.format(str(e)))
       sys.exit()
    if not messagebox.askokcancel('Do you want to continue?','Do you want to continue?') :
       sys.exit()