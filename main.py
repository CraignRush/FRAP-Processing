# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 11:10:18 2022

@author: damlatetiker
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage import io, measure, filters
from matplotlib.widgets import Slider, RectangleSelector, Button
import process_imgs

file_path = 'FRAP GFP-Ede1-GFP/test1.tif'


class ImageVisualizer:
    def __init__(self, file_path):
        self.fig, self.ax = plt.subplots(figsize=(30,20))
        self.mic_img = io.imread(file_path)
        self.file_path = file_path
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
        self.connect()
        return
    
    def connect(self):
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('key_press_event', self.on_press)
        self.slider.on_changed(self.update_from_slider)
        return
    
    def connect2(self):
        self.but1.on_clicked(self.ROI_method1)
        self.but2.on_clicked(self.ROI_method2)
        self.but3.on_clicked(self.export)
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
            self.ind_before, self.ind_after = process_imgs.detect_frap(self.curr_img)
            self.ax.set_title('Now showing the ROIs calculated with method 1.\nTo swith press button ROI method 2.\nTo see the background ROI press shift alt (not implemented yet)\nTo export press button Export')
            ax_met1 = self.fig.add_axes([0.8, 0.8, 0.1, 0.06])
            ax_met2 = self.fig.add_axes([0.8, 0.7, 0.1, 0.06])
            ax_met3 = self.fig.add_axes([0.8, 0.6, 0.1, 0.06])
            self.but1 = Button(ax_met1, 'ROI method 1')
            self.but2 = Button(ax_met2, 'ROI method 2')
            self.but3 = Button(ax_met3, 'Export')
            # mask_roi1 is the total area, mask_roi2 is the bleached area
            # To get the unbleached area (necessary for exporting, see the function process_imgs.export_intensity) we subtract the second mask from the first one
            self.mask_roi1, self.mask_roi2 = process_imgs.refine_ROIs(self.curr_img, self.ind_before, self.ind_after)
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
        self.mask_roi1, self.mask_roi2 = process_imgs.refine_ROIs(self.curr_img, self.ind_before, self.ind_after)
        self.draw_ROI(self.mask_roi1, self.mask_roi2)
        return
    
    def ROI_method2(self, event):
        self.ax.set_title('Now showing the ROIs calculated with method 2.\nTo swith press button ROI method 1.\nTo see the background ROI press shift alt (not implemented yet)\nTo export press button Export')
        self.mask_roi1, self.mask_roi2 = process_imgs.refine_ROIs2(self.curr_img, self.ind_before, self.ind_after)
        self.draw_ROI(self.mask_roi1, self.mask_roi2)
        return
    
    def get_background(self):
        process_imgs.get_background_(self.mic_img, self.area_cond)
        return
        
    def export(self, event):
        process_imgs.export_intensity(self.curr_img, self.mask_roi1, self.mask_roi2, self.file_path)
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


visualizer = ImageVisualizer(file_path)
