# ---------------- User Configuration Settings for speed-cam.py ---------------------------------
#         Ver 8.4 speed-cam.py picam720 Stream Variable Configuration Settings

#######################################
#    speed-cam.py plugin settings
#######################################

# Calibration Settings
# ===================
cal_obj_px_L2R = 300     # L2R Moving Objects, Length of a calibration object in pixels
cal_obj_mm_L2R = 4700.0  # L2R Moving Objects, Length of the calibration object in millimetres
cal_obj_px_R2L = 320     # R2L Moving Objects, Length of a calibration object in pixels
cal_obj_mm_R2L = 4700.0  # R2L Moving Objects, Length of the calibration object in millimetres

# Motion Event Settings
# ---------------------
MIN_AREA = 100         # Default= 100 Exclude all contours less than or equal to this sq-px Area
x_diff_max = 30        # Default= 25  Exclude if max px away >= last motion event x pos
x_diff_min = 1         # Default= 1  Exclude if min px away <= last event x pos
track_timeout = 0.0    # Default= 0.0 Optional seconds to wait after track End (Avoid dual tracking)
event_timeout = 0.4    # Default= 0.4 seconds to wait for next motion event before starting new track
log_data_to_CSV = True # Default= True True= Save log data as CSV comma separated values

# Camera Settings
# ---------------
WEBCAM = False         # Default= False False=PiCamera True=USB WebCamera

# Pi Camera Settings
# ------------------
CAMERA_WIDTH = 1280    # Default= 1280 Image stream width for opencv motion scanning (quad core)
CAMERA_HEIGHT = 720    # Default= 720 Image stream height for opencv motion scanning (quad core)
CAMERA_FRAMERATE = 25  # Default= 25 framerate for video stream max for V2 can be higher

# Camera Image Settings
# ---------------------
image_font_size = 20   # Default= 20 Font text height in px for text on images
image_bigger = 1       # Default= 1 Resize saved speed image by value

# ---------------------------------------------- End of User Variables -----------------------------------------------------
