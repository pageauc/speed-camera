# ---------------- User Configuration Settings for speed-cam.py ---------------------------------
#         Ver 8.4 speed-cam.py picam480 Stream Variable Configuration Settings

#######################################
#    speed-cam.py plugin settings
#######################################

# Calibration Settings
# --------------------
cal_obj_px = 180       # Length of a calibration object in pixels
cal_obj_mm = 4330.0    # Length of the calibration object in millimetres

# Crop Area for motion detection Tracking
# ---------------------------------------
x_left  = 150          # Default= 150 Exclude event if x less than this px position
x_right = 490          # Default= 490 Exclude event if x greater than this px position
y_upper = 140          # Default= 140 Exclude event if y less that this value
y_lower = 340          # Default= 340 Exclude event if y greater than this value

# Motion Event Settings
# ---------------------
SPEED_MPH = False      # Set the speed conversion  kph=False  mph=True
MIN_AREA = 200         # Default= 200 Exclude all contours less than or equal to this sq-px Area
track_len_trig = 75    # Default= 75 Length of track to trigger speed photo
x_diff_max = 35        # Default= 35 Exclude if max px away >= last motion event x pos
x_diff_min = 1         # Default= 1  Exclude if min px away <= last event x pos
track_timeout = 0.0    # Default= 0.0 Optional seconds to wait after track End (Avoid dual tracking)
event_timeout = 0.7    # Default= 0.7 seconds to wait for next motion event before starting new track
log_data_to_CSV = True # Default= True True= Save log data as CSV comma separated values

# Camera Settings
# ---------------
WEBCAM = False         # Default= False False=PiCamera True=USB WebCamera

# Pi Camera Settings
# ------------------
CAMERA_WIDTH = 640     # Default= 640 Image stream width for opencv motion scanning default=320
CAMERA_HEIGHT = 480    # Default= 480 Image stream height for opencv motion scanning  default=240
CAMERA_FRAMERATE = 30  # Default= 30 Frame rate for video stream V2 picam can be higher

# Camera Image Settings
# ---------------------
image_bigger = 1.5     # Default= 1.5 Resize saved speed image by value
image_font_size = 16   # Default= 18 Font text height in px for text on images

# ---------------------------------------------- End of User Variables -----------------------------------------------------
