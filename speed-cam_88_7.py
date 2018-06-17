#!/usr/bin/python
"""
speed-cam.py written by Claude Pageau pageauc@gmail.com
Windows, Unix, Raspberry (Pi) - python opencv2 Speed tracking
using picamera module or Web Cam
GitHub Repo here https://github.com/pageauc/rpi-speed-camera/tree/master/

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

"""
from __future__ import print_function
print("Loading ...")
import time
import datetime
import os
import sys
import glob
import shutil
import logging
from threading import Thread
import subprocess

progVer = "8.87"
mypath = os.path.abspath(__file__)  # Find the full path of this python script
# get the path location only (excluding script name)
baseDir = mypath[0:mypath.rfind("/")+1]
baseFileName = mypath[mypath.rfind("/")+1:mypath.rfind(".")]
progName = os.path.basename(__file__)
print("----------------------------------------------------------------------")
print("%s %s   written by Claude Pageau" % (progName, progVer))
# Color data for OpenCV lines and text
cvWhite = (255, 255, 255)
cvBlack = (0, 0, 0)
cvBlue = (255, 0, 0)
cvGreen = (0, 255, 0)
cvRed = (0, 0, 255)
# Check for variable file to import and error out if not found.
configFilePath = baseDir + "config.py"
if not os.path.exists(configFilePath):
    print("ERROR : Missing config.py file - File Not Found %s"
          % configFilePath)
    import urllib2
    config_url = "https://raw.github.com/pageauc/speed-camera/master/config.py"
    print("INFO  : Attempting to Download config.py file from %s" % config_url)
    try:
        wgetfile = urllib2.urlopen(config_url)
    except:
        print("ERROR : Download of config.py Failed")
        print("        Try Rerunning the speed-install.sh Again.")
        print("        or")
        print("        Perform GitHub curl install per Readme.md")
        print("        and Try Again.")
        print("        %s %s Exiting Due to Error" % (progName, progVer))
        sys.exit(1)
    f = open('config.py', 'wb')
    f.write(wgetfile.read())
    f.close()
# Read Configuration variables from config.py file
from config import *

# Now that variables are imported from config.py Setup Logging
if loggingToFile:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=logFilePath,
                        filemode='w')
elif verbose:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("Logging to Console per Variable verbose=True")
else:
    logging.basicConfig(level=logging.CRITICAL,
                        format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
if not verbose:
    logging.info("Logging Disabled per Variable verbose=False")
from search_config import search_dest_path
# Setup appropriate plugin if enabled
if pluginEnable:     # Check and verify plugin and load variable overlay
    pluginDir = os.path.join(baseDir, "plugins")
    # Check if there is a .py at the end of pluginName variable
    if pluginName.endswith('.py'):
        pluginName = pluginName[:-3]    # Remove .py extensiion
    pluginPath = os.path.join(pluginDir, pluginName + '.py')
    logging.info("pluginEnabled - loading pluginName %s", pluginPath)
    if not os.path.isdir(pluginDir):
        print("ERROR : plugin Directory Not Found at %s" % pluginDir)
        print("        Rerun github curl install script to install plugins")
        print("        https://github.com/pageauc/pi-timolo/wiki/"
              "How-to-Install-or-Upgrade#quick-install")
        print("        %s %s Exiting Due to Error" % (progName, progVer))
        sys.exit(1)
    elif not os.path.exists(pluginPath):
        print("ERROR : File Not Found pluginName %s" % pluginPath)
        print("        Check Spelling of pluginName Value in %s"
              % configFilePath)
        print("        ------- Valid Names -------")
        validPlugin = glob.glob(pluginDir + "/*py")
        validPlugin.sort()
        for entry in validPlugin:
            pluginFile = os.path.basename(entry)
            plugin = pluginFile.rsplit('.', 1)[0]
            if not ((plugin == "__init__") or (plugin == "current")):
                print("        %s"  % plugin)
        print("        ------- End of List -------")
        print("        Note: pluginName Should Not have .py Ending.")
        print("INFO  : or Rerun github curl install command.  See github wiki")
        print("        https://github.com/pageauc/speed-camera/wiki/"
              "How-to-Install-or-Upgrade#quick-install")
        print("        %s %s Exiting Due to Error" % (progName, progVer))
        sys.exit(1)
    else:
        pluginCurrent = os.path.join(pluginDir, "current.py")
        try:    # Copy image file to recent folder
            print("INFO  : Copy %s to %s" % (pluginPath, pluginCurrent))
            shutil.copy(pluginPath, pluginCurrent)
        except OSError as err:
            print('ERROR : Copy Failed from %s to %s - %s'
                  % (pluginPath, pluginCurrent, err))
            print("        Check permissions, disk space, Etc.")
            print("        %s %s Exiting Due to Error" % (progName, progVer))
            sys.exit(1)
        print("INFO  : Import Plugin %s" % pluginPath)
        # add plugin directory to program PATH
        sys.path.insert(0, pluginDir)
        from plugins.current import *
        try:
            if os.path.exists(pluginCurrent):
                os.remove(pluginCurrent)
            pluginCurrentpyc = os.path.join(pluginDir, "current.pyc")
            if os.path.exists(pluginCurrentpyc):
                os.remove(pluginCurrentpyc)
        except OSError as err:
            print("WARN  : Failed To Remove File %s - %s"
                  % (pluginCurrentpyc, err))
            print("        %s %s Exiting Due to Error"
                  % (progName, progVer))
else:
    logging.info("No Plugins Enabled per pluginEnable=%s", pluginEnable)
# import the necessary packages
# -----------------------------
try:  #Add this check in case running on non RPI platform using web cam
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except ImportError:
    WEBCAM = True
if not WEBCAM:
    # Check that pi camera module is installed and enabled
    camResult = subprocess.check_output("vcgencmd get_camera", shell=True)
    camResult = camResult.decode("utf-8")
    camResult = camResult.replace("\n", "")
    if (camResult.find("0")) >= 0:   # -1 is zero not found. Cam OK
        logging.error("Pi Camera Module Not Found %s", camResult)
        logging.error("if supported=0 Enable Camera per command sudo raspi-config")
        logging.error("if detected=0 Check Pi Camera Module is Installed Correctly")
        logging.error("%s %s Exiting Due to Error", progName, progVer)
        sys.exit(1)
    else:
        logging.info("Camera Module is Enabled and Connected %s", camResult)
try:   # Check to see if opencv is installed
    import cv2
except ImportError:
    logging.error("Could not import cv2 library")
    if sys.version_info > (2, 9):
        logging.error("python3 failed to import cv2")
        logging.error("Try installing opencv for python3")
        logging.error("For RPI See https://github.com/pageauc/opencv3-setup")
    else:
        logging.error("python2 failed to import cv2")
        logging.error("Try RPI Install per command")
        logging.error("%s %s Exiting Due to Error", progName, progVer)
    sys.exit(1)
# fix possible invalid values
if WINDOW_BIGGER < 1.0:
    WINDOW_BIGGER = 1.0
if image_bigger < 1.0:
    image_bigger = 1.0
# fix event_timeout if too low
if event_timeout < 0.5:
    event_timeout = 0.5
# System Settings
if WEBCAM:
    # Set width of trigger point image to save
    image_width = int(WEBCAM_WIDTH * image_bigger)
    # Set height of trigger point image to save
    image_height = int(WEBCAM_HEIGHT * image_bigger)
else:
    # Set width of trigger point image to save
    image_width = int(CAMERA_WIDTH * image_bigger)
    # Set height of trigger point image to save
    image_height = int(CAMERA_HEIGHT * image_bigger)
# Calculate conversion from camera pixel width to actual speed.
px_to_kph = float(cal_obj_mm/cal_obj_px * 0.0036)
quote = '"'  # Used for creating quote delimited log file of speed data
if SPEED_MPH:
    speed_units = "mph"
    speed_conv = 0.621371 * px_to_kph
else:
    speed_units = "kph"
    speed_conv = px_to_kph

#------------------------------------------------------------------------------
class PiVideoStream:
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT),
                 framerate=CAMERA_FRAMERATE, rotation=0,
                 hflip=CAMERA_HFLIP, vflip=CAMERA_VFLIP):
        """ initialize the camera and stream """
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
        self.stream = self.camera.capture_continuous(self.rawCapture,
                                                     format="bgr",
                                                     use_video_port=True)
        """
        initialize the frame and the variable used to indicate
        if the thread should be stopped
        """
        self.frame = None
        self.stopped = False

    def start(self):
        """ start the thread to read frames from the video stream """
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        """ keep looping infinitely until the thread is stopped """
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
        """ return the frame most recently read """
        return self.frame

    def stop(self):
        """ indicate that the thread should be stopped """
        self.stopped = True

#------------------------------------------------------------------------------
class WebcamVideoStream:
    def __init__(self, CAM_SRC=WEBCAM_SRC, CAM_WIDTH=WEBCAM_WIDTH,
                 CAM_HEIGHT=WEBCAM_HEIGHT):
        """
        initialize the video camera stream and read the first frame
        from the stream
        """
        self.stream = CAM_SRC
        self.stream = cv2.VideoCapture(CAM_SRC)
        self.stream.set(3, CAM_WIDTH)
        self.stream.set(4, CAM_HEIGHT)
        (self.grabbed, self.frame) = self.stream.read()
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        """ start the thread to read frames from the video stream """
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        """ keep looping infinitely until the thread is stopped """
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        """ return the frame most recently read """
        return self.frame

    def stop(self):
        """ indicate that the thread should be stopped """
        self.stopped = True

#------------------------------------------------------------------------------
def get_fps(start_time, frame_count):
    """ Calculate and display frames per second processing """
    if frame_count >= 1000:
        duration = float(time.time() - start_time)
        FPS = float(frame_count / duration)
        logging.info("%.2f fps Last %i Frames", FPS, frame_count)
        frame_count = 0
        start_time = time.time()
    else:
        frame_count += 1
    return start_time, frame_count

#------------------------------------------------------------------------------
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
                logging.error('Failed to Create Folder %s - %s',
                              imageRecentDir, err)
    if not os.path.isdir(search_dest_path):
        logging.info("Creating Search Folder %s", search_dest_path)
        os.makedirs(search_dest_path)
    if not os.path.isdir(html_path):
        logging.info("Creating html Folder %s", html_path)
        os.makedirs(html_path)
    os.chdir(cwd)
    if verbose:
        print("--------------------------------------------------------------------------------")
        print("Note: To Send Full Output to File Use command")
        print("python -u ./%s | tee -a log.txt" % progName)
        print("Set log_data_to_file=True to Send speed_Data to CSV File %s.log"
              % baseFileName)
        print("--------------------------------- Settings -------------------------------------")
        print("")
        print("Plugins ......... pluginEnable=%s  pluginName=%s"
              % (pluginEnable, pluginName))
        print("Message Display . verbose=%s  display_fps=%s calibrate=%s"
              % (verbose, display_fps, calibrate))
        print("                  show_out_range=%s" % show_out_range)
        print("Logging ......... Log_data_to_CSV=%s  log_filename=%s.csv (CSV format)"
              % (log_data_to_CSV, baseFileName))
        print("                  loggingToFile=%s  logFilePath=%s"
              % (loggingToFile, logFilePath))
        print("                  Log if max_speed_over > %i %s"
              % (max_speed_over, speed_units))
        print("Speed Trigger ... If  track_len_trig > %i px" % track_len_trig)
        print("Exclude Events .. If  x_diff_min < %i or x_diff_max > %i px"
              % (x_diff_min, x_diff_max))
        print("                  If  y_upper < %i or y_lower > %i px"
              % (y_upper, y_lower))
        print("                  or  x_left < %i or x_right > %i px"
              % (x_left, x_right))
        print("                  If  max_speed_over < %i %s"
              % (max_speed_over, speed_units))
        print("                  If  event_timeout > %.2f seconds Start New Track"
              % (event_timeout))
        print("                  track_timeout=%.2f sec wait after Track Ends"
              " (avoid retrack of same object)"
              % (track_timeout))
        print("Speed Photo ..... Size=%ix%i px  image_bigger=%.1f"
              "  rotation=%i  VFlip=%s  HFlip=%s "
              % (image_width, image_height, image_bigger,
                 CAMERA_ROTATION, CAMERA_VFLIP, CAMERA_HFLIP))
        print("                  image_path=%s  image_Prefix=%s"
              % (image_path, image_prefix))
        print("                  image_font_size=%i px high  image_text_bottom=%s"
              % (image_font_size, image_text_bottom))
        print("Motion Settings . Size=%ix%i px  px_to_kph=%f  speed_units=%s"
              % (CAMERA_WIDTH, CAMERA_HEIGHT, px_to_kph, speed_units))
        print("OpenCV Settings . MIN_AREA=%i sq-px  BLUR_SIZE=%i"
              "  THRESHOLD_SENSITIVITY=%i  CIRCLE_SIZE=%i px"
              % (MIN_AREA, BLUR_SIZE, THRESHOLD_SENSITIVITY, CIRCLE_SIZE))
        print("                  WINDOW_BIGGER=%i gui_window_on=%s"
              " (Display OpenCV Status Windows on GUI Desktop)"
              % (WINDOW_BIGGER, gui_window_on))
        print("                  CAMERA_FRAMERATE=%i fps video stream speed"
              % CAMERA_FRAMERATE)
        print("Sub-Directories . imageSubDirMaxHours=%i (0=off)"
              "  imageSubDirMaxFiles=%i (0=off)"
              % (imageSubDirMaxHours, imageSubDirMaxFiles))
        print("                  imageRecentDir=%s imageRecentMax=%i (0=off)"
              % (imageRecentDir, imageRecentMax))
        if spaceTimerHrs > 0:   # Check if disk mgmnt is enabled
            print("Disk Space  ..... Enabled - Manage Target Free Disk Space."
                  " Delete Oldest %s Files if Needed" % (spaceFileExt))
            print("                  Check Every spaceTimerHrs=%i hr(s) (0=off)"
                  "  Target spaceFreeMB=%i MB  min is 100 MB)"
                  % (spaceTimerHrs, spaceFreeMB))
            print("                  If Needed Delete Oldest spaceFileExt=%s  spaceMediaDir=%s"
                  % (spaceFileExt, spaceMediaDir))
        else:
            print("Disk Space  ..... Disabled - spaceTimerHrs=%i"
                  "  Manage Target Free Disk Space. Delete Oldest %s Files"
                  % (spaceTimerHrs, spaceFileExt))
            print("            ..... spaceTimerHrs=%i (0=Off)"
                  "  Target spaceFreeMB=%i (min=100 MB)"
                  % (spaceTimerHrs, spaceFreeMB))
        print("")
        print("--------------------------------------------------------------------------------")
    return

#------------------------------------------------------------------------------
def take_calibration_image(filename, cal_image):
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
    cv2.line(cal_image, (x_left, y_upper), (x_right, y_upper), motion_win_color, 1)
    cv2.line(cal_image, (x_left, y_lower), (x_right, y_lower), motion_win_color, 1)
    cv2.line(cal_image, (x_left, y_upper), (x_left, y_lower), motion_win_color, 1)
    cv2.line(cal_image, (x_right, y_upper), (x_right, y_lower), motion_win_color, 1)
    print("")
    print("----------------------------- Create Calibration Image "
          "-----------------------------")
    print("")
    print("    Instructions for using %s image for camera calibration" % filename)
    print("")
    print("1 - Use a known size reference object in the image like a vehicle")
    print("    at the required distance.")
    print("2 - Record cal_obj_px  Value using Red y_upper hash marks at every 10 px")
    print("3 - Record cal_obj_mm of object. This is Actual length in mm of object above")
    print("4 - Edit config.py and enter the values for the above variables.")
    print("")
    print("    Calibration Image Saved To %s%s" % (baseDir, filename))
    print("")
    print("---------------------- Press cntl-c to Quit Calibration Mode "
          "-----------------------")
    print("")
    return cal_image

#------------------------------------------------------------------------------
def subDirLatest(directory):
    """ Scan for directories and return most recent """
    dirList = ([name for name in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, name))])
    if len(dirList) > 0:
        lastSubDir = sorted(dirList)[-1]
        lastSubDir = os.path.join(directory, lastSubDir)
    else:
        lastSubDir = directory
    return lastSubDir

#------------------------------------------------------------------------------
def subDirCreate(directory, prefix):
    """ Create media subdirectories base on required naming """
    now = datetime.datetime.now()
    # Specify folder naming
    subDirName = ('%s%d%02d%02d-%02d%02d' %
                  (prefix,
                   now.year, now.month, now.day,
                   now.hour, now.minute))
    subDirPath = os.path.join(directory, subDirName)
    if not os.path.exists(subDirPath):
        try:
            os.makedirs(subDirPath)
        except OSError as err:
            logging.error('Cannot Create Dir %s - %s, using default location.',
                          subDirPath, err)
            subDirPath = directory
        else:
            logging.info('Created %s', subDirPath)
    else:
        subDirPath = directory
    return subDirPath

#------------------------------------------------------------------------------
def deleteOldFiles(maxFiles, dirPath, prefix):
    """
    Delete Oldest files gt or
    equal to maxfiles that match filename prefix
    """
    try:
        fileList = sorted(glob.glob(os.path.join(dirPath, prefix + '*')),
                          key=os.path.getmtime)
    except OSError as err:
        logging.error('Problem Reading Directory %s - %s', dirPath, err)
    else:
        while len(fileList) >= maxFiles:
            oldest = fileList[0]
            oldestFile = oldest
            try:   # Remove oldest file in recent folder
                fileList.remove(oldest)
                os.remove(oldestFile)
            except OSError as err:
                logging.error('Cannot Remove %s - %s', oldestFile, err)

#------------------------------------------------------------------------------
def subDirCheckMaxFiles(directory, filesMax):
    """ Count number of files in a folder path """
    fileList = glob.glob(directory + '/*jpg')
    count = len(fileList)
    if count > filesMax:
        makeNewDir = True
        logging.info('Total Files in %s Exceeds %i ', directory, filesMax)
    else:
        makeNewDir = False
    return makeNewDir

#------------------------------------------------------------------------------
def subDirCheckMaxHrs(directory, hrsMax, prefix):
    """ extract the date-time from the directory name """
    # Note to self need to add error checking
    dirName = os.path.split(directory)[1]   # split dir path and keep dirName
    # remove prefix from dirName so just date-time left
    dirStr = dirName.replace(prefix, '')
    # convert string to datetime
    dirDate = datetime.datetime.strptime(dirStr, "%Y-%m-%d-%H:%M")
    rightNow = datetime.datetime.now()   # get datetime now
    diff = rightNow - dirDate  # get time difference between dates
    days, seconds = diff.days, diff.seconds
    dirAgeHours = days * 24 + seconds // 3600  # convert to hours
    if dirAgeHours > hrsMax:   # See if hours are exceeded
        makeNewDir = True
        logging.info('MaxHrs %i Exceeds %i for %s',
                     dirAgeHours, hrsMax, directory)
    else:
        makeNewDir = False
    return makeNewDir

#------------------------------------------------------------------------------
def subDirChecks(maxHours, maxFiles, directory, prefix):
    """ Check if motion SubDir needs to be created """
    if maxHours < 1 and maxFiles < 1:  # No Checks required
        # logging.info('No sub-folders Required in %s', directory)
        subDirPath = directory
    else:
        subDirPath = subDirLatest(directory)
        if subDirPath == directory:   # No subDir Found
            logging.info('No sub folders Found in %s', directory)
            subDirPath = subDirCreate(directory, prefix)
        elif (maxHours > 0 and maxFiles < 1): # Check MaxHours Folder Age Only
            if subDirCheckMaxHrs(subDirPath, maxHours, prefix):
                subDirPath = subDirCreate(directory, prefix)
        elif (maxHours < 1 and maxFiles > 0):   # Check Max Files Only
            if subDirCheckMaxFiles(subDirPath, maxFiles):
                subDirPath = subDirCreate(directory, prefix)
        elif maxHours > 0 and maxFiles > 0:   # Check both Max Files and Age
            if subDirCheckMaxHrs(subDirPath, maxHours, prefix):
                if subDirCheckMaxFiles(subDirPath, maxFiles):
                    subDirPath = subDirCreate(directory, prefix)
                else:
                    logging.info('MaxFiles Not Exceeded in %s', subDirPath)
    os.path.abspath(subDirPath)
    return subDirPath

#------------------------------------------------------------------------------
def filesToDelete(mediaDirPath, extension=image_format):
    """ Return a list of files to be deleted """
    return sorted(
        (os.path.join(dirname, filename)
         for dirname, dirnames, filenames in os.walk(mediaDirPath)
         for filename in filenames
         if filename.endswith(extension)),
        key=lambda fn: os.stat(fn).st_mtime, reverse=True)

#------------------------------------------------------------------------------
def saveRecent(recentMax, recentDir, filename, prefix):
    """
    Create a symlink file in recent folder or file if non unix system
    or symlink creation fails.
    Delete Oldest symlink file if recentMax exceeded.
    """
    src = os.path.abspath(filename)  # Original Source File Path
    # Destination Recent Directory Path
    dest = os.path.abspath(os.path.join(recentDir,
                                        os.path.basename(filename)))
    deleteOldFiles(recentMax, os.path.abspath(recentDir), prefix)
    try:    # Create symlink in recent folder
        logging.info('symlink to %s', dest)
        os.symlink(src, dest)  # Create a symlink to actual file
    # Symlink can fail on non unix systems so copy file to Recent Dir instead
    except OSError as err:
        logging.error('symlink Failed: %s', err)
        try:  # Copy image file to recent folder (if no support for symlinks)
            shutil.copy(filename, recentDir)
        except OSError as err:
            logging.error('Copy from %s to %s - %s', filename, recentDir, err)

#------------------------------------------------------------------------------
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
        logging.info('Session Started')
        while fileList:
            statv = os.statvfs(mediaDirPath)
            availFreeBytes = statv.f_bfree*statv.f_bsize
            if availFreeBytes >= targetFreeBytes:
                break
            filePath = fileList.pop()
            try:
                os.remove(filePath)
            except OSError as err:
                logging.error('Del Failed %s', filePath)
                logging.error('Error: %s', err)
            else:
                delcnt += 1
                logging.info('Del %s', filePath)
                logging.info('Target=%i MB  Avail=%i MB  Deleted %i of %i Files ',
                             targetFreeBytes / MB2Bytes,
                             availFreeBytes / MB2Bytes,
                             delcnt, totFiles)
                # Avoid deleting more than 1/4 of files at one time
                if delcnt > totFiles / 4:
                    logging.warning('Max Deletions Reached %i of %i',
                                    delcnt, totFiles)
                    logging.warning('Deletions Restricted to 1/4 of total files per session.')
                    break
        logging.info('Session Ended')
    else:
        logging.error('Directory Not Found - %s', mediaDirPath)

#------------------------------------------------------------------------------
def freeDiskSpaceCheck(lastSpaceCheck):
    """ Free disk space by deleting some older files """
    if spaceTimerHrs > 0:   # Check if disk free space timer hours is enabled
        # See if it is time to do disk clean-up check
        if (datetime.datetime.now() - lastSpaceCheck).total_seconds() > spaceTimerHrs * 3600:
            lastSpaceCheck = datetime.datetime.now()
            # Set freeSpaceMB to reasonable value if too low
            if spaceFreeMB < 100:
                diskFreeMB = 100
            else:
                diskFreeMB = spaceFreeMB
            logging.info('spaceTimerHrs=%i  diskFreeMB=%i  spaceMediaDir=%s spaceFileExt=%s',
                         spaceTimerHrs, diskFreeMB, spaceMediaDir, spaceFileExt)
            freeSpaceUpTo(diskFreeMB, spaceMediaDir, spaceFileExt)
    return lastSpaceCheck

#------------------------------------------------------------------------------
def get_image_name(path, prefix):
    """ build image file names by number sequence or date/time """
    rightNow = datetime.datetime.now()
    filename = ("%s/%s%04d%02d%02d-%02d%02d%02d.jpg" %
                (path, prefix, rightNow.year, rightNow.month, rightNow.day,
                 rightNow.hour, rightNow.minute, rightNow.second))
    return filename

#------------------------------------------------------------------------------
def log_to_csv_file(data_to_append):
    """ Store date to a comma separated value file """
    log_file_path = baseDir + baseFileName + ".csv"
    if not os.path.exists(log_file_path):
        open(log_file_path, 'w').close()
        f = open(log_file_path, 'ab')
        # header_text = ('"YYYYMMDD","HH","MM","Speed","Unit",
        #                  "    Speed Photo Path            ",
        #                  "X","Y","W","H","Area","Direction"' + "\n")
        # f.write( header_text )
        f.close()
        logging.info("Create New Data Log File %s", log_file_path)
    filecontents = data_to_append + "\n"
    f = open(log_file_path, 'a+')
    f.write(filecontents)
    f.close()
    return

#------------------------------------------------------------------------------
def speed_camera():
    """ Main speed camera processing function """
    ave_speed = 0.0
    # initialize variables
    frame_count = 0
    fps_time = time.time()
    first_event = True   # Start a New Motion Track
    event_timer = time.time()
    start_pos_x = None
    end_pos_x = None
    # setup buffer area to ensure contour is fully contained in crop area
    x_buf = int((x_right - x_left) / 10)
    y_buf = int((y_lower - y_upper) / 8)
    travel_direction = ""
    # initialize a cropped grayimage1 image
    # Only needs to be done once
    image2 = vs.read()  # Get image from PiVideoSteam thread instance
    try:
        # crop image to motion tracking area only
        image_crop = image2[y_upper:y_lower, x_left:x_right]
    except:
        vs.stop()
        logging.warn("Problem Connecting To Camera Stream.")
        logging.warn("Restarting Camera.  One Moment Please ...")
        time.sleep(4)
        return
    if verbose:
        if gui_window_on:
            logging.info("Press lower case q on OpenCV GUI Window to Quit program")
            logging.info("        or ctrl-c in this terminal session to Quit")
        else:
            logging.info("Press ctrl-c in this terminal session to Quit")

        if loggingToFile:
            logging.info("Sending Logging Data to %s (Console Messages Disabled)",
                         logFilePath)
        else:
            logging.info("Start Logging Speed Camera Activity to Console")
    else:
        print("INFO  : NOTE: Logging Messages Disabled per verbose=%s"
              % verbose)
    if pluginEnable:
        logging.info("Plugin %s is Enabled." % pluginName)
    if calibrate:
        logging.info("IMPORTANT: Camera Is In Calibration Mode ....")
    logging.info("Begin Motion Tracking .....")
    # Calculate position of text on the images
    font = cv2.FONT_HERSHEY_SIMPLEX
    if image_text_bottom:
        text_y = (image_height - 50)  # show text at bottom of image
    else:
        text_y = 10  # show text at top of image
    grayimage1 = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
    event_timer = time.time()
    # Initialize prev_image used for taking speed image photo
    prev_image = image2
    still_scanning = True
    lastSpaceCheck = datetime.datetime.now()
    speed_path = image_path
    while still_scanning:  # process camera thread images and calculate speed
        image2 = vs.read() # Read image data from video steam thread instance
        if WEBCAM:
            if (WEBCAM_HFLIP and WEBCAM_VFLIP):
                image2 = cv2.flip(image2, -1)
            elif WEBCAM_HFLIP:
                image2 = cv2.flip(image2, 1)
            elif WEBCAM_VFLIP:
                image2 = cv2.flip(image2, 0)
        # crop image to motion tracking area only
        try:
            image_crop = image2[y_upper:y_lower, x_left:x_right]
        except ValueError:
            logging.error("image2 Stream Image is Not Complete. Cannot Crop.")
            continue
        # Convert to gray scale, which is easier
        grayimage2 = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
        # Get differences between the two greyed images
        differenceimage = cv2.absdiff(grayimage1, grayimage2)
        # Blur difference image to enhance motion vectors
        differenceimage = cv2.blur(differenceimage, (BLUR_SIZE, BLUR_SIZE))
        # Get threshold of blurred difference image
        # based on THRESHOLD_SENSITIVITY variable
        retval, thresholdimage = cv2.threshold(differenceimage,
                                               THRESHOLD_SENSITIVITY,
                                               255, cv2.THRESH_BINARY)
        try:
            # opencv 2 syntax default
            contours, hierarchy = cv2.findContours(thresholdimage,
                                                   cv2.RETR_EXTERNAL,
                                                   cv2.CHAIN_APPROX_SIMPLE)
        except ValueError:
            # opencv 3 syntax
            thresholdimage, contours, hierarchy = cv2.findContours(thresholdimage,
                                                                   cv2.RETR_EXTERNAL,
                                                                   cv2.CHAIN_APPROX_SIMPLE)
        total_contours = len(contours)
        # Update grayimage1 to grayimage2 ready for next image2
        grayimage1 = grayimage2
        # initialize variables
        motion_found = False
        biggest_area = MIN_AREA
        # if contours found, find the one with biggest area
        if contours:
            for c in contours:
                # get area of contour
                found_area = cv2.contourArea(c)
                if found_area > biggest_area:
                    (x, y, w, h) = cv2.boundingRect(c)
                    # check if object contour is completely within crop area
                    if (x > x_buf and
                            x + w < x_right - x_left - x_buf and
                            y > y_buf and
                            y + h < y_lower - y_upper - y_buf):
                        motion_found = True
                        biggest_area = found_area
                        # track contour center points since it seems to be
                        # more stable than x contour position although
                        # lighting and other factors can cause unexpected
                        # jumps in position.
                        cx = int(x + w/2) # middle of contour width
                        cy = int(y + h/2) # middle of contour height
                        mw = w  # movement width of object contour
                        mh = h  # movement height of object contour
            if motion_found:
                # Check if last motion event timed out
                if time.time() - event_timer > event_timeout:
                    # event_timer exceeded so reset for new track
                    event_timer = time.time()
                    first_event = True
                    start_pos_x = None
                    end_pos_x = None
                    logging.info("Reset- event_timer %.2f sec Exceeded",
                                 event_timeout)
                # Process motion events and track object movement
                if first_event:   # This is a first valid motion event
                    first_event = False  # Only one first track event
                    track_start_time = time.time() # Record track start time
                    event_timer = time.time() # Reset event timeout
                    # set start and end of track to the start center point
                    start_pos_x = cx
                    end_pos_x = cx
                    logging.info("New  - cxy(%i,%i) Start New Track", cx, cy)
                else:
                    if end_pos_x - start_pos_x > 0:
                        travel_direction = "L2R"
                    else:
                        travel_direction = "R2L"
                    # check if movement is within acceptable distance
                    # range of last event
                    if (abs(cx - end_pos_x) > x_diff_min and
                            abs(cx - end_pos_x) < x_diff_max):
                        end_pos_x = cx # new position of track end point
                        tot_track_dist = abs(end_pos_x - start_pos_x)
                        tot_track_time = abs(time.time() - track_start_time)
                        ave_speed = float((abs(tot_track_dist / tot_track_time)) * speed_conv)
                        if abs(end_pos_x - start_pos_x) >= track_len_trig:
                            # Track length exceeded so take process speed photo
                            if ave_speed > max_speed_over or calibrate:
                                logging.info(" Add - cxy(%i,%i) %3.2f %s px=%i/%i"
                                             " C=%i %ix%i=%i sqpx %s",
                                             cx, cy, ave_speed, speed_units,
                                             abs(start_pos_x - end_pos_x),
                                             track_len_trig, total_contours,
                                             mw, mh, biggest_area,
                                             travel_direction)
                                # Resize and process previous image
                                # before saving to disk
                                prev_image = image2
                                # Create a calibration image file name
                                # There are no subdirectories to deal with
                                if calibrate:
                                    filename = get_image_name(speed_path, "calib-")
                                    prev_image = take_calibration_image(filename,
                                                                        prev_image)
                                else:
                                    # Check if subdirectories configured
                                    # and create as required
                                    speed_path = subDirChecks(imageSubDirMaxHours,
                                                              imageSubDirMaxFiles,
                                                              image_path, image_prefix)
                                    # Create image file name prefix
                                    if image_filename_speed:
                                        speed_prefix = (str(int(round(ave_speed)))
                                                        + "-" + image_prefix)
                                    else:
                                        speed_prefix = image_prefix
                                    # create image file name path
                                    filename = get_image_name(speed_path,
                                                              speed_prefix)
                                # Add motion rectangle to image
                                # if required
                                if image_show_motion_area:
                                    cv2.line(prev_image, (x_left, y_upper),
                                             (x_right, y_upper), cvRed, 1)
                                    cv2.line(prev_image, (x_left, y_lower),
                                             (x_right, y_lower), cvRed, 1)
                                    cv2.line(prev_image, (x_left, y_upper),
                                             (x_left, y_lower), cvRed, 1)
                                    cv2.line(prev_image, (x_right, y_upper),
                                             (x_right, y_lower), cvRed, 1)
                                    # show centre of motion if required
                                    if SHOW_CIRCLE:
                                        cv2.circle(prev_image,
                                                   (cx + x_left, cy + y_upper),
                                                   CIRCLE_SIZE,
                                                   cvGreen, LINE_THICKNESS)
                                    else:
                                        cv2.rectangle(prev_image,
                                                      (int(cx + x_left - mw/2),
                                                       int(cy + y_upper - mh/2)),
                                                      (int(cx + x_left + mw/2),
                                                       int(cy + y_upper + mh/2)),
                                                      cvGreen, LINE_THICKNESS)
                                big_image = cv2.resize(prev_image,
                                                       (image_width,
                                                       image_height))
                                # Write text on image before saving
                                # if required.
                                if image_text_on:
                                    image_text = ("SPEED %.1f %s - %s"
                                                  % (ave_speed,
                                                     speed_units,
                                                     filename))
                                    text_x = int((image_width / 2) -
                                                 (len(image_text) *
                                                  image_font_size / 3))
                                    if text_x < 2:
                                        text_x = 2
                                    logging.info(" Ave Speed is %.1f %s %s ",
                                                 ave_speed,
                                                 speed_units,
                                                 travel_direction)
                                    cv2.putText(big_image,
                                                image_text,
                                                (text_x, text_y),
                                                font,
                                                FONT_SCALE,
                                                (cvWhite), 2)
                                logging.info(" Saved %s", filename)
                                # Save resized image
                                cv2.imwrite(filename, big_image)
                                # if required check free disk space
                                # and delete older files (jpg)
                                if spaceTimerHrs > 0:
                                    lastSpaceCheck = freeDiskSpaceCheck(lastSpaceCheck)
                                # Manage a maximum number of files
                                # and delete oldest if required.
                                if image_max_files > 0:
                                    deleteOldFiles(image_max_files,
                                                   speed_path,
                                                   image_prefix)
                                # Save most recent files
                                # to a recent folder if required
                                if imageRecentMax > 0 and not calibrate:
                                    saveRecent(imageRecentMax,
                                               imageRecentDir,
                                               filename,
                                               image_prefix)
                                # Format and Save Data to CSV Log File
                                if log_data_to_CSV:
                                    log_time = datetime.datetime.now()
                                    log_csv_time = ("%s%04d%02d%02d%s,"
                                                    "%s%02d%s,%s%02d%s"
                                                    % (quote,
                                                       log_time.year,
                                                       log_time.month,
                                                       log_time.day,
                                                       quote,
                                                       quote,
                                                       log_time.hour,
                                                       quote,
                                                       quote,
                                                       log_time.minute,
                                                       quote))
                                    log_csv_text = ("%s,%.2f,%s%s%s,%s%s%s,"
                                                    "%i,%i,%i,%i,%i,%s%s%s"
                                                    % (log_csv_time,
                                                       ave_speed,
                                                       quote,
                                                       speed_units,
                                                       quote,
                                                       quote,
                                                       filename,
                                                       quote,
                                                       cx, cy,
                                                       mw, mh,
                                                       mw * mh,
                                                       quote,
                                                       travel_direction,
                                                       quote))
                                    log_to_csv_file(log_csv_text)
                                logging.info("End  - Tracked %i px in %.3f sec",
                                             tot_track_dist, tot_track_time)
                                # Wait to avoid dual tracking same object.
                                time.sleep(track_timeout)
                            else:
                                logging.info("End  - Skip Photo SPEED %.1f %s"
                                             " max_speed_over=%i  %i px in %.3f sec"
                                             " C=%i A=%i sqpx",
                                             ave_speed, speed_units,
                                             max_speed_over, tot_track_dist,
                                             tot_track_time, total_contours,
                                             biggest_area)
                                # Optional Wait to avoid dual tracking
                                time.sleep(track_timeout)
                            # Track Ended so Reset Variables for
                            # next cycle through loop
                            start_pos_x = None
                            end_pos_x = None
                            first_event = True # Reset Track
                        else:
                            logging.info(" Add - cxy(%i,%i) %3.1f %s"
                                         " px=%i/%i C=%i %ix%i=%i sqpx %s",
                                         cx, cy, ave_speed, speed_units,
                                         abs(start_pos_x - end_pos_x),
                                         track_len_trig, total_contours,
                                         mw, mh, biggest_area,
                                         travel_direction)
                            end_pos_x = cx
                            # valid motion found so update event_timer
                            event_timer = time.time()
                    # Movement was now within range parameters
                    else:
                        if show_out_range:
                            # movements exceeds Max px movement
                            # allowed so Ignore and do not update event_timer
                            if abs(cx - end_pos_x) >= x_diff_max:
                                logging.info(" Out - cxy(%i,%i) Dist=%i is "
                                             ">=%i px C=%i %ix%i=%i sqpx %s",
                                             cx, cy, abs(cx - end_pos_x),
                                             x_diff_max, total_contours,
                                             mw, mh, biggest_area,
                                             travel_direction)
                            # Did not move much so update event_timer
                            # and wait for next valid movement.
                            else:
                                event_timer = time.time()
                                logging.info(" Out - cxy(%i,%i) Dist=%i is "
                                             "<=%i px C=%i %ix%i=%i sqpx %s",
                                             cx, cy, abs(cx - end_pos_x),
                                             x_diff_min, total_contours,
                                             mw, mh, biggest_area,
                                             travel_direction)
                if gui_window_on:
                    # show small circle at contour centre if required
                    # otherwise a rectangle around most recent contour
                    if SHOW_CIRCLE:
                        cv2.circle(image2,
                                   (cx + x_left * WINDOW_BIGGER,
                                    cy + y_upper * WINDOW_BIGGER),
                                   CIRCLE_SIZE, cvGreen, LINE_THICKNESS)
                    else:
                        cv2.rectangle(image2,
                                      (int(cx + x_left - mw/2),
                                       int(cy + y_upper - mh/2)),
                                      (int(cx + x_left + mw/2),
                                       int(cy + y_upper + mh/2)),
                                      cvGreen, LINE_THICKNESS)
        if gui_window_on:
            # cv2.imshow('Difference Image',difference image)
            cv2.line(image2, (x_left, y_upper), (x_right, y_upper), cvRed, 1)
            cv2.line(image2, (x_left, y_lower), (x_right, y_lower), cvRed, 1)
            cv2.line(image2, (x_left, y_upper), (x_left, y_lower), cvRed, 1)
            cv2.line(image2, (x_right, y_upper), (x_right, y_lower), cvRed, 1)
            image_view = cv2.resize(image2, (image_width, image_height))
            cv2.imshow('Movement (q Quits)', image_view)
            if show_thresh_on:
                cv2.imshow('Threshold', thresholdimage)
            if show_crop_on:
                cv2.imshow('Crop Area', image_crop)
            # Close Window if q pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                logging.info("End Motion Tracking ......")
                vs.stop()
                still_scanning = False
        if display_fps:   # Optionally show motion image processing loop fps
            fps_time, frame_count = get_fps(fps_time, frame_count)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    show_settings()  # Show variable settings
    try:
        WEBCAM_TRIES = 0
        while True:
            # Start Web Cam stream (Note USB webcam must be plugged in)
            if WEBCAM:
                WEBCAM_TRIES += 1
                logging.info("Initializing USB Web Camera Try .. %i",
                             WEBCAM_TRIES)
                # Start video stream on a processor Thread for faster speed
                vs = WebcamVideoStream().start()
                vs.CAM_SRC = WEBCAM_SRC
                vs.CAM_WIDTH = WEBCAM_WIDTH
                vs.CAM_HEIGHT = WEBCAM_HEIGHT
                if WEBCAM_TRIES > 3:
                    logging.error("USB Web Cam Not Connecting to WEBCAM_SRC %i",
                                  WEBCAM_SRC)
                    logging.error("Check Camera is Plugged In and Working")
                    logging.error("on Specified SRC")
                    logging.error("and Not Used(busy) by Another Process.")
                    logging.error("%s %s Exiting Due to Error",
                                  progName, progVer)
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
            speed_camera() # run main speed camera processing loop
    except KeyboardInterrupt:
        vs.stop()
        print("")
        logging.info("User Pressed Keyboard ctrl-c")
        logging.info("%s %s Exiting Program", progName, progVer)
        sys.exit()
