# ver 13.00 configcam.py Camera Settings. These are imported by strmcam.py

CAMERA = "pilibcam"    # valid values usbcam, rtspcam, pilibcam, pilegcam
CAM_LOCATION = "Front Window"

USBCAM_SRC = 0         # Device number of USB connection usually 0, 1, 2, Etc
RTSPCAM_SRC = "rtsp://user:password@IP:554/path"  # Set per IP Cam Docs and config see example below
                                                  # rtsp://admin:myped@192.168.1.100:554/12

# Camera Image Stream Settings
IM_SIZE = (320, 240)   # Image resolution width, height pixels
IM_VFLIP = False       # True enables flipping image vertically
IM_HFLIP = False       # True enables flipping image horizonally
IM_ROTATION = 0        # Rotate camera image valid values are 0, 90, 180, 270
IM_FRAMERATE = 30      # Legacy Picamera Framerate
