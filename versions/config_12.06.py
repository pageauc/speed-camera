# ---------------- User Configuration Settings for speed-cam.py ---------------------------------
#         Ver 12.04 speed-cam.py Variable Configuration Settings

#######################################
#  speed-cam.py Variable Settings
#  Default is 320x240 image stream size
#  Note motion track crop area is now
#  auto configured so you may not need to use a plugin
#  to change resolution.
#######################################

# Calibration Settings
# --------------------
calibrate = True         # Create a calibration image file with calibration hash markers 10 px per mark
SHOW_SETTINGS_ON = False  # True = Show config.py settings
align_cam_on = False     # Default=False True Saves align_cam.jpg See Web page recent align cam
align_delay_sec = 2      # Default=2 seconds delay between each alignment image (disables motion tracking)

cal_obj_px_L2R = 80      # L2R Moving Objects, Length of a calibration object in pixels
cal_obj_mm_L2R = 4700    # L2R Moving Objects, Length of the calibration object in millimetres

cal_obj_px_R2L = 85      # R2L Moving Objects, Length of a calibration object in pixels
cal_obj_mm_R2L = 4700    # R2L Moving Objects, Length of the calibration object in millimetres

# Camera Settings
# ---------------
CAMERA = "pilibcam"      # valid values are usbcam, ipcam, pilibcam, pilegcam
CAM_LOCATION = 'None'    # Specify an address, physical location Etc for camera
SHOW_CAM_SETTINGS_ON = True  # True Displays configcam.py settings

# Libcam (Bullseye or later) and Legacy Pi Camera Settings
# --------------------------------------------------------
CAMERA_WIDTH = 320     # Image stream width for opencv motion scanning Default=320
CAMERA_HEIGHT = 240    # Image stream height for opencv motion scanning  Default=240
CAMERA_FRAMERATE = 22  # Default= 20 Frame rate for video stream V2 picam can be higher
CAMERA_ROTATION = 0    # Rotate camera image valid values are 0, 90, 180, 270
CAMERA_VFLIP = True    # Flip the camera image vertically if required
CAMERA_HFLIP = True    # Flip the camera image horizontally if required

# USB, WEB and RTSP IP Cam Settings
# ---------------------------------
USBCAM_SRC = 1         # Used if CAMERA = "usbcam"
IPCAM_SRC = "rtsp://USERID:PASSWORD@IP:PORT/PATH"  # Set low res stream per IP Cam Docs and config
WEBCAM_WIDTH = 320     # Default= 320 USB, RTSP cam image stream width
WEBCAM_HEIGHT = 240    # Default= 240 USB, RTSP cam image stream height
WEBCAM_HFLIP = False   # Default= False USB Webcam flip image horizontally
WEBCAM_VFLIP = False   # Default= False USB Webcam flip image vertically
                       # IMPORTANT Webcam Streaming Performance Hit if Stream Flipped.

# Note if tested speed is too low increase appropriate cal_obj_mm  value and redo speed test for desired direction.
# IMPORTANT - If plugins Enabled Edit Settings in specified plugin file located in plugins folder.

# Plugins overlay the config.py variable settings
# -----------------------------------------------
pluginEnable = False
pluginName = "picam240" # Specify filename in plugins subfolder without .py extension per below
                        # picam240, webcam240 (Recommended for RPI2 or greater)
                        # picam480, webcam480, picam720, webcam720  (can use RPI3 but Test)
                        # picam1080   (Experimental Not Recommended)
                        # secpicam480, secwebcam480 (Experimental no CSV entries)

# Display opencv windows on gui desktop
# gui_window_on suppresses All Windows if False
# ----------------------------------------------
gui_window_on = False  # True= Turn On All desktop GUI openCV windows. False=Don't Show (req'd for SSH) .
gui_show_camera = True # True=Show the camera on gui windows. False=Don't Show (useful for image_sign)
show_thresh_on = False # Display desktop GUI openCV cropped threshold window. True=Show, False=Don't Show
show_crop_on = False   # Same as show_thresh_on but in color. True=Show, False=Don't Show (Default)

# Display and Log settings
# ------------------------
verbose = True         # True= Display basic status information on console False= Off
display_fps = False    # True= Show average frame count every 1000 loops False= Off
log_data_to_CSV = False # True= Save log data as CSV comma separated values  False= Off
loggingToFile = False  # True= Send logging to file False= No Logging to File
logFilePath = 'speed-cam.log'  # Location of log file when loggingToFile=True

# Motion Event Settings
# ---------------------
SPEED_MPH = False      # Set Speed Units   kph=False  mph=True
track_counter = 6      # Default= 6 Number of Consecutive Motion Events to trigger speed photo. Adjust to suit.
                       # Suggest single core cpu=4-7 quad core=8-15 but adjust to smooth erratic readings due to contour jumps
MIN_AREA = 200         # Default= 200 Exclude all contours less than or equal to this sq-px Area
show_out_range = True  # Default= True Show Out of Range Events per x_diff settings below False= Off
x_diff_max = 24        # Default= 20 Exclude if max px away >= last motion event x position
x_diff_min = 1         # Default= 1 Exclude if min px away <= last event x position
x_buf_adjust = 10      # Default= 10 Divides motion Rect x for L&R Buffer Space to Ensure contours are in
track_timeout = 0.5    # Default= 0.5 Optional seconds to wait after track End (Avoids dual tracking)
event_timeout = 0.3    # Default= 0.3 seconds to wait for next motion event before starting new track
max_speed_over = 0     # Exclude track if Speed less than or equal to value specified 0=All
                       # Can be useful to exclude pedestrians and/or bikes, Etc or track only fast objects

# Motion Tracking Window Crop Area Settings
# -----------------------------------------
# Note: Values based on 320x240 image stream size.
# If variable is commented, value will be set automatically based on image size.
# To see motion tracking crop area on images, Set variable image_show_motion_area = True
# Set align_cam_on = True to help with adjusting settings.
x_left = 50           # Default=50 comment variable for auto calculate
x_right = 250         # Default=250 comment variable for auto calculate
y_upper = 90          # Default=90 comment variable for auto calculate
y_lower = 150         # Default=150 comment variable for auto calculate



# Camera Image Settings
# ---------------------
image_path = "media/images"   # folder name to store images
image_prefix = "speed-"       # image name prefix
image_format = ".jpg"         # Default = ".jpg"  image Formats .jpg .jpeg .png .gif .bmp
image_jpeg_quality = 98       # Set the quality of the jpeg. Default = 95 https://docs.opencv.org/3.4/d8/d6a/group__imgcodecs__flags.html#ga292d81be8d76901bff7988d18d2b42ac
image_jpeg_optimize = True    # Optimize the image. Default = False https://docs.opencv.org/3.4/d8/d6a/group__imgcodecs__flags.html#ga292d81be8d76901bff7988d18d2b42ac
image_show_motion_area = True # True= Display motion detection rectangle area on saved images
image_filename_speed = True   # True= Include speed value in filename
image_text_on = True          # True= Show Text on speed images   False= No Text on images
image_text_bottom = True      # True= Show image text at bottom otherwise at top
image_font_size = 12          # Default= 12 Font text height in px for text on images
image_font_scale = 0.5        # Default= 0.5 Font scale factor that is multiplied by the font-specific base size.
image_font_thickness = 2      # Default= 2  Font text thickness in px for text on images
image_font_color = (255, 255, 255)  # Default= (255, 255, 255) White
image_bigger = 3.0            # Default= 3.0 min=0.1 Resize saved speed image by specified multiplier value
image_max_files = 0           # 0=off or specify MaxFiles to maintain then oldest are deleted  Default=0 (off)

image_sign_on = False
image_sign_show_camera = False
image_sign_resize = (1280, 720)
image_sign_text_xy = (100, 675)
image_sign_font_scale = 30.0
image_sign_font_thickness = 60
image_sign_font_color = (255, 255, 255)
image_sign_timeout = 5        # Keep the image sign for 5 seconds.

# Optional Manage SubDir Creation by time, number of files or both (not recommended)
# ----------------------------------------------------------------
imageSubDirMaxFiles = 2000    # 0=off or specify MaxFiles - Creates New dated sub-folder if MaxFiles exceeded
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
WINDOW_BIGGER = 1.0           # Default= 1.0 min=0.1 Resize multiplier for opencv window if gui_window_on=True
BLUR_SIZE = 10                # Default= 10 OpenCV setting for Gaussian difference image blur
THRESHOLD_SENSITIVITY = 20    # Default= 20 OpenCV setting for difference image threshold

# Sqlite3 Settings
# ----------------
DB_DIR   = "data"
DB_NAME  = "speed_cam.db"
DB_TABLE = "speed"

# matplotlib graph image settings
# -------------------------------
GRAPH_PATH = 'media/graphs'  # Directory path for storing graph images
GRAPH_ADD_DATE_TO_FILENAME = False  # True - Prefix graph image filenames with datetime default = False
GRAPH_RUN_TIMER_HOURS = 0.5   # Default= 0.5 Update Graphs every specified hours wait (Continuous).
# List of sql query Data for sql-make-graph-count-totals.py and sql-make-graph-speed-ave.py (with no parameters)
#                [[Group_By, Days_Prev, Speed_Over]]  where Group_By is 'hour', 'day' or 'month'
GRAPH_RUN_LIST = [
                  ['day', 28, 10],
                  ['hour', 28, 10],
                  ['hour', 7, 0],
                  ['hour', 2, 0]
                 ]

#======================================
#       webserver.py Settings
#======================================

# Web Server settings
# -------------------
web_server_port = 8080        # Default= 8080 Web server access port eg http://192.168.1.100:8080
web_server_root = "media"     # Default= "media" webserver root path to webserver image/video sub-folders
web_page_title = "SPEED-CAMERA Media"  # web page title that browser show (not displayed on web page)
web_page_refresh_on = True    # False=Off (never)  Refresh True=On (per seconds below)
web_page_refresh_sec = "900"  # Default= "900" seconds to wait for web page refresh  seconds (15 minutes)
web_page_blank = False        # True Starts left image with a blank page until a right menu item is selected
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
