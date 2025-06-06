# Written by Claude Pageau 18 Nov 2022
# Import required libraries
from threading import Thread
import cv2
import time

class CamStream:
    def __init__(self,
                 filepath="",
                 size=(320, 240),
                 name="VidFileStream"):
        # initialize the video File stream and read the first frame
        self.stream = cv2.VideoCapture(filepath)
        self.stream.set(3, size[0])
        self.stream.set(4, size[1])
        self.framerate = 30.0  # set ip csm to CBR (constant bitrate)
        self.cam_delay = float(1.0 / self.framerate)
        (self.ret, self.frame) = self.stream.read()

        # initialize the thread name
        self.name = name

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            time.sleep(self.cam_delay)

    def read(self):
        # return the frame most recently read
        (self.ret, self.frame) = self.cap.read()
        if self.ret == True:
            return self.frame
        else:
            self.stopped = True

    def stop(self):
        # release cameera and stop thread
        self.stream.release()
        time.sleep(2)  # allow time for cam to shut down
        # indicates that the thread should be stopped
        self.stopped = True
