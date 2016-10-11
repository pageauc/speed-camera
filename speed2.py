#!/usr/bin/env python
version = "version 2.09"

"""
speed2 written by Claude Pageau pageauc@gmail.com
Raspberry (Pi) - python opencv2 Speed tracking using picamera module
GitHub Repo here https://github.com/pageauc/motion-track/tree/master/speed-track-2

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

wget https://raw.github.com/pageauc/motion-track/master/speed-track-2/install.sh
chmod +x install.sh
./install.sh
./speed2.py

"""
print("Loading Please Wait ....")
print("-------------------------------------------------------------------------------------------------")
print("speed2.py %s using python2 and OpenCV2    written by Claude Pageau" % ( version ))

# Setup program folder path requirements
import os
mypath=os.path.abspath(__file__)       # Find the full path of this python script
baseDir=mypath[0:mypath.rfind("/")+1]  # get the path location only (excluding script name)
baseFileName=mypath[mypath.rfind("/")+1:mypath.rfind(".")]
progName = os.path.basename(__file__)

# Check for variable config.py file to import and quit if Not Found.
configFilePath = baseDir + "config.py"
if not os.path.exists(configFilePath):
    print("ERROR - Missing config.py file - Could not import Configuration file %s" % (configFilePath))
    quit()
else:
    # File exists so read Configuration variables from config.py file
    from config import *

# import the necessary packages
from picamera.array import PiRGBArray
import numpy as np
from picamera import PiCamera
from threading import Thread

import sys  
try:
    import cv2
except:
    print("------------------------------------")
    print("Error - Could not import cv2 library")
    print("")
    if (sys.version_info > (3, 0)):
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

import io
import time
import datetime
if not (sys.version_info > (3, 0)):
    import pyexiv2
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# System Settings    
image_width  = int(CAMERA_WIDTH * WINDOW_BIGGER)        # Set width of trigger point image to save 
image_height = int(CAMERA_HEIGHT * WINDOW_BIGGER)       # Set height of trigger point image to save    
    
# Calculate conversion from camera pixel width to actual speed.
px_to_mph = float(( CAMERA_WIDTH / IMAGE_VIEW_FT ) * 5280 / 3600)

if SPEED_MPH:
    speed_units = "mph"
    speed_conv = 1.0 * px_to_mph
else:
    speed_units = "kph"
    speed_conv = 1.609344 * px_to_mph

quote = '"'  # Used for creating quote delimited log file of speed data
    
#-----------------------------------------------------------------------------------------------    
def show_time():
    rightNow = datetime.datetime.now()
    currentTime = "%04d%02d%02d_%02d:%02d:%02d" % ( rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second )
    return currentTime    

#-----------------------------------------------------------------------------------------------    
def show_message(function_name, message_str):
    if verbose:
        now = show_time()
        print("%s %s - %s " % ( now, function_name, message_str ))
    return
    
#----------------------------------------------------------------------------------------------
def get_fps( start_time, frame_count ):
    # Calculate and display frames per second processing
    if frame_count >= 1000:
        duration = float( time.time() - start_time )
        FPS = float( frame_count / duration )
        print("%s get_fps - %.2f fps Last %i Frames" %( show_time(), FPS, frame_count ))
        frame_count = 0
        start_time = time.time()
    else:
        frame_count += 1
    return start_time, frame_count   
    
#-----------------------------------------------------------------------------------------------
def show_settings():
    if verbose:
        if not os.path.isdir(image_path):
            msgStr = "Creating Image Storage Folder " + image_path
            show_message ("show_settings", msgStr)
            os.makedirs(image_path)
        print("")
        print("Note: To Send Full Output to File Use command -   python -u ./%s | tee -a log.txt" % progName)
        print("      Set log_data_to_file=True to Send speed_Data to CSV File %s.log" % baseFileName) 
        print("-------------------------------------- Settings -------------------------------------------------")
        print("")
        print("Message Display . verbose=%s  display_fps=%s calibrate=%s" % ( verbose, display_fps, calibrate ))
        print("                  show_out_range=%s" % ( show_out_range ))
        print("Logging ......... Log_data_to_file=%s  log_filename=%s.csv (CSV format)"  % ( log_data_to_file, baseFileName ))
        print("                  Log if max_speed_over > %i %s" % ( max_speed_over, speed_units))        
        print("Speed Trigger ... If  track_len_trig > %i px" % ( track_len_trig ))                      
        print("Exclude Events .. If  x_diff_min < %i or x_diff_max > %i px" % ( x_diff_min, x_diff_max )) 
        print("                  If  y_upper < %i or y_lower > %i px" % ( y_upper, y_lower ))
        print("                  or  x_left < %i or x_right > %i px" % ( x_left, x_right ))        
        print("                  If  max_speed_over < %i %s" % ( max_speed_over, speed_units ))         
        print("                  If  event_timeout > %i seconds Start New Track" % ( event_timeout ))         
        print("                  track_timeout=%i sec wait after Track Ends (avoid retrack of same object)" % ( track_timeout ))      
        print("Speed Photo ..... Size=%ix%i px  WINDOW_BIGGER=%i  rotation=%i  VFlip=%s  HFlip=%s " % ( image_width, image_height, WINDOW_BIGGER, CAMERA_ROTATION, CAMERA_VFLIP, CAMERA_HFLIP ))
        print("                  image_path=%s  image_Prefix=%s" % ( image_path, image_prefix ))
        print("                  image_font_size=%i px high  image_text_bottom=%s" % ( image_font_size, image_text_bottom ))
        print("Motion Settings . Size=%ix%i px  IMAGE_VIEW_FT=%i  speed_units=%s" % ( CAMERA_WIDTH, CAMERA_HEIGHT, IMAGE_VIEW_FT, speed_units ))
        print("OpenCV Settings . MIN_AREA=%i sq-px  BLUR_SIZE=%i  THRESHOLD_SENSITIVITY=%i  CIRCLE_SIZE=%i px" % ( MIN_AREA, BLUR_SIZE, THRESHOLD_SENSITIVITY, CIRCLE_SIZE ))
        print("                  gui_window_on=%s (Display OpenCV Status Windows on GUI Desktop)" % ( gui_window_on ))
        print("                  CAMERA_FRAMERATE=%i fps video stream speed" % ( CAMERA_FRAMERATE ))
        print("")
        print("-------------------------------------------------------------------------------------------------")
    return
  
def take_calibration_image(filename, cal_image):
    # Create a calibration image for determining value of IMG_VIEW_FT variable       
    cv2.line( cal_image,( 0,y_upper ),( CAMERA_WIDTH, y_upper ),(255,0,0), 1 )
    cv2.line( cal_image,( 0,y_lower ),( CAMERA_WIDTH, y_lower ),(255,0,0), 1 )
    for i in range ( 10, CAMERA_WIDTH - 9, 10 ):
        cv2.line( cal_image,( i ,y_upper - 5 ),( i, y_upper + 30 ),(255,0,0), 1 )
    print("")
    print("----------------------------------- Create Calibration Image --------------------------------------")    
    print("")
    print("    Instructions for using %s image to calculate value for IMG_VIEW_FT variable" % ( filename ))
    print("")
    print("1 - Use a known size reference object in the image like a vehicle at the required distance.")
    print("2 - Calculate the px to FT conversion using the reference object and the image y_upper marks at every 10 px")
    print("3 - Calculate IMG_VIEW_FT per formula below See speed-track.md for details")
    print("")
    print("    IMG_VIEW_FT = (%i * Ref_Obj_ft) / num_px_for_Ref_Object" % ( CAMERA_WIDTH ))
    print("    eg. (%i * 18) / 80 = %.1f" % ( CAMERA_WIDTH, ((CAMERA_WIDTH * 18)/80)))
    print("")
    print("4 - Update the IMG_VIEW_FT variable in the speed_settings.py file")
    print("5 - Perform a test using a vehicle at a known speed to verify calibration.")
    print("6 - Make sure y_upper and y_lower variables are correctly set for the roadway to monitor")
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
    filename = "%s/%s%04d%02d%02d-%02d%02d%02d.jpg" % ( path, prefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second )     
    return filename  

#-----------------------------------------------------------------------------------------------    
def log_to_file(data_to_append):
    if log_data_to_file:
        log_file_path = baseDir + baseFileName + ".csv"
        if not os.path.exists(log_file_path):
            open( log_file_path, 'w' ).close()
            header_text = '"YYYYMMDD","HH","MM","Speed","Unit","    Speed Photo Path            ","W","H","Area"' + "\n"
            f = open( log_file_path, 'ab' )
            f.write( header_text )
            f.close()
            msgStr = "Create New Data Log File %s" % log_file_path
            show_message("log_to_file ", msgStr)
        filecontents = data_to_append + "\n"
        f = open( log_file_path, 'ab' )
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
    TEXT = text_to_print
    font_path = '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf'
    font = ImageFont.truetype( font_path, font_size, encoding='unic' )
    text = TEXT.decode( 'utf-8' )

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
    msgStr = " Image Saved - " + text_to_print
    show_message("image_write ", msgStr)
    return
         
#----------------------------------------------------------------------------------------------    
def speed_camera():
    ave_speed = 0.0
    if verbose:
        if calibrate:
            print("In Calibration Mode ....")
        if gui_window_on:
            print("Press lower case q on OpenCV GUI Window to Quit program")
            print("or ctrl-c in this terminal session to Quit")
        else:
            print("Press ctrl-c in this terminal session to Quit")
        print("")
        
    msg_str = "Initializing Pi Camera ...."
    show_message("speed_camera", msg_str)

    # Setup video stream on a processor Thread for faster speed
    vs = PiVideoStream().start()
    vs.camera.rotation = CAMERA_ROTATION
    vs.camera.hflip = CAMERA_HFLIP
    vs.camera.vflip = CAMERA_VFLIP
    time.sleep(2.0)  # Give Camera time to initialize
     
    # initialize variables
    frame_count = 0
    fps_time = time.time()
    first_event = True   # Start a New Motion Track      
    event_timer = time.time()
    start_pos_x = 0
    end_pos_x = 0
    msgStr = "Start Speed Motion Tracking"
    show_message("speed_camera", msgStr)                     

    # initialize a cropped grayimage1 image
    # Only needs to be done once 
    image2 = vs.read()    # Get image from PiVideoSteam thread instance
    # crop image to motion tracking area only
    image_crop = image2[y_upper:y_lower,x_left:x_right]
    grayimage1 = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
    event_timer = time.time()
    # Initialize prev_image used for taking speed image photo
    prev_image = image2   
    still_scanning = True
    while still_scanning:    # process camera thread images and calculate speed
        image2 = vs.read()    # Get image from PiVideoSteam thread instance
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
        cx = 0
        cy = 0
        cw = 0
        ch = 0
        # Convert to gray scale, which is easier
        grayimage2 = cv2.cvtColor( image_crop, cv2.COLOR_BGR2GRAY )
        # Get differences between the two greyed images
        differenceimage = cv2.absdiff( grayimage1, grayimage2 )
        # Blur difference image to enhance motion vectors
        differenceimage = cv2.blur( differenceimage,(BLUR_SIZE,BLUR_SIZE ))
        # Get threshold of blurred difference image based on THRESHOLD_SENSITIVITY variable
        # Check if python 3 or 2 is running and proces opencv accordingly.
        if (sys.version_info > (3, 0)):
            thresholdimage,contours,hierarchy = cv2.findContours(differenceimage,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        else:
            retval, thresholdimage = cv2.threshold( differenceimage,THRESHOLD_SENSITIVITY,255,cv2.THRESH_BINARY )
            # Get all the contours found in the threshold image
            contours, hierarchy = cv2.findContours( thresholdimage,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE )
        total_contours = len( contours )
        # Update grayimage1 to grayimage2 ready for next image2
        grayimage1 = grayimage2
        
        # find contour with biggest area
        for c in contours:
            # get area of next contour
            found_area = cv2.contourArea(c)
            if found_area > biggest_area:
                motion_found = True
                biggest_area = found_area
                ( x, y, w, h ) = cv2.boundingRect(c)
                cx = int(x + w/2) + x_left   # put circle in middle of width
                cy = int(y + h/2) + y_upper  # put circle in middle of height
                cw = w
                ch = h
                
        if motion_found:
            # Process motion event and track data
            if first_event:   # This is a first valide motion event
                first_event = False
                start_pos_x = cx
                end_pos_x = cx
                track_start_time = time.time()                                   
                msgStr = "New Track    - Motion at cx=%3i cy=%3i" % ( cx, cy )
                show_message("speed_camera", msgStr)           
            else:
                if ( abs( cx - end_pos_x ) > x_diff_min and abs( cx - end_pos_x ) < x_diff_max ):
                # movement is within acceptable distance range of last event
                    end_pos_x = cx
                    tot_track_dist = abs( end_pos_x - start_pos_x )
                    tot_track_time = abs( time.time() - track_start_time )
                    ave_speed = float((abs( tot_track_dist / tot_track_time)) / speed_conv)
                    if abs( end_pos_x - start_pos_x ) > track_len_trig:
                        # Track length exceeded so take process speed photo                                     
                        if ave_speed > max_speed_over or calibrate:
                            # Resized and process prev image before saving to disk 
                            if calibrate:       # Create a calibration image                                             
                                filename = get_image_name( image_path, "calib-" )                                               
                                prev_image = take_calibration_image( filename, prev_image )                    
                            else:
                                speed_prefix = str(int(round(ave_speed))) + "-" + image_prefix                                               
                                filename = get_image_name( image_path, speed_prefix)
                            big_image = cv2.resize(prev_image,(image_width, image_height))                                            
                            cv2.imwrite(filename, big_image)
                            msgStr = " Event Add   - cx=%3i cy=%3i %3.1f %s Len=%3i of %i px Contours=%2i Area=%i " % ( cx, cy, ave_speed, speed_units, abs( start_pos_x - end_pos_x), track_len_trig, total_contours, biggest_area )
                            show_message("speed_camera", msgStr)                  
                            # Format and Save Data to CSV Log File
                            log_time = datetime.datetime.now()                                               
                            log_csv_time = "%s%04d%02d%02d%s,%s%02d%s,%s%02d%s" % ( quote, log_time.year, log_time.month, log_time.day, quote, quote, log_time.hour, quote, quote, log_time.minute, quote)                                          
                            # Add Text to image                                                
                            image_text = "SPEED %.1f %s - %s" % ( ave_speed, speed_units, filename )
                            image_write( filename, image_text )
                            log_text = "%s,%.2f,%s%s%s,%s%s%s,%i,%i,%i" % ( log_csv_time, ave_speed, quote, speed_units, quote, quote, filename, quote, cw, ch, cw * ch )
                            log_to_file( log_text )
                            msgStr = "End Track    - Tracked %i px in %.1f sec" % ( tot_track_dist, tot_track_time )
                            show_message("speed_camera", msgStr)                                                  
                        else:
                            msgStr = "End Track    - Skip Photo SPEED %.1f %s max_speed_over=%i  %i px in %.1f sec  Contours=%2i Area=%i sq-px " % ( ave_speed, speed_units, max_speed_over, tot_track_dist, tot_track_time, total_contours, biggest_area )
                            show_message("speed_camera", msgStr)
                        # Track Ended so Reset Variables for next cycle through loop
                        start_pos_x = 0
                        end_pos_x = 0
                        first_event = True                         
                        time.sleep( track_timeout )  # Pause so object is not immediately tracked again 
                    else:
                        msgStr = " Event Add   - cx=%3i cy=%3i %3.1f %s Len=%3i of %i px Contours=%2i Area=%i" % ( cx, cy, ave_speed, speed_units, abs( start_pos_x - end_pos_x), track_len_trig, total_contours, biggest_area )
                        end_pos_x = cx
                        show_message("speed_camera", msgStr)
                    prev_image = image2  # keep a colour copy for saving to disk at end of Track
                else:
                    if show_out_range:
                        msgStr = " Out Range   - cx=%3i cy=%3i Dist=%3i is <%i or >%i px  Contours=%2i Area=%i" % ( cx, cy, abs( cx - end_pos_x ), x_diff_min, x_diff_max, total_contours, biggest_area  )                                    
                        show_message("speed_camera", msgStr)                             
             
            if gui_window_on:
                # show small circle at motion location
                cv2.circle( image2,( cx,cy ),CIRCLE_SIZE,( 0,255,0 ), 2 )

                if ave_speed > 0:
                    speed_text = str('%3.1f %s'  % ( ave_speed, speed_units )) 
                    cv2.putText( image2, speed_text, (cx + 8, cy), cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE , (255,255,255), 1)                           
            event_timer = time.time()  # Reset event_timer since valid motion was found
            
        if gui_window_on:
            # cv2.imshow('Difference Image',difference image) 
            cv2.line( image2,( x_left, y_upper ),( x_right, y_upper ),(255,0,0),1 )
            cv2.line( image2,( x_left, y_lower ),( x_right, y_lower ),(255,0,0),1 )                              
            cv2.line( image2,( x_left, y_upper ),( x_left , y_lower ),(255,0,0),1 )
            cv2.line( image2,( x_right, y_upper ),( x_right, y_lower ),(255,0,0),1 )
            image2 = cv2.resize( image2,( image_width, image_height ))                         
            #cv2.imshow('Threshold Image', thresholdimage)
            cv2.imshow('Movement Status (Press q Here to Quit)', image2)
            cv2.imshow('Movement Crop Area',image_crop)
            # Close Window if q pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                print("End Motion Tracking ......")
                vs.stop()
                still_scanning = False

#-----------------------------------------------------------------------------------------------    
if __name__ == '__main__':
    try:
        show_settings()  
        speed_camera()
    finally:
        print("")
        print("+++++++++++++++++++++++++++++++++++")
        print("%s - Exiting Program" % progName)
        print("+++++++++++++++++++++++++++++++++++")
        print("")                           
                            


