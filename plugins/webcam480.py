# ---------------- User Configuration Settings for speed-cam.py ---------------------------------
#         Ver 8.4 speed-cam.py webcam480 Stream Variable Configuration Settings

#######################################
#    speed-cam.py plugin settings
#######################################

# Calibration Settings
# --------------------
cal_obj_px_L2R = 80      # L2R Moving Objects, Length of a calibration object in pixels
cal_obj_mm_L2R = 4700.0  # L2R Moving Objects, Length of the calibration object in millimetres
cal_obj_px_R2L = 85      # R2L Moving Objects, Length of a calibration object in pixels
cal_obj_mm_R2L = 4700.0  # R2L Moving Objects, Length of the calibration object in millimetres

# Motion Event Settings
# ---------------------
MIN_AREA = 100         # Default= 200 Exclude all contours less than or equal to this sq-px Area
x_diff_max = 200       # Default= 200 Exclude if max px away >= last motion event x pos
x_diff_min = 1         # Default= 1  Exclude if min px away <= last event x pos
track_timeout = 0.0    # Default= 0.0 Optional seconds to wait after track End (Avoid dual tracking)
event_timeout = 0.4    # Default= 0.4 seconds to wait for next motion event before starting new track
log_data_to_CSV = False # Default= True True= Save log data as CSV comma separated values

# Camera Settings
# ---------------
WEBCAM = True          # Default= False False=PiCamera True=USB WebCamera

# Web Camera Settings
WEBCAM_SRC = 0         # Default= 0   USB opencv connection number
WEBCAM_WIDTH = 640     # Default= 640 USB Webcam Image width
WEBCAM_HEIGHT = 480    # Default= 480 USB Webcam Image height

# Camera Image Settings
# ---------------------
image_font_size = 15   # Default = 15 Font text height in px for text on images
image_bigger = 1.5     # Default = 1.5 Resize saved speed image by value

# ---------------------------------------------- End of User Variables -----------------------------------------------------
