# ---------------- User Configuration Settings for speed-cam.py ---------------------------------
#         Ver 7.0 speed-cam.py picam480 Stream Variable Configuration Settings

#######################################
#    speed-cam.py plugin settings
#######################################

# Calibration Settings
# --------------------
calibrate = True       # Create a calibration image file with calibration hash markers 10 px per mark
cal_obj_px = 180       # Length of a calibration object in pixels
cal_obj_mm = 4330.0    # Length of the calibration object in millimetres

# Crop Area for motion detection Tracking
# ---------------------------------------
x_left  = 150          # Exclude event if x less than this px position Default=25
x_right = 490          # Exclude event if x greater than this px position Default=295
y_upper = 140          # Exclude event if y less that this value default=100
y_lower = 340          # Exclude event if y greater than this value default=175

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
CAMERA_WIDTH = 640     # Image stream width for opencv motion scanning default=320
CAMERA_HEIGHT = 480    # Image stream height for opencv motion scanning  default=240
CAMERA_FRAMERATE = 30  # Default = 30 Frame rate for video stream V2 picam can be higher

# Camera Image Settings
# ---------------------
image_bigger = 1.5            # Default = 1.5 Resize saved speed image by value
image_font_size = 18          # Default = 18 Font text height in px for text on images

# ---------------------------------------------- End of User Variables -----------------------------------------------------
