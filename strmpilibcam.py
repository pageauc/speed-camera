# Written by Claude Pageau 18 Nov 2022
# Import required libraries
from picamera2 import Picamera2
from libcamera import Transform
import time
from threading import Thread

class CamStream:
    """
    Create a picamera2 libcamera in memory image stream that
    runs in a Thread (Bullseye or later)
    returns image array when read() called

    sample implementation for your python script.
    Note pilibcamstream.py must be in same folder as your script.
    ----------------------------------------------------------

    from pilibcamstream import PiLibCamStream
    vs = PiLibCamStream(im_size=(640, 480), vflip=True, hflip=False).start()
    while True:
        frame = vs.read()  # frame will be array that opencv can process.
        # add code to process stream image arrays.
    """

    def __init__(self, size=(320, 248), vflip=False, hflip=False):
        self.size = size
        self.vflip = vflip
        self.hflip = hflip
        self.framerate = 40.0  # set a reasonable fps for pilibcamera
        self.cam_delay = float(1.0 / self.framerate)

        # initialize the camera and stream
        self.picam2 = Picamera2()
        self.picam2.set_logging(Picamera2.INFO)
        self.picam2.configure(self.picam2.create_preview_configuration(
                              main={"format": 'XRGB8888',
                              "size": self.size},
                              raw={"size":self.picam2.sensor_resolution},
                              transform=Transform(vflip=self.vflip,
                                                  hflip=self.hflip)))
        self.picam2.start()
        time.sleep(2) # Allow camera time to warm up

        # initialize variables
        self.thread = None  # Initialize Thread variable
        self.frame = None   # Initialize frame array var as None
        self.stopped = False  # Indicate if Thread is to be stopped

    def start(self):
        '''start the thread to read frames from the video stream'''
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def update(self):
        '''keep looping infinitely until the thread is stopped'''
        while True:
            # if the thread indicator variable is set,
            # release camera resources and stop the thread
            if self.stopped:
                return
            time.sleep(self.cam_delay) # Slow down loop

    def read(self):
        '''return the frame array data'''
        self.frame = self.picam2.capture_array("main")
        return self.frame

    def stop(self):
        '''Stop lib camera and thread'''
        self.picam2.stop()  # stop picamera2 libcamera
        time.sleep(2)  # allow camera time to released
        self.stopped = True
