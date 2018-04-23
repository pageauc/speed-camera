# ---------------- User Configuration Settings for speed-cam.py ---------------------------------
#         Ver 8.5 speed-cam.py Variable Configuration Settings (using picam480 plugin)

#######################################
#  speed-cam.py Variable Settings
#  Default is 320x240 image stream size
#  if using RPI3 you can try picam480 
#  or larger stream image plugin.
#######################################

# Calibration Settings
# --------------------
calibrate = True       # Create a calibration image file with calibration hash markers 10 px per mark
cal_obj_px = 90        # Length of a calibration object in pixels
cal_obj_mm = 4330.0    # Length of the calibration object in millimetres

# Plugins overlay the config.py variable settings
# -----------------------------------------------
pluginEnable = False
pluginName = "picam480" # Specify filename in plugins subfolder without .py extension per below
                        # picam240, webcam240 (Recommended for RPI2 or greater) 
                        # picam480, webcam480, picam720, webcam720  (Recommended for RPI3)
                        # picam1080   (Experimental Not Recommended)
                        # secpicam480, secwebcam480 (Experimental no csv entries)

# 480 Crop Area for motion detection Tracking
# Use plugins to override this configuration
# ---------------------------------------
x_left  = 25           # Default= 25 Exclude event if x less than this px position Default=25
x_right = 295          # Default= 295 Exclude event if x greater than this px position Default=295
y_upper = 75           # Default= 75 Exclude event if y less that this value Default=100
y_lower = 185          # Default= 185 Exclude event if y greater than this value Default=175

# Display opencv windows on gui desktop
# gui_window_on suppresses All Windows if False
# ----------------------------------------------
gui_window_on = False  # True= Turn On All desktop GUI openCV windows. False=Don't Show (req'd for SSH) .
show_thresh_on = False # Display desktop GUI openCV cropped threshold window. True=Show, False=Don't Show
show_crop_on = False   # Same as show_thresh_on but in color. True=Show, False=Don't Show (Default)

# Display and Log settings
# ------------------------
verbose = True         # True= Display basic status information on console False= Off
display_fps = False    # True= Show average frame count every 1000 loops False= Off
log_data_to_CSV = True # True= Save log data as CSV comma separated values  False= Off
loggingToFile = False  # True= Send logging to file False= No Logging to File
logFilePath = 'speed-cam.log'  # Location of log file when logDataToFile=True

# Motion Event Settings
# ---------------------
SPEED_MPH = False      # Set Speed Units   kph=False  mph=True
MIN_AREA = 200         # Default= 200 Exclude all contours less than or equal to this sq-px Area
track_len_trig = 60    # Default= 60 Length of track to trigger speed photo
show_out_range = True  # Default= True Show Out of Range Events per x_diff settings below False= Off
x_diff_max = 30        # Default= 30 Exclude if max px away >= last motion event x position
x_diff_min = 1         # Default= 1 Exclude if min px away <= last event x position
track_timeout = 0.0    # Default= 0.0 Optional seconds to wait after track End (Avoids dual tracking)
event_timeout = 0.7    # Default= 0.7 seconds to wait for next motion event before starting new track
max_speed_over = 0     # Exclude track if Speed less than or equal to value specified 0=All

# Camera Settings
# ---------------
WEBCAM = False         # Default = False False=PiCamera True=USB WebCamera

# Web Camera Settings
WEBCAM_SRC = 0         # Default= 0   USB opencv connection number
WEBCAM_WIDTH = 320     # Default= 320 USB Webcam Image width
WEBCAM_HEIGHT = 240    # Default= 240 USB Webcam Image height
WEBCAM_HFLIP = True    # Default= False USB Webcam flip image horizontally
WEBCAM_VFLIP = False   # Default= False USB Webcam flip image vertically

# Pi Camera Settings
# ------------------
CAMERA_WIDTH = 320     # Image stream width for opencv motion scanning Default=320
CAMERA_HEIGHT = 240    # Image stream height for opencv motion scanning  Default=240
CAMERA_FRAMERATE = 25  # Default= 25 Frame rate for video stream V2 picam can be higher
CAMERA_ROTATION = 0    # Rotate camera image valid values are 0, 90, 180, 270
CAMERA_VFLIP = True    # Flip the camera image vertically if required
CAMERA_HFLIP = True    # Flip the camera image horizontally if required

# Camera Image Settings
# ---------------------
image_path = "media/images"   # folder name to store images
image_prefix = "speed-"       # image name prefix
image_format = ".jpg"         # Default = ".jpg"  image Formats .jpeg .png .gif .bmp
image_show_motion_area = True # True= Display motion detection rectangle area on saved images
image_filename_speed = False  # True= Prefix filename with speed value
image_text_on = True          # True= Show Text on speed images   False= No Text on images
image_text_bottom = True      # True= Show image text at bottom otherwise at top
image_font_size = 12          # Default= 12 Font text height in px for text on images
image_bigger = 3.0            # Default= 3.0 Resize saved speed image by specified multiplier value
image_max_files = 0           # 0=off or specify MaxFiles to maintain then oldest are deleted  Default=0 (off)

# Optional Manage SubDir Creation by time, number of files or both (not recommended)
# ----------------------------------------------------------------
imageSubDirMaxFiles = 1000    # 0=off or specify MaxFiles - Creates New dated sub-folder if MaxFiles exceeded
imageSubDirMaxHours = 0       # 0=off or specify MaxHours - Creates New dated sub-folder if MaxHours exceeded

# Optional Save Most Recent files in recent folder
# ------------------------------------------------
imageRecentMax = 100          # 0=off  Maintain specified number of most recent files in motionRecentDir
imageRecentDir = "media/recent"  # Default= "media/recent"  save recent files directory path

# Optional Manage Free Disk Space Settings
# ----------------------------------------
spaceTimerHrs = 0             # Default= 0  0=off or specify hours frequency to perform free disk space check
spaceFreeMB = 500             # Default= 500  Target Free space in MB Required.
spaceMediaDir = 'media/images'  # Default= 'media/images'  Starting point for directory walk
spaceFileExt  = 'jpg'         # Default= 'jpg' File extension to Delete Oldest Files

# OpenCV Motion Settings
# ----------------------
SHOW_CIRCLE = False           # True=circle in center of motion, False=rectangle
CIRCLE_SIZE = 5               # Default= 5 Diameter circle in px if SHOW_CIRCLE = True
LINE_THICKNESS = 1            # Default= 1 Size of lines for circle or Rectangle
FONT_SCALE = 0.5              # Default= 0.5 OpenCV window text font size scaling factor Default=.5 (lower is smaller)
WINDOW_BIGGER = 1.0           # Default= 1.0 Resize multiplier for opencv window if gui_window_on=True
BLUR_SIZE = 10                # Default= 10 OpenCV setting for Gaussian difference image blur
THRESHOLD_SENSITIVITY = 20    # Default= 20 OpenCV setting for difference image threshold

#======================================
#       webserver.py Settings
#======================================

# Web Server settings
# -------------------
web_server_port = 8080        # Default= 8080 Web server access port eg http://192.168.1.100:8080
web_server_root = "media"     # Default= "media" webserver root path to webserver image/video sub-folders
web_page_title = "SPEED-CAMERA Media"  # web page title that browser show (not displayed on web page)
web_page_refresh_on = False   # False=Off (never)  Refresh True=On (per seconds below)
web_page_refresh_sec = "180"  # Default= "180" seconds to wait for web page refresh  seconds (three minutes)
web_page_blank = True         # True Starts left image with a blank page until a right menu item is selected
                              # False displays second list[1] item since first may be in progress

# Left iFrame Image Settings
# --------------------------
web_image_height = "768"       # Default= "768" px height of images to display in iframe
web_iframe_width_usage = "70%" # Left Pane - Sets % of total screen width allowed for iframe. Rest for right list
web_iframe_width = "100%"      # Desired frame width to display images. can be eg percent "80%" or px "1280"
web_iframe_height = "100%"     # Desired frame height to display images. Scroll bars if image larger (percent or px)

# Right Side Files List
# ---------------------
web_max_list_entries = 0           # 0 = All or Specify Max right side file entries to show (must be > 1)
web_list_height = web_image_height # Right List - side menu height in px (link selection)
web_list_by_datetime = True        # True=datetime False=filename
web_list_sort_descending = True    # reverse sort order (filename or datetime per web_list_by_datetime setting

# ---------------------------------------------- End of User Variables -----------------------------------------------------
