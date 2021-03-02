# ---------------- User Configuration Settings for speed-cam.py ---------------------------------
#         Ver 8.4 speed-cam.py picam1080 Stream Variable Configuration Settings

#######################################
#    speed-cam.py plugin settings
#          EXPERIMENTAL
#######################################

# Calibration Settings
# ===================
cal_obj_px_L2R = 600     # L2R Moving Objects, Length of a calibration object in pixels
cal_obj_mm_L2R = 4700.0  # L2R Moving Objects, Length of the calibration object in millimetres
cal_obj_px_R2L = 650     # R2L Moving Objects, Length of a calibration object in pixels
cal_obj_mm_R2L = 4700.0  # R2L Moving Objects, Length of the calibration object in millimetres

# Motion Event Settings
# ---------------------
MIN_AREA = 300         # Default= 300 Exclude all contours less than or equal to this sq-px Area
track_len_trig = 100   # Default= 100 Length of track to trigger speed photo
x_diff_max = 30        # Default= 25 Exclude if max px away >= last motion event x pos
x_diff_min = 1         # Default= 1  Exclude if min px away <= last event x pos
track_timeout = 0.0    # Default= 0.0 Optional seconds to wait after track End (Avoid dual tracking)
event_timeout = 0.3    # Default= 0.3 seconds to wait for next motion event before starting new track

# Camera Settings
# ---------------
WEBCAM = False         # Default= False False=PiCamera True=USB WebCamera

# Pi Camera Settings
# ------------------
CAMERA_WIDTH = 1920    # Default= 1920 Image stream width for opencv motion scanning (quad core)
CAMERA_HEIGHT = 1088   # Default= 1088 Image stream height for opencv motion scanning (quad core)
CAMERA_FRAMERATE = 15  # Default= 15 framerate for video stream max for V2 can be higher

# Camera Image Settings
# ---------------------
image_font_size = 20   # Default= 20 Font text height in px for text on images
image_bigger = 1       # Default= 1 Resize saved speed image by value

# ---------------------------------------------- End of User Variables -----------------------------------------------------
