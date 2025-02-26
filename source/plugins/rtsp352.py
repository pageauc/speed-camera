# ---------------- User Configuration Settings for speed-cam.py ---------------------------------
#         Ver 13.11 speed-cam.py plugin rtsp352.py IP cam Stream Config Settings

#######################################
#    speed-cam.py plugin settings
#######################################

CALIBRATE_ON = False         # Create a calibration image file with calibration hash markers 10 px per mark
ALIGN_CAM_ON = False         # Default=False  True Saves alignment image to help with camera pointing
CAMERA = "rtspcam"           # valid values usbcam, rtspcam, pilibcam, pilegcam

RTSPCAM_SRC = "rtsp://admin:mypassword@192.168.1.210:554/12"  # Set per IP Cam Docs and config see example below
                                                  # rtsp://admin:myped@192.168.1.100:554/12

# Camera Image Stream Settings
IM_SIZE = (640, 352)   # Image resolution width, height pixels
GUI_WINDOW_ON = False
GUU_IMAGE_WIN_ON = True

# Motion Tracking Window Crop Area Settings
# -----------------------------------------
# To see motion tracking crop area on images, Set variable IM_SHOW_CROP_AREA_ON = True
# Set ALIGN_CAM_ON = True to Help with adjusting settings.
MO_CROP_AUTO_ON = False       # True enables rough Auto Calculation of Motion Crop Area
MO_CROP_X_LEFT = 200          # Default=50 comment variable for auto calculate
MO_CROP_X_RIGHT = 450         # Default=250 comment variable for auto calculate
MO_CROP_Y_UPPER = 140         # Default=90 comment variable for auto calculate
MO_CROP_Y_LOWER = 220         # Default=150 comment variable for auto calculate

# Motion Event Settings
# ---------------------
MO_TRACK_EVENT_COUNT = 5    # Default= 6 Number of Consecutive Motion Events to trigger speed photo. Adjust to suit.
                            # Suggest single core cpu=4-7 quad core=8-15 but adjust to smooth erratic readings due to contour jumps
MO_MIN_AREA_PX = 500        # Default= 200 Exclude all contours less than or equal to this sq-px Area
MO_LOG_OUT_RANGE_ON = True  # Default= True Show Out of Range Events per x_diff settings below False= Off
MO_MAX_X_DIFF_PX = 26       # Default= 20 Exclude if max px away >= last motion event x position
MO_MIN_X_DIFF_PX = 1        # Default= 1 Exclude if min px away <= last event x position
MO_X_LR_SIDE_BUFF_PX = 10   # Default= 10 Divides motion Rect x for L&R Buffer Space to Ensure contours are in
MO_TRACK_TIMEOUT_SEC = 0.5  # Default= 0.5 Optional seconds to wait after track End (Avoids dual tracking)
MO_EVENT_TIMEOUT_SEC = 0.3  # Default= 0.3 seconds to wait for next motion event before starting new track
MO_MAX_SPEED_OVER = 0       # Exclude track if Speed less than or equal to value specified 0=All
                            # Can be useful to exclude pedestrians and/or bikes, Etc or track only fast objects

# Camera Image Settings
# ---------------------
IM_FRAMERATE = 20
IM_SHOW_CROP_AREA_ON = True      # True= Display motion detection rectangle area on saved images
IM_SHOW_SPEED_FILENAME_ON = True # True= Include speed value in filename
IM_SHOW_TEXT_ON = True           # True= Show Text on speed images   False= No Text on images
IM_SHOW_TEXT_BOTTOM_ON = True    # True= Show image text at bottom otherwise at top
IM_FONT_SIZE_PX = 16             # Default= 12 Font text height in px for text on images
IM_FONT_SCALE = 0.5              # Default= 0.5 Font scale factor that is multiplied by the font-specific base size.
IM_FONT_THICKNESS = 2            # Default= 2  Font text thickness in px for text on images
IM_FONT_COLOR = (255, 255, 255)  # Default= (255, 255, 255) White
IM_BIGGER = 1.8                  # Default= 3.0 min=0.1 Resize saved speed image by specified multiplier value

# ---------------------------------------- End of User Variables ------------------------------------------
