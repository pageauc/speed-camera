# ---------------- User Configuration Settings for speed-cam.py ---------------------------------
#         Ver 7.0 speed-cam.py picam720 Stream Variable Configuration Settings

#######################################
#    speed-cam.py plugin settings
#######################################

# Calibration Settings
# ===================
cal_obj_px = 310       # Length of a calibration object in pixels
cal_obj_mm = 4330.0    # Length of the calibration object in millimetres

# Crop Area for motion detection Tracking
# =======================================
x_left  = 380          # Exclude event if x less than this px position Default=25
x_right = 900          # Exclude event if x greater than this px position Default=295
y_upper = 260          # Exclude event if y less that this value default=100
y_lower = 460          # Exclude event if y greater than this value default=175

# Motion Event Settings
# ---------------------
SPEED_MPH = False      # Set the speed conversion  kph=False  mph=True
track_len_trig = 75    # Default=75 Length of track to trigger speed photo
track_timeout = 1      # Number of seconds to wait after track End (prevents dual tracking)
event_timeout = 2      # Number of seconds to wait for next motion event before starting new track

# Camera Settings
# ---------------
WEBCAM = False        # default = False False=PiCamera True=USB WebCamera

# Pi Camera Settings
# ------------------
CAMERA_WIDTH = 1280    # default = 1280 Image stream width for opencv motion scanning (quad core)
CAMERA_HEIGHT = 720    # default = 720 Image stream height for opencv motion scanning (quad core)
CAMERA_FRAMERATE = 20  # default = 25 framerate for video stream max for V2 can be higher

# Camera Image Settings
# ---------------------
image_font_size = 20          # Default = 20 Font text height in px for text on images
image_bigger = 1              # Default = 1 Resize saved speed image by value

# Motion Event Exclusion Settings
# -------------------------------
MIN_AREA = 170         # Exclude all contours less than or equal to this sq-px Area
x_diff_min = 1         # Exclude if min px away exceeds last event x pos
x_diff_max = 50        # Exclude if max px away for last motion event x pos
max_speed_over = 0     # Exclude track if Speed less than or equal to value specified 0=All

# ---------------------------------------------- End of User Variables -----------------------------------------------------
