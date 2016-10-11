# ---------------- User Configuration Settings for speed2.py ---------------------------------
#               Ver 2.09  speed2.py Variable Configuration Settings

# Display and Log settings
#-------------------------
verbose = True              # display basic status information on console
calibrate = False           # Create a speed_calibrate.jpg file with markers to calculate a px to FT conversion
display_fps = False         # show average frame count every 1000 loops
gui_window_on = False       # Display desktop GUI openCV windows. Set to False if running from ssh console only.
log_data_to_file = True     # save log data as CSV comma separated values
show_out_range = False      # Show Out of Range Events Default=False)

# Motion Event Settings
# ---------------------
IMAGE_VIEW_FT = 72     # Set the width in feet for the road width that the camera width sees
SPEED_MPH = True       # Set the speed conversion  kph=False  mph=True
track_len_trig = 100   # Length of track to trigger speed photo Default=125
track_timeout = 2      # Number of seconds to wait after track End (prevents dual tracking)
event_timeout = 2      # Number of seconds to wait for next motion event before starting new track

# Camera Settings
#----------------
CAMERA_WIDTH = 320     # Image stream width for opencv motion scanning default=320
CAMERA_HEIGHT = 240    # Image stream height for opencv motion scanning  default=240
CAMERA_FRAMERATE = 35  # framerate for video stream default=35 90 max for V1 cam. V2 can be higher
CAMERA_ROTATION = 0    # Rotate camera image valid values are 0, 90, 180, 270
CAMERA_VFLIP = True    # Flip the camera image vertically if required
CAMERA_HFLIP = False   # Flip the camera image horizontally if required

# Camera Image Settings
#-----------------------
image_path = "images"     # folder name to store images 
image_prefix = "cam1-"    # image name prefix
image_text_bottom = True  # True = Show image text at bottom otherwise at top
image_font_size = 18      # font text height in px for text on images default=18 
image_bigger = 3          # multiply value to resize the default image size 320x240
 
# Motion Event Exclusion Settings
# -------------------------------
MIN_AREA = 170         # Exclude all contours less than or equal to this sq-px Area
x_diff_min = 1         # Exclude if min px away exceeds last event x pos
x_diff_max = 50        # Exclude if max px away for last motion event x pos
max_speed_over = 0     # Exclude track if Speed less than or equal to value specified 0=All 

# This is the Crop Area for motion tracking
y_upper = 100          # Exclude event if y less that this value default=100
y_lower = 200          # Exclude event if y greater than this value default=200
x_left  = 25           # Exclude event if x less than this px position Default=25
x_right = 295          # Exclude event if x greater than this px position Default=295

# OpenCV Motion Tracking Settings
#--------------------------------
FONT_SCALE = .5    # OpenCV window text font size scaling factor default=.5 (lower is smaller)
WINDOW_BIGGER = 2  # resize multiplier for opencv window if gui_window_on=True default = 3
CIRCLE_SIZE = 1    # diameter of circle to show motion location in window
BLUR_SIZE = 10     # OpenCV setting for Gaussian difference image blur 
THRESHOLD_SENSITIVITY = 25  # OpenCV setting for difference image threshold

#--------------------------- End of User Settings -------------------------------------------------
