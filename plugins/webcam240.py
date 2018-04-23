# ---------------- User Configuration Settings for speed-cam.py ---------------------------------
#         Ver 8.4 speed-cam.py picam240 Stream Variable Configuration Settings

#######################################
#    speed-cam.py plugin settings
#######################################

# Calibration Settings
# --------------------
cal_obj_px = 90        # Length of a calibration object in pixels
cal_obj_mm = 4330.0    # Length of the calibration object in millimetres

# Crop Area for motion detection Tracking
# ---------------------------------------
x_left  = 25           # Default= 25 Exclude event if x less than this px position
x_right = 295          # Default= 295 Exclude event if x greater than this px position
y_upper = 75           # Default= 75 Exclude event if y less that this value
y_lower = 185          # Default= 185 Exclude event if y greater than this value

# Motion Event Settings
# ---------------------
SPEED_MPH = False      # Set the speed conversion  kph=False  mph=True
MIN_AREA = 170         # Default= 170 Exclude all contours less than or equal to this sq-px Area
track_len_trig = 60    # Default= 60 Length of track to trigger speed photo
x_diff_max = 30        # Default= 30 Exclude if max px away >= last motion event x pos
x_diff_min = 1         # Default= 1  Exclude if min px away <= last event x pos
track_timeout = 0.0    # Default= 0.0 Optional seconds to wait after track End (Avoid dual tracking)
event_timeout = 0.7    # Default= 0.7 seconds to wait for next motion event before starting new track
log_data_to_CSV = True # Default= True True= Save log data as CSV comma separated values

# Camera Settings
# ---------------
WEBCAM = True          # Default = False False=PiCamera True=USB WebCamera

# Pi Camera Settings
# ------------------
CAMERA_WIDTH = 320     # Default= 320 Image stream width for opencv motion scanning default=320
CAMERA_HEIGHT = 240    # Default= 240 Image stream height for opencv motion scanning  default=240
CAMERA_FRAMERATE = 30  # Default= 30 Frame rate for video stream V2 picam can be higher

# Camera Image Settings
# ---------------------
image_font_size = 12   # Default= 15 Font text height in px for text on images
image_bigger = 3       # Default= 3 Resize saved speed image by value

# ---------------------------------------------- End of User Variables -----------------------------------------------------
