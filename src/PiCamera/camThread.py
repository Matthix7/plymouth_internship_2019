#!/usr/bin/env python
# -*- coding: utf-8 -*-

####### USING https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/ ###########


# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2
import time
from numpy import array

class PiVideoStream:
    def __init__(self, resolution=(640, 480), framerate=15, mode = 'sports'):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.camera.exposure_mode = mode

        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,format="bgr", use_video_port=True)

        #Load the calibration data (manually...) from calibration_data.txt
        self.calibration_matrix = array([[485.36568341, 0., 308.96642615], [0., 486.22575965, 236.66818825], [0., 0., 1.]])
        self.calibration_dist = array([[1.37958351e-01, -2.43061015e-01, -5.22562568e-05, -6.84849581e-03, -2.59284496e-02]])

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

        # allow the camera to warmup
        time.sleep(0.1)

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = cv2.undistort(f.array, self.calibration_matrix, self.calibration_dist, None)
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True







