#!/usr/bin/python3
"""
speed-cam.py written by Claude Pageau
Windows, Unix, Raspberry (Pi) - python opencv2 Object Speed tracking
using picamera module, Web Cam or RTSP IP Camera
GitHub Repo at https://github.com/pageauc/speed-camera
Post issue to Github.

This is a python openCV object speed tracking demonstration program.
It will detect speed in the field of view and use openCV to calculate the
largest contour and return its x,y center coordinate.  The image is tracked for
a specified loop count and the final speed is calculated.
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
Requires a Raspberry Pi or compatible, Windows, Unix PC or Mac with webcam or RTSP IP Camera.
or a virtual machine unix distro eg Debian. Runs best under python3 but code is compatible with python2.
Works with RPI camera module using picamera or libpicamera2 python module.
See github wiki for detail https://github.com/pageauc/speed-camera/wiki

Install from a GitHub download, Docker or using Curl install from logged in SSH session per commands below.
Code should run on a non RPI platform using a Web Cam or RTSP ip cam

    curl -L https://raw.github.com/pageauc/rpi-speed-camera/master/speed-install.sh | bash
or
    wget https://raw.github.com/pageauc/rpi-speed-camera/master/speed-install.sh
    chmod +x speed-install.sh
    ./speed-install.sh
    ./speed-cam.py

Note to Self - Look at eliminating python variable camel case and use all snake naming

"""
from __future__ import print_function
PROG_VER = "13.2"  # current version of this python script
print('Loading Wait...')
import os
import sys
import time
import datetime
import glob
import shutil
import logging
import sqlite3
import numpy as np

# import the main strmcam launch module
try:
    from strmcam import strmcam
except Exception as err_msg:
    print("ERROR: %s" % err_msg)
    sys.exit(1)

# Get information about this script including name, launch path, etc.
# This allows script to be renamed or relocated to another directory
mypath = os.path.abspath(__file__)  # Find the full path of this python script
# get the path location only (excluding script name)
baseDir = mypath[0 : mypath.rfind("/") + 1]
baseFileName = mypath[mypath.rfind("/") + 1 : mypath.rfind(".")]
PROG_NAME = os.path.basename(__file__)

HORIZ_LINE = "----------------------------------------------------------------------"
print(HORIZ_LINE)
print("%s %s  written by Claude Pageau" % (PROG_NAME, PROG_VER))
print("Motion Track Largest Moving Object and Calculate Speed per Calibration.")
print(HORIZ_LINE)

# This is a dictionary of the default settings for speed-cam.py
# If you don't want to use a config.py file these will create the required
# variables with default values.  Change dictionary values if you want different
# variable default values.
# A message will be displayed if a variable is Not imported from config.py.
# Note: plugins can override default and config.py values if plugins are
#       enabled.  This happens after config.py variables are imported
default_settings = {
    "CALIBRATE_ON": True,
    "ALIGN_CAM_ON": False,
    "ALIGN_DELAY_SEC": 2,
    "SHOW_SETTINGS_ON": False,
    "CAL_OBJ_PX_L2R": 90,
    "CAL_OBJ_MM_L2R": 4700.0,
    "CAL_OBJ_PX_R2L": 95,
    "CAL_OBJ_MM_R2L": 4700.0,
    "PLUGIN_ENABLE_ON": False,
    "PLUGIN_NAME": "picam240",
    "GUI_WINDOW_ON": False,
    "GUI_THRESH_WIN_ON": False,
    "GUI_CROP_WIN_ON": False,
    "LOG_VERBOSE_ON": True,
    "LOG_FPS_ON": False,
    "LOG_DATA_TO_CSV": False,
    "LOG_TO_FILE_ON": False,
    "LOG_FILE_PATH": "speed-cam.log",
    "MO_SPEED_MPH_ON": False,
    "MO_TRACK_EVENT_COUNT": 5,
    "MO_MIN_AREA_PX": 100,
    "MO_LOG_OUT_RANGE_ON": True,
    "MO_MAX_X_DIFF_PX": 20,
    "MO_MIN_X_DIFF_PX": 1,
    "MO_X_LR_SIDE_BUFF_PX": 10,
    "MO_TRACK_TIMEOUT_SEC": 0.5,
    "MO_EVENT_TIMEOUT_SEC": 0.3,
    "MO_MAX_SPEED_OVER": 0,
    "MO_CROP_AUTO_ON": False,
    "MO_CROP_X_LEFT": 50,
    "MO_CROP_X_RIGHT": 250,
    "MO_CROP_Y_UPPER": 90,
    "MO_CROP_Y_LOWER": 150,
    "CAMERA": "pilibcam",
    "CAM_LOCATION": "Front Window",
    "USBCAM_SRC": 0,
    "RTSPCAM_SRC": "rtsp://user:password@IP:554/path",
    "IM_SIZE": (320, 240),
    "IM_VFLIP": False,
    "IM_HFLIP": False,
    "IM_ROTATION": 0,
    "IM_FRAMERATE": 30,
    "IM_DIR_PATH": "media/images",
    "IM_PREFIX": "speed-",
    "IM_FORMAT_EXT": ".jpg",
    "IM_JPG_QUALITY": 95,
    "IM_JPG_OPTIMIZE_ON": False,
    "IM_SAVE_4AI_ON": False,
    "IM_SAVE_4AI_POS_DIR": "media/ai/pos",
    "IM_SAVE_4AI_NEG_DIR": "media/ai/pos",
    "IM_SAVE_4AI_DAY_THRESH": 10,
    "IM_SAVE_4AI_NEG_TIMER_SEC": 60 * 60 * 6,
    "IM_FIRST_AND_LAST_ON": False,
    "IM_SHOW_CROP_AREA_ON": True,
    "IM_SHOW_SPEED_FILENAME_ON": False,
    "IM_SHOW_TEXT_ON": True,
    "IM_SHOW_TEXT_BOTTOM_ON": True,
    "IM_FONT_SIZE_PX": 12,
    "IM_FONT_THICKNESS": 2,
    "IM_FONT_SCALE": 0.5,
    "IM_FONT_COLOR": (255, 255, 255),
    "IM_BIGGER": 3.0,
    "IM_MAX_FILES": 0,
    "IM_SUBDIR_MAX_FILES": 1000,
    "IM_SUBDIR_MAX_HOURS": 0,
    "IM_RECENT_MAX_FILES": 100,
    "IM_RECENT_DIR_PATH": "media/recent",
    "SPACE_TIMER_HRS": 0,
    "SPACE_FREE_MB": 500,
    "SPACE_MEDIA_DIR": "media/images",
    "SPACE_FILE_EXT ": "jpg",
    "CV_SHOW_CIRCLE_ON": False,
    "CV_CIRCLE_SIZE_PX": 5,
    "CV_LINE_WIDTH_PX": 1,
    "CV_WINDOW_BIGGER": 1.0,
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
    "WEB_SERVER_PORT": 8080,
    "WEB_SERVER_ROOT": "media",
    "WEB_PAGE_TITLE": "SPEED-CAMERA Media",
    "WEB_PAGE_REFRESH_ON": True,
    "WEB_PAGE_REFRESH_SEC": "900",
    "WEB_PAGE_BLANK_ON": False,
    "WEB_IMAGE_HEIGHT": "768",
    "WEB_IFRAME_WIDTH_PERCENT": "70%",
    "WEB_IFRAME_WIDTH": "100%",
    "WEB_IFRAME_HEIGHT": "100%",
    "WEB_MAX_LIST_ENTRIES": 0,
    "WEB_LIST_HEIGHT": "768",
    "WEB_LIST_BY_DATETIME_ON": True,
    "WEB_LIST_SORT_DESC_ON": True,
    "IM_SHOW_SIGN_ON": False,
    "IM_SIGN_RESIZE": (1280, 720),
    "IM_SIGN_TEXT_XY": (100, 675),
    "IM_SIGN_FONT_SCALE": 30.0,
    "IM_SIGN_FONT_THICK_PX": 60,
    "IM_SIGN_FONT_COLOR": (255, 255, 255),
    "IM_SIGN_TIMEOUT_SEC": 5,
}

# Color data for OpenCV lines and text
cvWhite = (255, 255, 255)
cvBlack = (0, 0, 0)
cvBlue = (255, 0, 0)
cvGreen = (0, 255, 0)
cvRed = (0, 0, 255)

QUOTE = '"'  # Used for creating QUOTE delimited log file of speed data
FIX_MSG = """
    ---------- Upgrade Instructions -----------
    To Fix Problem Run ./menubox.sh UPGRADE menu pick.
    After upgrade newest config.py will be named config.py.new
    In SSH or terminal perform the following commands
    to update to latest config.py

        cd ~/speed-camera
        cp config.py config.py.bak
        cp config.py.new config.py

    Then Edit nsno config.py and transfer any customized settings
    from config.py.bak File to config.py
    -------------------------------------------
    Wait 5 sec ....

    """

# Check for config.py variable file and import. Warn if file not Found.
# Logging is not used since the LOG_FILE_PATH variable is needed before
# setting up logging
configFilePath = os.path.join(baseDir, "config.py")
if os.path.exists(configFilePath):
    # Read Configuration variables from config.py file
    try:
        from config import *
    except Exception as err_msg:
        print("WARN : %s" % err_msg)
else:
    print("WARN  : Missing config.py file - File Not Found %s" % configFilePath)

# Check if variables were imported from config.py. If not create variable using
# the values in the default_settings dictionary above.
warn_msg = False
for key, val in default_settings.items():
    try:
        exec(key)
    except NameError:
        print("WARN : config.py Variable Not Found. Setting " + key + " = " + str(val))
        exec(key + "=val")
        warn_msg = True
if warn_msg:
    print(FIX_MSG)
    time.sleep(5)

# Now that variables are imported from config.py Setup Logging since we have LOG_FILE_PATH
if LOG_TO_FILE_ON:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=LOG_FILE_PATH,
        filemode="w",
    )
elif LOG_VERBOSE_ON:
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
        logging.error("Try running menubox.sh then UPGRADE menu pick.")
    logging.error("%s %s Exiting Due to Error", PROG_NAME, PROG_VER)
    sys.exit(1)

# Import a single variable from the search_config.py file
# This is done to auto create a media/search directory
try:
    from search_config import search_dest_path
except ImportError:
    search_dest_path = "media/search"
    logging.warning("Problem importing search_dest_path variable")
    logging.info("Setting default value search_dest_path = %s", search_dest_path)

# Check for user_motion_code.py file to import and error out if not found.
userMotionFilePath = os.path.join(baseDir, "user_motion_code.py")
USER_MOTION_CODE_ON = True     # Set Flag to run user_motion_code.py
if os.path.isfile(userMotionFilePath):
    try:
        import user_motion_code
    except Exception as err_msg:
        print("WARN: %s" % err_msg)
        # set flag to ignore running user motion code after succsessful track.
        USER_MOTION_CODE_ON = False
else:
    print("WARN : import Failed. File Not Found %s" % userMotionFilePath)
    USER_MOTION_CODE_ON = False

# Import Settings from specified plugin if PLUGIN_ENABLE_ON=True
if PLUGIN_ENABLE_ON:  # Check and verify plugin and load variable overlay
    pluginDir = os.path.join(baseDir, "plugins")
    # Check if there is a .py at the end of PLUGIN_NAME variable
    if PLUGIN_NAME.endswith(".py"):
        PLUGIN_NAME = PLUGIN_NAME[:-3]  # Remove .py extensiion
    pluginPath = os.path.join(pluginDir, PLUGIN_NAME + ".py")
    logging.info("pluginEnabled %s", pluginPath)
    if not os.path.isdir(pluginDir):
        logging.error("plugin Directory Not Found at %s", pluginDir)
        logging.info("Rerun github curl install script to install plugins")
        logging.info("https://github.com/pageauc/pi-timolo/wiki/")
        logging.info("How-to-Install-or-Upgrade#quick-install")
        logging.warning("%s %s Exiting Due to Error", PROG_NAME, PROG_VER)
        sys.exit(1)
    elif not os.path.exists(pluginPath):
        logging.error("Plugin File Not Found %s", pluginPath)
        logging.info("Check Spelling of PLUGIN_NAME Value in %s", configFilePath)
        logging.info("------- Valid Names -------")
        validPlugin = glob.glob(pluginDir + "/*py")
        validPlugin.sort()
        for entry in validPlugin:
            pluginFile = os.path.basename(entry)
            plugin = pluginFile.rsplit(".", 1)[0]
            if not ((plugin == "__init__") or (plugin == "current")):
                logging.info("        %s", plugin)
        logging.info("------- End of List -------")
        logging.info("        Note: PLUGIN_NAME Should Not have .py Ending.")
        logging.info("or Rerun github curl install command.  See github wiki")
        logging.info("https://github.com/pageauc/speed-camera/wiki/")
        logging.info("How-to-Install-or-Upgrade#quick-install")
        logging.warning("%s %s Exiting Due to Error", PROG_NAME, PROG_VER)
        sys.exit(1)
    else:
        pluginCurrent = os.path.join(pluginDir, "current.py")
        try:  # Copy image file to recent folder
            logging.info("Copy %s to %s", pluginPath, pluginCurrent)
            shutil.copy(pluginPath, pluginCurrent)
        except OSError as err:
            logging.error("Copy Failed %s to %s - %s", pluginPath, pluginCurrent, err)
            logging.info("Check permissions, disk space, Etc.")
            logging.warning("%s %s Exiting Due to Error", PROG_NAME, PROG_VER)
            sys.exit(1)
        # add plugin directory to program PATH
        sys.path.insert(0, pluginDir)
        try:
            from plugins.current import *
        except Exception as err_msg:
            logging.warning("%s" % err_msg)

CAMERA_WIDTH, CAMERA_HEIGHT = IM_SIZE
# fix possible invalid values when resizing
if CV_WINDOW_BIGGER < 0.1:
    CV_WINDOW_BIGGER = 0.1
if IM_BIGGER < 0.1:
    IM_BIGGER = 0.1

# Calculate conversion from camera pixel width to actual speed.
CONV_KPH_2_MPH = 0.621371       # conversion from KPH to MPH
CONV_MM_PER_SEC_2_KPH = 0.0036  # conversion from MM/sec to KPH
px_to_kph_L2R = float(CAL_OBJ_MM_L2R / CAL_OBJ_PX_L2R * CONV_MM_PER_SEC_2_KPH)
px_to_kph_R2L = float(CAL_OBJ_MM_R2L / CAL_OBJ_PX_R2L * CONV_MM_PER_SEC_2_KPH)
if MO_SPEED_MPH_ON:
    speed_units = "mph"
    speed_conv_L2R = CONV_KPH_2_MPH * px_to_kph_L2R
    speed_conv_R2L = CONV_KPH_2_MPH * px_to_kph_R2L
else:
    speed_units = "kph"
    speed_conv_L2R = px_to_kph_L2R
    speed_conv_R2L = px_to_kph_R2L

# path to alignment camera image
align_filename = os.path.join(IM_RECENT_DIR_PATH, "align_cam.jpg")
speed_CSV_filepath = os.path.join(baseDir, baseFileName + ".csv")
AI_CSV_filepath = os.path.join(baseDir, "ai_pos_data.csv")

# ------------------------------------------------------------------------------
def show_config(filename):
    '''
    Display program configuration variable settings
    read config file and print each decoded line
    '''
    print("")
    logging.info("Reading settings per %s", configFilePath)
    with open(filename, 'rb') as f:
        for line in f:
            print(line.decode().strip())
    if PLUGIN_ENABLE_ON:
        logging.warning("Some Settings Above will be changed by Plugin %s", PLUGIN_NAME)


# ------------------------------------------------------------------------------
def get_fps(start_time, frame_count):
    """
    Calculate and display frames per second processing
    """
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
def is_daytime(image, threshold):
    """
    Calculate the mean pixel average value for a grayimage
    used for determining if it is day or night. Bright enough to save image.
    """
    day = False
    grayimage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    pix_ave = int(np.mean(grayimage))
    if pix_ave >= threshold:
        day = True
    return day


# ------------------------------------------------------------------------------
def timer_is_on(sched_time):
    """
    Based on schedule date setting see if current
    datetime is past and return boolean
    to indicate timer is off
    """
    is_on = True
    if sched_time <= datetime.datetime.now():
        is_on = False  # sched date/time has passed so start sequence
    return is_on


# ------------------------------------------------------------------------------
def make_media_dirs():
    """
    Create media default folders per config.py settings.
    """
    cwd = os.getcwd()
    html_path = "media/html"
    if not os.path.isdir(IM_DIR_PATH):
        logging.info("Creating Image Storage Folder %s", IM_DIR_PATH)
        os.makedirs(IM_DIR_PATH)
    os.chdir(IM_DIR_PATH)
    os.chdir(cwd)
    if IM_RECENT_MAX_FILES > 0:
        if not os.path.isdir(IM_RECENT_DIR_PATH):
            logging.info("Create Recent Folder %s", IM_RECENT_DIR_PATH)
            try:
                os.makedirs(IM_RECENT_DIR_PATH)
            except OSError as err:
                logging.error("Failed to Create Folder %s - %s", IM_RECENT_DIR_PATH, err)
    if not os.path.isdir(search_dest_path):
        logging.info("Creating Search Folder %s", search_dest_path)
        os.makedirs(search_dest_path)
    if not os.path.isdir(html_path):
        logging.info("Creating html Folder %s", html_path)
        os.makedirs(html_path)
    if IM_SAVE_4AI_ON and not os.path.isdir(IM_SAVE_4AI_POS_DIR):
        os.makedirs(IM_SAVE_4AI_POS_DIR)
    if IM_SAVE_4AI_ON and not os.path.isdir(IM_SAVE_4AI_NEG_DIR):
        os.makedirs(IM_SAVE_4AI_NEG_DIR)
    os.chdir(cwd)


# ------------------------------------------------------------------------------
def show_settings():
    """
    Display formatted program variable settings from config.py
    """
    if LOG_VERBOSE_ON:
        print(HORIZ_LINE)
        print("Note: To Send Full Output to File Use command")
        print("python -u ./%s | tee -a log.txt" % PROG_NAME)
        print(
            "Set log_data_to_file=True to Send speed_Data to CSV File %s.log"
            % baseFileName
        )
        print(HORIZ_LINE)
        print("")
        print(
            "Debug Messages .. LOG_VERBOSE_ON=%s  LOG_FPS_ON=%s CALIBRATE_ON=%s"
            % (LOG_VERBOSE_ON, LOG_FPS_ON, CALIBRATE_ON)
        )
        print("                  MO_LOG_OUT_RANGE_ON=%s" % MO_LOG_OUT_RANGE_ON)
        print(
            "Plugins ......... PLUGIN_ENABLE_ON=%s  PLUGIN_NAME=%s"
            % (PLUGIN_ENABLE_ON, PLUGIN_NAME)
        )
        print(
            "Calibration ..... CAL_OBJ_PX_L2R=%i px  CAL_OBJ_MM_L2R=%i mm  speed_conv_L2R=%.5f"
            % (CAL_OBJ_PX_L2R, CAL_OBJ_MM_L2R, speed_conv_L2R)
        )
        print(
            "                  CAL_OBJ_PX_R2L=%i px  CAL_OBJ_MM_R2L=%i mm  speed_conv_R2L=%.5f"
            % (CAL_OBJ_PX_R2L, CAL_OBJ_MM_R2L, speed_conv_R2L)
        )
        if PLUGIN_ENABLE_ON:
            print("                  (Change Settings in %s)" % pluginPath)
        else:
            print("                  (Change Settings in %s)" % configFilePath)
        print(
            "Logging ......... Log_data_to_CSV=%s  log_filename=%s.csv (CSV format)"
            % (LOG_DATA_TO_CSV, baseFileName)
        )
        print(
            "                  LOG_TO_FILE_ON=%s  LOG_FILE_PATH=%s"
            % (LOG_TO_FILE_ON, LOG_FILE_PATH)
        )
        print("                  SQLITE3 DB_PATH=%s  DB_TABLE=%s" % (DB_PATH, DB_TABLE))
        print(
            "Speed Trigger ... Log only if MO_MAX_SPEED_OVER > %i %s"
            % (MO_MAX_SPEED_OVER, speed_units)
        )
        print(
            "                  and MO_TRACK_EVENT_COUNT >= %i consecutive motion events"
            % MO_TRACK_EVENT_COUNT
        )
        print(
            "Exclude Events .. If  MO_MIN_X_DIFF_PX < %i or MO_MAX_X_DIFF_PX > %i px"
            % (MO_MIN_X_DIFF_PX, MO_MAX_X_DIFF_PX)
        )
        print(
            "                  If  MO_CROP_Y_UPPER < %i or MO_CROP_Y_LOWER > %i px" % (MO_CROP_Y_UPPER, MO_CROP_Y_LOWER)
        )
        print(
            "                  or  MO_CROP_X_LEFT < %i or MO_CROP_X_RIGHT > %i px" % (MO_CROP_X_LEFT, MO_CROP_X_RIGHT)
        )
        print(
            "                  If  MO_MAX_SPEED_OVER < %i %s"
            % (MO_MAX_SPEED_OVER, speed_units)
        )
        print(
            "                  If  MO_EVENT_TIMEOUT_SEC > %.2f seconds Start New Track"
            % (MO_EVENT_TIMEOUT_SEC)
        )
        print(
            "                  MO_TRACK_TIMEOUT_SEC=%.2f sec wait after Track Ends"
            " (avoid retrack of same object)" % (MO_TRACK_TIMEOUT_SEC)
        )
        print(
            "Speed Photo ..... Size=%ix%i px  IM_BIGGER=%.1f"
            "  rotation=%i  VFlip=%s  HFlip=%s "
            % (
                image_width,
                image_height,
                IM_BIGGER,
                IM_ROTATION,
                IM_VFLIP,
                IM_HFLIP,
            )
        )
        print(
            "                  IM_DIR_PATH=%s  image_Prefix=%s"
            % (IM_DIR_PATH, IM_PREFIX)
        )
        print(
            "                  IM_FONT_SIZE_PX=%i px high  IM_SHOW_TEXT_BOTTOM_ON=%s"
            % (IM_FONT_SIZE_PX, IM_SHOW_TEXT_BOTTOM_ON)
        )
        print(
            "                  IM_JPG_QUALITY=%s  IM_JPG_OPTIMIZE_ON=%s"
            % (IM_JPG_QUALITY, IM_JPG_OPTIMIZE_ON)
        )
        print(
            "Motion Settings . Size=%ix%i px  px_to_kph_L2R=%f  px_to_kph_R2L=%f speed_units=%s"
            % (CAMERA_WIDTH, CAMERA_HEIGHT, px_to_kph_L2R, px_to_kph_R2L, speed_units)
        )
        print("                  CAM_LOCATION= %s" % CAM_LOCATION)
        print(
            "OpenCV Settings . MO_MIN_AREA_PX=%i sq-px  BLUR_SIZE=%i"
            "  THRESHOLD_SENSITIVITY=%i  CV_CIRCLE_SIZE_PX=%i px"
            % (MO_MIN_AREA_PX, BLUR_SIZE, THRESHOLD_SENSITIVITY, CV_CIRCLE_SIZE_PX)
        )
        print(
            "                  CV_WINDOW_BIGGER=%d GUI_WINDOW_ON=%s"
            " (Display OpenCV Status Windows on GUI Desktop)"
            % (CV_WINDOW_BIGGER, GUI_WINDOW_ON)
        )
        print(
            "                  IM_FRAMERATE=%i fps video stream speed"
            % IM_FRAMERATE
        )
        print(
            "Sub-Directories . IM_SUBDIR_MAX_HOURS=%i (0=off)"
            "  IM_SUBDIR_MAX_FILES=%i (0=off)"
            % (IM_SUBDIR_MAX_HOURS, IM_SUBDIR_MAX_FILES)
        )
        print(
            "                  IM_RECENT_DIR_PATH=%s IM_RECENT_MAX_FILES=%i (0=off)"
            % (IM_RECENT_DIR_PATH, IM_RECENT_MAX_FILES)
        )
        if SPACE_TIMER_HRS > 0:  # Check if disk mgmnt is enabled
            print(
                "Disk Space  ..... Enabled - Manage Target Free Disk Space."
                " Delete Oldest %s Files if Needed" % (SPACE_FILE_EXT)
            )
            print(
                "                  Check Every SPACE_TIMER_HRS=%i hr(s) (0=off)"
                "  Target SPACE_FREE_MB=%i MB  min is 100 MB)"
                % (SPACE_TIMER_HRS, SPACE_FREE_MB)
            )
            print(
                "                  If Needed Delete Oldest SPACE_FILE_EXT=%s  SPACE_MEDIA_DIR=%s"
                % (SPACE_FILE_EXT, SPACE_MEDIA_DIR)
            )
        else:
            print(
                "Disk Space  ..... Disabled - SPACE_TIMER_HRS=%i"
                "  Manage Target Free Disk Space. Delete Oldest %s Files"
                % (SPACE_TIMER_HRS, SPACE_FILE_EXT)
            )
            print(
                "                  SPACE_TIMER_HRS=%i (0=Off)"
                " Target SPACE_FREE_MB=%i (min=100 MB)" % (SPACE_TIMER_HRS, SPACE_FREE_MB)
            )
        print("")
        print(HORIZ_LINE)
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
        cv2.line(cal_image, (i, MO_CROP_Y_UPPER - 5), (i, MO_CROP_Y_UPPER + 30), hash_color, 1)
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
        "  2 - For objects moving L2R Record CAL_OBJ_PX_L2R Value Using Red MO_CROP_Y_UPPER Hash Marks at every 10 px  Current Setting is %i px"
        % CAL_OBJ_PX_L2R
    )
    print(
        "  3 - Record CAL_OBJ_MM_L2R of object. This is Actual length in mm of object above Current Setting is %i mm"
        % CAL_OBJ_MM_L2R
    )
    print(
        "      If Recorded Speed %.1f %s is Too Low, Increasing CAL_OBJ_MM_L2R to Adjust or Visa-Versa"
        % (speed, speed_units)
    )
    print(
        "Repeat Calibration with same object moving R2L and update config.py R2L variables"
    )
    print("CAL_OBJ_MM_R2L and CAL_OBJ_PX_R2L accordingly")
    if PLUGIN_ENABLE_ON:
        print("  4 - Edit %s File and Change Values for Above Variables." % pluginPath)
    else:
        print(
            "  4 - Edit %s File and Change Values for the Above Variables."
            % configFilePath
        )
    print("  5 - Do a Speed Test to Confirm/Tune Settings.  You May Need to Repeat.")
    print(
        "  6 - When Calibration is Finished, Set config.py Variable  CALIBRATE_ON = False"
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
def subdir_latest(directory):
    """
    Scan for directories and return most recent
    """
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
def subdir_create(directory, prefix):
    """
    Create media subdirectories base on required naming
    """
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
def delete_old_files(maxFiles, dirPath, prefix):
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
def subdir_check_max_files(directory, filesMax):
    """
    Count number of files in a folder path
    """
    fileList = glob.glob(directory + "/*")
    count = len(fileList)
    if count > filesMax:
        makeNewDir = True
        logging.info("Total Files in %s Exceeds %i ", directory, filesMax)
    else:
        makeNewDir = False
    return makeNewDir


# ------------------------------------------------------------------------------
def subdir_check_max_hrs(directory, hrsMax, prefix):
    """
    Rxtract the date-time from the directory name
    """
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
def subdir_checks(maxHours, maxFiles, directory, prefix):
    """
    Check if motion SubDir needs to be created
    """
    if maxHours < 1 and maxFiles < 1:  # No Checks required
        # logging.info('No sub-folders Required in %s', directory)
        subDirPath = directory
    else:
        subDirPath = subdir_latest(directory)
        if subDirPath == directory:  # No subDir Found
            logging.info("No sub folders Found in %s", directory)
            subDirPath = subdir_create(directory, prefix)
        elif maxHours > 0 and maxFiles < 1:  # Check MaxHours Folder Age Only
            if subdir_check_max_hrs(subDirPath, maxHours, prefix):
                subDirPath = subdir_create(directory, prefix)
        elif maxHours < 1 and maxFiles > 0:  # Check Max Files Only
            if subdir_check_max_files(subDirPath, maxFiles):
                subDirPath = subdir_create(directory, prefix)
        elif maxHours > 0 and maxFiles > 0:  # Check both Max Files and Age
            if subdir_check_max_hrs(subDirPath, maxHours, prefix):
                if subdir_check_max_files(subDirPath, maxFiles):
                    subDirPath = subdir_create(directory, prefix)
                else:
                    logging.info("MaxFiles Not Exceeded in %s", subDirPath)
    os.path.abspath(subDirPath)
    return subDirPath


# ------------------------------------------------------------------------------
def files_to_delete(mediaDirPath, extension=IM_FORMAT_EXT):
    """
    Return a list of files to be deleted
    """
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
def make_rel_symlink(sourceFilenamePath, symDestDir):
    '''
    Creates a relative symlink in the specified symDestDir
    that points to the Target file via a relative rather than
    absolute path. If a symlink already exists it will be replaced.
    Warning message will be displayed if symlink path is a file
    rather than an existing symlink.
    '''
    # Initialize target and symlink file paths
    targetDirPath = os.path.dirname(sourceFilenamePath)
    srcfilename = os.path.basename(sourceFilenamePath)
    symDestFilePath = os.path.join(symDestDir, srcfilename)
    # Check if symlink already exists and unlink if required.
    if os.path.islink(symDestFilePath):
        logging.info("Remove Existing Symlink at %s ", symDestFilePath)
        os.unlink(symDestFilePath)
    # Check if symlink path is a file rather than a symlink. Error out if required
    if os.path.isfile(symDestFilePath):
        logging.warning("Failed. File Exists at %s.", symDestFilePath)
        return

    # Initialize required entries for creating a relative symlink to target file
    absTargetDirPath = os.path.abspath(targetDirPath)
    absSymDirPath = os.path.abspath(symDestDir)
    relativeDirPath = os.path.relpath(absTargetDirPath, absSymDirPath)
    # Initialize relative symlink entries to target file.

    symFilePath = os.path.join(relativeDirPath, srcfilename)
    # logging.info("ln -s %s %s ", symFilePath, symDestFilePath)
    os.symlink(symFilePath, symDestFilePath)  # Create the symlink
    # Check if symlink was created successfully
    if os.path.islink(symDestFilePath):
        logging.info("Saved at %s", symDestFilePath)
    else:
        logging.warning("Failed to Create Symlink at %s", symDestFilePath)


# ------------------------------------------------------------------------------
def save_recent(recentMax, recentDir, filepath, prefix):
    """
    Create a symlink file in recent folder or file if non unix system
    or symlink creation fails.
    Delete Oldest symlink file if recentMax exceeded.
    """
    if recentMax > 0:
        delete_old_files(recentMax, os.path.abspath(recentDir), prefix)
        try:
            make_rel_symlink(filepath, recentDir)
        except OSError as err:
            logging.error("symlink Failed: %s", err)
            try:  # Copy image file to recent folder (if no support for symlinks)
                shutil.copy(filepath, recentDir)
                logging.info("Saved %s to %s", filepath, recentDir)
            except OSError as err:
                logging.error("Copy Failed %s to %s - %s", filepath, recentDir, err)


# ------------------------------------------------------------------------------
def free_disk_space_upto(freeMB, mediaDir, extension=IM_FORMAT_EXT):
    """
    Walks mediaDir and deletes oldest files
    until SPACE_FREE_MB is achieved Use with Caution
    """
    mediaDirPath = os.path.abspath(mediaDir)
    if os.path.isdir(mediaDirPath):
        MB2Bytes = 1048576  # Conversion from MB to Bytes
        targetFreeBytes = freeMB * MB2Bytes
        fileList = files_to_delete(mediaDir, extension)
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
def free_disk_space_check(lastSpaceCheck):
    """
    Free disk space by deleting some older files
    """
    if SPACE_TIMER_HRS > 0:  # Check if disk free space timer hours is enabled
        # See if it is time to do disk clean-up check
        if (
            datetime.datetime.now() - lastSpaceCheck
        ).total_seconds() > SPACE_TIMER_HRS * 3600:
            lastSpaceCheck = datetime.datetime.now()
            # Set freeSpaceMB to reasonable value if too low
            if SPACE_FREE_MB < 100:
                diskFreeMB = 100
            else:
                diskFreeMB = SPACE_FREE_MB
            logging.info(
                "SPACE_TIMER_HRS=%i  diskFreeMB=%i  SPACE_MEDIA_DIR=%s SPACE_FILE_EXT=%s",
                SPACE_TIMER_HRS,
                diskFreeMB,
                SPACE_MEDIA_DIR,
                SPACE_FILE_EXT,
            )
            free_disk_space_upto(diskFreeMB, SPACE_MEDIA_DIR, SPACE_FILE_EXT)
    return lastSpaceCheck


# ------------------------------------------------------------------------------
def get_image_name(path, prefix):
    """
    build image file names by number sequence or
    date/time Added tenth of second
    """
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
def log_to_csv(csv_file_path, data_to_append):
    """
    Store date to a comma separated value file
    """
    if not os.path.exists(csv_file_path):
        open(csv_file_path, "w").close()
        f = open(csv_file_path, "ab")
        f.close()
        logging.info("Create New Data Log File %s", csv_file_path)
    filecontents = data_to_append + "\n"
    f = open(csv_file_path, "a+")
    f.write(filecontents)
    f.close()
    logging.info("   CSV - Appended Data into %s", csv_file_path)
    return


# ------------------------------------------------------------------------------
def is_SQLite3(filename):
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
    if is_SQLite3(db_file):
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
def get_motion_contours(grayimage1):
    """
    Read a Camera stream image frame, crop and
    get diff of two cropped greyscale images.
    Use opencv to detect motion contours.
    Added timeout in case camera has a problem.
    Eg. Network problem with RTSP cam
    """
    image_ok = False
    start_time = time.time()
    timeout = 60  # seconds to wait if camera communications is lost eg network stream.
                  # Note to self.  Look at adding setting to config.py
    global differenceimage

    while not image_ok:
        image = vs.read()  # Read image data from video steam thread instance
        # crop image to motion tracking area only
        try:
            image_crop = image[MO_CROP_Y_UPPER:MO_CROP_Y_LOWER, MO_CROP_X_LEFT:MO_CROP_X_RIGHT]
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
    differenceimage = cv2.absdiff(grayimage1, grayimage2)
    # Blur difference image to enhance motion vectors
    differenceimage = cv2.blur(differenceimage, (BLUR_SIZE, BLUR_SIZE))
    # Get threshold of blurred difference image
    # based on THRESHOLD_SENSITIVITY variable
    retval, thresholdimage = cv2.threshold(
        differenceimage, THRESHOLD_SENSITIVITY, 255, cv2.THRESH_BINARY
    )
    try:
        # opencv 3 syntax default
        contours, hierarchy = cv2.findContours(
            thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
    except ValueError:
        # opencv 2 syntax
        thresholdimage, contours, hierarchy = cv2.findContours(
            thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
    return image, grayimage2, contours


# ------------------------------------------------------------------------------
def get_biggest_contour(contours):
    """
    Process contours and return biggest if found
    within rect of interest
    """
    motion_found = False
    biggest_contour = []
    # if contours found, find the one with biggest area
    if contours:
        biggest_area = MO_MIN_AREA_PX
        for c in contours:
            # get area of contour
            found_area = cv2.contourArea(c)
            if found_area > biggest_area:
                cur_contour = cv2.boundingRect(c)
                (x, y, w, h) = cur_contour
                # check if object contour is completely within crop area
                if x > x_buf and x + w < MO_CROP_X_RIGHT - MO_CROP_X_LEFT - x_buf:
                    biggest_contour = cur_contour
                    motion_found = True
                    biggest_area = found_area
    return motion_found, biggest_contour


# ------------------------------------------------------------------------------
def speed_image_add_lines(image, color):
    """
    Draw lines on image to show crop rectangle tracking area
    """
    cv2.line(image, (MO_CROP_X_LEFT, MO_CROP_Y_UPPER), (MO_CROP_X_RIGHT, MO_CROP_Y_UPPER), color, 1)
    cv2.line(image, (MO_CROP_X_LEFT, MO_CROP_Y_LOWER), (MO_CROP_X_RIGHT, MO_CROP_Y_LOWER), color, 1)
    cv2.line(image, (MO_CROP_X_LEFT, MO_CROP_Y_UPPER), (MO_CROP_X_LEFT, MO_CROP_Y_LOWER), color, 1)
    cv2.line(image, (MO_CROP_X_RIGHT, MO_CROP_Y_UPPER), (MO_CROP_X_RIGHT, MO_CROP_Y_LOWER), color, 1)
    return image


# ------------------------------------------------------------------------------
def speed_notify():
    """
    Display information log messages at start of motion tracking loop
    """
    if PLUGIN_ENABLE_ON:
        logging.info("Plugin Enabled per PLUGIN_NAME=%s", PLUGIN_NAME)
    else:
        logging.info("Plugin Disabled per PLUGIN_ENABLE_ON=%s", PLUGIN_ENABLE_ON)

    if CALIBRATE_ON:
        logging.warning("IMPORTANT: Camera Is In Calibration Mode ....")
    if ALIGN_CAM_ON:
        logging.warning("IMPORTANT: Camera is in Alignment Mode ....")
    else:
        if os.path.isfile(align_filename):
            os.remove(align_filename)
            logging.info("Removed camera alignment image at %s", align_filename)
    logging.info("%s video stream size is %i x %i", CAMERA.upper(), img_width, img_height)
    logging.info("Resized Photos after IM_BIGGER=%.2f is %i x %i", IM_BIGGER, image_width, image_height)


# ------------------------------------------------------------------------------
def speed_camera():
    """
    Main speed camera loop processing function
    """
    if SHOW_SETTINGS_ON:
        # show_config(configFilePath)
        show_settings()  # Show variable settings

    # initialize variables and settings
    ave_speed = 0.0
    # initialize variables
    frame_count = 0   # used for FPS calculation
    fps_time = time.time()
    first_event = True  # Start a New Motion Track
    start_pos_x = None
    end_pos_x = None
    prev_pos_x = None
    travel_direction = None
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Calculate position of text on the images
    if IM_SHOW_TEXT_BOTTOM_ON:
        text_y = image_height - 50  # show text at bottom of image
    else:
        text_y = 10  # show text at top of image

    lastSpaceCheck = datetime.datetime.now()
    speed_path = IM_DIR_PATH

    # check and open sqlite3 db
    db_conn = db_check(DB_PATH)
    if db_conn is not None:
        db_conn = db_open(DB_PATH)
        if db_conn is None:
            logging.error("Failed: Connect to sqlite3 DB %s", DB_PATH)
        else:
            logging.info("sqlite3 DB is Open %s", DB_PATH)
            db_cur = db_conn.cursor()  # Set cursor position
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

    # initialize a cropped grayimage1 image
    image2 = vs.read()  # Get image from VideoSteam thread instance
    try:
        # crop image to motion tracking area only
        image_crop = image2[MO_CROP_Y_UPPER:MO_CROP_Y_LOWER, MO_CROP_X_LEFT:MO_CROP_X_RIGHT]
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
    image_sign_bg = np.zeros((IM_SIGN_RESIZE[0], IM_SIGN_RESIZE[1], 4))
    image_sign_view = cv2.resize(image_sign_bg, (IM_SIGN_RESIZE))
    image_sign_view_time = time.time()

    if LOG_VERBOSE_ON:
        if LOG_TO_FILE_ON:
            print("Logging to File %s (Console Messages Disabled)" % LOG_FILE_PATH)
        else:
            logging.info("Logging to Console per Variable LOG_VERBOSE_ON=True")
        if GUI_WINDOW_ON:
            logging.info("Press lower case q on OpenCV GUI Window to Quit program")
            logging.info("        or ctrl-c in this terminal session to Quit")
        else:
            logging.info("Press ctrl-c in this terminal session to Quit")
    else:
        print("Logging Messages Disabled per LOG_VERBOSE_ON=%s" % LOG_VERBOSE_ON)

    mo_track_timeout = datetime.datetime.now()
    ai_neg_time_on = datetime.datetime.now()
    print(HORIZ_LINE)
    logging.info("Begin Motion Tracking .....")
    # Start main speed camera loop
    still_scanning = True
    while still_scanning:
        cur_track_time = time.time() # record event time.  Used for speed calc
        # Detect motion snd return latest image, cropped greyscale and
        # All motion contours
        image2, grayimage1, contours = get_motion_contours(grayimage1)
        # If contours found, returns the one with biggest area GT MO_MIN_AREA_PX
        motion_found, big_contour = get_biggest_contour(contours)

        # Keep camera running while waiting for timer to expire per MO_TRACK_TIMEOUT_SEC
        if timer_is_on(mo_track_timeout):
            continue

        if GUI_WINDOW_ON or ALIGN_CAM_ON or CALIBRATE_ON:
            image2_copy = image2  # make a copy of current image2 when needed

        if not motion_found:
            if IM_SAVE_4AI_ON and not timer_is_on(ai_neg_time_on):
                if is_daytime(image2, IM_SAVE_4AI_DAY_THRESH):
                    AI_neg_filename = get_image_name(IM_SAVE_4AI_NEG_DIR, IM_PREFIX)
                    logging.info(" Saved neg %s", AI_neg_filename)
                    cv2.imwrite(AI_neg_filename, image2)
                else:
                    logging.info(' Low Light - AI neg Image Not Saved IM_SAVE_4AI_DAY_THRESH = %i'
                                 % IM_SAVE_4AI_DAY_THRESH)
                ai_neg_time_on = (datetime.datetime.now() +
                                  datetime.timedelta(seconds=IM_SAVE_4AI_NEG_TIMER_SEC))
                logging.info(" Next AI neg image in %.2f hours",
                              float(IM_SAVE_4AI_NEG_TIMER_SEC / 3600))

        else:   # Motion Found
            (track_x, track_y, track_w, track_h) = big_contour
            total_contours = len(contours)
            biggest_area = int(track_w * track_h)
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
                    MO_TRACK_EVENT_COUNT,
                    track_x,
                    track_y,
                )
                event_timer = time.time()  # Reset event timeout
                track_count = 0
                speed_list = []
                if IM_FIRST_AND_LAST_ON:
                    mo_im_first = image2
                continue
            else:
                # Check if last motion event timed out
                reset_time_diff = time.time() - event_timer
                if reset_time_diff >= MO_EVENT_TIMEOUT_SEC:
                    # event_timer exceeded so reset for new track
                    event_timer = time.time()
                    first_event = True
                    logging.info(
                        "Reset- event_timer %.2f>%.2f sec Exceeded",
                        reset_time_diff,
                        MO_EVENT_TIMEOUT_SEC,
                    )
                    print(HORIZ_LINE)
                    continue
                prev_pos_x = end_pos_x
                end_pos_x = track_x

                # set calibration for direction of travel
                if end_pos_x - start_pos_x > 0:
                    travel_direction = "L2R"
                    cal_obj_px = CAL_OBJ_PX_L2R
                    cal_obj_mm = CAL_OBJ_MM_L2R
                else:
                    travel_direction = "R2L"
                    cal_obj_px = CAL_OBJ_PX_R2L
                    cal_obj_mm = CAL_OBJ_MM_R2L

                # check if movement is within acceptable distance
                # range of last event
                if (abs(end_pos_x - prev_pos_x) >= MO_MIN_X_DIFF_PX and
                    abs(end_pos_x - prev_pos_x) <= MO_MAX_X_DIFF_PX):
                    cur_track_dist = abs(end_pos_x - prev_pos_x)
                    try:
                        if travel_direction == "L2R":
                            cur_ave_speed = float(
                                abs(cur_track_dist / float(abs(cur_track_time - prev_start_time)))
                                * speed_conv_L2R)
                        else:
                            cur_ave_speed = float(
                                abs(cur_track_dist / float( abs(cur_track_time - prev_start_time)))
                                * speed_conv_R2L)
                    except ZeroDivisionError:  # This sometimes happens on windows due to clock precision issue
                        logging.warning(
                            "Division by Zero Error. Aborting this track event."
                        )
                        event_timer = time.time() # reset event timer
                        continue
                    track_count += 1  # increment track counter
                    speed_list.append(cur_ave_speed)
                    ave_speed = np.median(speed_list)  # Cslculate the median ave speed
                    prev_start_time = cur_track_time
                    event_timer = time.time()

                    # check if trscking is complete
                    if track_count >= MO_TRACK_EVENT_COUNT:
                        tot_track_dist = abs(track_x - start_pos_x)
                        tot_track_time = abs(track_start_time - cur_track_time)
                        if IM_FIRST_AND_LAST_ON or IM_SAVE_4AI_ON:
                            mo_im_last = image2
                        if ave_speed > MO_MAX_SPEED_OVER or CALIBRATE_ON:
                            logging.info(
                                " Add - %i/%i xy(%i,%i) %3.2f %s"
                                " D=%i/%i C=%i %ix%i=%i sqpx %s",
                                track_count,
                                MO_TRACK_EVENT_COUNT,
                                track_x,
                                track_y,
                                ave_speed,
                                speed_units,
                                abs(track_x - prev_pos_x),
                                MO_MAX_X_DIFF_PX,
                                total_contours,
                                track_w,
                                track_h,
                                biggest_area,
                                travel_direction,
                            )
                            # Resize and process previous image
                            # before saving to disk
                            # Create a calibration image file name
                            # There are no subdirectories to deal with
                            if CALIBRATE_ON:
                                log_time = datetime.datetime.now()
                                filename = get_image_name(speed_path, "calib-")
                                image2 = take_calibration_image(ave_speed, filename, image2_copy)
                            else:
                                # Check if subdirectories configured
                                # and create new subdirectory if required
                                speed_path = subdir_checks(
                                    IM_SUBDIR_MAX_HOURS,
                                    IM_SUBDIR_MAX_FILES,
                                    IM_DIR_PATH,
                                    IM_PREFIX,
                                )

                                # Record log_time for use later in csv and sqlite
                                log_time = datetime.datetime.now()
                                # Create image file name
                                if IM_SHOW_SPEED_FILENAME_ON:
                                    # add ave_speed value to filename after prefix
                                    speed_prefix = (
                                        IM_PREFIX
                                        + str(int(round(ave_speed)))
                                        + "-"
                                    )
                                    filename = get_image_name(
                                        speed_path, speed_prefix
                                    )
                                else:
                                    # create image file name path
                                    filename = get_image_name(
                                        speed_path, IM_PREFIX
                                    )

                            # Add motion rectangle to image if required
                            if IM_SHOW_CROP_AREA_ON:
                                image2 = speed_image_add_lines(image2, cvRed)
                                # show centre of motion if required
                                if CV_SHOW_CIRCLE_ON:
                                    cv2.circle(
                                        image2,
                                        (track_x + MO_CROP_X_LEFT, track_y + MO_CROP_Y_UPPER),
                                        CV_CIRCLE_SIZE_PX,
                                        cvGreen,
                                        CV_LINE_WIDTH_PX,
                                    )
                                else:
                                    cv2.rectangle(
                                        image2,
                                        (
                                        int(track_x + MO_CROP_X_LEFT),
                                        int(track_y + MO_CROP_Y_UPPER),
                                        ),
                                        (
                                        int(track_x + MO_CROP_X_LEFT + track_w),
                                        int(track_y + MO_CROP_Y_UPPER + track_h),
                                        ),
                                        cvGreen,
                                        CV_LINE_WIDTH_PX,
                                        )
                            big_image = cv2.resize(image2, (image_width, image_height ))
                            if IM_SHOW_SIGN_ON:
                                image_sign_view_time = time.time()
                                image_sign_bg = np.zeros(
                                    (IM_SIGN_RESIZE[0], IM_SIGN_RESIZE[1], 4)
                                )
                                image_sign_view = cv2.resize(
                                    image_sign_bg, (IM_SIGN_RESIZE)
                                )
                                image_sign_text = str(int(round(ave_speed, 0)))
                                cv2.putText(
                                    image_sign_view,
                                    image_sign_text,
                                    IM_SIGN_TEXT_XY,
                                    font,
                                    IM_SIGN_FONT_SCALE,
                                    IM_SIGN_FONT_COLOR,
                                    IM_SIGN_FONT_THICK_PX,
                                )

                            # Write text on image before saving
                            # if required.
                            if IM_SHOW_TEXT_ON:
                                image_text = "SPEED %.1f %s - %s" % (
                                    ave_speed,
                                    speed_units,
                                    filename,
                                )
                                text_x = int(
                                    (image_width / 2)
                                    - (len(image_text) * IM_FONT_SIZE_PX / 3)
                                )
                                if text_x < 2:
                                    text_x = 2
                                cv2.putText(
                                    big_image,
                                    image_text,
                                    (text_x, text_y),
                                    font,
                                    IM_FONT_SCALE,
                                    IM_FONT_COLOR,
                                    IM_FONT_THICKNESS,
                                )

                            # Save resized image. If jpg format, user can customize image quality 1-100 (higher is better)
                            # and/or enble/disable optimization per config.py settings.
                            # otherwise if png, bmp, gif, etc normal image write will occur
                            logging.info(" Saved %ix%i %s", image_width, image_height, filename)
                            if ((IM_FORMAT_EXT.lower() == ".jpg" or IM_FORMAT_EXT.lower() == ".jpeg")
                                 and IM_JPG_OPTIMIZE_ON):
                                try:
                                    cv2.imwrite(filename, big_image,
                                                [ int(cv2.IMWRITE_JPEG_QUALITY), IM_JPG_QUALITY,
                                                  int(cv2.IMWRITE_JPEG_OPTIMIZE), 1
                                                ]
                                               )
                                except:  # sometimes issue with IP camera so default to non optimized imwrite
                                    logging.warning('Problem writing optimized. Saving Normal %s', filename)
                                    cv2.imwrite(filename, big_image)
                            else:
                                cv2.imwrite(filename, big_image)

                            # Save a positive AI motion image for later processing
                            # make sure there is enough light for a clear image.
                            if IM_SAVE_4AI_ON:
                                if is_daytime(mo_im_last, IM_SAVE_4AI_DAY_THRESH):
                                    AI_pos_filename = get_image_name(IM_SAVE_4AI_POS_DIR, IM_PREFIX)
                                    logging.info(" Saved %s", AI_pos_filename)
                                    cv2.imwrite(AI_pos_filename, mo_im_last)
                                    ai_data = ("%s, %i, %i, %i, %i" %
                                               (QUOTE + AI_pos_filename + QUOTE,
                                               MO_CROP_X_LEFT + track_x,
                                               MO_CROP_Y_UPPER + track_y,
                                               track_w, track_h))
                                    log_to_csv(AI_CSV_filepath, ai_data)
                                else:
                                    logging.info(' Low Light - AI pos Image Not Saved IM_SAVE_4AI_DAY_THRESH = %i'
                                                 % IM_SAVE_4AI_DAY_THRESH)

                            if IM_FIRST_AND_LAST_ON:
                                # Save first and last image for later AI processing
                                fn_split = os.path.splitext(filename)
                                filename_first = fn_split[0] + "_1" + fn_split[1]
                                filename_last = fn_split[0] + "_2" + fn_split[1]
                                logging.info("Saving first %s", filename_first)
                                cv2.imwrite(filename_first, mo_im_first)
                                logging.info("Saving last %s", filename_last)
                                cv2.imwrite(filename_last, mo_im_last)

                            if USER_MOTION_CODE_ON:
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
                                QUOTE,
                                log_time.year,
                                log_time.month,
                                log_time.day,
                                log_time.hour,
                                log_time.minute,
                                log_time.second,
                                QUOTE,
                            )
                            m_area = track_w * track_h

                            if PLUGIN_ENABLE_ON:
                                plugin_name = PLUGIN_NAME
                            else:
                                plugin_name = "None"

                            # create the speed data list ready for db insert
                            speed_data = (
                                log_idx,
                                log_timestamp,
                                CAMERA.upper(),
                                round(ave_speed, 2),
                                speed_units,
                                filename,
                                image_width,
                                image_height,
                                IM_BIGGER,
                                travel_direction,
                                plugin_name,
                                track_x,
                                track_y,
                                track_w,
                                track_h,
                                m_area,
                                MO_CROP_X_LEFT,
                                MO_CROP_X_RIGHT,
                                MO_CROP_Y_UPPER,
                                MO_CROP_Y_LOWER,
                                MO_MAX_SPEED_OVER,
                                MO_MIN_AREA_PX,
                                MO_TRACK_EVENT_COUNT,
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
                            if LOG_DATA_TO_CSV:
                                log_csv_time = (
                                    "%s%04d-%02d-%02d %02d:%02d:%02d%s"
                                    % (
                                        QUOTE,
                                        log_time.year,
                                        log_time.month,
                                        log_time.day,
                                        log_time.hour,
                                        log_time.minute,
                                        log_time.second,
                                        QUOTE,
                                    )
                                )
                                log_csv_text = (
                                    "%s,%.2f,%s%s%s,%s%s%s,"
                                    "%i,%i,%i,%i,%i,%s%s%s,%s,%s,%s"
                                    % (
                                        log_csv_time,
                                        ave_speed,
                                        QUOTE,
                                        speed_units,
                                        QUOTE,
                                        QUOTE,
                                        filename,
                                        QUOTE,
                                        track_x,
                                        track_y,
                                        track_w,
                                        track_h,
                                        track_w * track_h,
                                        QUOTE,
                                        travel_direction,
                                        QUOTE,
                                        QUOTE,
                                        CAM_LOCATION,
                                        QUOTE,
                                    )
                                )
                                log_to_csv(speed_CSV_filepath, log_csv_text)

                            if SPACE_TIMER_HRS > 0:
                                lastSpaceCheck = free_disk_space_check(lastSpaceCheck)

                            # Manage a maximum number of files
                            # and delete oldest if required.
                            if IM_MAX_FILES > 0:
                                delete_old_files(
                                    IM_MAX_FILES, speed_path, IM_PREFIX
                                )

                            # Save most recent files
                            # to a recent folder if required
                            if IM_RECENT_MAX_FILES > 0 and not CALIBRATE_ON:
                                save_recent(
                                    IM_RECENT_MAX_FILES,
                                    IM_RECENT_DIR_PATH,
                                    filename,
                                    IM_PREFIX,
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
                                " MO_MAX_SPEED_OVER=%i  %i px in %.3f sec"
                                " C=%i A=%i sqpx",
                                ave_speed,
                                speed_units,
                                MO_MAX_SPEED_OVER,
                                tot_track_dist,
                                tot_track_time,
                                total_contours,
                                biggest_area,
                            )
                        # Optional Wait to avoid multiple recording of same object
                        print(HORIZ_LINE)
                        if MO_TRACK_TIMEOUT_SEC > 0:
                            logging.info(
                                "MO_TRACK_TIMEOUT_SEC %0.2f sec Delay to Avoid Tracking Same Object Multiple Times."
                                % MO_TRACK_TIMEOUT_SEC
                            )
                            first_event = True  # Reset Track
                            # Set track timeout time
                            mo_track_timeout = (datetime.datetime.now() +
                                                datetime.timedelta(seconds=MO_TRACK_TIMEOUT_SEC))
                            continue  # go back to start of speed loop to idle camera
                        first_event = True
                    else:
                        logging.info(
                            " Add - %i/%i xy(%i,%i) %3.2f %s"
                            " D=%i/%i C=%i %ix%i=%i sqpx %s",
                            track_count,
                            MO_TRACK_EVENT_COUNT,
                            track_x,
                            track_y,
                            ave_speed,
                            speed_units,
                            abs(track_x - prev_pos_x),
                            MO_MAX_X_DIFF_PX,
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
                    # Check if Max px distance from prev position is greater
                    # than the MO_MAX_X_DIFF_PX setting
                    if abs(track_x - prev_pos_x) >= MO_MAX_X_DIFF_PX:
                        if MO_LOG_OUT_RANGE_ON:  # Log event if True
                            logging.info(
                                " Out - %i/%i xy(%i,%i) Max D=%i>=%ipx"
                                " C=%i %ix%i=%i sqpx %s",
                                track_count,
                                MO_TRACK_EVENT_COUNT,
                                track_x,
                                track_y,
                                abs(track_x - prev_pos_x),
                                MO_MAX_X_DIFF_PX,
                                total_contours,
                                track_w,
                                track_h,
                                biggest_area,
                                travel_direction,
                            )
                        # if track_count is LT or EQ to half MO_TRACK_EVENT_COUNT
                        if track_count <= MO_TRACK_EVENT_COUNT / 2:
                            event_timer = time.time()  # Reset Event Timer
                        else:
                            first_event = True  # start new track
                        continue  # go back to start of loop

            if GUI_WINDOW_ON:
                # show small circle at contour xy if required
                # otherwise a rectangle around most recent contour
                if CV_SHOW_CIRCLE_ON:
                    cv2.circle(
                        image2,
                        (
                            int(track_x + MO_CROP_X_LEFT * CV_WINDOW_BIGGER),
                            int(track_y + MO_CROP_Y_UPPER * CV_WINDOW_BIGGER),
                        ),
                        CV_CIRCLE_SIZE_PX,
                        cvGreen,
                        CV_LINE_WIDTH_PX,
                    )
                else:
                    cv2.rectangle(
                        image2,
                        (int(MO_CROP_X_LEFT + track_x), int(MO_CROP_Y_UPPER + track_y)),
                        (
                            int(MO_CROP_X_LEFT + track_x + track_w),
                            int(MO_CROP_Y_UPPER + track_y + track_h),
                        ),
                        cvGreen,
                        CV_LINE_WIDTH_PX,
                    )

        if ALIGN_CAM_ON:
            image2 = speed_image_add_lines(image2_copy, cvRed)
            image_align = cv2.resize(image2, (image_width, image_height))
            cv2.imwrite(align_filename, image_align)
            logging.info(
                "ALIGN_CAM_ON=%s ALIGN_DELAY_SEC=%i - Browser View Cam Align Image at %s",
                ALIGN_CAM_ON,
                ALIGN_DELAY_SEC,
                align_filename,
            )
            time.sleep(ALIGN_DELAY_SEC)

        if GUI_WINDOW_ON:
            if GUI_IMAGE_WIN_ON:
                image2 = speed_image_add_lines(image2_copy, cvRed)
                big_image = cv2.resize(image2, (image_width, image_height))
                cv2.imshow("Movement (q Quits)", big_image)

            if GUI_THRESH_WIN_ON:
                # resize and display motion threshold image
                diff_size = (int(differenceimage.shape[1] * IM_BIGGER),
                             int(differenceimage.shape[0] * IM_BIGGER))
                big_diff_image = cv2.resize(differenceimage, diff_size)
                cv2.imshow("Threshold", big_diff_image)

            if GUI_CROP_WIN_ON:
                # resize and display cropped image
                crop_image = image2[MO_CROP_Y_UPPER + CV_LINE_WIDTH_PX:MO_CROP_Y_LOWER, MO_CROP_X_LEFT + CV_LINE_WIDTH_PX:MO_CROP_X_RIGHT]
                crop_size = (int(crop_image.shape[1] * IM_BIGGER),
                             int(crop_image.shape[0] * IM_BIGGER))
                big_crop_image = cv2.resize(crop_image, crop_size)
                cv2.imshow("Crop Area", big_crop_image)

            if IM_SHOW_SIGN_ON:
                if time.time() - image_sign_view_time > IM_SIGN_TIMEOUT_SEC:
                    # Cleanup the image_sign_view
                    image_sign_bg = np.zeros(
                        (IM_SIGN_RESIZE[0], IM_SIGN_RESIZE[1], 4)
                    )
                    image_sign_view = cv2.resize(image_sign_bg, (IM_SIGN_RESIZE))
                cv2_window_speed_sign = "Last Average Speed:"
                cv2.namedWindow(cv2_window_speed_sign, cv2.WINDOW_NORMAL)
                cv2.setWindowProperty(
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

        # Optionally show fps motion image processing every 1000 loops
        if LOG_FPS_ON:
            fps_time, frame_count = get_fps(fps_time, frame_count)


# ------------------------------------------------------------------------------
if __name__ == "__main__":

    vs = strmcam()  # start video stream thread
    image1 = vs.read()
    try:
        grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    except cv2.error as err_msg:
        logging.error('%s Problem Connecting Camera. Review Log Messages and Correct', CAMERA.upper())
        logging.error(err_msg)
        logging.error('Check camera connection settings and Hardware')
        sys.exit(1)

    # Get actual image size (shape) from video stream.
    # Necessary for IP camera
    img_height, img_width, _ = image1.shape
    image_width = int(img_width * IM_BIGGER)
    # Set height of trigger point image to save
    image_height = int(img_height * IM_BIGGER)
    # Auto Calculate motion crop area settings

    if MO_CROP_AUTO_ON:
        X_SCALE = 8.0
        Y_SCALE = 4.0
        # reduce motion area for larger stream sizes
        if img_width > 1000:
            X_SCALE = 3.0
            Y_SCALE = 3.0
        # If motion box crop settings not found in config.py then
        # Auto adjust the crop image to suit the real image size.
        # For details See comments in config.py Motion Events settings section
        MO_CROP_X_LEFT = int(img_width / X_SCALE)
        MO_CROP_X_RIGHT = int(img_width - MO_CROP_X_LEFT)
        MO_CROP_Y_UPPER = int(img_height / Y_SCALE)
        MO_CROP_Y_LOWER = int(img_height - MO_CROP_Y_UPPER)
    # setup buffer area to ensure contour is mostly contained in crop area
    x_buf = int((MO_CROP_X_RIGHT - MO_CROP_X_LEFT) / MO_X_LR_SIDE_BUFF_PX)
    make_media_dirs()

    try:
        speed_camera()  # run main speed camera processing loop
    except KeyboardInterrupt:
        print("")
        logging.info("User Pressed Keyboard ctrl-c")
        # Remove temporary plugin configuration file if it exists.  plugins/current.py
        if PLUGIN_ENABLE_ON:
            logging.info("Remove Temporary plugin config Files")
            try:
                if os.path.exists(pluginCurrent):
                    logging.info("Delete %s", pluginCurrent)
                    os.remove(pluginCurrent)
                pluginCurrentpyc = os.path.join(pluginDir, "current.pyc")
                if os.path.exists(pluginCurrentpyc):
                    logging.info("Delete %s", pluginCurrentpyc)
                    os.remove(pluginCurrentpyc)
            except OSError as err_msg:
                logging.warning("Failed To Remove File %s - %s", pluginCurrentpyc, err_msg)
        logging.info("%s Stop Camera Stream Thread.", CAMERA.upper())
        vs.stop()
        logging.info("%s %s Exiting Program", PROG_NAME, PROG_VER)
        logging.info("Bye ...")
        sys.exit()
