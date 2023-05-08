# Written by Claude Pageau 18 Nov 2022
# Import required libraries
from threading import Thread
import cv2
import time
class Webcam:
    def __init__(self, src=0, size=(320, 240), hflip=False, vflip=False):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.width = size[0]
        self.height = size[1]
        self.vflip = vflip
        self.hflip = hflip
        self.frame = None
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        while self.frame is None:
            (self.grabbed, self.frame) = self.stream.read()

        # initialize the thread name
        self.thread = None

        # Initialize var to indicate when thread to be stopped.
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                if self.thread is not None:
                    self.stream.release() # close stream
                    self.thread.join() # close thread
                return
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        if self.vflip and self.hflip:
            self.frame = cv2.flip(self.frame, -1)
        elif self.vflip:
            self.frame = cv2.flip(self.frame, 0)
        elif self.hflip:
            self.frame = cv2.flip(self.frame, 1)
        # return the frame most recently read
        return self.frame

    def stop(self):
        self.stopped = True
        # indicate that the thread should be stopped

