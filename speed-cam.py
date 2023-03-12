#!/usr/bin/env python
"""
speed-cam.py written by Claude Pageau
Windows, Unix, Raspberry (Pi) - python opencv2 Speed tracking
using picamera module, Web Cam or RTSP IP Camera
GitHub Repo here https://github.com/pageauc/rpi-speed-camera/tree/master/
Post issue to Github.

This is a python openCV object speed tracking demonstration program.
It will detect speed in the field of view and use openCV to calculate the
largest contour and return its x,y coordinate.  The image is tracked for
a specified pixel length and the final speed is calculated.
Note: Variables for this program are stored in config.py

Some of this code is based on a YouTube tutorial by
Kyle Hounslow using C here https://www.youtube.com/watch?v=X6rPdRZzgjg

Thanks to Adrian Rosebrock jrosebr1 at http://www.pyimagesearch.com
for the PiVideoStream Class code available on github at
https://github.com/jrosebr1/imutils/blob/master/imutils/video/pivideostream.py

Here is my YouTube video demonstrating a previous speed tracking demo
program using a Raspberry Pi B2 https://youtu.be/09JS7twPBsQ
and a fun speed lapse video https://youtu.be/-xdB_x_CbC8

Installation
------------
Requires a Raspberry Pi with a RPI camera module or Web Cam installed and working
or Windows, Unix Distro computer with a USB Web Cam.  See github wiki for
more detail https://github.com/pageauc/speed-camera/wiki

Install from a logged in SSH session per commands below.
Code should run on a non RPI platform using a Web Cam

    curl -L https://raw.github.com/pageauc/rpi-speed-camera/master/speed-install.sh | bash
or
    wget https://raw.github.com/pageauc/rpi-speed-camera/master/speed-install.sh
    chmod +x speed-install.sh
    ./speed-install.sh
    ./speed-cam.py

Note to Self - Look at eliminating python variable camel case and use all snake naming

"""
from __future__ import print_function

progVer = "11.26"  # current version of this python script

import os
import sys

# Get information about this script including name, launch path, etc.
# This allows script to be renamed or relocated to another directory
mypath = os.path.abspath(__file__)  # Find the full path of this python script
# get the path location only (excluding script name)
baseDir = mypath[0 : mypath.rfind("/") + 1]
baseFileName = mypath[mypath.rfind("/") + 1 : mypath.rfind(".")]
progName = os.path.basename(__file__)
horiz_line = "----------------------------------------------------------------------"
print(horiz_line)
print("%s %s  written by Claude Pageau" % (progName, progVer))
print("Motion Track Largest Moving Object and Calculate Speed per Calibration.")
print(horiz_line)
print("Loading  Wait ...")

import time
import datetime
import glob
import shutil
import logging
import sqlite3
from threading import Thread
import subprocess
import numpy as np

"""
This is a dictionary of the default settings for speed-cam.py
If you don't want to use a config.py file these will create the required
variables with default values.  Change dictionary values if you want different
variable default values.
A message will be displayed if a variable is Not imported from config.py.
Note: plugins can override default and config.py values if plugins are
      enabled.  This happens after config.py variables are imported
"""
default_settings = {
    "calibrate": True,
    "align_cam_on": False,
    "align_delay_sec": 5,
    "cal_obj_px_L2R": 90,
    "cal_obj_mm_L2R": 4700.0,
    "cal_obj_px_R2L": 95,
    "cal_obj_mm_R2L": 4700.0,
    "pluginEnable": False,
    "pluginName": "picam240",
    "gui_window_on": False,
    "show_thresh_on": False,
    "show_crop_on": False,
    "verbose": True,
    "display_fps": False,
    "log_data_to_CSV": False,
    "loggingToFile": False,
    "logFilePath": "speed-cam.log",
    "SPEED_MPH": False,
    "track_counter": 5,
    "MIN_AREA": 100,
    "show_out_range": True,
    "x_diff_max": 20,
    "x_diff_min": 1,
    "x_buf_adjust": 10,
    "track_timeout": 0.5,
    "event_timeout": 0.3,
    "max_speed_over": 0,
    "CAM_LOCATION": "None",
    "WEBCAM_SRC": 0,
    "WEBCAM_WIDTH": 320,
    "WEBCAM_HEIGHT": 240,
    "WEBCAM_HFLIP": False,
    "WEBCAM_VFLIP": False,
    "CAMERA_WIDTH": 320,
    "CAMERA_HEIGHT": 240,
    "CAMERA_FRAMERATE": 20,
    "CAMERA_ROTATION": 0,
    "CAMERA_VFLIP": True,
    "CAMERA_HFLIP": True,
    "image_path": "media/images",
    "image_prefix": "speed-",
    "image_format": ".jpg",
    "image_jpeg_quality": 95,
    "image_jpeg_optimize": False,
    "image_show_motion_area": True,
    "image_filename_speed": False,
    "image_text_on": True,
    "image_text_bottom": True,
    "image_font_size": 12,
    "image_font_thickness": 2,
    "image_font_scale": 0.5,
    "image_font_color": (255, 255, 255),
    "image_bigger": 3.0,
    "image_max_files": 0,
    "imageSubDirMaxFiles": 1000,
    "imageSubDirMaxHours": 0,
    "imageRecentMax": 100,
    "imageRecentDir": "media/recent",
    "spaceTimerHrs": 0,
    "spaceFreeMB": 500,
    "spaceMediaDir": "media/images",
    "spaceFileExt ": "jpg",
    "SHOW_CIRCLE": False,
    "CIRCLE_SIZE": 5,
    "LINE_THICKNESS": 1,
    "WINDOW_BIGGER": 1.0,
    "BLUR_SIZE": 10,
    "THRESHOLD_SENSITIVITY": 20,
    "DB_DIR": "data",
    "DB_NAME": "speed_cam.db",
    "DB_TABLE": "speed",
    "GRAPH_PATH": "media/graphs",
    "GRAPH_ADD_DATE_TO_FILENAME": False,
    "GRAPH_RUN_TIMER_HOURS": 0.5,
    "GRAPH_RUN_LIST": [
        ["hour", 2, 0],
        ["hour", 7, 10],
        ["hour", 14, 10],
        ["day", 28, 0],
    ],
    "web_server_port": 8080,
    "web_server_root": "media",
    "web_page_title": "SPEED-CAMERA Media",
    "web_page_refresh_on": True,
    "web_page_refresh_sec": "900",
    "web_page_blank": False,
    "web_image_height": "768",
    "web_iframe_width_usage": "70%",
    "web_iframe_width": "100%",
    "web_iframe_height": "100%",
    "web_max_list_entries": 0,
    "web_list_height": "768",
    "web_list_by_datetime": True,
    "web_list_sort_descending": True,
    "image_sign_on": False,
    "image_sign_show_camera": False,
    "image_sign_resize": (1280, 720),
    "image_sign_text_xy": (100, 675),
    "image_sign_font_scale": 30.0,
    "image_sign_font_thickness": 60,
    "image_sign_font_color": (255, 255, 255),
    "image_sign_timeout": 5,
}

# Color data for OpenCV lines and text
cvWhite = (255, 255, 255)
cvBlack = (0, 0, 0)
cvBlue = (255, 0, 0)
cvGreen = (0, 255, 0)
cvRed = (0, 0, 255)

"""
Check for config.py variable file to import and warn if not Found.
Logging is not used since the logFilePath variable is needed before
setting up logging
"""
configFilePath = os.path.join(baseDir, "config.py")
if os.path.exists(configFilePath):
    # Read Configuration variables from config.py file
    try:
        from config import *
    except ImportError:
        print(
            "WARN  : Problem reading configuration variables from %s" % configFilePath
        )
else:
    print("WARN  : Missing config.py file - File Not Found %s" % configFilePath)
"""
Check if variables were imported from config.py. If not create variable using
the values in the default_settings dictionary above.
"""
for key, val in default_settings.items():
    try:
        exec(key)
    except NameError:
        print("WARN  : config.py Variable Not Found. Setting " + key + " = " + str(val))
        exec(key + "=val")
# fix rounding problems with picamera resolution
CAMERA_WIDTH = (CAMERA_WIDTH + 31) // 32 * 32
CAMERA_HEIGHT = (CAMERA_HEIGHT + 15) // 16 * 16

# Now that variables are imported from config.py Setup Logging since we have logFilePath
if loggingToFile:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=logFilePath,
        filemode="w",
    )
elif verbose:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
else:
    logging.basicConfig(
        level=logging.CRITICAL,
        format="%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
# Do a quick check to see if the sqlite database directory path exists
DB_DIR_PATH = os.path.join(baseDir, DB_DIR)
if not os.path.exists(DB_DIR_PATH):  # Check if database directory exists
    os.makedirs(DB_DIR_PATH)  # make directory if Not Found
DB_PATH = os.path.join(DB_DIR_PATH, DB_NAME)  # Create path to db file

# import a single variable from the search_config.py file
# This is done to auto create a media/search directory
try:
    from search_config import search_dest_path
except ImportError:
    search_dest_path = "media/search"
    logging.warning("Problem importing search_dest_path variable")
    logging.info("Setting default value search_dest_path = %s", search_dest_path)
# Check for user_motion_code.py file to import and error out if not found.
userMotionFilePath = os.path.join(baseDir, "user_motion_code.py")
motionCode = False
if os.path.isfile(userMotionFilePath):
    try:
        motionCode = True
        import user_motion_code
    except ImportError:
        print("WARN  : Failed Import of File user_motion_code.py Investigate Problem")
        motionCode = False
else:
    print(
        "WARN  : %s File Not Found. Cannot Import user_motion_code functions."
        % userMotionFilePath
    )
# Import Settings from specified plugin if pluginEnable=True
if pluginEnable:  # Check and verify plugin and load variable overlay
    pluginDir = os.path.join(baseDir, "plugins")
    # Check if there is a .py at the end of pluginName variable
    if pluginName.endswith(".py"):
        pluginName = pluginName[:-3]  # Remove .py extensiion
    pluginPath = os.path.join(pluginDir, pluginName + ".py")
    logging.info("pluginEnabled - loading pluginName %s", pluginPath)
    if not os.path.isdir(pluginDir):
        logging.error("plugin Directory Not Found at %s", pluginDir)
        logging.info("Rerun github curl install script to install plugins")
        logging.info("https://github.com/pageauc/pi-timolo/wiki/")
        logging.info("How-to-Install-or-Upgrade#quick-install")
        logging.warning("%s %s Exiting Due to Error", progName, progVer)
        sys.exit(1)
    elif not os.path.exists(pluginPath):
        logging.error("File Not Found pluginName %s", pluginPath)
        logging.info("Check Spelling of pluginName Value in %s", configFilePath)
        logging.info("------- Valid Names -------")
        validPlugin = glob.glob(pluginDir + "/*py")
        validPlugin.sort()
        for entry in validPlugin:
            pluginFile = os.path.basename(entry)
            plugin = pluginFile.rsplit(".", 1)[0]
            if not ((plugin == "__init__") or (plugin == "current")):
                logging.info("        %s", plugin)
        logging.info("------- End of List -------")
        logging.info("        Note: pluginName Should Not have .py Ending.")
        logging.info("or Rerun github curl install command.  See github wiki")
        logging.info("https://github.com/pageauc/speed-camera/wiki/")
        logging.info("How-to-Install-or-Upgrade#quick-install")
        logging.warning("%s %s Exiting Due to Error", progName, progVer)
        sys.exit(1)
    else:
        pluginCurrent = os.path.join(pluginDir, "current.py")
        try:  # Copy image file to recent folder
            logging.info("Copy %s to %s", pluginPath, pluginCurrent)
            shutil.copy(pluginPath, pluginCurrent)
        except OSError as err:
            logging.error(
                "Copy Failed from %s to %s - %s", pluginPath, pluginCurrent, err
            )
            logging.info("Check permissions, disk space, Etc.")
            logging.warning("%s %s Exiting Due to Error", progName, progVer)
            sys.exit(1)
        logging.info("Import Plugin %s", pluginPath)
        # add plugin directory to program PATH
        sys.path.insert(0, pluginDir)
        try:
            from plugins.current import *
        except ImportError:
            logging.warning("Problem importing variables from %s", pluginDir)
        try:
            if os.path.exists(pluginCurrent):
                os.remove(pluginCurrent)
            pluginCurrentpyc = os.path.join(pluginDir, "current.pyc")
            if os.path.exists(pluginCurrentpyc):
                os.remove(pluginCurrentpyc)
        except OSError as err:
            logging.warning("Failed To Remove File %s - %s", pluginCurrentpyc, err)
# import the necessary packages
# -----------------------------
try:  # Add this check in case running on non RPI platform using web cam
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except OSError or ImportError:
    WEBCAM = True
if not WEBCAM:
    # Check that pi camera module is installed and enabled
    print("Checking Pi Camera Module using command - vcgencmd get_camera")
    camResult = subprocess.check_output("vcgencmd get_camera", shell=True)
    camResult = camResult.decode("utf-8")
    camResult = camResult.replace("\n", "")
    print("Camera Status is %s" % camResult)
    print("Checking supported and detected Status")
    params = camResult.split()
    for x in range(0,2):
        if params[x].find("0") >= 0:
            print("Detected Problem with Pi Camera Module per %s" % params[x])
            print("")
            print("  if supported=0 Enable Camera per command sudo raspi-config")
            print("  if detected=0 Check Pi Camera Module is Installed Correctly.")
            print("")
            print("%s %s Exiting Due to Error" % ( progName, progVer))
            sys.exit(1)
    else:
        print("Success Pi Camera Module is Enabled and Connected %s" % camResult)

try:  # Check to see if opencv is installed
    import cv2
except ImportError:
    logging.error("Could Not import cv2 library")
    if sys.version_info > (2, 9):
        logging.error("python3 failed to import cv2")
        logging.error("Try installing opencv for python3")
        logging.error("For RPI See https://github.com/pageauc/opencv3-setup")
    else:
        logging.error("python2 failed to import cv2")
        logging.error("Try RPI Install per command")
        logging.error("%s %s Exiting Due to Error", progName, progVer)
    sys.exit(1)
# fix possible invalid values when resizing
if WINDOW_BIGGER < 0.1:
    WINDOW_BIGGER = 0.1
if image_bigger < 0.1:
    image_bigger = 0.1
WEBCAM_FLIPPED = False
if WEBCAM:
    # Check if Web Cam image flipped in any way
    if WEBCAM_HFLIP or WEBCAM_VFLIP:
        WEBCAM_FLIPPED = True
quote = '"'  # Used for creating quote delimited log file of speed data
fix_msg = """
    ---------- Upgrade Instructions -----------
    To Fix Problem Run ./menubox.sh UPGRADE menu pick.
    After upgrade newest config.py will be named config.py.new
    In SSH or terminal perform the following commands to update to latest config.py

        cd ~/speed-camera
        cp config.py config.py.bak
        cp config.py.new config.py

    Then Edit config.py and transfer any customized settings from config.py.bak File
    """

# Calculate conversion from camera pixel width to actual speed.
px_to_kph_L2R = float(cal_obj_mm_L2R / cal_obj_px_L2R * 0.0036)
px_to_kph_R2L = float(cal_obj_mm_R2L / cal_obj_px_R2L * 0.0036)

if SPEED_MPH:
    speed_units = "mph"
    speed_conv_L2R = 0.621371 * px_to_kph_L2R
    speed_conv_R2L = 0.621371 * px_to_kph_R2L
else:
    speed_units = "kph"
    speed_conv_L2R = px_to_kph_L2R
    speed_conv_R2L = px_to_kph_R2L
# path to alignment camera image
align_filename = os.path.join(imageRecentDir, "align_cam.jpg")

# ------------------------------------------------------------------------------
class PiVideoStream:
    def __init__(
        self,
        resolution=(CAMERA_WIDTH, CAMERA_HEIGHT),
        framerate=CAMERA_FRAMERATE,
        rotation=0,
        hflip=CAMERA_HFLIP,
        vflip=CAMERA_VFLIP,
    ):
        """initialize the camera and stream"""
        try:
            self.camera = PiCamera()
        except:
            logging.error("PiCamera Already in Use by Another Process")
            logging.error("%s %s Exiting Due to Error", progName, progVer)
            sys.exit(1)
        self.camera.resolution = resolution
        self.camera.rotation = rotation
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(
            self.rawCapture, format="bgr", use_video_port=True
        )

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
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        """return the frame most recently read"""
        return self.frame

    def stop(self):
        """indicate that the thread should be stopped"""
        self.stopped = True
        if self.thread is not None:
            self.thread.join()


# ------------------------------------------------------------------------------
class WebcamVideoStream:
    def __init__(
        self, CAM_SRC=WEBCAM_SRC, CAM_WIDTH=WEBCAM_WIDTH, CAM_HEIGHT=WEBCAM_HEIGHT
    ):
        """
        initialize the video camera stream and read the first frame
        from the stream
        """
        self.stream = CAM_SRC
        self.stream = cv2.VideoCapture(CAM_SRC)
        self.stream.set(3, CAM_WIDTH)
        self.stream.set(4, CAM_HEIGHT)
        (self.grabbed, self.frame) = self.stream.read()
        self.thread = None
        # initialize the variable used to indicate if the thread should
        # be stopped
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
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                self.stream.release()
                return
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
            # check for valid frames
            if not self.grabbed:
                # no frames recieved, then safely exit
                self.stopped = True
        self.stream.release()  # release resources

    def read(self):
        """return the frame most recently read
        Note there will be a significant performance hit to
        flip the webcam image so it is advised to just
        physically flip the camera and avoid
        setting WEBCAM_HFLIP = True or WEBCAM_VFLIP = True
        """
        if WEBCAM_FLIPPED:
            if WEBCAM_HFLIP and WEBCAM_VFLIP:
                self.frame = cv2.flip(self.frame, -1)
            elif WEBCAM_HFLIP:
                self.frame = cv2.flip(self.frame, 1)
            elif WEBCAM_VFLIP:
                self.frame = cv2.flip(self.frame, 0)
        return self.frame

    def stop(self):
        """indicate that the thread should be stopped"""
        self.stopped = True
        # wait until stream resources are released (producer thread might be still grabbing frame)
        if self.thread is not None:
            self.thread.join()  # properly handle thread exit

    def isOpened(self):
        return self.stream.isOpened()


# ------------------------------------------------------------------------------
def get_fps(start_time, frame_count):
    """Calculate and display frames per second processing"""
    if frame_count >= 1000:
        duration = float(time.time() - start_time)
        FPS = float(frame_count / duration)
        logging.info("%.2f fps Last %i Frames", FPS, frame_count)
        frame_count = 0
        start_time = time.time()
    else:
        frame_count += 1
    return start_time, frame_count


# ------------------------------------------------------------------------------
def show_settings():
    """Initialize and Display program variable settings from config.py"""
    cwd = os.getcwd()
    html_path = "media/html"
    if not os.path.isdir(image_path):
        logging.info("Creating Image Storage Folder %s", image_path)
        os.makedirs(image_path)
    os.chdir(image_path)
    os.chdir(cwd)
    if imageRecentMax > 0:
        if not os.path.isdir(imageRecentDir):
            logging.info("Create Recent Folder %s", imageRecentDir)
            try:
                os.makedirs(imageRecentDir)
            except OSError as err:
                logging.error("Failed to Create Folder %s - %s", imageRecentDir, err)
    if not os.path.isdir(search_dest_path):
        logging.info("Creating Search Folder %s", search_dest_path)
        os.makedirs(search_dest_path)
    if not os.path.isdir(html_path):
        logging.info("Creating html Folder %s", html_path)
        os.makedirs(html_path)
    os.chdir(cwd)
    if verbose:
        print(horiz_line)
        print("Note: To Send Full Output to File Use command")
        print("python -u ./%s | tee -a log.txt" % progName)
        print(
            "Set log_data_to_file=True to Send speed_Data to CSV File %s.log"
            % baseFileName
        )
        print(horiz_line)
        print("")
        print(
            "Debug Messages .. verbose=%s  display_fps=%s calibrate=%s"
            % (verbose, display_fps, calibrate)
        )
        print("                  show_out_range=%s" % show_out_range)
        print(
            "Plugins ......... pluginEnable=%s  pluginName=%s"
            % (pluginEnable, pluginName)
        )
        print(
            "Calibration ..... cal_obj_px_L2R=%i px  cal_obj_mm_L2R=%i mm  speed_conv_L2R=%.5f"
            % (cal_obj_px_L2R, cal_obj_mm_L2R, speed_conv_L2R)
        )
        print(
            "                  cal_obj_px_R2L=%i px  cal_obj_mm_R2L=%i mm  speed_conv_R2L=%.5f"
            % (cal_obj_px_R2L, cal_obj_mm_R2L, speed_conv_R2L)
        )
        if pluginEnable:
            print("                  (Change Settings in %s)" % pluginPath)
        else:
            print("                  (Change Settings in %s)" % configFilePath)
        print(
            "Logging ......... Log_data_to_CSV=%s  log_filename=%s.csv (CSV format)"
            % (log_data_to_CSV, baseFileName)
        )
        print(
            "                  loggingToFile=%s  logFilePath=%s"
            % (loggingToFile, logFilePath)
        )
        print("                  SQLITE3 DB_PATH=%s  DB_TABLE=%s" % (DB_PATH, DB_TABLE))
        print(
            "Speed Trigger ... Log only if max_speed_over > %i %s"
            % (max_speed_over, speed_units)
        )
        print(
            "                  and track_counter >= %i consecutive motion events"
            % track_counter
        )
        print(
            "Exclude Events .. If  x_diff_min < %i or x_diff_max > %i px"
            % (x_diff_min, x_diff_max)
        )
        print(
            "                  If  y_upper < %i or y_lower > %i px" % (y_upper, y_lower)
        )
        print(
            "                  or  x_left < %i or x_right > %i px" % (x_left, x_right)
        )
        print(
            "                  If  max_speed_over < %i %s"
            % (max_speed_over, speed_units)
        )
        print(
            "                  If  event_timeout > %.2f seconds Start New Track"
            % (event_timeout)
        )
        print(
            "                  track_timeout=%.2f sec wait after Track Ends"
            " (avoid retrack of same object)" % (track_timeout)
        )
        print(
            "Speed Photo ..... Size=%ix%i px  image_bigger=%.1f"
            "  rotation=%i  VFlip=%s  HFlip=%s "
            % (
                image_width,
                image_height,
                image_bigger,
                CAMERA_ROTATION,
                CAMERA_VFLIP,
                CAMERA_HFLIP,
            )
        )
        print(
            "                  image_path=%s  image_Prefix=%s"
            % (image_path, image_prefix)
        )
        print(
            "                  image_font_size=%i px high  image_text_bottom=%s"
            % (image_font_size, image_text_bottom)
        )
        print(
            "                  image_jpeg_quality=%s  image_jpeg_optimize=%s"
            % (image_jpeg_quality, image_jpeg_optimize)
        )
        print(
            "Motion Settings . Size=%ix%i px  px_to_kph_L2R=%f  px_to_kph_R2L=%f speed_units=%s"
            % (CAMERA_WIDTH, CAMERA_HEIGHT, px_to_kph_L2R, px_to_kph_R2L, speed_units)
        )
        print("                  CAM_LOCATION= %s" % CAM_LOCATION)
        print(
            "OpenCV Settings . MIN_AREA=%i sq-px  BLUR_SIZE=%i"
            "  THRESHOLD_SENSITIVITY=%i  CIRCLE_SIZE=%i px"
            % (MIN_AREA, BLUR_SIZE, THRESHOLD_SENSITIVITY, CIRCLE_SIZE)
        )
        print(
            "                  WINDOW_BIGGER=%i gui_window_on=%s"
            " (Display OpenCV Status Windows on GUI Desktop)"
            % (WINDOW_BIGGER, gui_window_on)
        )
        print(
            "                  CAMERA_FRAMERATE=%i fps video stream speed"
            % CAMERA_FRAMERATE
        )
        print(
            "Sub-Directories . imageSubDirMaxHours=%i (0=off)"
            "  imageSubDirMaxFiles=%i (0=off)"
            % (imageSubDirMaxHours, imageSubDirMaxFiles)
        )
        print(
            "                  imageRecentDir=%s imageRecentMax=%i (0=off)"
            % (imageRecentDir, imageRecentMax)
        )
        if spaceTimerHrs > 0:  # Check if disk mgmnt is enabled
            print(
                "Disk Space  ..... Enabled - Manage Target Free Disk Space."
                " Delete Oldest %s Files if Needed" % (spaceFileExt)
            )
            print(
                "                  Check Every spaceTimerHrs=%i hr(s) (0=off)"
                "  Target spaceFreeMB=%i MB  min is 100 MB)"
                % (spaceTimerHrs, spaceFreeMB)
            )
            print(
                "                  If Needed Delete Oldest spaceFileExt=%s  spaceMediaDir=%s"
                % (spaceFileExt, spaceMediaDir)
            )
        else:
            print(
                "Disk Space  ..... Disabled - spaceTimerHrs=%i"
                "  Manage Target Free Disk Space. Delete Oldest %s Files"
                % (spaceTimerHrs, spaceFileExt)
            )
            print(
                "                  spaceTimerHrs=%i (0=Off)"
                " Target spaceFreeMB=%i (min=100 MB)" % (spaceTimerHrs, spaceFreeMB)
            )
        print("")
        print(horiz_line)
    return


# ------------------------------------------------------------------------------
def take_calibration_image(speed, filename, cal_image):
    """
    Create a calibration image for determining value of IMG_VIEW_FT variable
    Create calibration hash marks
    """
    # If there is bad contrast with background you can change the hash
    # colors to give more contrast.  You need to change values below
    # per values cvRed, cvBlue, cvWhite, cvBlack, cvGreen

    hash_color = cvRed
    motion_win_color = cvBlue

    for i in range(10, image_width - 9, 10):
        cv2.line(cal_image, (i, y_upper - 5), (i, y_upper + 30), hash_color, 1)
    # This is motion window
    cal_image = speed_image_add_lines(cal_image, motion_win_color)

    print(
        "----------------------------- Create Calibration Image "
        "-----------------------------"
    )
    print("")
    print("  Instructions for using %s image for camera calibration" % filename)
    print("")
    print(
        "  Note: If there is only one lane then L2R and R2L settings will be the same"
    )
    print(
        "  1 - Use L2R and R2L with Same Size Reference Object, Eg. same vehicle for both directions."
    )
    print(
        "  2 - For objects moving L2R Record cal_obj_px_L2R Value Using Red y_upper Hash Marks at every 10 px  Current Setting is %i px"
        % cal_obj_px_L2R
    )
    print(
        "  3 - Record cal_obj_mm_L2R of object. This is Actual length in mm of object above Current Setting is %i mm"
        % cal_obj_mm_L2R
    )
    print(
        "      If Recorded Speed %.1f %s is Too Low, Increasing cal_obj_mm_L2R to Adjust or Visa-Versa"
        % (speed, speed_units)
    )
    print(
        "Repeat Calibration with same object moving R2L and update config.py R2L variables"
    )
    print("cal_obj_mm_R2L and cal_obj_px_R2L accordingly")
    if pluginEnable:
        print("  4 - Edit %s File and Change Values for Above Variables." % pluginPath)
    else:
        print(
            "  4 - Edit %s File and Change Values for the Above Variables."
            % configFilePath
        )
    print("  5 - Do a Speed Test to Confirm/Tune Settings.  You May Need to Repeat.")
    print(
        "  6 - When Calibration is Finished, Set config.py Variable  calibrate = False"
    )
    print("      Then Restart speed-cam.py and monitor activity.")
    print("")
    print("  WARNING: It is Advised to Use 320x240 Stream for Best Performance.")
    print("           Higher Resolutions Need More OpenCV Processing")
    print("           and May Reduce Data Accuracy and Reliability.")
    print("")
    print("  Calibration Image Saved To %s%s  " % (baseDir, filename))
    print("  View Calibration Image in Web Browser (Ensure webserver.py is started)")
    print("")
    print(
        "---------------------- Press cntl-c to Quit Calibration Mode "
        "-----------------------"
    )
    return cal_image


# ------------------------------------------------------------------------------
def subDirLatest(directory):
    """Scan for directories and return most recent"""
    dirList = [
        name
        for name in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, name))
    ]
    if len(dirList) > 0:
        lastSubDir = sorted(dirList)[-1]
        lastSubDir = os.path.join(directory, lastSubDir)
    else:
        lastSubDir = directory
    return lastSubDir


# ------------------------------------------------------------------------------
def subDirCreate(directory, prefix):
    """Create media subdirectories base on required naming"""
    now = datetime.datetime.now()
    # Specify folder naming
    subDirName = "%s%d%02d%02d-%02d%02d" % (
        prefix,
        now.year,
        now.month,
        now.day,
        now.hour,
        now.minute,
    )
    subDirPath = os.path.join(directory, subDirName)
    if not os.path.exists(subDirPath):
        try:
            os.makedirs(subDirPath)
        except OSError as err:
            logging.error(
                "Cannot Create Dir %s - %s, using default location.", subDirPath, err
            )
            subDirPath = directory
        else:
            logging.info("Created %s", subDirPath)
    else:
        subDirPath = directory
    return subDirPath


# ------------------------------------------------------------------------------
def deleteOldFiles(maxFiles, dirPath, prefix):
    """
    Delete Oldest files gt or
    equal to maxfiles that match filename prefix
    """
    try:
        fileList = sorted(
            glob.glob(os.path.join(dirPath, prefix + "*")), key=os.path.getmtime
        )
    except OSError as err:
        logging.error("Problem Reading Directory %s", dirPath)
        logging.error("%s", err)
        logging.error("Possibly symlink destination File Does Not Exist")
        logging.error("To Fix - Try Deleting All Files in recent folder %s", dirPath)
    else:
        while len(fileList) >= maxFiles:
            oldest = fileList[0]
            oldestFile = oldest
            try:  # Remove oldest file in recent folder
                fileList.remove(oldest)
                os.remove(oldestFile)
            except OSError as err:
                logging.error("Cannot Remove %s - %s", oldestFile, err)


# ------------------------------------------------------------------------------
def subDirCheckMaxFiles(directory, filesMax):
    """Count number of files in a folder path"""
    fileList = glob.glob(directory + "/*")
    count = len(fileList)
    if count > filesMax:
        makeNewDir = True
        logging.info("Total Files in %s Exceeds %i ", directory, filesMax)
    else:
        makeNewDir = False
    return makeNewDir


# ------------------------------------------------------------------------------
def subDirCheckMaxHrs(directory, hrsMax, prefix):
    """extract the date-time from the directory name"""
    # Note to self need to add error checking
    dirName = os.path.split(directory)[1]  # split dir path and keep dirName
    # remove prefix from dirName so just date-time left
    dirStr = dirName.replace(prefix, "")
    # convert string to datetime
    dirDate = datetime.datetime.strptime(dirStr, "%Y%m%d-%H%M")
    rightNow = datetime.datetime.now()  # get datetime now
    diff = rightNow - dirDate  # get time difference between dates
    days, seconds = diff.days, diff.seconds
    dirAgeHours = days * 24 + seconds // 3600  # convert to hours
    if dirAgeHours > hrsMax:  # See if hours are exceeded
        makeNewDir = True
        logging.info("MaxHrs %i Exceeds %i for %s", dirAgeHours, hrsMax, directory)
    else:
        makeNewDir = False
    return makeNewDir


# ------------------------------------------------------------------------------
def subDirChecks(maxHours, maxFiles, directory, prefix):
    """Check if motion SubDir needs to be created"""
    if maxHours < 1 and maxFiles < 1:  # No Checks required
        # logging.info('No sub-folders Required in %s', directory)
        subDirPath = directory
    else:
        subDirPath = subDirLatest(directory)
        if subDirPath == directory:  # No subDir Found
            logging.info("No sub folders Found in %s", directory)
            subDirPath = subDirCreate(directory, prefix)
        elif maxHours > 0 and maxFiles < 1:  # Check MaxHours Folder Age Only
            if subDirCheckMaxHrs(subDirPath, maxHours, prefix):
                subDirPath = subDirCreate(directory, prefix)
        elif maxHours < 1 and maxFiles > 0:  # Check Max Files Only
            if subDirCheckMaxFiles(subDirPath, maxFiles):
                subDirPath = subDirCreate(directory, prefix)
        elif maxHours > 0 and maxFiles > 0:  # Check both Max Files and Age
            if subDirCheckMaxHrs(subDirPath, maxHours, prefix):
                if subDirCheckMaxFiles(subDirPath, maxFiles):
                    subDirPath = subDirCreate(directory, prefix)
                else:
                    logging.info("MaxFiles Not Exceeded in %s", subDirPath)
    os.path.abspath(subDirPath)
    return subDirPath


# ------------------------------------------------------------------------------
def filesToDelete(mediaDirPath, extension=image_format):
    """Return a list of files to be deleted"""
    return sorted(
        (
            os.path.join(dirname, filename)
            for dirname, dirnames, filenames in os.walk(mediaDirPath)
            for filename in filenames
            if filename.endswith(extension)
        ),
        key=lambda fn: os.stat(fn).st_mtime,
        reverse=True,
    )


# ------------------------------------------------------------------------------
def saveRecent(recentMax, recentDir, filename, prefix):
    """
    Create a symlink file in recent folder or file if non unix system
    or symlink creation fails.
    Delete Oldest symlink file if recentMax exceeded.
    """
    src = os.path.abspath(filename)  # Original Source File Path
    # Destination Recent Directory Path
    dest = os.path.abspath(os.path.join(recentDir, os.path.basename(filename)))
    deleteOldFiles(recentMax, os.path.abspath(recentDir), prefix)
    try:  # Create symlink in recent folder
        logging.info("   symlink %s", dest)
        os.symlink(src, dest)  # Create a symlink to actual file
    # Symlink can fail on non unix systems so copy file to Recent Dir instead
    except OSError as err:
        logging.error("symlink Failed: %s", err)
        try:  # Copy image file to recent folder (if no support for symlinks)
            shutil.copy(filename, recentDir)
        except OSError as err:
            logging.error("Copy from %s to %s - %s", filename, recentDir, err)


# ------------------------------------------------------------------------------
def freeSpaceUpTo(freeMB, mediaDir, extension=image_format):
    """
    Walks mediaDir and deletes oldest files
    until spaceFreeMB is achieved Use with Caution
    """
    mediaDirPath = os.path.abspath(mediaDir)
    if os.path.isdir(mediaDirPath):
        MB2Bytes = 1048576  # Conversion from MB to Bytes
        targetFreeBytes = freeMB * MB2Bytes
        fileList = filesToDelete(mediaDir, extension)
        totFiles = len(fileList)
        delcnt = 0
        logging.info("Session Started")
        while fileList:
            statv = os.statvfs(mediaDirPath)
            availFreeBytes = statv.f_bfree * statv.f_bsize
            if availFreeBytes >= targetFreeBytes:
                break
            filePath = fileList.pop()
            try:
                os.remove(filePath)
            except OSError as err:
                logging.error("Del Failed %s", filePath)
                logging.error("Error: %s", err)
            else:
                delcnt += 1
                logging.info("Del %s", filePath)
                logging.info(
                    "Target=%i MB  Avail=%i MB  Deleted %i of %i Files ",
                    targetFreeBytes / MB2Bytes,
                    availFreeBytes / MB2Bytes,
                    delcnt,
                    totFiles,
                )
                # Avoid deleting more than 1/4 of files at one time
                if delcnt > totFiles / 4:
                    logging.warning("Max Deletions Reached %i of %i", delcnt, totFiles)
                    logging.warning(
                        "Deletions Restricted to 1/4 of total files per session."
                    )
                    break
        logging.info("Session Ended")
    else:
        logging.error("Directory Not Found - %s", mediaDirPath)


# ------------------------------------------------------------------------------
def freeDiskSpaceCheck(lastSpaceCheck):
    """Free disk space by deleting some older files"""
    if spaceTimerHrs > 0:  # Check if disk free space timer hours is enabled
        # See if it is time to do disk clean-up check
        if (
            datetime.datetime.now() - lastSpaceCheck
        ).total_seconds() > spaceTimerHrs * 3600:
            lastSpaceCheck = datetime.datetime.now()
            # Set freeSpaceMB to reasonable value if too low
            if spaceFreeMB < 100:
                diskFreeMB = 100
            else:
                diskFreeMB = spaceFreeMB
            logging.info(
                "spaceTimerHrs=%i  diskFreeMB=%i  spaceMediaDir=%s spaceFileExt=%s",
                spaceTimerHrs,
                diskFreeMB,
                spaceMediaDir,
                spaceFileExt,
            )
            freeSpaceUpTo(diskFreeMB, spaceMediaDir, spaceFileExt)
    return lastSpaceCheck


# ------------------------------------------------------------------------------
def get_image_name(path, prefix):
    """build image file names by number sequence or date/time Added tenth of second"""
    rightNow = datetime.datetime.now()
    filename = "%s/%s%04d%02d%02d-%02d%02d%02d%d.jpg" % (
        path,
        prefix,
        rightNow.year,
        rightNow.month,
        rightNow.day,
        rightNow.hour,
        rightNow.minute,
        rightNow.second,
        rightNow.microsecond / 100000,
    )
    return filename


# ------------------------------------------------------------------------------
def log_to_csv(data_to_append):
    """Store date to a comma separated value file"""
    log_file_path = baseDir + baseFileName + ".csv"
    if not os.path.exists(log_file_path):
        open(log_file_path, "w").close()
        f = open(log_file_path, "ab")
        # header_text = ('"YYYY-MM-DD HH:MM:SS","Speed","Unit",
        #                  "    Speed Photo Path            ",
        #                  "X","Y","W","H","Area","Direction"' + "\n")
        # f.write( header_text )
        f.close()
        logging.info("Create New Data Log File %s", log_file_path)
    filecontents = data_to_append + "\n"
    f = open(log_file_path, "a+")
    f.write(filecontents)
    f.close()
    logging.info("   CSV - Appended Data into %s", log_file_path)
    return


# ------------------------------------------------------------------------------
def isSQLite3(filename):
    """
    Determine if filename is in sqlite3 format
    """
    if os.path.isfile(filename):
        if os.path.getsize(filename) < 100:  # SQLite database file header is 100 bytes
            size = os.path.getsize(filename)
            logging.error("%s %d is Less than 100 bytes", filename, size)
            return False
        with open(filename, "rb") as fd:
            header = fd.read(100)
            if header.startswith(b"SQLite format 3"):
                logging.info("Success: File is sqlite3 Format %s", filename)
                return True
            else:
                logging.error("Failed: File NOT sqlite3 Header Format %s", filename)
                return False
    else:
        logging.warning("File Not Found %s", filename)
        logging.info("Create sqlite3 database File %s", filename)
        try:
            conn = sqlite3.connect(filename)
        except sqlite3.Error as e:
            logging.error("Failed: Create Database %s.", filename)
            logging.error("Error Msg: %s", e)
            return False
        conn.commit()
        conn.close()
        logging.info("Success: Created sqlite3 Database %s", filename)
        return True


# ------------------------------------------------------------------------------
def db_check(db_file):
    """
    Check if db_file is a sqlite3 file and connect if possible
    """
    if isSQLite3(db_file):
        try:
            conn = sqlite3.connect(db_file, timeout=1)
        except sqlite3.Error as e:
            logging.error("Failed: sqlite3 Connect to DB %s", db_file)
            logging.error("Error Msg: %s", e)
            return None
    else:
        logging.error("Failed: sqlite3 Not DB Format %s", db_file)
        return None
    conn.commit()
    logging.info("Success: sqlite3 Connected to DB %s", db_file)
    return conn


# ------------------------------------------------------------------------------
def db_open(db_file):
    """
    Insert speed data into database table
    """
    try:
        db_conn = sqlite3.connect(db_file)
        cursor = db_conn.cursor()
    except sqlite3.Error as e:
        logging.error("Failed: sqlite3 Connect to DB %s", db_file)
        logging.error("Error Msg: %s", e)
        return None
    sql_cmd = """create table if not exists {} (idx text primary key,
                 log_timestamp text,
                 camera text,
                 ave_speed real, speed_units text, image_path text,
                 image_w integer, image_h integer, image_bigger integer,
                 direction text, plugin_name text,
                 cx integer, cy integer,
                 mw integer, mh integer, m_area integer,
                 x_left integer, x_right integer,
                 y_upper integer, y_lower integer,
                 max_speed_over integer,
                 min_area integer, track_counter integer,
                 cal_obj_px integer, cal_obj_mm integer, status text, cam_location text)""".format(
        DB_TABLE
    )
    try:
        db_conn.execute(sql_cmd)
    except sqlite3.Error as e:
        logging.error("Failed: To Create Table %s on sqlite3 DB %s", DB_TABLE, db_file)
        logging.error("Error Msg: %s", e)
        return None
    else:
        db_conn.commit()
    return db_conn


# ------------------------------------------------------------------------------
def speed_get_contours(image, grayimage1):
    """
    Read Camera image and crop and process
    with opencv to detect motion contours.
    Added timeout in case camera has a problem.
    """
    image_ok = False
    start_time = time.time()
    timeout = 60  # seconds to wait if camera communications is lost.
    # Note to self.  Look at adding setting to config.py
    while not image_ok:
        image = vs.read()  # Read image data from video steam thread instance
        # crop image to motion tracking area only
        try:
            image_crop = image[y_upper:y_lower, x_left:x_right]
            image_ok = True
        except (ValueError, TypeError):
            logging.error("image Stream Image is Not Complete. Cannot Crop. Retry.")
            if time.time() - start_time > timeout:
                logging.error(
                    "%i second timeout exceeded.  Partial or No images received.",
                    timeout,
                )
                logging.error(
                    "Possible camera or communication problem.  Please Investigate."
                )
                sys.exit(1)
            else:
                image_ok = False
    # Convert to gray scale, which is easier
    grayimage2 = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
    # Get differences between the two greyed images
    global differenceimage
    differenceimage = cv2.absdiff(grayimage1, grayimage2)
    # Blur difference image to enhance motion vectors
    differenceimage = cv2.blur(differenceimage, (BLUR_SIZE, BLUR_SIZE))
    # Get threshold of blurred difference image
    # based on THRESHOLD_SENSITIVITY variable
    retval, thresholdimage = cv2.threshold(
        differenceimage, THRESHOLD_SENSITIVITY, 255, cv2.THRESH_BINARY
    )
    try:
        # opencv 2 syntax default
        contours, hierarchy = cv2.findContours(
            thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
    except ValueError:
        # opencv 3 syntax
        thresholdimage, contours, hierarchy = cv2.findContours(
            thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
    # Update grayimage1 to grayimage2 ready for next image2
    grayimage1 = grayimage2
    return grayimage1, contours


# ------------------------------------------------------------------------------
def speed_image_add_lines(image, color):
    cv2.line(image, (x_left, y_upper), (x_right, y_upper), color, 1)
    cv2.line(image, (x_left, y_lower), (x_right, y_lower), color, 1)
    cv2.line(image, (x_left, y_upper), (x_left, y_lower), color, 1)
    cv2.line(image, (x_right, y_upper), (x_right, y_lower), color, 1)
    return image


# ------------------------------------------------------------------------------
def speed_notify():
    if pluginEnable:
        logging.info("Plugin Enabled per pluginName=%s", pluginName)
    else:
        logging.info("Plugin Disabled per pluginEnable=%s", pluginEnable)
    if verbose:
        if loggingToFile:
            print("Logging to File %s (Console Messages Disabled)" % logFilePath)
        else:
            logging.info("Logging to Console per Variable verbose=True")
        if gui_window_on:
            logging.info("Press lower case q on OpenCV GUI Window to Quit program")
            logging.info("        or ctrl-c in this terminal session to Quit")
        else:
            logging.info("Press ctrl-c in this terminal session to Quit")
    else:
        print("Logging Messages Disabled per verbose=%s" % verbose)
    if calibrate:
        logging.warning("IMPORTANT: Camera Is In Calibration Mode ....")
    if align_cam_on:
        logging.warning("IMPORTANT: Camera is in Alignment Mode ....")
    else:
        if os.path.isfile(align_filename):
            os.remove(align_filename)
            logging.info("Removed camera alignment image at %s", align_filename)
    logging.info("Begin Motion Tracking .....")


# ------------------------------------------------------------------------------
def speed_camera():
    """Main speed camera processing function"""
    ave_speed = 0.0
    # initialize variables
    frame_count = 0
    fps_time = time.time()
    first_event = True  # Start a New Motion Track
    event_timer = time.time()
    start_pos_x = None
    end_pos_x = None
    prev_pos_x = None
    travel_direction = None
    font = cv2.FONT_HERSHEY_SIMPLEX
    # Calculate position of text on the images
    if image_text_bottom:
        text_y = image_height - 50  # show text at bottom of image
    else:
        text_y = 10  # show text at top of image
    # Initialize prev_image used for taking speed image photo
    lastSpaceCheck = datetime.datetime.now()
    speed_path = image_path
    db_conn = db_check(DB_PATH)
    # check and open sqlite3 db
    if db_conn is not None:
        db_conn = db_open(DB_PATH)
        if db_conn is None:
            logging.error("Failed: Connect to sqlite3 DB %s", DB_PATH)
            db_is_open = False
        else:
            logging.info("sqlite3 DB is Open %s", DB_PATH)
            db_cur = db_conn.cursor()  # Set cursor position
            db_is_open = True
    # insert status column into speed table.  Can be used for
    # alpr (automatic license plate reader) processing to indicate
    # images to be processed eg null field entry.
    try:
        db_conn.execute("alter table speed add status text")
        db_conn.execute("alter table speed add cam_location text")
    except sqlite3.OperationalError:
        pass
    db_conn.close()
    speed_notify()
    # Warn user of performance hit if webcam image flipped
    if WEBCAM and WEBCAM_FLIPPED:
        logging.warning("Recommend you do NOT Flip Webcam stream")
        logging.warning("Otherwise SLOW streaming Will Result...")
        logging.warning("If necessary physically flip camera and")
        logging.warning("Set config.py WEBCAM_HFLIP and WEBCAM_VFLIP to False")
    # initialize a cropped grayimage1 image
    image2 = vs.read()  # Get image from VideoSteam thread instance
    prev_image = image2  # make a copy of the first image

    try:
        # crop image to motion tracking area only
        image_crop = image2[y_upper:y_lower, x_left:x_right]
    except:
        vs.stop()
        logging.warning("Problem Connecting To Camera Stream.")
        logging.warning("Restarting Camera.  One Moment Please ...")
        time.sleep(4)
        return
    grayimage1 = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
    track_count = 0
    speed_list = []
    event_timer = time.time()
    still_scanning = True
    image_sign_bg = np.zeros((image_sign_resize[0], image_sign_resize[1], 4))
    image_sign_view = cv2.resize(image_sign_bg, (image_sign_resize))
    image_sign_view_time = time.time()
    while still_scanning:  # process camera thread images and calculate speed
        image2 = vs.read()  # Read image data from video steam thread instance
        grayimage1, contours = speed_get_contours(image2, grayimage1)
        # if contours found, find the one with biggest area
        if contours:
            total_contours = len(contours)
            motion_found = False
            biggest_area = MIN_AREA
            for c in contours:
                # get area of contour
                found_area = cv2.contourArea(c)
                if found_area > biggest_area:
                    (x, y, w, h) = cv2.boundingRect(c)
                    # check if object contour is completely within crop area
                    if x > x_buf and x + w < x_right - x_left - x_buf:

                        track_x = x
                        track_y = y
                        track_w = w  # movement width of object contour
                        track_h = h  # movement height of object contour
                        motion_found = True
                        biggest_area = found_area
                        cur_track_time = time.time()  # record cur track time
            if motion_found:
                # Check if last motion event timed out
                reset_time_diff = time.time() - event_timer
                if reset_time_diff > event_timeout:
                    # event_timer exceeded so reset for new track
                    event_timer = time.time()
                    first_event = True
                    start_pos_x = None
                    prev_pos_x = None
                    end_pos_x = None
                    logging.info(
                        "Reset- event_timer %.2f>%.2f sec Exceeded",
                        reset_time_diff,
                        event_timeout,
                    )
                    print(horiz_line)
                ##############################
                # Process motion events and track object movement
                ##############################
                if first_event:  # This is a first valid motion event
                    first_event = False  # Only one first track event
                    track_start_time = cur_track_time  # Record track start time
                    prev_start_time = cur_track_time
                    start_pos_x = track_x
                    prev_pos_x = track_x
                    end_pos_x = track_x
                    logging.info(
                        "New  - 0/%i xy(%i,%i) Start New Track",
                        track_counter,
                        track_x,
                        track_y,
                    )
                    event_timer = time.time()  # Reset event timeout
                    track_count = 0
                    speed_list = []
                else:
                    prev_pos_x = end_pos_x
                    end_pos_x = track_x
                    if end_pos_x - prev_pos_x > 0:
                        travel_direction = "L2R"
                        cal_obj_px = cal_obj_px_L2R
                        cal_obj_mm = cal_obj_mm_L2R
                    else:
                        travel_direction = "R2L"
                        cal_obj_px = cal_obj_px_R2L
                        cal_obj_mm = cal_obj_mm_R2L
                    # check if movement is within acceptable distance
                    # range of last event
                    if (
                        abs(end_pos_x - prev_pos_x) > x_diff_min
                        and abs(end_pos_x - prev_pos_x) <= x_diff_max
                    ):

                        cur_track_dist = abs(end_pos_x - prev_pos_x)
                        try:
                            if travel_direction == "L2R":
                                cur_ave_speed = float(
                                    (
                                        abs(
                                            cur_track_dist
                                            / float(
                                                abs(cur_track_time - prev_start_time)
                                            )
                                        )
                                    )
                                    * speed_conv_L2R
                                )
                            else:
                                cur_ave_speed = float(
                                    (
                                        abs(
                                            cur_track_dist
                                            / float(
                                                abs(cur_track_time - prev_start_time)
                                            )
                                        )
                                    )
                                    * speed_conv_R2L
                                )
                        except ZeroDivisionError:  # This sometimes happens on windows due to clock precision issue
                            logging.warning(
                                "Division by Zero Error. Aborting this track event."
                            )
                            continue
                        track_count += 1  # increment track counter
                        speed_list.append(cur_ave_speed)
                        ave_speed = np.mean(speed_list)
                        prev_start_time = cur_track_time
                        event_timer = time.time()
                        if track_count >= track_counter:
                            tot_track_dist = abs(track_x - start_pos_x)
                            tot_track_time = abs(track_start_time - cur_track_time)

                            # Track length exceeded so take process speed photo
                            if ave_speed > max_speed_over or calibrate:
                                logging.info(
                                    " Add - %i/%i xy(%i,%i) %3.2f %s"
                                    " D=%i/%i C=%i %ix%i=%i sqpx %s",
                                    track_count,
                                    track_counter,
                                    track_x,
                                    track_y,
                                    ave_speed,
                                    speed_units,
                                    abs(track_x - prev_pos_x),
                                    x_diff_max,
                                    total_contours,
                                    track_w,
                                    track_h,
                                    biggest_area,
                                    travel_direction,
                                )
                                # Resize and process previous image
                                # before saving to disk
                                prev_image = image2
                                # Create a calibration image file name
                                # There are no subdirectories to deal with
                                if calibrate:
                                    log_time = datetime.datetime.now()
                                    filename = get_image_name(speed_path, "calib-")
                                    prev_image = take_calibration_image(
                                        ave_speed, filename, prev_image
                                    )
                                else:
                                    # Check if subdirectories configured
                                    # and create new subdirectory if required
                                    speed_path = subDirChecks(
                                        imageSubDirMaxHours,
                                        imageSubDirMaxFiles,
                                        image_path,
                                        image_prefix,
                                    )

                                    # Record log_time for use later in csv and sqlite
                                    log_time = datetime.datetime.now()
                                    # Create image file name
                                    if image_filename_speed:
                                        # add ave_speed value to filename after prefix
                                        speed_prefix = (
                                            image_prefix
                                            + str(int(round(ave_speed)))
                                            + "-"
                                        )
                                        filename = get_image_name(
                                            speed_path, speed_prefix
                                        )
                                    else:
                                        # create image file name path
                                        filename = get_image_name(
                                            speed_path, image_prefix
                                        )
                                # Add motion rectangle to image if required
                                if image_show_motion_area:
                                    prev_image = speed_image_add_lines(
                                        prev_image, cvRed
                                    )
                                    # show centre of motion if required
                                    if SHOW_CIRCLE:
                                        cv2.circle(
                                            prev_image,
                                            (track_x + x_left, track_y + y_upper),
                                            CIRCLE_SIZE,
                                            cvGreen,
                                            LINE_THICKNESS,
                                        )
                                    else:
                                        cv2.rectangle(
                                            prev_image,
                                            (
                                                int(track_x + x_left),
                                                int(track_y + y_upper),
                                            ),
                                            (
                                                int(track_x + x_left + track_w),
                                                int(track_y + y_upper + track_h),
                                            ),
                                            cvGreen,
                                            LINE_THICKNESS,
                                        )
                                big_image = cv2.resize(
                                    prev_image, (image_width, image_height)
                                )
                                if image_sign_on:
                                    image_sign_view_time = time.time()
                                    image_sign_bg = np.zeros(
                                        (image_sign_resize[0], image_sign_resize[1], 4)
                                    )
                                    image_sign_view = cv2.resize(
                                        image_sign_bg, (image_sign_resize)
                                    )
                                    image_sign_text = str(int(round(ave_speed, 0)))
                                    cv2.putText(
                                        image_sign_view,
                                        image_sign_text,
                                        image_sign_text_xy,
                                        font,
                                        image_sign_font_scale,
                                        image_sign_font_color,
                                        image_sign_font_thickness,
                                    )
                                # Write text on image before saving
                                # if required.
                                if image_text_on:
                                    image_text = "SPEED %.1f %s - %s" % (
                                        ave_speed,
                                        speed_units,
                                        filename,
                                    )
                                    text_x = int(
                                        (image_width / 2)
                                        - (len(image_text) * image_font_size / 3)
                                    )
                                    if text_x < 2:
                                        text_x = 2
                                    cv2.putText(
                                        big_image,
                                        image_text,
                                        (text_x, text_y),
                                        font,
                                        image_font_scale,
                                        image_font_color,
                                        image_font_thickness,
                                    )
                                logging.info(" Saved %s", filename)
                                # Save resized image. If jpg format, user can customize image quality 1-100 (higher is better)
                                # and/or enble/disable optimization per config.py settings.
                                # otherwise if png, bmp, gif, etc normal image write will occur
                                if (
                                    image_format.lower() == ".jpg"
                                    or image_format.lower() == ".jpeg"
                                ):
                                    try:
                                        cv2.imwrite(
                                            filename,
                                            big_image,
                                            [
                                                int(cv2.IMWRITE_JPEG_QUALITY),
                                                image_jpeg_quality,
                                                int(cv2.IMWRITE_JPEG_OPTIMIZE),
                                                image_jpeg_optimize,
                                            ],
                                        )
                                    except:  # sometimes issue with IP camera so default to non optimized imwrite
                                        cv2.imwrite(filename, big_image)
                                else:
                                    cv2.imwrite(filename, big_image)
                                if motionCode:
                                    # ===========================================
                                    # Put your user code in userMotionCode() function
                                    # In the File user_motion_code.py
                                    # ===========================================
                                    try:
                                        user_motion_code.userMotionCode(
                                            vs, image_width, image_height, filename
                                        )
                                    except ValueError:
                                        logging.error(
                                            "Problem running userMotionCode function from File %s",
                                            userMotionFilePath,
                                        )
                                    except TypeError as err:
                                        logging.error(
                                            "Problem with file user_motion_code.py Possibly out of date"
                                        )
                                        logging.error("Err Msg: %s", err)
                                        logging.error(
                                            "Suggest you delete/rename file and perform menubox UPGRADE"
                                        )

                                log_idx = "%04d%02d%02d-%02d%02d%02d%d" % (
                                    log_time.year,
                                    log_time.month,
                                    log_time.day,
                                    log_time.hour,
                                    log_time.minute,
                                    log_time.second,
                                    log_time.microsecond / 100000,
                                )
                                log_timestamp = "%s%04d-%02d-%02d %02d:%02d:%02d%s" % (
                                    quote,
                                    log_time.year,
                                    log_time.month,
                                    log_time.day,
                                    log_time.hour,
                                    log_time.minute,
                                    log_time.second,
                                    quote,
                                )
                                m_area = track_w * track_h
                                if WEBCAM:
                                    camera = "WebCam"
                                else:
                                    camera = "PiCam"
                                if pluginEnable:
                                    plugin_name = pluginName
                                else:
                                    plugin_name = "None"
                                # create the speed data list ready for db insert
                                speed_data = (
                                    log_idx,
                                    log_timestamp,
                                    camera,
                                    round(ave_speed, 2),
                                    speed_units,
                                    filename,
                                    image_width,
                                    image_height,
                                    image_bigger,
                                    travel_direction,
                                    plugin_name,
                                    track_x,
                                    track_y,
                                    track_w,
                                    track_h,
                                    m_area,
                                    x_left,
                                    x_right,
                                    y_upper,
                                    y_lower,
                                    max_speed_over,
                                    MIN_AREA,
                                    track_counter,
                                    cal_obj_px,
                                    cal_obj_mm,
                                    "",
                                    CAM_LOCATION,
                                )

                                # Insert speed_data into sqlite3 database table
                                # Note cam_location and status may not be in proper order
                                # Unless speed table is recreated.
                                try:
                                    sql_cmd = """insert into {} values {}""".format(
                                        DB_TABLE, speed_data
                                    )
                                    db_conn = db_check(DB_PATH)
                                    db_conn.execute(sql_cmd)
                                    db_conn.commit()
                                    db_conn.close()
                                except sqlite3.Error as e:
                                    logging.error("sqlite3 DB %s", DB_PATH)
                                    logging.error(
                                        "Failed: To INSERT Speed Data into TABLE %s",
                                        DB_TABLE,
                                    )
                                    logging.error("Err Msg: %s", e)
                                else:
                                    logging.info(
                                        " SQL - Inserted Data Row into %s", DB_PATH
                                    )
                                # Format and Save Data to CSV Log File
                                if log_data_to_CSV:
                                    log_csv_time = (
                                        "%s%04d-%02d-%02d %02d:%02d:%02d%s"
                                        % (
                                            quote,
                                            log_time.year,
                                            log_time.month,
                                            log_time.day,
                                            log_time.hour,
                                            log_time.minute,
                                            log_time.second,
                                            quote,
                                        )
                                    )
                                    log_csv_text = (
                                        "%s,%.2f,%s%s%s,%s%s%s,"
                                        "%i,%i,%i,%i,%i,%s%s%s,%s,%s,%s"
                                        % (
                                            log_csv_time,
                                            ave_speed,
                                            quote,
                                            speed_units,
                                            quote,
                                            quote,
                                            filename,
                                            quote,
                                            track_x,
                                            track_y,
                                            track_w,
                                            track_h,
                                            track_w * track_h,
                                            quote,
                                            travel_direction,
                                            quote,
                                            quote,
                                            CAM_LOCATION,
                                            quote,
                                        )
                                    )
                                    log_to_csv(log_csv_text)
                                if spaceTimerHrs > 0:
                                    lastSpaceCheck = freeDiskSpaceCheck(lastSpaceCheck)
                                # Manage a maximum number of files
                                # and delete oldest if required.
                                if image_max_files > 0:
                                    deleteOldFiles(
                                        image_max_files, speed_path, image_prefix
                                    )
                                # Save most recent files
                                # to a recent folder if required
                                if imageRecentMax > 0 and not calibrate:
                                    saveRecent(
                                        imageRecentMax,
                                        imageRecentDir,
                                        filename,
                                        image_prefix,
                                    )
                                logging.info(
                                    "End  - %s Ave Speed %.1f %s Tracked %i px in %.3f sec Calib %ipx %imm",
                                    travel_direction,
                                    ave_speed,
                                    speed_units,
                                    tot_track_dist,
                                    tot_track_time,
                                    cal_obj_px,
                                    cal_obj_mm,
                                )
                            else:
                                logging.info(
                                    "End  - Skip Photo SPEED %.1f %s"
                                    " max_speed_over=%i  %i px in %.3f sec"
                                    " C=%i A=%i sqpx",
                                    ave_speed,
                                    speed_units,
                                    max_speed_over,
                                    tot_track_dist,
                                    tot_track_time,
                                    total_contours,
                                    biggest_area,
                                )
                            # Optional Wait to avoid multiple recording of same object
                            print(horiz_line)
                            if track_timeout > 0:
                                logging.info(
                                    "track_timeout %0.2f sec Sleep to Avoid Tracking Same Object Multiple Times."
                                    % track_timeout
                                )
                                time.sleep(track_timeout)
                            # Track Ended so Reset Variables ready for
                            # next tracking sequence
                            start_pos_x = None
                            end_pos_x = None
                            first_event = True  # Reset Track
                            track_count = 0
                            event_timer = time.time()
                        else:
                            logging.info(
                                " Add - %i/%i xy(%i,%i) %3.2f %s"
                                " D=%i/%i C=%i %ix%i=%i sqpx %s",
                                track_count,
                                track_counter,
                                track_x,
                                track_y,
                                ave_speed,
                                speed_units,
                                abs(track_x - prev_pos_x),
                                x_diff_max,
                                total_contours,
                                track_w,
                                track_h,
                                biggest_area,
                                travel_direction,
                            )
                            end_pos_x = track_x
                            # valid motion found so update event_timer
                            event_timer = time.time()
                    # Movement was not within range parameters
                    else:
                        if show_out_range:
                            # movements exceeds Max px movement
                            # allowed so Ignore and do not update event_timer
                            if abs(track_x - prev_pos_x) >= x_diff_max:
                                logging.info(
                                    " Out - %i/%i xy(%i,%i) Max D=%i>=%ipx"
                                    " C=%i %ix%i=%i sqpx %s",
                                    track_count,
                                    track_counter,
                                    track_x,
                                    track_y,
                                    abs(track_x - prev_pos_x),
                                    x_diff_max,
                                    total_contours,
                                    track_w,
                                    track_h,
                                    biggest_area,
                                    travel_direction,
                                )
                                # if track_count is over half way then do not start new track
                                if track_count > track_counter / 2:
                                    pass
                                else:
                                    first_event = True  # Too Far Away so restart Track
                            # Did not move much so update event_timer
                            # and wait for next valid movement.
                            else:
                                logging.info(
                                    " Out - %i/%i xy(%i,%i) Min D=%i<=%ipx"
                                    " C=%i %ix%i=%i sqpx %s",
                                    track_count,
                                    track_counter,
                                    track_x,
                                    track_y,
                                    abs(track_x - end_pos_x),
                                    x_diff_min,
                                    total_contours,
                                    track_w,
                                    track_h,
                                    biggest_area,
                                    travel_direction,
                                )
                                # Restart Track if first event otherwise continue
                                if track_count == 0:
                                    first_event = True
                        event_timer = time.time()  # Reset Event Timer
                if gui_window_on:
                    # show small circle at contour xy if required
                    # otherwise a rectangle around most recent contour
                    if SHOW_CIRCLE:
                        cv2.circle(
                            image2,
                            (
                                int(track_x + x_left * WINDOW_BIGGER),
                                int(track_y + y_upper * WINDOW_BIGGER),
                            ),
                            CIRCLE_SIZE,
                            cvGreen,
                            LINE_THICKNESS,
                        )
                    else:
                        cv2.rectangle(
                            image2,
                            (int(x_left + track_x), int(y_upper + track_y)),
                            (
                                int(x_left + track_x + track_w),
                                int(y_upper + track_y + track_h),
                            ),
                            cvGreen,
                            LINE_THICKNESS,
                        )
        if align_cam_on:
            image2 = speed_image_add_lines(image2, cvRed)
            image_view = cv2.resize(image2, (image_width, image_height))
            cv2.imwrite(align_filename, image_view)
            logging.info(
                "align_cam_on=%s align_delay_sec=%i - Browser View Cam Align Image at %s",
                align_cam_on,
                align_delay_sec,
                align_filename,
            )
            time.sleep(align_delay_sec)
        if gui_window_on:
            # cv2.imshow('Difference Image',difference image)
            image2 = speed_image_add_lines(image2, cvRed)
            image_view = cv2.resize(image2, (image_width, image_height))
            if gui_show_camera:
                cv2.imshow("Movement (q Quits)", image_view)
            if show_thresh_on:
                cv2.imshow("Threshold", differenceimage)
            if show_crop_on:
                cv2.imshow("Crop Area", image_crop)
            if image_sign_on:
                if time.time() - image_sign_view_time > image_sign_timeout:
                    # Cleanup the image_sign_view
                    image_sign_bg = np.zeros(
                        (image_sign_resize[0], image_sign_resize[1], 4)
                    )
                    image_sign_view = cv2.resize(image_sign_bg, (image_sign_resize))
                cv2_window_speed_sign = "Last Average Speed:"
                cv2.namedWindow(cv2_window_speed_sign, cv2.WINDOW_NORMAL)
                cv2.cv2.setWindowProperty(
                    cv2_window_speed_sign,
                    cv2.WND_PROP_FULLSCREEN,
                    cv2.WINDOW_FULLSCREEN,
                )
                cv2.imshow(cv2_window_speed_sign, image_sign_view)
            # Close Window if q pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                logging.info("End Motion Tracking ......")
                vs.stop()
                still_scanning = False
        if display_fps:  # Optionally show motion image processing loop fps
            fps_time, frame_count = get_fps(fps_time, frame_count)


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        WEBCAM_TRIES = 0
        while True:
            # Start Web Cam stream (Note USB webcam must be plugged in)
            if WEBCAM:
                WEBCAM_TRIES += 1
                logging.info("Initializing USB Web Camera Try .. %i", WEBCAM_TRIES)
                # Start video stream on a processor Thread for faster speed
                vs = WebcamVideoStream().start()
                vs.CAM_SRC = WEBCAM_SRC
                vs.CAM_WIDTH = WEBCAM_WIDTH
                vs.CAM_HEIGHT = WEBCAM_HEIGHT
                if WEBCAM_TRIES > 3:
                    logging.error(
                        "USB Web Cam Not Connecting to WEBCAM_SRC %i", WEBCAM_SRC
                    )
                    logging.error("Check Camera is Plugged In and Working")
                    logging.error("on Specified SRC")
                    logging.error("and Not Used(busy) by Another Process.")
                    logging.error("%s %s Exiting Due to Error", progName, progVer)
                    vs.stop()
                    sys.exit(1)
                time.sleep(4.0)  # Allow WebCam to initialize
            else:
                logging.info("Initializing Pi Camera ....")
                # Start a pi-camera video stream thread
                vs = PiVideoStream().start()
                vs.camera.rotation = CAMERA_ROTATION
                vs.camera.hflip = CAMERA_HFLIP
                vs.camera.vflip = CAMERA_VFLIP
                time.sleep(2.0)  # Allow PiCamera to initialize
            # Get actual image size from stream.
            # Necessary for IP camera
            test_img = vs.read()
            img_height, img_width, _ = test_img.shape
            # Set width of trigger point image to save
            image_width = int(img_width * image_bigger)
            # Set height of trigger point image to save
            image_height = int(img_height * image_bigger)

            x_scale = 8.0
            y_scale = 4.0
            # reduce motion area for larger stream sizes
            if img_width > 1000:
                x_scale = 3.0
                y_scale = 3.0
            # If motion box crop settings not found in config.py then
            # Auto adjust the crop image to suit the real image size.
            # For details See comments in config.py Motion Events settings section
            try:
                x_left
            except NameError:
                x_left = int(img_width / x_scale)
            try:
                x_right
            except NameError:
                x_right = int(img_width - x_left)
            try:
                y_upper
            except NameError:
                y_upper = int(img_height / y_scale)
            try:
                y_lower
            except NameError:
                y_lower = int(img_height - y_upper)
            # setup buffer area to ensure contour is mostly contained in crop area
            x_buf = int((x_right - x_left) / x_buf_adjust)

            show_settings()  # Show variable settings
            speed_camera()  # run main speed camera processing loop
    except KeyboardInterrupt:
        vs.stop()
        print("")
        logging.info("User Pressed Keyboard ctrl-c")
        logging.info("%s %s Exiting Program", progName, progVer)
        sys.exit()
