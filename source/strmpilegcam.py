# Written by Claude Pageau 18 Nov 2022 based on piimagesearch code

# Import required libraries
import sys
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread

# ------------------------------------------------------------------------------
class CamStream:
    def __init__(self,
                 size=(320, 257),
                 framerate=30,
                 rotation=0,
                 hflip=False,
                 vflip=False,
                 **kwargs
                ):
        """initialize the camera and stream"""
        self.size = size
        try:
            self.camera = PiCamera()
        except:
            print("PiCamera Already in Use by Another Process")
            print("Exiting Due to PiCamera Error")
            sys.exit(1)
        self.camera.resolution = self.size
        self.camera.rotation = rotation
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip

         # set optional camera parameters (refer to PiCamera docs)
        for (arg, value) in kwargs.items():
            setattr(self.camera, arg, value)

        self.rawCapture = PiRGBArray(self.camera, size=self.size)
        self.stream = self.camera.capture_continuous(self.rawCapture,
                                                     format="bgr",
                                                     use_video_port=True)

        """
        initialize the frame and the variable used to indicate
        if the thread should be stopped
        """
        self.thread = None
        self.frame = None
        self.stopped = False

    def start(self):
        """start the thread to read frames from the video stream"""
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def update(self):
        """keep looping infinitely until the thread is stopped"""
        while True:
            for f in self.stream:
                self.frame = f.array # grab the frame from the stream
                # clear the stream in preparation for next frame
                self.rawCapture.truncate(0)
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                if self.thread is not None:
                    self.thread.join()
                return

    def read(self):
        """return the frame most recently read"""
        return self.frame

    def stop(self):
        """indicate that the thread should be stopped"""
        self.stopped = True
