import numpy as np
import cv2 as cv
import time

camera = cv.VideoCapture(0) 
#camera = cv.VideoCapture(0,cv.CAP_DSHOW) 
#camera = cv.VideoCapture("http://93.48.88.159/mjpg/video.mjpg")

while True:
    hasFrame, frame = camera.read()
    if not hasFrame:
        break
    cv.imshow('camera',frame)
    key = cv.waitKey(10) & 0xff
    if key == 27:
        break
    elif key == ord('s'): # save the image
        name = str(round(time.time()))
        cv.imwrite(name+'.png',frame)

camera.release()
cv.destroyAllWindows()
