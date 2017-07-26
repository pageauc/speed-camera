#!/usr/bin/env python
version = "version 5.00"

"""
speed-cam.py written by Claude Pageau pageauc@gmail.com
Raspberry (Pi) - python opencv2 Speed tracking using picamera module or web cam
GitHub Repo here https://github.com/pageauc/rpi-speed-camera/tree/master/

This is a raspberry pi python opencv2 speed tracking demonstration program.
It will detect speed in the field of view and use opencv to calculate the
largest contour and return its x,y coordinate.  The image is tracked for
a specified threshold length and then the speed is calculated.
Note: Variables for this program are stored in config.py

Some of this code is based on a YouTube tutorial by
Kyle Hounslow using C here https://www.youtube.com/watch?v=X6rPdRZzgjg

Thanks to Adrian Rosebrock jrosebr1 at http://www.pyimagesearch.com
for the PiVideoStream Class code available on github at
https://github.com/jrosebr1/imutils/blob/master/imutils/video/pivideostream.py

Here is my YouTube video demonstrating a previous speed tracking demo
program using a Raspberry Pi B2 https://youtu.be/09JS7twPBsQ

Installation
Requires a Raspberry Pi with a RPI camera module installed and working
Install from a logged in SSH session per commands below

wget https://raw.github.com/pageauc/rpi-speed-camera/master/speed-install.sh
chmod +x speed-install.sh
./speed-install.sh
./speed-cam.py

"""
print("Loading Please Wait ....")
print("-------------------------------------------------------------------------------------------------")
print("speed-cam.py %s using python2 and OpenCV2    written by Claude Pageau" % ( version ))

import os
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
    print("ERROR - Missing config.py file - Could not find Configuration file %s" % (configFilePath))
    import urllib2
    config_url = "https://raw.github.com/pageauc/rpi-speed-camera/master/config.py"
    print("   Attempting to Download config.py file from %s" % ( config_url ))
    try:
        wgetfile = urllib2.urlopen(config_url)
    except:
        print("ERROR - Download of config.py Failed")
        print("   Try Rerunning the speed-install.sh Again.")
        print("   or")
        print("   Perform GitHub curl install per Readme.md")
        print("   and Try Again")
        print("Exiting %s" % ( progName ))
        quit()
    f = open('config.py','wb')
    f.write(wgetfile.read())
    f.close()
# Read Configuration variables from config.py file
from config import *

# fix possible invalid values
if WINDOW_BIGGER < 1:
    WINDOW_BIGGER = 1
if image_bigger < 1:
    image_bigger = 1

# import the necessary packages
from picamera.array import PiRGBArray
import numpy as np
from picamera import PiCamera
from threading import Thread
import logging
import io
import time
import datetime
import sys
if not (sys.version_info > (3, 0)):
    import pyexiv2
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

try:
    import cv2
except:
    print("------------------------------------")
    print("Error - Could not import cv2 library")
    print("")
    if (sys.version_info > (2, 9)):
        print("python3 failed to import cv2")
        print("Try installing opencv for python3")
        print("google for details regarding installing opencv for python3")
    else:
        print("python2 failed to import cv2")
        print("Try reinstalling per command")
        print("sudo apt-get install python-opencv")
    print("")
    print("Exiting speed2.py Due to Error")
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

#-----------------------------------------------------------------------------------------------
class PiVideoStream:
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=CAMERA_FRAMERATE, rotation=0, hflip=False, vflip=False):
        # initialize the camera and stream
        self.camera = PiCamera()
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
    html_path = "html"
    sym_name = "images"
    if not os.path.isdir(image_path):
        logging.info("Creating Image Storage Folder %s", image_path )
        os.makedirs(image_path)
    os.chdir(image_path)
    img_dir = os.getcwd()
    os.chdir(cwd)
    if not os.path.isdir(html_path):
        logging.info("Creating html Folder %s", html_path)
        os.makedirs(html_path)
    os.chdir(html_path)
    html_dir = os.getcwd()
    sym_path = html_dir + "/" + sym_name
    if not os.path.isdir(sym_path):
        os.chdir(html_dir)
        logging.info("Creating html Folder images symlink %s", sym_path)
        os.symlink(img_dir, sym_name)
    os.chdir(cwd)
    if verbose:
        print("")
        print("Note: To Send Full Output to File Use command -   python -u ./%s | tee -a log.txt" % progName)
        print("      Set log_data_to_file=True to Send speed_Data to CSV File %s.log" % baseFileName)
        print("-------------------------------------- Settings -------------------------------------------------")
        print("")
        print("Message Display . verbose=%s  display_fps=%s calibrate=%s" % ( verbose, display_fps, calibrate ))
        print("                  show_out_range=%s" % ( show_out_range ))
        print("Logging ......... Log_data_to_file=%s  log_filename=%s.csv (CSV format)"  % ( log_data_to_file, baseFileName ))
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
def get_image_name(path, prefix):
    # build image file names by number sequence or date/time
    rightNow = datetime.datetime.now()
    filename = ("%s/%s%04d%02d%02d-%02d%02d%02d.jpg" %
          ( path, prefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second ))
    return filename

#-----------------------------------------------------------------------------------------------
def log_to_csv_file(data_to_append):
    if log_data_to_file:
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

#-----------------------------------------------------------------------------------------------
def image_write(image_filename, text_to_print):
    # function to write date/time stamp directly on top or bottom of images.
    FOREGROUND = ( 255, 255, 255 )  # rgb settings for white text foreground
    text_colour = "White"
    font_size = image_font_size

    # centre text and compensate for graphics text being wider
    x =  int(( image_width / 2) - (len( text_to_print ) * font_size / 4) )
    if image_text_bottom:
        y = ( image_height - 50 )  # show text at bottom of image
    else:
        y = 10  # show text at top of image
    text = text_to_print
    font_path = '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf'
    font = ImageFont.truetype( font_path, font_size, encoding='unic' )

    # Read exif data since ImageDraw does not save this metadata
    if not (sys.version_info > (3, 0)):
        metadata = pyexiv2.ImageMetadata(image_filename)
        metadata.read()
    img = Image.open( image_filename )
    draw = ImageDraw.Draw( img )
    # draw.text((x, y),"Sample Text",(r,g,b))
    draw.text( ( x, y ), text, FOREGROUND, font=font )
    img.save( image_filename )
    if not (sys.version_info > (3, 0)):
        metadata.write()    # Write previously saved exif data to image file
    logging.info("  Image Saved - %s", text_to_print )
    return

#----------------------------------------------------------------------------------------------
def speed_camera():
    ave_speed = 0.0
    if verbose:
        if loggingToFile:
            print("Sending Logging Data to %s  (Console Messages Disabled)" %( logFilePath ))
        if calibrate:
            print("In Calibration Mode ....")
        if gui_window_on:
            print("Press lower case q on OpenCV GUI Window to Quit program")
            print("or ctrl-c in this terminal session to Quit")
        else:
            print("Press ctrl-c in this terminal session to Quit")

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
    print("Start Speed Motion Tracking Ready ....")
    travel_direction = ""

    # initialize a cropped grayimage1 image
    # Only needs to be done once
    image2 = vs.read()    # Get image from PiVideoSteam thread instance
    try:
        # crop image to motion tracking area only
        image_crop = image2[y_upper:y_lower,x_left:x_right]
    except:
        vs.stop()
        print("Problem Connecting To Camera Stream.")
        print("Restarting Camera.  One Moment Please .....")
        time.sleep(4)
        return

    grayimage1 = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
    event_timer = time.time()
    # Initialize prev_image used for taking speed image photo
    prev_image = image2
    still_scanning = True
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
        image_crop = image2[y_upper:y_lower,x_left:x_right]

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
        mx, my = 0, 0   # x,y of top right position contour
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
                        mx = x
                        my = y
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
                                # Resized and process prev image before saving to disk
                                if calibrate:       # Create a calibration image
                                    filename = get_image_name( image_path, "calib-" )
                                    prev_image = take_calibration_image( filename, prev_image )
                                else:
                                    if image_filename_speed :
                                        speed_prefix = str(int(round(ave_speed))) + "-" + image_prefix
                                    else:
                                        speed_prefix = image_prefix
                                    filename = get_image_name( image_path, speed_prefix)
                                    # Add motion rectangle to image
                                    if image_show_motion_area:
                                        cv2.line( prev_image ,( x_left, y_upper ),( x_right, y_upper ),cvRed,1 )
                                        cv2.line( prev_image ,( x_left, y_lower ),( x_right, y_lower ),cvRed,1 )
                                        cv2.line( prev_image ,( x_left, y_upper ),( x_left , y_lower ),cvRed,1 )
                                        cv2.line( prev_image ,( x_right, y_upper ),( x_right, y_lower ),cvRed,1 )
                                big_image = cv2.resize(prev_image,(image_width, image_height))
                                cv2.imwrite(filename, big_image)
                                logging.info(" Event Add   - cx,cy(%i,%i) %3.2f %s %s Len=%i/%i px C=%i A=%i sqPx",
                                                            cx, cy, ave_speed, speed_units, travel_direction, 
                                                            abs( start_pos_x - end_pos_x), track_len_trig,
                                                            total_contours, biggest_area)

                                # Format and Save Data to CSV Log File
                                log_time = datetime.datetime.now()
                                log_csv_time = ("%s%04d%02d%02d%s,%s%02d%s,%s%02d%s" %
                                              ( quote, log_time.year, log_time.month,
                                                log_time.day, quote, quote, log_time.hour,
                                                quote, quote, log_time.minute, quote))
                                # Add Text to image
                                if image_text_on:
                                    image_text = "SPEED %.1f %s - %s" % ( ave_speed, speed_units, filename )
                                    image_write( filename, image_text )
                                log_csv_text = ("%s,%.2f,%s%s%s,%s%s%s,%i,%i,%i,%i,%i,%s%s%s" %
                                            ( log_csv_time, ave_speed, quote, speed_units,
                                              quote, quote, filename, quote, mx, my, mw, mh, mw * mh,
                                              quote, travel_direction, quote ))
                                log_to_csv_file( log_csv_text )
                                logging.info("End Track    - Tracked %i px in %.2f sec", tot_track_dist, tot_track_time )
                            else:
                                logging.info("End Track    - Skip Photo SPEED %.1f %s max_speed_over=%i  %i px in %.1f sec  C=%i A=%i sqPx ",
                                                            ave_speed, speed_units, max_speed_over, tot_track_dist,
                                                            tot_track_time, total_contours, biggest_area )
                                                            
                            # Track Ended so Reset Variables for next cycle through loop
                            start_pos_x = 0
                            end_pos_x = 0
                            first_event = True
                            time.sleep( track_timeout )  # Pause so object is not immediately tracked again
                        else:
                            logging.info(" Event Add   - cx,cy(%i,%i) %3.1f %s Len=%i/%i px C=%i A=%i sqPx",
                                                         cx, cy, ave_speed, speed_units, abs( start_pos_x - end_pos_x),
                                                         track_len_trig, total_contours, biggest_area )
                            end_pos_x = cx
                        prev_image = image2  # keep a colour copy for saving to disk at end of Track
                    else:
                        if show_out_range:
                            logging.info(" Out Range   - cx,cy(%i,%i) Dist=%i is <%i or >%i px  C=%2i A=%i sqPx",
                                                         cx, cy, abs( cx - end_pos_x ), x_diff_min, x_diff_max,
                                                         total_contours, biggest_area  )
            if gui_window_on:
                # show small circle at motion location
                if SHOW_CIRCLE:
                    cv2.circle(image2,( cx + x_left * WINDOW_BIGGER ,cy + y_upper * WINDOW_BIGGER ),CIRCLE_SIZE,cvGreen, LINE_THICKNESS)
                else:
                    cv2.rectangle(image2,( int( cx + x_left - mw/2) , int( cy + y_upper - mh/2)),
                                        (( int( cx + x_left + mw/2)), int( cy + y_upper + mh/2 )),cvGreen, LINE_THICKNESS)

                if ave_speed > 0:
                    speed_text = str('%3.1f %s'  % ( ave_speed, speed_units ))
                    cv2.putText( image2, speed_text, (cx + x_left + 8, cy + y_upper), cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE , cvWhite, 1)
            event_timer = time.time()  # Reset event_timer since valid motion was found

        if gui_window_on:
            # cv2.imshow('Difference Image',difference image)
            cv2.line( image2,( x_left, y_upper ),( x_right, y_upper ),cvBlue,1 )
            cv2.line( image2,( x_left, y_lower ),( x_right, y_lower ),cvBlue,1 )
            cv2.line( image2,( x_left, y_upper ),( x_left , y_lower ),cvBlue,1 )
            cv2.line( image2,( x_right, y_upper ),( x_right, y_lower ),cvBlue,1 )
            image2 = cv2.resize( image2,( image_width, image_height ))
            cv2.imshow('Movement (q Quits)', image2)
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
        while True:
            # Save images to an in-program stream
            # Setup video stream on a processor Thread for faster speed
            if WEBCAM:   #  Start Web Cam stream (Note USB webcam must be plugged in)
                print("Initializing USB Web Camera ....")
                vs = WebcamVideoStream().start()
                vs.CAM_SRC = WEBCAM_SRC
                vs.CAM_WIDTH = WEBCAM_WIDTH
                vs.CAM_HEIGHT = WEBCAM_HEIGHT
                time.sleep(4.0)  # Allow WebCam to initialize
            else:
                print("Initializing Pi Camera ....")
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


