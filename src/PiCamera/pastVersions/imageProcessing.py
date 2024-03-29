#!/usr/bin/env python
# -*- coding: utf-8 -*-

##import rospy

# import the necessary packages
import time
import cv2
from cv2 import aruco
import numpy as np
from math import atan2
from numpy import pi, cos, sin, array, shape


from picamera.array import PiRGBArray
from picamera import PiCamera


from detectionBuoy import detectBuoy, getColorRange
from detectionHorizonMast import horizonArea, detectMast
from detectionAruco import detectAruco


def run():


    cv2.namedWindow('Global', cv2.WINDOW_NORMAL)
#    cv2.namedWindow('Horizon', cv2.WINDOW_NORMAL)

    horizon_prev = (0, 320, 240)

    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)

    c = 0

###############          VIDEO           #############################
######################################################################
##    Running on test video
#    cap = cv2.VideoCapture('testImages/some_boats.mp4')

#    t0 = time.time()

#    dodo = 0.1

#    while(cap.isOpened()):

#        # Capture frame-by-frame
#        ret, image = cap.read()

#        if not ret:
#            break

#        image = cv2.resize(image, (640,480))



#################     CAMERA     ####################################
#####################################################################
#    Running with the camera
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 30

    camera.exposure_mode = 'sports'

    rawCapture = PiRGBArray(camera, size=(640, 480))

    # allow the camera to warmup
    time.sleep(0.1)

    dodo = 0

    t0 = time.time()
    Tframe, T1, T2, T3, T4, T5 = [], [], [], [], [], []
    tframe = 0

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

        if tframe != 0:
            Tframe.append(time.time()-tframe)
        tframe = time.time()

        image = frame.array

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
######################################################################
######################################################################


        c += 1

##        #Find the area where horizon is located and return a frame containing the horizon, transformed to be horizontal.
##        #Takes about 0.04s per frame.
##        #horizon: image cropped around the horizon
##        #horizon_height: vertical position in pixels of the horizon in the cropped image (for masts detection)
##        #horizon_prev: vertical position in pixels of the horizon in the previous uncropped image, in case horizon is not
##        #detected in the new image.


        t1 = time.time()
#        horizon, horizon_height, horizon_prev = horizonArea(image, horizon_prev)
        T1.append(time.time()-t1)

##        #Find the areas where vertical lines are found (ie possible sailboats).
##        #Takes about 0.1s per frame.
##        #masts: image cropped around the horizon, where vertical lines are highlighted

#        t2 = time.time()
#        masts = detectMast(horizon, horizon_height)
#        T2.append(time.time()-t2)

##        #Find the buoy in the cropped image and highlight them in the result image
#        t3 = time.time()
#        colorRange = getColorRange()
#        center, buoy = detectBuoy(image, image.copy(), colorRange)
#        T3.append(time.time()-t3)

##        #Find the April Tags in the cropped image

#        t4 = time.time()
#        frame_markers, corners = detectAruco(image, buoy, aruco_dict)
#        T4.append(time.time()-t4)


#        t5 = time.time()
#        cv2.imshow('Horizon', masts)
        cv2.imshow('Global', image)
#        T5.append(time.time()-t5)


##        time.sleep(dodo)

#####################################################################
#############        INTERACTION          ###########################

#        t6 = time.time()
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
                break

        elif key == 32:
            key = cv2.waitKey(1) & 0xFF
            while key != 32:
                key = cv2.waitKey(1) & 0xFF

        elif key == ord('c'):
            cv2.imwrite('sample.png',masts)
            print("Picture saved")

#        print('T6', time.time()-t6)


    try:
        cap.release()
    except:
        pass
    cv2.destroyAllWindows()
    print("Total time : ",time.time()-t0)
    print("Computed frames : ", c)
    print("Global time per frame : ", (time.time()-t0)/c - dodo)
    print("Time horizon : ", np.mean(T1))
    print("Time per frame accurate: ", np.mean(Tframe))


if __name__ == "__main__":
    run()
