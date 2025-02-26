def strmcam():
    # This is a launcher for creating a video stream for one of various camera types
    # per CAMLIST variable list below

    import sys
    import os
    import time
    import subprocess
    import logging

    PROG_VER="13.1"   # version of this module
    CAM_WARMUP_SEC = 3
    # List of valid camera values in the config.py file
    CAMLIST = ('usbcam', 'rtspcam', 'pilibcam', 'pilegcam')

    # Setup logging
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S"
                       )

    # Import Required Variables from config.py
    try:
        from config import (PLUGIN_ENABLE_ON,
                            PLUGIN_NAME,
                            CAMERA,
                            IM_SIZE,
                            RTSPCAM_SRC,
                            USBCAM_SRC,
                            IM_FRAMERATE,
                            IM_ROTATION,
                            IM_HFLIP,
                            IM_VFLIP
                           )
    except Exception as err_msg:
        logging.error(err_msg)
        sys.exit(1)
    logging.info("Imported Required Camera Stream Settings from config.py")

    if PLUGIN_ENABLE_ON:
        mypath = os.path.abspath(__file__)  # Find the full path of this python script
        # get the path location only (excluding script name)
        baseDir = mypath[0 : mypath.rfind("/") + 1]
        pluginDir = os.path.join(baseDir, "plugins")
        pluginPath = os.path.join(pluginDir, PLUGIN_NAME + ".py")

        # add plugin directory to program PATH
        sys.path.insert(0, pluginDir)
        # Try importing any camera plugin settings if present
        try:
            from plugins.current import (CAMERA, IM_SIZE, RTSPCAM_SRC, USBCAM_SRC,
                                         IM_FRAMERATE, IM_ROTATION, IM_HFLIP, IM_VFLIP)
        except Exception as err_msg:
            logging.warning("%s", err_msg)
        logging.info("%s Imported New Camera Stream Settings from plugin %s", CAMERA.upper(), PLUGIN_NAME)

    # ------------------------------------------------------------------------------
    def is_pi_legacy_cam():
        '''
        Determine if pi camera is configured for Legacy = True or Libcam = False.
        '''
        logging.info("Check for Legacy Pi Camera Module with command - vcgencmd get_camera")
        try:
            camResult = subprocess.check_output("vcgencmd get_camera", shell=True)
            camResult = camResult.decode("utf-8")
            camResult = camResult.replace("\n", "")
            params = camResult.split()
        except Exception as err_msg:
            logging.warning(err_msg)
            return False

        if params[0].find("=1") >= 1 and params[1].find("=1") >= 1:
            logging.info("Pi Camera Module Found %s", camResult)
            return True
        else:
            logging.warning("Problem Finding Pi Legacy Camera %s", camResult)
            logging.warning('Check Camera Connections and Legacy Pi Cam is Enabled per command sudo raspi-config')
            return False


    # ------------------------------------------------------------------------------
    def create_cam_thread(cam_name):
        '''
        Create the appropriate video stream thread
        bassed on the specified camera name
        returns vs video stream and updated camera name with source if applicable
        '''

        cam_name = cam_name.lower()
        if not cam_name in CAMLIST:
            logging.error('%s Not a Valid Camera Value', cam_name)
            logging.info('Valid Values are %s', ' '.join(CAMLIST))
            logging.info('Edit config.py CAMERA variable.')
            sys.exit(1)

        cam_title = None
        if cam_name == 'pilibcam':
            # check if pi libcam
            if not is_pi_legacy_cam():
                if not os.path.exists('/usr/bin/libcamera-still'):
                    logging.error('libcamera not Installed')
                    logging.info('Edit config.py and Change CAMERA variable as Required.')
                    sys.exit(1)
                if not os.path.exists('strmpilibcam.py'):
                    logging.error("strmpilibcam.py File Not Found.")
                    sys.exit(1)
                try:
                    from strmpilibcam import CamStream
                except ImportError:
                    logging.error("import Failed. from strmpilibcam import PiLibCamStream")
                    sys.exit(1)
                cam_title = cam_name
                vs = CamStream(size=IM_SIZE,
                               vflip=IM_VFLIP,
                               hflip=IM_HFLIP).start()

            else:
                logging.error('Looks like Pi Legacy Camera is Enabled')
                logging.info('Edit config.py and Change CAMERA variable as Required.')
                logging.info('or Disable Legacy Pi Camera using command sudo raspi-config')
                sys.exit(1)

        elif cam_name == 'pilegcam':
            # Check if Pi Legacy Camera
            if not is_pi_legacy_cam():
                sys.exit(1)

            # Check if the
            if not os.path.exists('strmpilegcam.py'):
                logging.error("File Not Found. Could Not Import strmpilegcam.py")
                sys.exit(1)

            # Now import the Pi Legacy stream library
            try:
                from strmpilegcam import CamStream
            except ImportError:
                logging.error("Import Failed. from strmpilegcam import CamStream")
                sys.exit(1)
            cam_title = cam_name.upper()

            # Create Legacy Pi Camera Video Stream Thread
            vs = CamStream(size=IM_SIZE,
                           framerate=IM_FRAMERATE,
                           rotation=IM_ROTATION,
                           hflip=IM_HFLIP,
                           vflip=IM_VFLIP).start()
        elif cam_name == 'usbcam' or cam_name == 'rtspcam':
            if cam_name == 'rtspcam':
                cam_src = RTSPCAM_SRC
                cam_title = cam_name.upper() + ' src=' + cam_src
            elif cam_name == 'usbcam':
                cam_src = USBCAM_SRC
                cam_title = cam_name.upper() + ' src=' + str(cam_src)

            if not os.path.exists('strmusbipcam.py'):
                logging.error("File Not Found. Could Not Import strmusbipcam.py")
                sys.exit(1)
            try:
                from strmusbipcam import CamStream
            except ImportError:
                logging.error("Could Not Import Webcam from strmusbipcam.py")
                sys.exit(1)
            vs = CamStream(src=cam_src, size=IM_SIZE).start()

        logging.info("%s", cam_title)
        return vs

    vs = create_cam_thread(CAMERA)
    logging.info("ver %s Warming Up Camera %i sec ...", PROG_VER, CAM_WARMUP_SEC)
    time.sleep(CAM_WARMUP_SEC)  # Allow Camera to warm up
    return vs
