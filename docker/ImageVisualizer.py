# C:/Users/Johann/miniconda3/pip3
# C:/Users/Johann/miniconda3/python3
#!python 3.9.7
#  -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 11:10:18 2022

@author: damlatetiker & johannbrenner
"""

import logging
import sys
from matplotlib.backend_bases import FigureCanvasBase
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, measure # type: ignore
from matplotlib.widgets import Slider, RectangleSelector, Button, PolygonSelector # type: ignore
import cv2
from analzer import detect_frap, correct_drift, refine_ROIs,refine_ROIs2,get_background_,export_intensity
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

class ImageVisualizer:
    '''
    A class to visualize a 3D-stack (t,x,y) in a Matplotlib window and detects the FRAP data.
    '''
    def __init__(self, path):
        self.file_path = path   
        self.supersampling = 2
        self.drift_correction = True
        self.create_figure(self.file_path)
        self.update()
        self.connect()

    def create_figure(self, path) -> None:
        self.fig, self.ax = plt.subplots(figsize=(9,6))      
        self.mic_img = io.imread(path)


        self.slices, rows, cols = self.mic_img.shape

        self.mic_img_dim = (int(cols * self.supersampling), int(rows * self.supersampling))
        if self.supersampling > 1:
            logging.info('Supersampling image to a final resolution of {}x{}'.format(self.mic_img_dim[0], self.mic_img_dim[1]))
            self.mic_img_supersampled_tmp = np.zeros((self.slices,self.mic_img_dim[0], self.mic_img_dim[1]))
            for i in range(self.slices):
                self.mic_img_supersampled_tmp[i,:,:] = cv2.resize(self.mic_img[i,:,:],(self.mic_img_dim[0], self.mic_img_dim[1]), interpolation = cv2.INTER_LANCZOS4) 
            self.mic_img = self.mic_img_supersampled_tmp
            del self.mic_img_supersampled_tmp
            logging.info('Supersampling image finished')
        
        if self.drift_correction:          
            logging.info('Starting drift correction...')
            self.mic_img = correct_drift(self.mic_img)

        axslid = self.fig.add_axes([0.3, 0.03, 0.4, 0.03])
        self.slider = Slider(ax=axslid, label='Slice', valmin=0, valmax=self.mic_img.shape[0]-1, valinit=0, valstep=1, initcolor='none', color='lightgrey')
        

        self.ax.set_aspect('equal')
        self.ax.set_title('use scroll wheel to navigate images')
        self.selector = RectangleSelector(self.ax,self.select_roi)
        
        self.curr_img = self.mic_img
        self.ind = 0

        self.im = self.ax.imshow(self.mic_img[self.ind, :, :], cmap='gray')#, vmax=2000)
        self.curr_img_bbox = [-0.5, self.mic_img_dim[1]+.5, self.mic_img_dim[0]+.5, -0.5]

        self.update()
        return
    
    def connect(self) -> None:
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('key_press_event', self.on_press)
        self.slider.on_changed(self.update_from_slider)
        self.fig.canvas.mpl_connect('close_event',lambda event: self.fig.canvas.stop_event_loop())
        return
    
    def connect2(self) -> None:
        self.but1.on_clicked(self.ROI_method1)
        self.but2.on_clicked(self.ROI_method2)
        self.but3.on_clicked(self.export)
        #self.but4.on_clicked(self.load_next_stack)
        return
    
    def on_scroll(self, event) -> None:
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
            self.curr_img_bbox = [-0.5, self.mic_img_dim[1] + .5, self.mic_img_dim[0] + .5, -0.5]
            self.ax.set_title('use scroll wheel to navigate images')
            for line in self.ax.get_lines(): # ax.lines:
                line.remove()
            self.selector.set_active(True)
        elif event.key == 'enter':
            self.ind_before, self.ind_after = detect_frap(self.curr_img)          
            self.ax.set_title('Now showing the ROIs calculated with method 1.\n'+
                    'To swith press button ROI method 2.\nTo see the background ROI press shift alt (not implemented yet)\n'+
                    'To export press button Export\nTo export and load the next stack, press Next Stack\n')
            
            #tool_bar = self.fig.canvas.manager.toolbar
            #tool_bar.mode = ''
            self.selector.set_active(False)
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
            self.draw_ROI(self.mask_roi1, self.mask_roi2)
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
        #for line in self.ax.get_lines(): # ax.lines:
        #    line.remove()
        contour1 = measure.find_contours(mask1 == 1)[0]
        contour2 = measure.find_contours(mask2 == 1)[0]
        bbox = self.curr_img_bbox
        poly_full_props = dict(color='r', linestyle='--', linewidth=2, alpha=0.5)           
        self.poly_full = PolygonSelector(self.ax, onselect=self.on_select_poly1, props=poly_full_props, grab_range=10)
        # Add three vertices
        poly_full_vertices = []
        for i in range(1,len(contour1[:,1]),4):
            poly_full_vertices.append((contour1[i,1]+bbox[0]+0.5, contour1[i,0]+bbox[3]+0.5))
        self.poly_full.verts = poly_full_vertices

        poly_bleach_props = dict(color='b', linestyle='--', linewidth=2, alpha=0.5)           
        self.poly_bleach = PolygonSelector(self.ax, onselect=self.on_select_poly2, props=poly_bleach_props, grab_range=10)
        # Add three vertices
        poly_bleach_vertices = []
        for i in range(1,len(contour2[:,1]),4):
            poly_bleach_vertices.append((contour2[i,1]+bbox[0]+0.5, contour2[i,0]+bbox[3]+0.5))
        self.poly_bleach.verts = poly_bleach_vertices

        #self.ax.plot(contour1[:,1]+bbox[0]+0.5, contour1[:,0]+bbox[3]+0.5, c='r')
        #self.ax.plot(contour2[:,1]+bbox[0]+0.5, contour2[:,0]+bbox[3]+0.5, c='b')
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
    
    def on_select_poly1(self, vertices):
        #self.
        #self.poly1 = plt.Polygon(vertices, animated=True, color='r')
        #self.ax.add_patch(self.poly1)
        #print('Vertices: {}'.format(vertices))
        #self.poly1.verts = vertices
        #self.poly1.update()
        #self.im.axes.figure.canvas.draw()
        self.redraw_roi1(vertices)
        self.fig.canvas.draw_idle() 
        
    def on_select_poly2(self, vertices):
        #self.
        #self.poly1 = plt.Polygon(vertices, animated=True, color='r')
        #self.ax.add_patch(self.poly1)
        #print('Vertices: {}'.format(vertices))
        #self.poly1.verts = vertices
        #self.poly1.update()
        #self.im.axes.figure.canvas.draw()
        self.redraw_roi2(vertices)
        self.fig.canvas.draw_idle()
    
    def redraw_roi1(self, vertices):
        black_image = np.zeros((self.mask_roi1.shape[0],self.mask_roi1.shape[1]),dtype=np.uint8)
        vertices_normalized = np.array([*vertices])
        vertices_normalized[:,0] = vertices_normalized[:,0] - self.curr_img_bbox[0] -0.5
        vertices_normalized[:,1] = vertices_normalized[:,1] - self.curr_img_bbox[3] -0.5
        self.mask_roi1= cv2.fillPoly(black_image, pts =np.int32([vertices_normalized]), color=(255,255,255))
        #self.mask_roi1 = cv2.threshold(self.mask_roi1, 128, 255, cv2.THRESH_BINARY)[1]
        self.mask_roi1 = self.mask_roi1 > 128
        return
        #self.ax.imshow(self.mask_roi1, cmap='gray')#, vmax=2000)
        #self.mask_roi1 = cv2.threshold(self.mask_roi1,125)
        #self.mask_roi1[self.mask_roi1 ==(255,255,255)] = True 

    def redraw_roi2(self, vertices):
        black_image = np.zeros((self.mask_roi2.shape[0],self.mask_roi2.shape[1]),dtype=np.uint8)
        vertices_normalized = np.array([*vertices], dtype=np.float16)
        vertices_normalized[:,0] = vertices_normalized[:,0] - self.curr_img_bbox[0] -0.5
        vertices_normalized[:,1] = vertices_normalized[:,1] - self.curr_img_bbox[3] -0.5
        self.mask_roi2 = cv2.fillPoly(black_image, pts =np.int32([vertices_normalized]), color=(255,255,255))
        #self.mask_roi2 = cv2.threshold(self.mask_roi2, 128, 255, cv2.THRESH_BINARY)[1]
        self.mask_roi2 = self.mask_roi2 > 128
        return
        #self.ax.imshow(self.mask_roi2, cmap='gray')#, vmax=2000)
        #self.mask_roi1 = cv2.threshold(self.mask_roi1,125)
        #self.mask_roi1[self.mask_roi1 ==(255,255,255)] = True

    def get_canvas(self) -> FigureCanvasBase:
        return self.fig.canvas
     