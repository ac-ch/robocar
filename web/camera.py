import time
import numpy as np
import imutils
import cv2
from collections import deque

redLower0 = (0, 50, 50)
redUpper0 = (10, 255, 255)

redLower1 = (170, 50, 50)
redUpper1 = (180, 255, 255)

pts = deque(maxlen=64)

class Camera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(0)
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        while True:
            success, image = self.video.read()
            if not success:
                break
            frame = image
            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
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
                    cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
                    text='x='+str(int(x))+',y='+str(int(y))
                    cv2.putText(frame, text,(10,30), cv2.FONT_HERSHEY_COMPLEX, 1,(255,255,255),2)                    
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
                cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
                pts.pop()        

            # We are using Motion JPEG, but OpenCV defaults to capture raw images,
            # so we must encode it into JPEG in order to correctly display the video stream.
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()
