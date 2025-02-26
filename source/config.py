# ---------------- User Configuration Settings for speed-cam.py ---------------------------
#        Ver 13.16 speed-cam.py Variable Configuration Settings

#######################################
#  speed-cam.py Variable Settings
#  Default is 320x240 image stream size
#  Note motion track crop area can now be
#  auto configured so you may not need to use a plugin
#  to change resolution.
#######################################

# Calibration Settings
# --------------------
CALIBRATE_ON = True       # Create a calibration image file with calibration hash markers 10 px per mark
CAL_OBJ_PX_L2R = 80       # L2R Moving Objects, Length of a calibration object in pixels
CAL_OBJ_MM_L2R = 4700     # L2R Moving Objects, Length of the calibration object in millimetres
CAL_OBJ_PX_R2L = 85       # R2L Moving Objects, Length of a calibration object in pixels
CAL_OBJ_MM_R2L = 4700     # R2L Moving Objects, Length of the calibration object in millimetres
# Note if tested speed is too low increase appropriate cal_obj_mm  value and redo speed test for desired direction.
# IMPORTANT - If plugins Enabled Edit Settings in specified plugin file located in plugins folder.

# Align Camera Settings
# ---------------------
ALIGN_CAM_ON = False      # Default=False  True Saves alignment image to help with camera pointing
ALIGN_DELAY_SEC = 3       # Default=3 seconds delay between each alignment image in recent folder

# Plugins override specified config.py variable settings
# ----------------------------------------------------------
PLUGIN_ENABLE_ON = False  # True enables import of the specified PLUGIN_NAME
PLUGIN_NAME = "picam240"  # Specify filename in plugins subfolder without .py extension per below
                          # picam240, webcam240 (Recommended for RPI2 or greater)
                          # picam480, webcam480, rtsp352, picam720, webcam720  (can use RPI3 but Test)
                          # picam1080   (Experimental Not Recommended)
                          # secpicam480, secwebcam480 (Experimental no CSV entries)

# Display and Log settings
# ------------------------
SHOW_SETTINGS_ON = False  # True Displays the config.py file on startup
LOG_VERBOSE_ON = True     # True= Display basic status information on console False= Off
LOG_DATA_TO_CSV = False   # True= Save log data as CSV comma separated values  False= Off
LOG_TO_FILE_ON = False    # True= Send logging to file False= No Logging to File
LOG_FILE_PATH = 'speed-cam.log'  # Location of log file when LOG_TO_FILE_ON=True
LOG_FPS_ON = False        # True= Show average frame count every 1000 loops False= Off

# Camera Settings
# ---------------
CAMERA = "pilibcam"    # valid values usbcam, rtspcam, pilibcam, pilegcam
CAM_LOCATION = "Front Window"
USBCAM_SRC = 0         # Device number of USB connection usually 0, 1, 2, Etc
RTSPCAM_SRC = "rtsp://user:password@IP:554/path"  # Set per IP Cam Docs and config see example below
                                                  # rtsp://admin:mypwd@192.168.1.100:554/12
# Camera Image Stream Settings
IM_SIZE = (320, 240)     # Image resolution width, height pixels
IM_VFLIP = False         # True enables flipping image vertically
IM_HFLIP = False         # True enables flipping image horizonally
IM_ROTATION = 0          # Rotate camera image valid values are 0, 90, 180, 270
IM_FRAMERATE = 30        # Legacy Picamera Framerate

# Image Settings
# --------------
IM_DIR_PATH = "media/images"     # folder name to store images
IM_PREFIX = "speed-"             # image name prefix
IM_FORMAT_EXT = ".jpg"           # Default = ".jpg"  image Formats .jpg .jpeg .png .gif .bmp
IM_JPG_QUALITY = 98              # Set the quality of the jpeg. Default = 95
                                 # https://docs.opencv.org/3.4/d8/d6a/group__imgcodecs__flags.html#ga292d81be8d76901bff7988d18d2b42ac
IM_JPG_OPTIMIZE_ON = True        # Optimize the image. Default = False
                                 # https://docs.opencv.org/3.4/d8/d6a/group__imgcodecs__flags.html#ga292d81be8d76901bff7988d18d2b42ac
IM_SHOW_SPEED_FILENAME_ON = True # True= Include speed value in filename
IM_SHOW_CROP_AREA_ON = False     # True= Display motion detection rectangle area on saved images
IM_BIGGER = 3.0                  # Default= 3.0 min=0.1 Resize saved speed image by specified multiplier value
IM_SHOW_TEXT_ON = True           # True= Show Text on speed images   False= No Text on images
IM_SHOW_TEXT_BOTTOM_ON = True    # True= Show image text at bottom otherwise at top
IM_FONT_SIZE_PX = 12             # Default= 12 Font text height in px for text on images
IM_FONT_SCALE = 0.5              # Default= 0.5 Font scale factor that is multiplied by the font-specific base size.
IM_FONT_THICKNESS = 2            # Default= 2  Font text thickness in px for text on images
IM_FONT_COLOR = (255, 255, 255)  # Default= (255, 255, 255) White
IM_MAX_FILES = 0                 # 0=off or specify MaxFiles to maintain then oldest are deleted  Default=0 (off)

# AI Settings
# ------------
IM_SAVE_4AI_ON = False                # will save small colour image for later AI processing
IM_SAVE_4AI_DAY_THRESH = 10           # Default = 10 Set mean px value to indicate day/night threshold. higher is day
IM_SAVE_4AI_POS_DIR = "media/ai/pos"  # Save positive ai images after tracking completed
IM_SAVE_4AI_NEG_DIR = "media/ai/neg"  # Save negative ai images (no motion detected)
IM_SAVE_4AI_NEG_TIMER_SEC = 60 * 60 * 6  # Save a non positive image every specified seconds
IM_FIRST_AND_LAST_ON = False          # Save and process first and last tracking images (NOT Fully Implemented)

# Sign Settings
# -------------
IM_SHOW_SIGN_ON = False
IM_SIGN_RESIZE = (1280, 720)
IM_SIGN_TEXT_XY = (100, 675)
IM_SIGN_FONT_SCALE = 30.0
IM_SIGN_FONT_THICK_PX = 60
IM_SIGN_FONT_COLOR = (255, 255, 255)
IM_SIGN_TIMEOUT_SEC = 5        # Keep the image sign for 5 seconds.

# Motion Event Settings
# ---------------------
MO_SPEED_MPH_ON = False     # Set Speed Units   kph=False  mph=True
MO_TRACK_EVENT_COUNT = 6    # Default= 6 Number of Consecutive Motion Events to trigger speed photo. Adjust to suit.
                            # Suggest single core cpu=4-7 quad core=8-15 but adjust to smooth erratic readings due to contour jumps
MO_MIN_AREA_PX = 200        # Default= 200 Exclude all contours less than or equal to this sq-px Area
MO_LOG_OUT_RANGE_ON = True  # Default= True Show Out of Range Events per x_diff settings below False= Off
MO_MAX_X_DIFF_PX = 24       # Default= 20 Exclude if max px away >= last motion event x position
MO_MIN_X_DIFF_PX = 1        # Default= 1 Exclude if min px away <= last event x position
MO_X_LR_SIDE_BUFF_PX = 10   # Default= 10 Divides motion Rect x for L&R Buffer Space to Ensure contours are in
MO_TRACK_TIMEOUT_SEC = 0.5  # Default= 0.5 Optional seconds to wait after track End (Avoids dual tracking)
MO_EVENT_TIMEOUT_SEC = 0.3  # Default= 0.3 seconds to wait for next motion event before starting new track
MO_MAX_SPEED_OVER = 0       # Exclude track if Speed less than or equal to value specified 0=All
                            # Can be useful to exclude pedestrians and/or bikes, Etc or track only fast objects
# Motion Tracking Window Crop Area Settings
# -----------------------------------------
# Note: Values based on 320x240 image stream size.
# To see motion tracking crop area on images, Set variable IM_SHOW_CROP_AREA_ON = True
# Set ALIGN_CAM_ON = True to help with adjusting settings.
MO_CROP_AUTO_ON = False       # True enables rough Auto Calculation of Motion Crop Area
MO_CROP_X_LEFT = 50           # Default=50
MO_CROP_X_RIGHT = 250         # Default=250
MO_CROP_Y_UPPER = 90          # Default=90
MO_CROP_Y_LOWER = 150         # Default=150

# Display opencv windows on GUI desktop
# GUI_WINDOW_ON suppresses All Windows if False
# ----------------------------------------------
GUI_WINDOW_ON = False     # True= Turn On All desktop GUI openCV windows. False=Don't Show (req'd for SSH) .
GUI_IMAGE_WIN_ON = True   # True=Show the camera on a gui windows. False=Don't Show (useful for image_sign)
GUI_THRESH_WIN_ON = False # True=Show openCV cropped BLUR, THRESHOLD grayscale image window. Used for detecting movement contours
GUI_CROP_WIN_ON = False   # True=Show crop window. Same as GUI_THRESH_WIN_ON but in color.
CV_SHOW_CIRCLE_ON = False     # True=circle in center of motion, False=rectangle
CV_CIRCLE_SIZE_PX = 5         # Default= 5 Diameter circle in px if CV_SHOW_CIRCLE_ON = True
CV_LINE_WIDTH_PX = 1          # Default= 1 Size of lines for circle or Rectangle
CV_WINDOW_BIGGER = 1.0        # Default= 1.0 min=0.1 Resize multiplier for opencv window if GUI_WINDOW_ON=True
BLUR_SIZE = 10                # Default= 10 OpenCV setting for Gaussian difference image blur
THRESHOLD_SENSITIVITY = 20    # Default= 20 OpenCV setting for difference image threshold

# Optional Manage SubDir Creation by time, number of files or both (not recommended)
# ----------------------------------------------------------------
IM_SUBDIR_MAX_FILES = 2000    # 0=off or specify MaxFiles - Creates New dated sub-folder if MaxFiles exceeded
IM_SUBDIR_MAX_HOURS = 0       # 0=off or specify MaxHours - Creates New dated sub-folder if MaxHours exceeded

# Optional Save Most Recent files in recent folder
# ------------------------------------------------
IM_RECENT_MAX_FILES = 200            # 0=off  Maintain specified number of most recent files in motionRecentDir
IM_RECENT_DIR_PATH = "media/recent"  # Default= "media/recent"  save recent files directory path

# Optional Manage Free Disk Space Settings
# ----------------------------------------
SPACE_TIMER_HRS = 0               # Default= 0  0=off or specify hours frequency to perform free disk space check
SPACE_FREE_MB = 500               # Default= 500  Target Free space in MB Required.
SPACE_MEDIA_DIR = 'media/images'  # Default= 'media/images'  Starting point for directory walk
SPACE_FILE_EXT  = 'jpg'           # Default= 'jpg' File extension to Delete Oldest Files

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
WEB_SERVER_PORT = 8080        # Default= 8080 Web server access port eg http://192.168.1.100:8080
WEB_SERVER_ROOT = "media"     # Default= "media" webserver root path to webserver image/video sub-folders
WEB_PAGE_TITLE = "SPEED-CAMERA Media"  # web page title that browser show (not displayed on web page)
WEB_PAGE_REFRESH_ON = True    # False=Off (never)  Refresh True=On (per seconds below)
WEB_PAGE_REFRESH_SEC = "900"  # Default= "900" seconds to wait for web page refresh  seconds (15 minutes)
WEB_PAGE_BLANK_ON = False     # True Starts left image with a blank page until a right menu item is selected
                              # False displays second list[1] item since first may be in progress

# Left iFrame Image Settings
# --------------------------
WEB_IMAGE_HEIGHT = "768"       # Default= "768" px height of images to display in iframe
WEB_IFRAME_WIDTH_PERCENT = "70%" # Left Pane - Sets % of total screen width allowed for iframe. Rest for right list
WEB_IFRAME_WIDTH = "100%"      # Desired frame width to display images. can be eg percent "80%" or px "1280"
WEB_IFRAME_HEIGHT = "100%"     # Desired frame height to display images. Scroll bars if image larger (percent or px)

# Right Side Files List
# ---------------------
WEB_MAX_LIST_ENTRIES = 0           # 0 = All or Specify Max right side file entries to show (must be > 1)
WEB_LIST_HEIGHT = WEB_IMAGE_HEIGHT # Right List - side menu height in px (link selection)
WEB_LIST_BY_DATETIME_ON = True        # True=datetime False=filename
WEB_LIST_SORT_DESC_ON = True    # reverse sort order (filename or datetime per web_list_by_datetime setting

# --------------------------------------- End of User Variables -------------------------------
