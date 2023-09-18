def strmcam():
    # This is a launcher for the creating video a stream for one of various camera types 
    # per CAMLIST list below

    import sys
    import os
    import time
    import subprocess
    import logging

    # Setup logging
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S"
                       )

    # List of valid camera values in the configcam.py file
    CAMLIST = ('usbcam', 'rtspcam', 'pilibcam', 'pilegcam')

    # Import Required Variables from configcam.py
    try:
        from configcam import (CAMERA,
                               IM_SIZE,
                               RTSPCAM_SRC,
                               USBCAM_SRC,
                               IM_FRAMERATE,
                               IM_ROTATION,
                               IM_HFLIP,
                               IM_VFLIP
                              )
    except Exception as e:
        logging.error(e)
        sys.exit(1)

    # fix rounding problems with picamera resolution
    new_im_w = (IM_SIZE[0] + 31) // 32 * 32
    new_im_h = (IM_SIZE[1] + 15) // 16 * 16
 
    new_im_size = (new_im_w, new_im_h)

    # ------------------------------------------------------------------------------
    def is_pi_legacy_cam():
        '''
        Determine if pi camera is configured for Legacy = True or Libcam = False.
        '''
        logging.info("Check for Legacy Pi Camera Module with command - vcgencmd get_camera")
        camResult = subprocess.check_output("vcgencmd get_camera", shell=True)
        camResult = camResult.decode("utf-8")
        camResult = camResult.replace("\n", "")
        params = camResult.split()
        if params[0].find("=1") >= 1 and params[1].find("=1") >= 1:
            logging.info("Pi Camera Module Found %s", camResult)
            return True
        else:
            logging.warn("Problem Finding Pi Legacy Camera %s", camResult)
            logging.warn('Check Camera Connections and Legacy Pi Cam is Enabled per command sudo raspi=config')
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
            logging.info('Edit configcam.py CAMERA variable.')
            sys.exit(1)

        cam_title = None
        if cam_name == 'pilibcam':
            # check if pi libcam
            if not is_pi_legacy_cam():
                if not os.path.exists('/usr/bin/libcamera-still'):
                    logging.error('libcamera not Installed')
                    logging.info('Edit configcam.py and Change CAMERA variable as Required.')
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
                vs = CamStream(size=new_im_size,
                               vflip=IM_VFLIP,
                               hflip=IM_HFLIP).start()

            else:
                logging.error('Looks like Pi Legacy Camera is Enabled')
                logging.info('Edit configcam.py and Change CAMERA variable as Required.')
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
            cam_title = cam_name

            # Create Legacy Pi Camera Video Stream Thread
            vs = CamStream(size=new_im_size,
                           framerate=IM_FRAMERATE,
                           rotation=IM_ROTATION,
                           hflip=IM_HFLIP,
                           vflip=IM_VFLIP).start()
        elif cam_name == 'usbcam' or cam_name == 'rtspcam':
            if cam_name == 'rtspcam':
                cam_src = RTSPCAM_SRC
                cam_title = cam_name + ' src=  ' + cam_src
            elif cam_name == 'usbcam':
                cam_src = USBCAM_SRC
                cam_title = cam_name + ' src= ' + str(cam_src)

            if not os.path.exists('strmusbipcam.py'):
                logging.error("File Not Found. Could Not Import strmusbipcam.py")
                sys.exit(1)
            try:
                from strmusbipcam import CamStream
            except ImportError:
                logging.error("Could Not Import Webcam from strmusbipcam.py")
                sys.exit(1)
            vs = CamStream(src=cam_src, size=new_im_size).start()

        logging.info("%s Started Video Stream Thread.", cam_title.upper())
        return vs

    vs = create_cam_thread(CAMERA)
    logging.info("Warming Up Camera.")
    time.sleep(3)  # Allow Camera to warm up
    return vs
