import cv2 as cv2
import numpy as np
import os
import time

import get_score_data

def read_image(img):
    h, w, _ = img.shape
    rois = {} # dict of images of regions of interest, different masked off areas of score image
    # creating ROIs
    for mask in os.listdir('resources/masks/'):
        thismask = cv2.imread(os.path.join('resources/masks/', mask), cv2.IMREAD_GRAYSCALE)
        # resizing mask to original image
        thismask = cv2.resize(thismask, (w, h), interpolation=cv2.INTER_NEAREST) 
        rois[mask[:-4]] = cv2.bitwise_and(img, img, mask=thismask) 

    score_data = {}
    # getting data from each ROI
    start = time.perf_counter()
    score_data['mode'] = get_score_data.find_mode(rois['mode'])
    end = time.perf_counter()
    #score_data.update(get_score_data.find_chart_info(rois['chart_info'], score_data['mode']))
    #score_data.update(get_score_data.find_score_values(rois['score_values']))
    #score_data.update(get_score_data.find_effectors(rois['effectors'], score_data['mode']))

    print(score_data)
    print(end-start)