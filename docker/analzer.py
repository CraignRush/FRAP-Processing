# C:/Users/Johann/miniconda3/pip3
# C:/Users/Johann/miniconda3/python3
#!python 3.9.7
"""
Created on Tue Nov  1 16:09:06 2022

@author: damlatetiker & johannbrenner
"""
import copy
import logging
import sys
from typing import Any, Literal
import numpy as np
from skimage import filters, morphology, measure
import pandas as pd
import cv2
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def detect_frap(curr_img) -> tuple[np.signedinteger[Any], np.signedinteger[Any]]:
    # this function determines the last frame before and first frame after bleaching by:
    # defining a rough estimate for the bleached condenste via thresholding (li's method is used) the first frame
    # summing the intensity over all pixels in this ROI over the whole time series
    # determining the sudden drop in the intensity
    # curr_img should be an array of M x N x K with M indexing the time
    logging.info('Starting bleaching slice detection...')
    # Get the first frame from the image stack and determine the ideal threshold with li's method
    first_frame = curr_img[0].astype(float)
    thresh_li = filters.threshold_li(first_frame)
    
    # Create a mask where foreground is True and background is False by thresholding
    mask = first_frame > thresh_li
    # Remove objects smaller than a given size (for now 20 pixels) to get rid of other structures than the desired condenste
    mask = morphology.remove_small_objects(mask, 15)
    
    # initialize a list that would hold the sum of pixel intensities within the ROI over the time series
    int_seq = []
    for i in range(len(curr_img)):
        int_seq.append(np.sum(np.where(mask==True, curr_img[i], 0)))
    # Change the datatype of the intensity sequence to float, otherwise there are problems
    int_seq = np.array(int_seq).astype(float)
    # Take the 'derivative' of the intensity sequence, it should be 0 eg. constant function except for one very small number, the drop of intensity
    der = np.diff(int_seq)
    # Find where the derivative has a minimum, this is the index of the frame before bleaching
    ind_before = np.argmin(der)
    ind_after = ind_before+1
    
    return ind_before, ind_after


def correct_drift(movie,alignment_slice=None,upsample_factor=4, verbose = 0):
    # Define the optical flow parameters
    lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    # Define the initial parameters
    old_gray = movie[0]
    #old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    h, w = old_gray.shape
    shift_x = np.zeros((len(movie),))
    shift_y = np.zeros((len(movie),))    

    
    logging.info('starting iterative correction')
    # Initialize the corrected_shift_movie array
    corrected_shift_movie = np.zeros_like(movie)

    # Iterate through each frame in the movie
    for i in range(1, len(movie)):
        # Get the next frame and convert to grayscale
        frame = movie[i]
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate the optical flow using sparse Lucas-Kanade method
        p0 = cv2.goodFeaturesToTrack(old_gray, maxCorners=200, qualityLevel=0.01, minDistance=4)
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
        
        # Calculate the mean shift
        good_new = p1[st==1]
        good_old = p0[st==1]
        mean_shift = np.mean(good_new - good_old, axis=0)
        
        # Update the shift values
        shift_x[i] = shift_x[i-1] + mean_shift[0]
        shift_y[i] = shift_y[i-1] + mean_shift[1]
        
        # Translate the current frame to align with the previous frame
        M = np.array([[1, 0, shift_x[i]], [0, 1, shift_y[i]]], dtype=np.float32)
        corrected_frame = cv2.warpAffine(frame_gray, M, (w, h))
        corrected_shift_movie[i] = corrected_frame
        
        # Set the current frame as the previous frame for the next iteration
        old_gray = frame_gray.copy()

    # Set the first frame in the corrected_shift_movie to be the same as in the original movie
    corrected_shift_movie[0] = movie[0]
    return corrected_shift_movie


def refine_ROIs(curr_img, ind_before, ind_after):
    # Refine the ROI by taking the average of all frames up to bleaching and thresholding this average image
    # one needs to take ind_before+1 since indexing starts at 0
    frames_before = curr_img[:ind_before]
    img_avg = np.mean(frames_before, axis=0)
    
    # Determine the ideal threhold for the average image with li's method and apply it to get a mask
    thresh_li1 = filters.threshold_li(img_avg)
    mask_roi1 = img_avg>thresh_li1
    mask_roi1 = morphology.remove_small_objects(mask_roi1, 20)
    
    # get the first frame after bleaching
    first_after = curr_img[ind_after].astype(float)
    
    # Determine the ideal threhold for the first frame after bleaching with li's method and apply it to get a mask
    thresh_li2 = filters.threshold_li(first_after)
    mask_int = first_after>thresh_li2
    mask_int = morphology.remove_small_objects(mask_int, 20)
    
    # The second ROI (bleaching site) are the pixels that are true in the first mask and false in the second one
    mask_roi2 = copy.deepcopy(mask_roi1)
    mask_roi2[mask_int==True] = False
    
    # Make sure you have only one region, as the process above may introduce some problems
    label_image,label_num = measure.label(mask_roi2, return_num = True)
    if label_num > 1:

        assert( label_image.max() != 0 ) # assume at least 1 CC
        mask_roi2 = label_image == np.argmax(np.bincount(label_image.flat)[1:])+1

        #mask_roi2 = mask_roi2()
        #raise NotImplementedError('The mask for the bleached area should have 1 label but instead has {}'.format(np.amax(label_image)))
        # It is not yet implemented how to deal with such an incorrect segmentation
    elif label_num == 0 :
        mask_roi2 = copy.deepcopy(mask_roi1)
    return mask_roi1, mask_roi2

def refine_ROIs2(curr_img, ind_before, ind_after) -> tuple[Literal[0], Literal[0]]:
    print('The second method for ROI calculation is not implemented yet')
    return 0, 0
def get_background_(mic_img, area_cond):
    avg_img = np.mean(mic_img, axis=0)
    thresh_mean = filters.threshold_mean(avg_img)
    backg_mask = avg_img<thresh_mean
    backg_size = int(np.sqrt(3*area_cond))
    
    return

def export_intensity(curr_img, mask_roi1, mask_roi2, file_path) -> None:
    # Total area
    img_area_1 = copy.deepcopy(curr_img)
    img_area_1[:, mask_roi1==False] = 0
    area_total_ = np.sum(mask_roi1)
    area_total = np.ones(len(curr_img))*area_total_
    mean_intensity_whole_area = np.sum(np.sum(img_area_1, axis=1), axis=1)/area_total_
    
    # Bleached area
    img_area_2 = copy.deepcopy(curr_img)
    img_area_2[:, mask_roi2==False] = 0
    area_bleached_ = np.sum(mask_roi2)
    area_bleached = np.ones(len(curr_img))*area_bleached_
    mean_intensity_bleached_area = np.sum(np.sum(img_area_2, axis=1), axis=1)/area_bleached_
    
    # Unbleached area
    mask_roi3 = copy.deepcopy(mask_roi1)
    mask_roi3[mask_roi2==True] = False
    img_area_3 = copy.deepcopy(curr_img)
    img_area_3[:, mask_roi3==False] = 0
    area_unbleached_ = np.sum(mask_roi3)
    area_unbleached = np.ones(len(curr_img))*area_unbleached_
    mean_intensity_unbleached_area = np.sum(np.sum(img_area_3, axis=1), axis=1)/area_unbleached_
    
    ## TODO: Parse frame times and write cumulative frame time
    
    ## TODO: Implement prebleach series length
    
    # doubleNoormlization = [(TotalROI_1-20 - Bg_1-20) * (TotalROI_slice - Bg_slice)] / [(Bleached_1-20 - Bg_1-20) * (Bleached_slice - Bg_slice)] 
    # singleNormalization = [Bleached_slice - Bg_slice] / [Bleach_1-20 - Bg_1-20]
    
    #TODO New script: concatenate double and single norm from whole FRAP experiment, first colum frame time
    
    results = {'Area(all)':area_total,
               'Mean_intensity(all)': mean_intensity_whole_area,
               'Area(bleached)': area_bleached,
               'Mean_intensity(bleached)': mean_intensity_bleached_area,
               'Area(unbleached)': area_unbleached,
               'Mean_intensity(unbleached)': mean_intensity_unbleached_area}
    
    results = pd.DataFrame(data=results)
    excel_path = file_path[:-4]+'.xlsx'
    print('wrote results to' + excel_path)
    results.to_excel(excel_path)   
    return
    
