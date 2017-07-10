import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera

class VideoCamera(object):
    def __init__(self):
        self.camera = PiCamera()
	self.camera.resolution = (640, 480)
	self.camera.framerate = 16
	self.rawCapture = PiRGBArray(self.camera, size=(640, 480))    
    def get_frame(self):
	self.camera.capture(self.rawCapture, format="bgr")
	image = self.rawCapture.array;
	self.rawCapture.truncate(0)        
	# We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpeg = cv2.imencode('.jpg', image)
        return np.array(jpeg).tostring()
