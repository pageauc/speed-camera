# ---------------- User Configuration Settings for speed-cam.py ---------------------------------
#         Ver 6.00 speed-cam.py 240p Stream Variable Configuration Settings

#######################################
#
#    speed-cam.py variable settings
#
#######################################

# Note - Set verbose to False if script is run in background or from /etc/rc.local
# Display and Log settings
# ------------------------
verbose = True              # Display basic status information on console
display_fps = False         # True = Show average frame count every 1000 loops
log_data_to_file = True     # True = Save log data as CSV comma separated values (default=True)
show_out_range = False      # Show Out of Range Events (default=False)
loggingToFile = False       # True = Send logging to file
logFilePath = 'speed-track.log'  # Location of log file when logDataToFile=True

# Calibration Settings
# --------------------
calibrate = True       # Create a calibration image file with calibration hash markers 10 px per mark
cal_obj_px = 90        # Length of a calibration object in pixels
cal_obj_mm = 4330.0    # Length of the calibration object in millimetres

# Crop Area for motion detection Tracking
# ---------------------------------------
x_left  = 25           # Exclude event if x less than this px position Default=25
x_right = 295          # Exclude event if x greater than this px position Default=295
y_upper = 75           # Exclude event if y less that this value default=100
y_lower = 185          # Exclude event if y greater than this value default=175

# Display opencv windows on rpi desktop
# gui_window_on suppresses All Windows if False
# ----------------------------------------------
gui_window_on = False       # True = Turn On All desktop GUI openCV windows. False=Don't Show (req'd for SSH) .
show_thresh_on = True       # Display desktop GUI openCV cropped threshold window. True=Show, False=Don't Show
show_crop_on = False        # Same as show_thresh_on but in color. True=Show, False=Don't Show (default)

# Motion Event Settings
# ---------------------
SPEED_MPH = False      # Set the speed conversion  kph=False  mph=True
track_len_trig = 75    # Default=75 Length of track to trigger speed photo
track_timeout = 1      # Number of seconds to wait after track End (prevents dual tracking)
event_timeout = 2      # Number of seconds to wait for next motion event before starting new track

# Camera Settings
# ---------------
WEBCAM = False        # default = False False=PiCamera True=USB WebCamera

# Web Camera Settings
WEBCAM_SRC = 0        # default = 0   USB opencv connection number
WEBCAM_WIDTH = 320    # default = 320 USB Webcam Image width
WEBCAM_HEIGHT = 240   # default = 240 USB Webcam Image height
WEBCAM_HFLIP = False  # default = False USB Webcam flip image horizontally
WEBCAM_VFLIP = False  # default = False USB Webcam flip image vertically

# Pi Camera Settings
# ------------------
CAMERA_WIDTH = 320     # Image stream width for opencv motion scanning default=320
CAMERA_HEIGHT = 240    # Image stream height for opencv motion scanning  default=240
CAMERA_FRAMERATE = 20  # Default = 20 Frame rate for video stream V2 picam can be higher
CAMERA_ROTATION = 0    # Rotate camera image valid values are 0, 90, 180, 270
CAMERA_VFLIP = False   # Flip the camera image vertically if required
CAMERA_HFLIP = False   # Flip the camera image horizontally if required

# Camera Image Settings
# ---------------------
image_path = "media/images"   # folder name to store images
image_prefix = "speed-"       # image name prefix
image_format = ".jpg"         # default = ".jpg"  image Formats .jpeg .png .gif .bmp
image_show_motion_area = True # True= Display motion detection rectangle area on saved images
image_filename_speed = False  # True= Prefix filename with speed value
image_text_on = True          # True= Show Text on speed images   False= No Text on images
image_text_bottom = True      # True= Show image text at bottom otherwise at top
image_font_size = 15          # Default = 15 Font text height in px for text on images
image_bigger = 2              # Default = 2 multiply saved speed image by value
image_max_files = 0           # 0=off or specify MaxFiles to maintain then oldest are deleted  default=0 (off)

# Optional Manage SubDir Creation by time, number of files or both
# ----------------------------------------------------------------
imageSubDirMaxHours = 0       # 0=off or specify MaxHours - Creates New dated sub-folder if MaxHours exceeded
imageSubDirMaxFiles = 0       # 0=off or specify MaxFiles - Creates New dated sub-folder if MaxFiles exceeded

# Optional Manage Free Disk Space Settings
# ----------------------------------------
spaceTimerHrs = 0           # default= 0  0=off or specify hours frequency to perform free disk space check
spaceFreeMB = 500           # default= 500  Target Free space in MB Required.
spaceMediaDir = '/home/pi/rpi-speed-camera/media'  # default= '/home/pi/rpi-speed-camera/media'  Starting point for directory walk
spaceFileExt  = 'jpg'       # default= 'jpg' File extension to Delete Oldest Files

# Motion Event Exclusion Settings
# -------------------------------
MIN_AREA = 170         # Exclude all contours less than or equal to this sq-px Area
x_diff_min = 1         # Exclude if min px away exceeds last event x pos
x_diff_max = 50        # Exclude if max px away for last motion event x pos
max_speed_over = 0     # Exclude track if Speed less than or equal to value specified 0=All

# OpenCV Motion Settings
# ----------------------
SHOW_CIRCLE = True          # True=circle in center of motion, False=rectangle
CIRCLE_SIZE = 2             # Diameter circle in px if SHOW_CIRCLE = True
LINE_THICKNESS = 1          # Size of lines for circle or Rectangle
FONT_SCALE = .5             # OpenCV window text font size scaling factor default=.5 (lower is smaller)
WINDOW_BIGGER = 1           # default=1 resize multiplier for opencv window if gui_window_on=True
BLUR_SIZE = 10              # OpenCV setting for Gaussian difference image blur
THRESHOLD_SENSITIVITY = 20  # OpenCV setting for difference image threshold

#======================================
#       webserver.py Settings
#======================================

# Web Server settings
# -------------------
web_server_port = 8080        # default= 8080 Web server access port eg http://192.168.1.100:8080
web_server_root = "media"     # default= "media" webserver root path to webserver image/video sub-folders
web_page_title = "Speed Camera"  # web page title that browser show (not displayed on web page)
web_page_refresh_on = False   # False=Off (never)  Refresh True=On (per seconds below)
web_page_refresh_sec = "180"  # default= "180" seconds to wait for web page refresh  seconds (three minutes)
web_page_blank = True         # True Starts left image with a blank page until a right menu item is selected
                              # False displays second list[1] item since first may be in progress

# Left iFrame Image Settings
# --------------------------
web_image_height = "768"       # default= "768" px height of images to display in iframe
web_iframe_width_usage = "70%" # Left Pane - Sets % of total screen width allowed for iframe. Rest for right list
web_iframe_width = "100%"      # Desired frame width to display images. can be eg percent "80%" or px "1280"
web_iframe_height = "100%"     # Desired frame height to display images. Scroll bars if image larger (percent or px)

# Right Side Files List
# ---------------------
web_max_list_entries = 0         # 0 = All or Specify Max right side file entries to show (must be > 1)
web_list_height = web_image_height  # Right List - side menu height in px (link selection)
web_list_by_datetime = True      # True=datetime False=filename
web_list_sort_descending = True  # reverse sort order (filename or datetime per web_list_by_datetime setting

# ---------------------------------------------- End of User Variables -----------------------------------------------------
