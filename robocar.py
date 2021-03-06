# import the necessary packages
from collections import deque
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import numpy as np
import imutils
import cv2


# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
#greenLower = (29, 86, 6)
#greenUpper = (64, 255, 255)
redLower0 = (0, 50, 50)
redUpper0 = (10, 255, 255)

redLower1 = (170, 50, 50)
redUpper1 = (180, 255, 255)

pts = deque(maxlen=64)

# if a video path was not supplied, grab the reference
# to the webcam

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate=32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)
#camera = cv2.VideoCapture(0)

# keep looping
for aframe in camera.capture_continuous(rawCapture, format="bgr", use_video_port
=True):
    # grab the current frame
    #(grabbed, frame) = camera.read()
    frame=aframe.array

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    #if args.get("video") and not grabbed:
    #   break

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=640)
    # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask0 = cv2.inRange(hsv, redLower0, redUpper0)
    mask1 = cv2.inRange(hsv, redLower1, redUpper1)
    mask = mask0 + mask1
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # cv2.imshow("mask", mask)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
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
        if radius > 50:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            text='x='+str(int(x))+',y='+str(int(y))+',r='+str(int(radius))
            cv2.putText(frame, text,(10,30), cv2.FONT_HERSHEY_COMPLEX, 1,(255,255,255),2)
            
            print(text)
    # update the points queue
    pts.appendleft(center)

    # loop over the set of tracked points
    for i in xrange(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
        pts.pop()        

    # show the frame to our screen
    # cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    
    rawCapture.truncate(0)

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows

camera.release()
cv2.destroyAllWindows()

