import time
import io
import threading
import picamera


class Robot(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera

    def initialize(self):
        if Robot.thread is None:
            # start background frame thread
            Robot.thread = threading.Thread(target=self._thread)
            Robot.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Robot.last_access = time.time()
        self.initialize()
        return self.frame

    @classmethod
    def _thread(cls):
        with picamera.PiCamera() as camera:
            # camera setup
            camera.resolution = (640, 480)
            camera.hflip = True
            camera.vflip = True
            # camera.rotation = 180

            # let camera warm up
            camera.start_preview()
            time.sleep(2)

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # store frame
                stream.seek(0)
                cls.frame = stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

                # do image processing
                
        cls.thread = None
