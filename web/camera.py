import time
import numpy as np
import imutils
import cv2
from collections import deque
from picamera.array import PiRGBArray
from picamera import PiCamera
import io
import threading

redLower0 = (0, 50, 50)
redUpper0 = (10, 255, 255)

redLower1 = (170, 50, 50)
redUpper1 = (180, 255, 255)

pts = deque(maxlen=64)

class Camera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    
    def __init__(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)
   
    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame
    
    @classmethod
    def _thread(cls):
        with picamera.PiCamera() as camera:
            # camera setup
            camera.resolution = (640, 480)
            camera.framerate=32
            camera.hflip = True
            camera.vflip = True            
            rawCapture = PiRGBArray(camera, size=(640, 480))

            # let camera warm up
            camera.start_preview()
            time.sleep(2)

            for aframe in camera.capture_continuous(rawCapture, 'bgr',
                                                 use_video_port=True):
                imgframe=aframe.array
                blurred = cv2.GaussianBlur(imgframe, (11, 11), 0)
                hsv = cv2.cvtColor(imgframe, cv2.COLOR_BGR2HSV)
                mask0 = cv2.inRange(hsv, redLower0, redUpper0)
                mask1 = cv2.inRange(hsv, redLower1, redUpper1)
                mask = mask0 + mask1
                mask = cv2.erode(mask, None, iterations=2)
                mask = cv2.dilate(mask, None, iterations=2)
            
                # cv2.imshow("mask", mask)

                # find contours in the mask and initialize the current
                # (x, y) center of the ball
                cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
                center = None
            
                # only proceed if at least one contour was found
                if len(cnts) > 0:
                    # find the largest contour in the mask, then use
                    # it to compute the minimum enclosing circle and
                    # centroid
                    c = max(cnts, key=cv2.contourArea)
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    M = cv2.moments(c)
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                    # only proceed if the radius meets a minimum size
                    if radius > 20:
                        # draw the circle and centroid on the frame,
                        # then update the list of tracked points
                        cv2.circle(imgframe, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                        cv2.circle(imgframe, center, 5, (0, 0, 255), -1)
                        text='x='+str(int(x))+',y='+str(int(y))
                        cv2.putText(imgframe, text,(10,30), cv2.FONT_HERSHEY_COMPLEX, 1,(255,255,255),2)                    
                        # update the points queue     
                        pts.appendleft(center)

                # loop over the set of tracked points
                for i in xrange(1, len(pts)):
        	        # if either of the tracked points are None, ignore them
                    if pts[i - 1] is None or pts[i] is None:
                        continue                    
                    # otherwise, compute the thickness of the line and
                    # draw the connecting lines
                    thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
                    cv2.line(imgframe, pts[i - 1], pts[i], (0, 0, 255), thickness)
                    pts.pop()
                    
                cls.frame=imgframe
                
        cls.thread = None
