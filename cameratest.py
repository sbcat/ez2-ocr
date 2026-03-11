import cv2
import time
from contextlib import contextmanager

import readimage
import img_processing
import params

@contextmanager
def VideoCapture(*args, **kwargs):
    cap = cv2.VideoCapture(*args, **kwargs)
    try:
        yield cap
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
template = cv2.imread('resources/stageresult.png', cv2.IMREAD_GRAYSCALE)
x, y, w, h = None
with VideoCapture(0, cv2.CAP_DSHOW) as cap:
    while True:
        _, img = cap.read()
        if x is None:
            x, y, w, h = img_processing.get_bounding_box(img)

        img = img[y:y+h, x:x+w] # cropping image to bounding box found earlier
        img_cmp = cv2.resize(img, (640, 480))
        img_cmp = cv2.cvtColor(img_cmp, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(img_cmp, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        #print(max_val)
        if max_val >= params.TEMPLATE_MATCH_THRESHOLD:
            detected_time = time.time() # need to wait for score screen to fade in 
            while time.time() <= detected_time + 1.8: # can't just time.sleep, need to keep buffer current
                _, img = cap.read() 

            img = img[y:y+h, x:x+w]
            print("score found")

            break

#cv2.imwrite("h.png", img)
readimage.read_image(img)

