#!/usr/bin/env python
# -*- coding: utf-8 -*-

##import rospy

# import the necessary packages
import time
import cv2
import numpy as np
from math import atan2
from numpy import pi, cos, sin, array, shape



def run():

    t0 = time.time()

    cap = cv2.VideoCapture('testImages/some_boat.mp4')
    cv2.namedWindow('Result', cv2.WINDOW_NORMAL)

    horizon_prev = (0, 320, 240)
    c = 0
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, image = cap.read()

        if ret:
            c += 1

            image = cv2.resize(image, (640,480))

#            cv2.imshow('Origin', image)

            #Find the area where is horizon is located and return a frame containing the horizon, transformed to be horizontal.
            #Takes about 0.04s per frame.
            horizon, horizon_height, horizon_prev = horizonArea(image, horizon_prev)

            #Find the areas where vertical lines are found (ie possible sailboats).
            #Takes about 0.1s per frame.
            masts, xMasts = detectMast(horizon, horizon_height)

            cv2.imshow('Result', masts)
            time.sleep(0.1)

            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):
                    break

            if key == 32:
                key = cv2.waitKey(1) & 0xFF
                while key != 32:
                    key = cv2.waitKey(1) & 0xFF

            elif key == ord('c'):
                cv2.imwrite('sample.png',masts)
                print("Picture saved")

        else:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Total time : ",time.time()-t0)
    print("Computed frames : ", c)
    print("Time per frame : ", (time.time()-t0)/c - 0.1)







####################################################################################################################################
####################################################################################################################################
######################                           USEFUL FUNCTIONS                            #######################################
####################################################################################################################################
####################################################################################################################################




def horizonArea(image, horizon_prev):

    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#    grey = cv2.bilateralFilter(grey,9,40,10) #more precision, but slower than medianBlur
#    grey = cv2.medianBlur(grey,7)


#    cv2.imshow('Blur', grey)

    rows,cols = grey.shape
#    tTest = time.time()

    kernel = np.zeros((7,7))
    kernel_side = np.ones((3,7))
    kernel[:3] = -(1./(4*7))*kernel_side
    kernel[-3:] = (1./(4*7))*kernel_side
    grad_y = cv2.filter2D(grey,cv2.CV_16S,kernel)
    grad_y = np.uint8(np.absolute(grad_y))
#    print('T_test', time.time()-tTest)


    ret, bin_y = cv2.threshold(grad_y,10,255,0)


    if __name__ == "__main__":
        cv2.imshow('Grad', grad_y)
        cv2.imshow('Bin', bin_y)

    horizontalLines = cv2.HoughLines(bin_y,5,np.pi/180,100)

    if horizontalLines is not None:
        for rho,theta in horizontalLines[0]:
            rotation = (theta-np.pi/2)*180/np.pi

            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 10000*(-b))
            y1 = int(y0 + 10000*(a))
            x2 = int(x0 - 10000*(-b))
            y2 = int(y0 - 10000*(a))

            if abs(rotation) < 70 and abs(y0-horizon_prev[2]) < 70:

                if __name__ == "__main__":
                    cv2.line(image, (x1, y1), (x2, y2), (0,255,0), 1)

                horizon_prev = (rotation, x0, y0)

            else:
                rotation = horizon_prev[0]
                x0 = horizon_prev[1]
                y0 = horizon_prev[2]
    else:
        rotation = horizon_prev[0]
        x0 = horizon_prev[1]
        y0 = horizon_prev[2]

    M = cv2.getRotationMatrix2D((x0, y0),rotation,1)

    rotated = cv2.warpAffine(image,M,(cols,rows))

    rows_rotated, cols_rotated = shape(rotated)[0], shape(rotated)[1]

    horizon = int(M[1,0]*x0 + M[1,1]*y0 + M[1,2])
    left = max( int(M[0,0]*0 + M[0,1]*0 + M[0,2]), int(M[0,0]*0 + M[0,1]*rows_rotated + M[0,2]))+1
    right = min( int(M[0,0]*cols_rotated + M[0,1]*0 + M[0,2]), int(M[0,0]*cols_rotated + M[0,1]*rows_rotated + M[0,2]))-1

    bottom_margin, top_margin = 0.05, 0.02
    bottom = min(rows_rotated,int(horizon + bottom_margin*rows_rotated))
    top = max(0, int(horizon - top_margin*rows_rotated))



    cropped = rotated[top:bottom, left:right]

    horizon_height = int(top_margin*rows_rotated)

    return cropped, horizon_height, horizon_prev


####################################################################################################################################
####################################################################################################################################

def detectMast(horizon, horizon_height):

    grey = cv2.cvtColor(horizon, cv2.COLOR_BGR2GRAY)
    result = horizon.copy()

    kernel = np.zeros((5,5))
    kernel_side = np.ones((5,2))
    kernel[:,:2] = -(1./(4*5))*kernel_side
    kernel[:,-2:] = (1./(4*5))*kernel_side
    grad_x = cv2.filter2D(grey,cv2.CV_16S,kernel)
    grad_x = np.uint8(np.absolute(grad_x))

#    grad_x = cv2.Sobel(grey, -1, 1, 0, ksize = 3)

    kernel = np.ones((15,1))
    ret, bin_x = cv2.threshold(grad_x,5,255,0)
    bin_x = cv2.morphologyEx(bin_x, cv2.MORPH_OPEN, kernel)


    kernel = np.zeros((7,7), np.uint8)
    kernel[:,3] = np.ones((7,), np.uint8)

    bin_x = cv2.morphologyEx(bin_x, cv2.MORPH_OPEN, kernel)

    verticalLines = cv2.HoughLines(bin_x,20,10*np.pi/180,70)

    possible_masts = []

    if verticalLines is not None:
#        print(len(verticalLines))
#        verticalLines = [verticalLines[i] for i in range(0, len(verticalLines), 1+len(verticalLines)//50)]
        for verticalLine in verticalLines:
            for rho,theta in verticalLine:

                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 10000*(-b))
                y1 = int(y0 + 10000*(a))
                x2 = int(x0 - 10000*(-b))
                y2 = int(y0 - 10000*(a))

                if y2!=y1:
                    xMast = x2 - ((x2-x1)*(y2-horizon_height))/(y2-y1)
                else:
                    continue

                if -pi/4 < theta and theta < pi/4 and newMast(xMast, possible_masts):
                    possible_masts.append(xMast)
                    cv2.line(result, (xMast, horizon_height-10), (xMast, horizon_height+10), (0,0,255), 2)
                    cv2.line(result, (x1, y1), (x2, y2), (0,0,255), 1)

    return result, possible_masts



####################################################################################################################################
####################################################################################################################################




def newMast(possibleNew, mastList):
    check = True
    for mast in mastList:
        if abs(possibleNew - mast) < 30:
            check = False
    return check






if __name__ == "__main__":
    run()
