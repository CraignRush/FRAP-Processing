# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 11:10:18 2022

@author: damlatetiker
"""


import numpy as np
import matplotlib.pyplot as plt
from skimage import io, measure, filters
from matplotlib.widgets import Slider, RectangleSelector, Button
import tkinter as tk
from tkinter import filedialog, messagebox
from os import listdir, _exit
from os.path import isfile, join
import logging, sys, time
logging.basicConfig(stream=sys.stderr, level=logging.INFO)



class ImageVisualizer:
    def __init__(self):
        return
    def __init__(self, path):
        self.file_path = path                        
        self.createFigure(self.file_path)
        self.update()
        self.connect()
        return

    # def __init__(self, path, filelist= []):
    #     if filelist.len() == 0 and path.endswith('.tif'):
    #         self.file_path = path
    #     elif filelist.len() > 0:
    #         self.file_dir = path
    #         self.file_list = filelist
    #         self.file_path = self.file_dir + '/' + self.file_list.pop(0)
    #     else:
    #         logging.debug(path)
    #         raise Exception('Unknown file path')

    #     self.createFigure()
    #     self.update()
    #     self.connect()
    #     return


    def createFigure(self, path):
        self.fig, self.ax = plt.subplots(figsize=(9,6))  
        self.mic_img = io.imread(path)
        axslid = self.fig.add_axes([0.3, 0.03, 0.4, 0.03])
        self.slider = Slider(ax=axslid, label='Slice', valmin=0, valmax=self.mic_img.shape[0]-1, valinit=0, valstep=1, initcolor='none', color='lightgrey')
        

        self.ax.set_aspect('equal')
        self.ax.set_title('use scroll wheel to navigate images')
        self.selector = RectangleSelector(self.ax,self.select_roi)
        
        self.curr_img = self.mic_img
        self.slices, rows, cols = self.mic_img.shape
        self.ind = 0

        self.im = self.ax.imshow(self.mic_img[self.ind, :, :], cmap='gray')#, vmax=2000)
        self.curr_img_bbox = [-0.5, 255.5, 255.5, -0.5]
        self.update()
        return
        
# #def load_next_stack(self, event):    
#         logging.info(self.file_list)       
#         if self.file_list.len() > 0:              
#             self.file_path = self.file_dir + '/' + self.file_list.pop(0)  
#             plt.close('all')
#             #self.createFigure(self.file_path)            
#             return
#         else:
#             messagebox.showinfo('Finished!')
#             plt.close()
#             _exit() 
    
    def connect(self):
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('key_press_event', self.on_press)
        self.slider.on_changed(self.update_from_slider)
        return
    
    def connect2(self):
        self.but1.on_clicked(self.ROI_method1)
        self.but2.on_clicked(self.ROI_method2)
        self.but3.on_clicked(self.export)
        #self.but4.on_clicked(self.load_next_stack)
        return
    
    def on_scroll(self, event):
        #print("%s %s" % (event.button, event.step))
        if event.button == 'up':
            self.ind = (self.ind + 1) % self.slices
        else:
            self.ind = (self.ind - 1) % self.slices
        self.slider.set_val(self.ind)
        self.update()
        return
        
    def on_press(self, event):
        if event.key == 'up' or event.key == 'right':
            self.ind = (self.ind + 1) % self.slices
        elif event.key == 'down'or event.key == 'left':
            self.ind = (self.ind - 1) % self.slices
        elif event.key == 'shift+alt':
            self.curr_img = self.mic_img
            self.curr_img_bbox = [-0.5, 255.5, 255.5, -0.5]
            self.ax.set_title('use scroll wheel to navigate images')
        elif event.key == 'enter':
            self.ind_before, self.ind_after = detect_frap(self.curr_img)
            self.ax.set_title('Now showing the ROIs calculated with method 1.\n'+
                    'To swith press button ROI method 2.\nTo see the background ROI press shift alt (not implemented yet)\n'+
                    'To export press button Export\nTo export and load the next stack, press Next Stack\n')
            ax_met1 = self.fig.add_axes([0.8, 0.8, 0.1, 0.06])
            ax_met2 = self.fig.add_axes([0.8, 0.7, 0.1, 0.06])
            ax_met3 = self.fig.add_axes([0.8, 0.6, 0.1, 0.06])            
            #ax_met4 = self.fig.add_axes([0.8, 0.5, 0.1, 0.06])
            self.but1 = Button(ax_met1, 'ROI method 1')
            self.but2 = Button(ax_met2, 'ROI method 2 \n not implem. ')
            self.but3 = Button(ax_met3, 'Export')
            #self.but4 = Button(ax_met4, 'Next Stack')
            # mask_roi1 is the total area, mask_roi2 is the bleached area
            # To get the unbleached area (necessary for exporting, see the function export_intensity) we subtract the second mask from the first one
            self.mask_roi1, self.mask_roi2 = refine_ROIs(self.curr_img, self.ind_before, self.ind_after)
            self.area_cond = np.sum(self.mask_roi1)
            self.get_background()
            contour1 = measure.find_contours(self.mask_roi1 == 1)[0]
            contour2 = measure.find_contours(self.mask_roi2 == 1)[0]
            bbox = self.curr_img_bbox
            self.ax.plot(contour1[:,1]+bbox[0]+0.5, contour1[:,0]+bbox[3]+0.5, c='r')
            self.ax.plot(contour2[:,1]+bbox[0]+0.5, contour2[:,0]+bbox[3]+0.5, c='b')
            self.connect2()
        self.slider.set_val(self.ind)
        self.update()
        return
  
    
    def ROI_method1(self, event):
        self.ax.set_title('Now showing the ROIs calculated with method 1.\nTo swith press button ROI method 2.\nTo see the background ROI press shift alt (not implemented yet)\nTo export press button Export')
        self.mask_roi1, self.mask_roi2 = refine_ROIs(self.curr_img, self.ind_before, self.ind_after)
        self.draw_ROI(self.mask_roi1, self.mask_roi2)
        return
    
    def ROI_method2(self, event):
        self.ax.set_title('Now showing the ROIs calculated with method 2.\nTo swith press button ROI method 1.\nTo see the background ROI press shift alt (not implemented yet)\nTo export press button Export')
        self.mask_roi1, self.mask_roi2 = refine_ROIs2(self.curr_img, self.ind_before, self.ind_after)
        self.draw_ROI(self.mask_roi1, self.mask_roi2)
        return
    
    def get_background(self):
        get_background_(self.mic_img, self.area_cond)
        return
        
    def export(self, event):
        export_intensity(self.curr_img, self.mask_roi1, self.mask_roi2, self.file_path)
        self.Finished = True
        return
    
    def draw_ROI(self, mask1, mask2):
        self.ax.lines=[]
        contour1 = measure.find_contours(mask1 == 1)[0]
        contour2 = measure.find_contours(mask2 == 1)[0]
        bbox = self.curr_img_bbox
        self.ax.plot(contour1[:,1]+bbox[0]+0.5, contour1[:,0]+bbox[3]+0.5, c='r')
        self.ax.plot(contour2[:,1]+bbox[0]+0.5, contour2[:,0]+bbox[3]+0.5, c='b')
        self.im.set_extent(bbox)
        return  
            
    def update(self):
        self.im.set_extent(self.curr_img_bbox)
        self.im.set_data(self.curr_img[self.ind, :, :])
        self.ax.set_aspect('equal')
        self.ax.set_ylabel('slice %s' % self.ind)
        self.im.axes.figure.canvas.draw()
        self.fig.canvas.draw_idle()
        return

    def update_from_slider(self, val):
        self.ind = val
        self.update()
        return
    
    def select_roi(self, eclick, erelease):
        self.curr_img = self.mic_img[:, int(eclick.ydata):int(erelease.ydata), int(eclick.xdata):int(erelease.xdata)]
        self.curr_img_bbox = [int(eclick.xdata)-0.5, int(erelease.xdata)-0.5, int(erelease.ydata)-0.5, int(eclick.ydata)-0.5]
        self.ax.set_title('Are you happy with the current ROI?\nTo reset press shift and alt\nTo continue with automated selection press enter')
        self.update()
        return
