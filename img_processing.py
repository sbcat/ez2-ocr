import cv2
import numpy as np

import params

def get_bounding_box(img):
    """
    gets position and size of game screen in case input not perfectly cropped
    """
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, img = cv2.threshold(img, params.IMG_CROP_MIN_BRIGHTNESS, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = np.vstack(contours)
    cnt = cv2.convexHull(contours)
    x, y, w, h = cv2.boundingRect(cnt)
    return (x, y, w, h)