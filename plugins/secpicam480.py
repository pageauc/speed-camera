# ---------------- User Configuration Settings for speed-cam.py ---------------------------------
#         Ver 8.4 speed-cam.py picam480 Stream Variable Configuration Settings

#######################################
#    speed-cam.py plugin settings
#######################################

# Calibration Settings
# --------------------
calibrate = False      # Create a calibration image file with calibration hash markers 10 px per mark

# Motion Event Settings
# ---------------------
MIN_AREA = 200         # Default= 200 Exclude all contours less than or equal to this sq-px Area
x_diff_max = 90        # Default= 90 Exclude if max px away >= last motion event x pos
x_diff_min = 1         # Default= 1  Exclude if min px away <= last event x pos
track_timeout = 0.0    # Default= 0.0 Optional seconds to wait after track End (Avoid dual tracking)
event_timeout = 0.7    # Default= 0.7 seconds to wait for next motion event before starting new track
log_data_to_CSV = False  # Default= False True = Save log data as CSV comma separated values

# Camera Settings
# ---------------
WEBCAM = False         # Default= False False=PiCamera True=USB WebCamera

# Pi Camera Settings
# ------------------
CAMERA_WIDTH = 640     # Default= 640 Image stream width for opencv motion scanning default=320
CAMERA_HEIGHT = 480    # Default= 480 Image stream height for opencv motion scanning  default=240
CAMERA_FRAMERATE = 20  # Default = 30 Frame rate for video stream V2 picam can be higher

# Camera Image Settings
# ---------------------
image_path = "media/security"  # folder name to store images
image_prefix = "scam-"         # image name prefix security camera
image_show_motion_area = False # True= Display motion detection rectangle area on saved images
image_filename_speed = False   # True= Prefix filename with speed value
image_text_on = False          # True= Show Text on speed images   False= No Text on images
image_bigger = 1.5             # Default= 1.5 Resize saved speed image by value
image_font_size = 18           # Default= 18 Font text height in px for text on images
imageRecentMax = 10            # 0=off  Maintain specified number of most recent files in motionRecentDir
imageRecentDir = "media/recent/security"  # default= "media/recent"  save recent files directory path

# Optional Manage SubDir Creation by time, number of files or both
# ----------------------------------------------------------------
imageSubDirMaxHours = 0       # 0=off or specify MaxHours - Creates New dated sub-folder if MaxHours exceeded
imageSubDirMaxFiles = 0       # 0=off or specify MaxFiles - Creates New dated sub-folder if MaxFiles exceeded

# ---------------------------------------------- End of User Variables -----------------------------------------------------
