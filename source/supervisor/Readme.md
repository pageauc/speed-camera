## speed-cam.sh and speed-web.sh
### Introduction
The bash scripts manage the speed-camera supervisorctl background service for speed-cam.py and speed-web.py.
The scripts can start, stop Etc. the .py scripts as background tasks under the specified ***user=*** per the conf file settings located in
the supervisor folder.
These .conf files will by default not autostart (run on boot) or perform a restart if there is a program issue.
Eg problem with camera.

### Install

The shell scripts ***install*** option creates a symlink at ***/etc/supervisor/conf.d*** folder back
to the speed-camera/supervisor folder .conf files.  Use ./speed-cam.sh and/or speed-web.sh to manage install option.

    cd ~/speed-camera
    ./speed-cam.sh install
    ./speed-web.sh install
	
Make sure you have test run speed-cam.py and speed-web.py to make sure they run correctly.
Use Ctrl-c to Exit python scripts.

    cd ~/speed-camera
    ./speed-cam.py
	
    ./speed-web.py
	
If they run OK, you can start them as a background process directly per below or use menubox.sh

     cd ~/speed-camera
    ./speed-cam.sh start
    ./speed-web.sh start
	
	./speed-cam.sh status	
	-----------------------------------------------
	./speed-cam.sh supervisorctl status
    speed-cam                      RUNNING   pid 21464, uptime 3:45:51
    speed-web                      RUNNING   pid 21452, uptime 3:46:05
    Done	

### Run
Access help for speed-cam.sh and or speed-web.sh

    cd ~/speed-camera
    ./speed-cam.sh help

    -----------------------------------------------
    ./speed-cam.sh supervisorctl help

    Usage: ./speed-cam.sh [Option]

      Options:
      start        Start supervisor service
      stop         Stop supervisor service
      restart      restart supervisor service
      status       Status of supervisor service
      edit         nano edit /home/pi/pi-speed/supervisor
      log          tail -n 200 /var/log/speed-cam.log
      install      Install symbolic link for speed-cam supervisor service
      uninstall    Uninstall symbolic link for speed-cam supervisor service
      upgrade      Upgrade pi-speed files from GitHub
      help

    Example:  ./speed-cam.sh status

    Wait ...

    speed-cam                      RUNNING   pid 21464, uptime 3:45:51
    speed-web                      RUNNING   pid 21452, uptime 3:46:05
    Done

	
### Edit Settings 	
***Note:*** The supervisor folder .conf files default to user=pi. 
The .sh scripts will ***auto modify the appropriate .conf file***
for the current logged in user (using sed) so user references need not be changed.

To edit a .conf file Eg. supervisor/speed-cam.conf

    ./speed-web.sh edit
    or
    ./speed-cam.sh edit

	[program:speed-cam]
	process_name=speed-cam
	autostart=false
	autorestart=false
	startsecs=5
	user=pi
	command=python3 speed-cam.py
	directory=/home/pi/speed-camera/
	stdout_logfile=/var/log/speed-cam.log
	stdout_logfile_maxbytes=1MB
	stdout_logfile_backups=1
	redirect_stderr=true

Ctrl-x y to save changes and exit nano

The script will then run supervisorctl to reread the .conf file for changes and update.  
Note process will be stopped.

Most settings should not need to be changed. The most common would be

	autostart=true    # Will start supervisorctl procees On system Boot

	autorestart=true  # Will try to restart program if it exits eg problem with camera

***Note*** autorestart=true may create a continuous loop if eg camera problem cannot be resolved
autorestart=false is the default. If there is a problem manually run the appropriate python script

    ./speed-cam.sh start
	Wait a while then retry
	./speed-cam.sh status   # in example below camera was already in use
	-----------------------------------------------
	./speed-cam.sh supervisorctl status
	speed-cam                        EXITED    Feb 27 09:41 AM
	speed-web                        STOPPED   Not started
	timolo2-cam                      RUNNING   pid 6725, uptime 2:01:15
	timolo2-web                      RUNNING   pid 1454, uptime 16:43:46


	pi@rpi-arducam:~/speed-camera $ ./speed-cam.py
	Loading Wait...
	----------------------------------------------------------------------
	speed-cam.py 13.2  written by Claude Pageau
	Motion Track Largest Moving Object and Calculate Speed per Calibration.
	----------------------------------------------------------------------
	2025-03-01 04:05:18 INFO     strmcam    Imported Required Camera Stream Settings from config.py
	2025-03-01 04:05:18 INFO     is_pi_legacy_cam Check for Legacy Pi Camera Module with command - vcgencmd get_camera
	2025-03-01 04:05:18 WARNING  is_pi_legacy_cam Problem Finding Pi Legacy Camera supported=0 detected=0, libcamera interfaces=0
	2025-03-01 04:05:18 WARNING  is_pi_legacy_cam Check Camera Connections and Legacy Pi Cam is Enabled per command sudo raspi-config
	[59:10:13.306679480] [26112]  INFO Camera camera_manager.cpp:327 libcamera v0.4.0+53-29156679
	[59:10:13.374879946] [26117] ERROR V4L2 v4l2_device.cpp:390 'imx708': Unable to set controls: Device or resource busy
	[59:10:13.447371690] [26117]  WARN RPiSdn sdn.cpp:40 Using legacy SDN tuning - please consider moving SDN inside rpi.denoise
	[59:10:13.457334918] [26117]  INFO RPI vc4.cpp:447 Registered camera /base/soc/i2c0mux/i2c@1/imx708@1a to Unicam device /dev/media3 and ISP device /dev/media0
	[59:10:13.457599708] [26117]  INFO RPI pipeline_base.cpp:1121 Using configuration file '/usr/share/libcamera/pipeline/rpi/vc4/rpi_apps.yaml'
	2025-03-01 04:05:21 INFO     _initialize_camera Initialization successful.
	[59:10:13.466883772] [26112]  INFO Camera camera.cpp:1008 Pipeline handler in use by another process
	2025-03-01 04:05:21 ERROR    __init__   Camera __init__ sequence did not complete.
	WARN : Camera Error. Retrying 3
	Traceback (most recent call last):
	  File "/usr/lib/python3/dist-packages/picamera2/picamera2.py", line 269, in __init__
		self._open_camera()
	  File "/usr/lib/python3/dist-packages/picamera2/picamera2.py", line 477, in _open_camera
		self.camera.acquire()
	RuntimeError: Failed to acquire camera: Device or resource busy


In example above timolo2-cam was using the camera



