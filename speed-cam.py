#!/usr/bin/python
version = "version 7.0"

"""
speed-cam.py written by Claude Pageau pageauc@gmail.com
Windows, Unix, Raspberry (Pi) - python opencv2 Speed tracking using picamera module or Web Cam
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
print("Loading Please Wait ....")
print("-------------------------------------------------------------------------------------------------")
print("speed-cam.py %s   written by Claude Pageau" % ( version ))

import os
import glob
import shutil
import sys

mypath=os.path.abspath(__file__)       # Find the full path of this python script
baseDir=mypath[0:mypath.rfind("/")+1]  # get the path location only (excluding script name)
baseFileName=mypath[mypath.rfind("/")+1:mypath.rfind(".")]
progName = os.path.basename(__file__)

# Color data for OpenCV lines and text
cvWhite = (255,255,255)
cvBlack = (0,0,0)
cvBlue = (255,0,0)
cvGreen = (0,255,0)
cvRed = (0,0,255)

# Check for variable file to import and error out if not found.
configFilePath = baseDir + "config.py"
if not os.path.exists(configFilePath):
    print("ERROR : Missing config.py file - Could not find Configuration file %s" % (configFilePath))
    import urllib2
    config_url = "https://raw.github.com/pageauc/speed-camera/master/config.py"
    print("INFO  : Attempting to Download config.py file from %s" % ( config_url ))
    try:
        wgetfile = urllib2.urlopen(config_url)
    except:
        print("ERROR : Download of config.py Failed")
        print("        Try Rerunning the speed-install.sh Again.")
        print("        or")
        print("        Perform GitHub curl install per Readme.md")
        print("        and Try Again.")
        print("Exiting %s" % ( progName ))
        quit()
    f = open('config.py','wb')
    f.write(wgetfile.read())
    f.close()
# Read Configuration variables from config.py file
from config import *
from search_config import search_dest_path

if pluginEnable:     # Check and verify plugin and load variable overlay
    pluginDir = os.path.join(baseDir,"plugins")
    if pluginName.endswith('.py'):      # Check if there is a .py at the end of pluginName variable
        pluginName = pluginName[:-3]    # Remove .py extensiion
    pluginPath = os.path.join(pluginDir, pluginName + '.py')
    print("INFO  : pluginEnabled - loading pluginName %s" % pluginPath)
    if not os.path.isdir(pluginDir):
        print("ERROR : plugin Directory Not Found at %s" % pluginDir )
        print("        Suggest you Rerun github curl install script to install plugins")
        print("        https://github.com/pageauc/pi-timolo/wiki/How-to-Install-or-Upgrade#quick-install")
        print("INFO  : Exiting %s Due to Error" % progName)
        quit()

    elif not os.path.exists(pluginPath):
        print("ERROR : File Not Found pluginName %s" % pluginPath )
        print("        Check Spelling of pluginName Value in %s" % configFilePath)
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
        print("        https://github.com/pageauc/speed-camera/wiki/How-to-Install-or-Upgrade#quick-install")
        print("INFO  : Exiting %s Due to Error" % progName)
        quit()
    else:
        pluginCurrent = os.path.join(pluginDir, "current.py")
        try:    # Copy image file to recent folder
            print("INFO  : Copy %s to %s" %( pluginPath, pluginCurrent ))
            shutil.copy(pluginPath, pluginCurrent)
        except OSError as err:
            print('ERROR : Copy Failed from %s to %s - %s' % ( pluginPath, pluginCurrent, err))
            Pring("        Check permissions, disk space, Etc.")
            print("INFO  : Exiting %s Due to Error" % progName)
            quit()
        print("INFO  : Import Plugin %s" % pluginPath)
        sys.path.insert(0,pluginDir)    # add plugin directory to program PATH
        from plugins.current import *
        try:
            if os.path.exists(pluginCurrent):
                os.remove(pluginCurrent)
            pluginCurrentpyc = os.path.join(pluginDir, "current.pyc")
            if os.path.exists(pluginCurrentpyc):
                os.remove(pluginCurrentpyc)
        except OSError as err:
            print("ERROR : Failed Removal of %s - %s" % ( pluginCurrentpyc, err ))
            print("INFO  : Exiting %s Due to Error" % progName)

else:
    print("INFO  : No Plugins Enabled per pluginEnable=%s" % pluginEnable)

# fix possible invalid values
if WINDOW_BIGGER < 1:
    WINDOW_BIGGER = 1
if image_bigger < 1:
    image_bigger = 1

# import the necessary packages
# -----------------------------
try:  #Add this check in case running on non RPI platform using web cam
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except:
    WEBCAM = True
    pass

import subprocess
if not WEBCAM:
    # Check for that pi camaera module is installed and enabled
    camResult = subprocess.check_output("vcgencmd get_camera", shell=True)
    camResult = camResult.decode("utf-8")
    camResult = camResult.replace("\n", "")
    if (camResult.find("0")) >= 0:   # -1 is zero not found. Cam OK
        print("ERROR : Pi Camera Module Not Found %s" % camResult)
        print("        if supported=0 Enable Camera using command sudo raspi-config")
        print("        if detected=0 Check Pi Camera Module is Installed Correctly")
        print("INFO  : Exiting %s" % progName)
        quit()
    else:
        print("INFO  : Pi Camera Module is Enabled and Connected %s" % camResult )

import numpy as np
from threading import Thread
import logging
import time
import datetime
import io

try:   # Check to see if opencv is installed
    import cv2
except:
    print("ERROR : Could not import cv2 library")
    print("")
    if (sys.version_info > (2, 9)):
        print("        python3 failed to import cv2")
        print("        Try installing opencv for python3")
        print("        For RPI See https://github.com/pageauc/opencv3-setup")
    else:
        print("        python2 failed to import cv2")
        print("        Try RPI Install per command")
    print("INFO  : Exiting %s" % progName)
    quit()

# Now that variables are imported from config.py Setup Logging
if loggingToFile:
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=logFilePath,
                    filemode='w')
elif verbose:
    print("Logging to Console per Variable verbose=True")
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
else:
    print("Logging Disabled per Variable verbose=False")
    logging.basicConfig(level=logging.CRITICAL,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# System Settings
image_width  = int(CAMERA_WIDTH * image_bigger)        # Set width of trigger point image to save
image_height = int(CAMERA_HEIGHT * image_bigger)       # Set height of trigger point image to save

# Calculate conversion from camera pixel width to actual speed.
px_to_kph = float(cal_obj_mm/cal_obj_px * 0.0036)

if SPEED_MPH:
    speed_units = "mph"
    speed_conv  = 0.621371 * px_to_kph
else:
    speed_units = "kph"
    speed_conv  = px_to_kph

quote = '"'  # Used for creating quote delimited log file of speed data

#-----------------------------------------------------------------------------------------------
class PiVideoStream:
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=CAMERA_FRAMERATE, rotation=0,
                                                   hflip=CAMERA_HFLIP, vflip=CAMERA_VFLIP):
        # initialize the camera and stream
        try:
           self.camera = PiCamera()
        except:
           print("ERROR : PiCamera Already in Use by Another Process")
           print("INFO  : Exit %s" % progName)
           quit()
        self.camera.resolution = resolution
        self.camera.rotation = rotation
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
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
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

#-----------------------------------------------------------------------------------------------
class WebcamVideoStream:
    def __init__(self, CAM_SRC=WEBCAM_SRC, CAM_WIDTH=WEBCAM_WIDTH, CAM_HEIGHT=WEBCAM_HEIGHT):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = CAM_SRC
        self.stream = cv2.VideoCapture(CAM_SRC)
        self.stream.set(3,CAM_WIDTH)
        self.stream.set(4,CAM_HEIGHT)
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                    return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

#----------------------------------------------------------------------------------------------
def get_fps( start_time, frame_count ):
    # Calculate and display frames per second processing
    if frame_count >= 1000:
        duration = float( time.time() - start_time )
        FPS = float( frame_count / duration )
        logging.info("%.2f fps Last %i Frames", FPS, frame_count )
        frame_count = 0
        start_time = time.time()
    else:
        frame_count += 1
    return start_time, frame_count

#-----------------------------------------------------------------------------------------------
def show_settings():
    cwd = os.getcwd()
    html_path = "media/html"
    if not os.path.isdir(image_path):
        logging.info("Creating Image Storage Folder %s", image_path )
        os.makedirs(image_path)
    os.chdir(image_path)
    img_dir = os.getcwd()
    os.chdir(cwd)
    if imageRecentMax > 0:
        if not os.path.isdir(imageRecentDir):
            logging.info("Create Recent Folder %s", imageRecentDir)
            try:
                os.makedirs(imageRecentDir)
            except OSError as err:
                logging.error('Failed to Create Folder %s - %s', imageRecentDir, err)
    if not os.path.isdir(search_dest_path):
        logging.info("Creating Search Folder %s", search_dest_path)
        os.makedirs(search_dest_path)
    if not os.path.isdir(html_path):
        logging.info("Creating html Folder %s", html_path)
        os.makedirs(html_path)
    os.chdir(cwd)
    if verbose:
        print("")
        print("Note: To Send Full Output to File Use command -   python -u ./%s | tee -a log.txt" % progName)
        print("      Set log_data_to_file=True to Send speed_Data to CSV File %s.log" % baseFileName)
        print("-------------------------------------- Settings -------------------------------------------------")
        print("")
        print("Plugins ......... pluginEnable=%s  pluginName=%s" % ( pluginEnable, pluginName ))
        print("Message Display . verbose=%s  display_fps=%s calibrate=%s" % ( verbose, display_fps, calibrate ))
        print("                  show_out_range=%s" % ( show_out_range ))
        print("Logging ......... Log_data_to_CSV=%s  log_filename=%s.csv (CSV format)"  % ( log_data_to_CSV, baseFileName ))
        print("                  loggingToFile=%s  logFilePath=%s" % (loggingToFile, logFilePath))
        print("                  Log if max_speed_over > %i %s" % ( max_speed_over, speed_units))
        print("Speed Trigger ... If  track_len_trig > %i px" % ( track_len_trig ))
        print("Exclude Events .. If  x_diff_min < %i or x_diff_max > %i px" % ( x_diff_min, x_diff_max ))
        print("                  If  y_upper < %i or y_lower > %i px" % ( y_upper, y_lower ))
        print("                  or  x_left < %i or x_right > %i px" % ( x_left, x_right ))
        print("                  If  max_speed_over < %i %s" % ( max_speed_over, speed_units ))
        print("                  If  event_timeout > %i seconds Start New Track" % ( event_timeout ))
        print("                  track_timeout=%i sec wait after Track Ends (avoid retrack of same object)" % ( track_timeout ))
        print("Speed Photo ..... Size=%ix%i px  image_bigger=%i  rotation=%i  VFlip=%s  HFlip=%s " %
                                 ( image_width, image_height, image_bigger, CAMERA_ROTATION, CAMERA_VFLIP, CAMERA_HFLIP ))
        print("                  image_path=%s  image_Prefix=%s" % ( image_path, image_prefix ))
        print("                  image_font_size=%i px high  image_text_bottom=%s" % ( image_font_size, image_text_bottom ))
        print("Motion Settings . Size=%ix%i px  px_to_kph=%f  speed_units=%s" %
                              ( CAMERA_WIDTH, CAMERA_HEIGHT, px_to_kph, speed_units ))
        print("OpenCV Settings . MIN_AREA=%i sq-px  BLUR_SIZE=%i  THRESHOLD_SENSITIVITY=%i  CIRCLE_SIZE=%i px" %
                               ( MIN_AREA, BLUR_SIZE, THRESHOLD_SENSITIVITY, CIRCLE_SIZE ))
        print("                  WINDOW_BIGGER=%i gui_window_on=%s (Display OpenCV Status Windows on GUI Desktop)" %
                               ( WINDOW_BIGGER, gui_window_on ))
        print("                  CAMERA_FRAMERATE=%i fps video stream speed" % ( CAMERA_FRAMERATE ))
        print("Sub-Directories . imageSubDirMaxHours=%i (0=off)  imageSubDirMaxFiles=%i (0=off)" %
                                         ( imageSubDirMaxHours, imageSubDirMaxFiles ))
        print("                  imageRecentDir=%s imageRecentMax=%i (0=off)" %
                                         ( imageRecentDir, imageRecentMax ))
        if spaceTimerHrs > 0:   # Check if disk mgmnt is enabled
            print("Disk Space  ..... Enabled - Manage Target Free Disk Space. Delete Oldest %s Files if Needed" % (spaceFileExt))
            print("                  Check Every spaceTimerHrs=%i hr(s) (0=off)  Target spaceFreeMB=%i MB  min is 100 MB)" %
                                                   ( spaceTimerHrs, spaceFreeMB))
            print("                  If Needed Delete Oldest spaceFileExt=%s  spaceMediaDir=%s" %
                                                    ( spaceFileExt, spaceMediaDir ))
        else:
            print("Disk Space  ..... Disabled - spaceTimerHrs=%i  Manage Target Free Disk Space. Delete Oldest %s Files" %
                                                    ( spaceTimerHrs, spaceFileExt ))
            print("            ..... spaceTimerHrs=%i (0=Off)  Target spaceFreeMB=%i (min=100 MB)" %
                                                    ( spaceTimerHrs, spaceFreeMB ))
        print("")
        print("-------------------------------------------------------------------------------------------------")
    return

#-----------------------------------------------------------------------------------------------
def take_calibration_image(filename, cal_image):
    # Create a calibration image for determining value of IMG_VIEW_FT variable
    # Create calibation hash marks
    for i in range ( 10, CAMERA_WIDTH - 9, 10 ):
        cv2.line( cal_image,( i ,y_upper - 5 ),( i, y_upper + 30 ),cvRed, 1 )
    # This is motion window
    cv2.line( cal_image,( x_left, y_upper ),( x_right, y_upper ),cvBlue,1 )
    cv2.line( cal_image,( x_left, y_lower ),( x_right, y_lower ),cvBlue,1 )
    cv2.line( cal_image,( x_left, y_upper ),( x_left , y_lower ),cvBlue,1 )
    cv2.line( cal_image,( x_right, y_upper ),( x_right, y_lower ),cvBlue,1 )

    print("")
    print("----------------------------------- Create Calibration Image --------------------------------------")
    print("")
    print("    Instructions for using %s image for camera calibration" % ( filename ))
    print("")
    print("1 - Use a known size reference object in the image like a vehicle at the required distance.")
    print("2 - Record cal_obj_px  Value using Red y_upper hash marks at every 10 px")
    print("3 - Record cal_obj_mm of object. This is Actual length in mm of object above")
    print("4 - Edit config.py and enter the values for the above variables.")
    print("")
    print("    Calibration Image Saved To %s%s" % ( baseDir, filename ))
    print("")
    print("---------------------------- Press cntl-c to Quit Calibration Mode --------------------------------")
    print("")
    return cal_image

#-----------------------------------------------------------------------------------------------
def subDirLatest(directory): # Scan for directories and return most recent
    dirList = [ name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name)) ]
    if len(dirList) > 0:
        lastSubDir = sorted(dirList)[-1]
        lastSubDir = os.path.join(directory, lastSubDir)
    else:
        lastSubDir = directory
    return lastSubDir

#-----------------------------------------------------------------------------------------------
def subDirCreate(directory, prefix):
    now = datetime.datetime.now()
    # Specify folder naming
    subDirName = ('%s%d%02d%02d-%02d%02d' % (prefix, now.year, now.month, now.day, now.hour, now.minute))
    subDirPath = os.path.join(directory, subDirName)
    if not os.path.exists(subDirPath):
        try:
            os.makedirs(subDirPath)
        except OSError as err:
            logging.error('Cannot Create Directory %s - %s, using default location.', subDirPath, err)
            subDirPath = directory
        else:
            logging.info('Created %s', subDirPath)
    else:
        subDirPath = directory
    return subDirPath

#-----------------------------------------------------------------------------------------------
def deleteOldFiles(maxFiles, dirPath, prefix):
    # Delete Oldest files gt or eq to maxfiles that match filename prefix
    try:
        fileList = sorted(glob.glob(os.path.join(dirPath, prefix + '*')), key=os.path.getmtime)
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

#-----------------------------------------------------------------------------------------------
def subDirCheckMaxFiles(directory, filesMax):  # Count number of files in a folder path
    fileList = glob.glob(directory + '/*jpg')
    count = len(fileList)
    if count > filesMax:
        makeNewDir = True
        logging.info('Total Files in %s Exceeds %i ' % ( directory, filesMax ))
    else:
        makeNewDir = False
    return makeNewDir

#-----------------------------------------------------------------------------------------------
def subDirCheckMaxHrs(directory, hrsMax, prefix):   # Note to self need to add error checking
    # extract the date-time from the directory name
    dirName = os.path.split(directory)[1]   # split dir path and keep dirName
    dirStr = dirName.replace(prefix,'')   # remove prefix from dirName so just date-time left
    dirDate = datetime.datetime.strptime(dirStr, "%Y-%m-%d-%H:%M")  # convert string to datetime
    rightNow = datetime.datetime.now()   # get datetime now
    diff =  rightNow - dirDate           # get time difference between dates
    days, seconds = diff.days, diff.seconds
    dirAgeHours = days * 24 + seconds // 3600  # convert to hours
    if dirAgeHours > hrsMax:   # See if hours are exceeded
        makeNewDir = True
        logging.info('MaxHrs %i Exceeds %i for %s' % ( dirAgeHours, hrsMax, directory ))
    else:
        makeNewDir = False
    return makeNewDir

#-----------------------------------------------------------------------------------------------
def subDirChecks(maxHours, maxFiles, directory, prefix):
    # Check if motion SubDir needs to be created
    if maxHours < 1 and maxFiles < 1:  # No Checks required
        # logging.info('No sub-folders Required in %s', directory)
        subDirPath = directory
    else:
        subDirPath = subDirLatest(directory)
        if subDirPath == directory:   # No subDir Found
            logging.info('No sub folders Found in %s' % directory)
            subDirPath = subDirCreate(directory, prefix)
        elif ( maxHours > 0 and maxFiles < 1 ):   # Check MaxHours Folder Age Only
            if subDirCheckMaxHrs(subDirPath, maxHours, prefix):
                subDirPath = subDirCreate(directory, prefix)
        elif ( maxHours < 1 and maxFiles > 0):   # Check Max Files Only
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

#-----------------------------------------------------------------------------------------------
def filesToDelete(mediaDirPath, extension=image_format):
    return sorted(
        (os.path.join(dirname, filename)
        for dirname, dirnames, filenames in os.walk(mediaDirPath)
        for filename in filenames
        if filename.endswith(extension)),
        key=lambda fn: os.stat(fn).st_mtime, reverse=True)

#-----------------------------------------------------------------------------------------------
def saveRecent(recentMax, recentDir, filename, prefix):
    # save specified most recent files (timelapse and/or motion) in recent subfolder
    deleteOldFiles(recentMax, recentDir, prefix)
    try:    # Copy image file to recent folder
        shutil.copy(filename, recentDir)
    except OSError as err:
        logging.error('Copy from %s to %s - %s', filename, oldestFile, err)

#-----------------------------------------------------------------------------------------------
def freeSpaceUpTo(spaceFreeMB, mediaDir, extension=image_format):
    # Walks mediaDir and deletes oldest files until spaceFreeMB is achieved
    # Use with Caution
    mediaDirPath = os.path.abspath(mediaDir)
    if os.path.isdir(mediaDirPath):
        MB2Bytes = 1048576  # Conversion from MB to Bytes
        targetFreeBytes = spaceFreeMB * MB2Bytes
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
                                   targetFreeBytes / MB2Bytes, availFreeBytes / MB2Bytes, delcnt, totFiles )
                if delcnt > totFiles / 4:  # Avoid deleting more than 1/4 of files at one time
                    logging.warning('Max Deletions Reached %i of %i', delcnt, totFiles)
                    logging.warning('Deletions Restricted to 1/4 of total files per session.')
                    break
        logging.info('Session Ended')
    else:
        logging.error('Directory Not Found - %s', mediaDirPath)

#-----------------------------------------------------------------------------------------------
def freeDiskSpaceCheck(lastSpaceCheck):
    if spaceTimerHrs > 0:   # Check if disk free space timer hours is enabled
        # See if it is time to do disk clean-up check
        if ((datetime.datetime.now() - lastSpaceCheck).total_seconds() > spaceTimerHrs * 3600):
            lastSpaceCheck = datetime.datetime.now()
            if spaceFreeMB < 100:   # set freeSpaceMB to reasonable value if too low
                diskFreeMB = 100
            else:
                diskFreeMB = spaceFreeMB
            logging.info('spaceTimerHrs=%i  diskFreeMB=%i  spaceMediaDir=%s spaceFileExt=%s',
                           spaceTimerHrs, diskFreeMB, spaceMediaDir, spaceFileExt)
            freeSpaceUpTo(diskFreeMB, spaceMediaDir, spaceFileExt)
    return lastSpaceCheck

#-----------------------------------------------------------------------------------------------
def get_image_name(path, prefix):
    # build image file names by number sequence or date/time
    rightNow = datetime.datetime.now()
    filename = ("%s/%s%04d%02d%02d-%02d%02d%02d.jpg" %
          ( path, prefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second ))
    return filename

#-----------------------------------------------------------------------------------------------
def log_to_csv_file(data_to_append):
    log_file_path = baseDir + baseFileName + ".csv"
    if not os.path.exists(log_file_path):
        open( log_file_path, 'w' ).close()
        f = open( log_file_path, 'ab' )
        # header_text = '"YYYYMMDD","HH","MM","Speed","Unit","    Speed Photo Path            ","X","Y","W","H","Area","Direction"' + "\n"
        # f.write( header_text )
        f.close()
        logging.info("Create New Data Log File %s", log_file_path )
    filecontents = data_to_append + "\n"
    f = open( log_file_path, 'a+' )
    f.write( filecontents )
    f.close()
    return

#----------------------------------------------------------------------------------------------
def speed_camera():
    ave_speed = 0.0
    # initialize variables
    frame_count = 0
    fps_time = time.time()
    first_event = True   # Start a New Motion Track
    event_timer = time.time()
    start_pos_x = 0
    end_pos_x = 0
    # setup buffer area to ensure contour is fully contained in crop area
    x_buf = int((x_right - x_left) / 10 )
    y_buf = int((y_lower - y_upper) / 8 )
    travel_direction = ""

    # initialize a cropped grayimage1 image
    # Only needs to be done once
    image2 = vs.read()    # Get image from PiVideoSteam thread instance
    try:
        # crop image to motion tracking area only
        image_crop = image2[y_upper:y_lower,x_left:x_right]
    except:
        vs.stop()
        print("ERROR : Problem Connecting To Camera Stream.")
        print("        Restarting Camera.  One Moment Please .....")
        time.sleep(4)
        return

    if verbose:
        if gui_window_on:
            print("INFO  : Press lower case q on OpenCV GUI Window to Quit program")
            print("        or ctrl-c in this terminal session to Quit")
        else:
            print("INFO  : Press ctrl-c in this terminal session to Quit")

        if loggingToFile:
            print("INFO  : Sending Logging Data to %s (Console Messages Disabled)" %( logFilePath ))
        else:
            print("INFO  : Start Logging Speed Camera Activity")
    else:
        print("INFO  : Note Logging Messages Disabled per verbose=%s" % verbose)

    if pluginEnable:
        print("INFO  : Plugin %s is Enabled." % pluginName)

    if calibrate:
        print("INFO  : IMPORTANT: Camera Is In Calibration Mode ....")
    logging.info("Start Motion Tracking .....")
    # Calculate position of text on the images
    font = cv2.FONT_HERSHEY_SIMPLEX
    if image_text_bottom:
        text_y = ( image_height - 50 )  # show text at bottom of image
    else:
        text_y = 10  # show text at top of image

    grayimage1 = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
    event_timer = time.time()
    # Initialize prev_image used for taking speed image photo
    prev_image = image2
    still_scanning = True
    lastSpaceCheck = datetime.datetime.now()
    speed_path = image_path
    while still_scanning:    # process camera thread images and calculate speed
        image2 = vs.read()    # Get image from PiVideoSteam thread instance
        if WEBCAM:
            if ( WEBCAM_HFLIP and WEBCAM_VFLIP ):
                image2 = cv2.flip( image2, -1 )
            elif WEBCAM_HFLIP:
                image2 = cv2.flip( image2, 1 )
            elif WEBCAM_VFLIP:
                image2 = cv2.flip( image2, 0 )

        # crop image to motion tracking area only
        image_crop = image2[ y_upper:y_lower, x_left:x_right ]

        if time.time() - event_timer > event_timeout:  # Check if event timed out
            # event_timer exceeded so reset for new track
            event_timer = time.time()
            first_event = True
            start_pos_x = 0
            end_pos_x = 0

        if display_fps:   # Optionally show motion image processing loop fps
            fps_time, frame_count = get_fps( fps_time, frame_count )

        # initialize variables
        motion_found = False
        biggest_area = MIN_AREA
        cx, cy = 0, 0   # Center of contour used for tracking
        mw, mh = 0, 0   # w,h width, height of contour

        # Convert to gray scale, which is easier
        grayimage2 = cv2.cvtColor( image_crop, cv2.COLOR_BGR2GRAY )
        # Get differences between the two greyed images
        differenceimage = cv2.absdiff( grayimage1, grayimage2 )
        # Blur difference image to enhance motion vectors
        differenceimage = cv2.blur( differenceimage,(BLUR_SIZE,BLUR_SIZE ))
        # Get threshold of blurred difference image based on THRESHOLD_SENSITIVITY variable
        retval, thresholdimage = cv2.threshold( differenceimage, THRESHOLD_SENSITIVITY, 255, cv2.THRESH_BINARY )
        try:
            thresholdimage, contours, hierarchy = cv2.findContours( thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
        except:
            contours, hierarchy = cv2.findContours( thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
        total_contours = len( contours )
        # Update grayimage1 to grayimage2 ready for next image2
        grayimage1 = grayimage2

        # find contour with biggest area
        if contours:
            for c in contours:
                # get area of next contour
                found_area = cv2.contourArea(c)
                if found_area > biggest_area:
                    ( x, y, w, h ) = cv2.boundingRect(c)
                    # check if complete contour is completely within crop area
                    if ( x > x_buf and
                         x + w < x_right - x_left - x_buf and
                         y > y_buf and
                         y + h < y_lower - y_upper - y_buf ):
                        motion_found = True
                        biggest_area = found_area
                        cx = int(x + w/2)   # put circle in middle of width
                        cy = int(y + h/2)   # put circle in middle of height
                        mw = w
                        mh = h

            if motion_found:
                # Process motion event and track data
                if first_event:   # This is a first valide motion event
                    first_event = False
                    start_pos_x = cx
                    end_pos_x = cx
                    track_start_time = time.time()
                    logging.info("New Track    - Motion at cx,cy(%i,%i)", cx, cy )
                else:
                    if ( abs( cx - end_pos_x ) > x_diff_min and abs( cx - end_pos_x ) < x_diff_max ):
                        # movement is within acceptable distance range of last event
                        end_pos_x = cx
                        tot_track_dist = abs( end_pos_x - start_pos_x )
                        tot_track_time = abs( time.time() - track_start_time )
                        ave_speed = float((abs( tot_track_dist / tot_track_time)) *  speed_conv)
                        if abs( end_pos_x - start_pos_x ) > track_len_trig:
                            if end_pos_x - start_pos_x > 0:
                                travel_direction = "L2R"
                            else:
                                travel_direction = "R2L"
                            # Track length exceeded so take process speed photo
                            if ave_speed > max_speed_over or calibrate:
                                logging.info(" Event Add   - cx,cy(%i,%i) %3.2f %s %s px=%i/%i C=%i A=%i sqpx",
                                                            cx, cy, ave_speed, speed_units, travel_direction,
                                                            abs( start_pos_x - end_pos_x), track_len_trig,
                                                            total_contours, biggest_area)
                                # Resized and process prev image before saving to disk
                                prev_image = image2
                                if calibrate:       # Create a calibration image
                                    filename = get_image_name( speed_path, "calib-" )
                                    prev_image = take_calibration_image( filename, prev_image )
                                else:
                                    # Check if subdirectories configured and create as required
                                    speed_path = subDirChecks( imageSubDirMaxHours, imageSubDirMaxFiles,
                                                                                image_path, image_prefix)
                                    if image_filename_speed :
                                        speed_prefix = str(int(round(ave_speed))) + "-" + image_prefix
                                    else:
                                        speed_prefix = image_prefix
                                    filename = get_image_name( speed_path, speed_prefix)

                                if spaceTimerHrs > 0:  # if required check free disk space and delete older files (jpg)
                                    lastSpaceCheck = freeDiskSpaceCheck(lastSpaceCheck)

                                if image_max_files > 0:    # Manage a maximum number of files and delete oldest if required.
                                    deleteOldFiles(image_max_files, speed_path, image_prefix)

                                # Add motion rectangle to image
                                if image_show_motion_area:
                                    if SHOW_CIRCLE:
                                        cv2.circle(prev_image,( cx + x_left ,cy + y_upper ),
                                                             CIRCLE_SIZE,cvRed, LINE_THICKNESS )
                                    cv2.line( prev_image ,( x_left, y_upper ),( x_right, y_upper ),cvRed,1 )
                                    cv2.line( prev_image ,( x_left, y_lower ),( x_right, y_lower ),cvRed,1 )
                                    cv2.line( prev_image ,( x_left, y_upper ),( x_left , y_lower ),cvRed,1 )
                                    cv2.line( prev_image ,( x_right, y_upper ),( x_right, y_lower ),cvRed,1 )

                                big_image = cv2.resize(prev_image,(image_width, image_height))
                                if image_text_on:
                                    # Write text on image before saving
                                    image_text = "SPEED %.1f %s - %s" % ( ave_speed, speed_units, filename )
                                    text_x =  int(( image_width / 2) - (len( image_text ) * image_font_size / 3) )
                                    if text_x < 2:
                                        text_x = 2
                                    logging.info(" Average Speed is %.1f %s  ", ave_speed, speed_units)
                                    cv2.putText( big_image,image_text,(text_x,text_y), font,FONT_SCALE,(cvWhite),2)
                                logging.info(" Saved %s", filename)
                                cv2.imwrite(filename, big_image)

                                if imageRecentMax > 0 and not calibrate:  # Optional save most recent files to a recent folder
                                    saveRecent(imageRecentMax, imageRecentDir, filename, image_prefix)

                                if log_data_to_CSV:    # Format and Save Data to CSV Log File
                                    log_time = datetime.datetime.now()
                                    log_csv_time = ("%s%04d%02d%02d%s,%s%02d%s,%s%02d%s" %
                                                  ( quote, log_time.year, log_time.month,
                                                    log_time.day, quote, quote, log_time.hour,
                                                    quote, quote, log_time.minute, quote))

                                    log_csv_text = ("%s,%.2f,%s%s%s,%s%s%s,%i,%i,%i,%i,%i,%s%s%s" %
                                                ( log_csv_time, ave_speed, quote, speed_units,
                                                  quote, quote, filename, quote, cx, cy, mw, mh, mw * mh,
                                                  quote, travel_direction, quote ))
                                    log_to_csv_file( log_csv_text )

                                logging.info("End Track    - Tracked %i px in %.3f sec", tot_track_dist, tot_track_time )
                            else:
                                logging.info("End Track    - Skip Photo SPEED %.1f %s max_speed_over=%i  %i px in %.3f sec  C=%i A=%i sqpx ",
                                                            ave_speed, speed_units, max_speed_over, tot_track_dist,
                                                            tot_track_time, total_contours, biggest_area )

                            # Track Ended so Reset Variables for next cycle through loop
                            start_pos_x = 0
                            end_pos_x = 0
                            first_event = True
                            time.sleep( track_timeout )  # Pause so object is not immediately tracked again
                        else:
                            logging.info(" Event Add   - cx,cy(%i,%i) %3.1f %s px=%i/%i C=%i A=%i sqpx",
                                                         cx, cy, ave_speed, speed_units, abs( start_pos_x - end_pos_x),
                                                         track_len_trig, total_contours, biggest_area )
                            end_pos_x = cx
                    else:
                        if show_out_range:
                            logging.info(" Out Range   - cx,cy(%i,%i) Dist=%i is <%i or >%i px  C=%2i A=%i sqpx",
                                                         cx, cy, abs( cx - end_pos_x ), x_diff_min, x_diff_max,
                                                         total_contours, biggest_area  )
            if gui_window_on:
                # show small circle at motion location
                if SHOW_CIRCLE:
                    cv2.circle(image2,( cx + x_left * WINDOW_BIGGER ,cy + y_upper * WINDOW_BIGGER ),CIRCLE_SIZE, cvRed, LINE_THICKNESS)
                else:
                    cv2.rectangle(image2,( int( cx + x_left - mw/2) , int( cy + y_upper - mh/2)),
                                        (( int( cx + x_left + mw/2)), int( cy + y_upper + mh/2 )),cvRed, LINE_THICKNESS)
                event_timer = time.time()  # Reset event_timer since valid motion was found

        if gui_window_on:
            # cv2.imshow('Difference Image',difference image)
            cv2.line( image2,( x_left, y_upper ),( x_right, y_upper ),cvRed,1 )
            cv2.line( image2,( x_left, y_lower ),( x_right, y_lower ),cvRed,1 )
            cv2.line( image2,( x_left, y_upper ),( x_left , y_lower ),cvRed,1 )
            cv2.line( image2,( x_right, y_upper ),( x_right, y_lower ),cvRed,1 )
            image_view = cv2.resize( image2,( image_width, image_height ))
            cv2.imshow('Movement (q Quits)', image_view)
            if show_thresh_on:
                cv2.imshow('Threshold', thresholdimage)
            if show_crop_on:
                cv2.imshow('Crop Area',image_crop)
            # Close Window if q pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                print("End Motion Tracking ......")
                vs.stop()
                still_scanning = False

#-----------------------------------------------------------------------------------------------
if __name__ == '__main__':

    show_settings()
    try:
        WEBCAM_TRIES = 0
        while True:
            # Save images to an in-program stream
            # Setup video stream on a processor Thread for faster speed
            if WEBCAM:   #  Start Web Cam stream (Note USB webcam must be plugged in)
                WEBCAM_TRIES += 1
                print("INFO  : Initializing USB Web Camera Try .. %i" % WEBCAM_TRIES)
                vs = WebcamVideoStream().start()
                vs.CAM_SRC = WEBCAM_SRC
                vs.CAM_WIDTH = WEBCAM_WIDTH
                vs.CAM_HEIGHT = WEBCAM_HEIGHT
                if WEBCAM_TRIES > 3:
                    print("ERROR : USB Web Cam Not Connecting to WEBCAM_SRC %i" % WEBCAM_SRC)
                    print("        Check Camera is Plugged In and Working on Specified SRC")
                    print("        and Not Used(busy) by Another Process.")
                    print("INFO  : Exiting %s" % progName)
                    quit()
                time.sleep(4.0)  # Allow WebCam to initialize
            else:
                print("INFO  : Initializing Pi Camera ....")
                vs = PiVideoStream().start()
                vs.camera.rotation = CAMERA_ROTATION
                vs.camera.hflip = CAMERA_HFLIP
                vs.camera.vflip = CAMERA_VFLIP
                time.sleep(2.0)  # Allow PiCamera to initialize
            speed_camera()
    except KeyboardInterrupt:
        vs.stop()
        print("")
        print("+++++++++++++++++++++++++++++++++++")
        print("User Pressed Keyboard ctrl-c")
        print("%s %s - Exiting" % (progName, version))
        print("+++++++++++++++++++++++++++++++++++")
        print("")
        quit(0)


