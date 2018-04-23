# ---------------- User Configuration Settings for speed-cam.py ---------------------------------
#         Ver 8.4 speed-cam.py webcam720 Stream Variable Configuration Settings

#######################################
#    speed-cam.py plugin settings
#######################################

# Calibration Settings
# ===================
cal_obj_px = 310       # Length of a calibration object in pixels
cal_obj_mm = 4330.0    # Length of the calibration object in millimetres

# Crop Area for motion detection Tracking
# =======================================
x_left  = 380          # Default= 380 Exclude event if x less than this px position
x_right = 900          # Default= 900 Exclude event if x greater than this px position
y_upper = 260          # Default= 260 Exclude event if y less that this value
y_lower = 460          # Default= 460 Exclude event if y greater than this value

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
WEBCAM = True          # Default= False False=PiCamera True=USB WebCamera

# Web Camera Settings
# -------------------
WEBCAM_SRC = 0         # Default= 0   USB opencv connection number
WEBCAM_WIDTH = 1280    # Default= 1280 USB Webcam Image width
WEBCAM_HEIGHT = 720    # Default= 720 USB Webcam Image height

# Camera Image Settings
# ---------------------
image_font_size = 20   # Default= 20 Font text height in px for text on images
image_bigger = 1       # Default= 1 Resize saved speed image by value

# ---------------------------------------------- End of User Variables -----------------------------------------------------
