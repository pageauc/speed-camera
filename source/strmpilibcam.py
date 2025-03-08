# Written by Claude Pageau Feb-2025
# Import required libraries
from picamera2 import Picamera2
from libcamera import Transform
import time
import sys
from threading import Thread

class CamStream:
    '''
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
    '''

    def __init__(self, size=(320, 248), vflip=False, hflip=False):
        self.size = size
        self.vflip = vflip
        self.hflip = hflip
        self.retries = 4
        while self.retries > 0:
            self.retries -= 1
            if self.retries < 1:
                import os
                prog_path = os.path.abspath(__file__)
                print(f"""
{prog_path}
ERROR: Problem Starting RPI Camera Stream Thread
------------------------------------------------
    RPI Camera Already in Use or has an Issue.
    To see if supervisorctl is using camera, Run command below.

        ./speed-cam.sh status
        ./speed-cam.sh stop   # Run if supervisorctl status shows speed-cam in use
                              otherwise check if another process is using camera.
        ./speed-cam.sh status # recheck status.

    If status does not show anything, Try

        pgrep -f speed-cam
        sudo kill PID    # if PID reported by pgrep

    and Try Again.
    If still not working. Check for something else using pi camera.
    Try htop command. Might be another app running in foreground or background.
    If all else fails Try a Reboot.
------------------------------------------------
Bye
Wait ...
""")
                sys.exit(1)
            try:
                self.picam2 = Picamera2() # initialize the camera
                # self.picam2.set_logging(Picamera2.ERROR)
                self.picam2.configure(self.picam2.create_preview_configuration(
                                      main={"format": 'XRGB8888',
                                      "size": self.size},
                                      transform=Transform(vflip=self.vflip,
                                                          hflip=self.hflip)))
            except RuntimeError:
                print(f'WARN : Camera Error. Retrying {self.retries}')
                self.picam2.close()
                continue
            break

        self.picam2.start()
        time.sleep(2) # Allow camera time to warm up
        self.picam2.set_controls({"AfMode": 0, "LensPosition": 1})   # turns off autofocus

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
            time.sleep(0.001) # Slow down loop a little

    def read(self):
        '''return the frame array data'''
        self.frame = self.picam2.capture_array("main")
        return self.frame

    def stop(self):
        '''Stop lib camera and thread'''
        self.picam2.close()  # Close Camera
        time.sleep(4)  # allow camera time to released
        self.stopped = True
