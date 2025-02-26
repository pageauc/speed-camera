## speed-cam.sh and speed-web.sh
The bash scripts manage the speed-camera supervisorctl background service for speed-cam.py and speed-web.py
located in the supervisor folder. 
The scripts can start the .py scripts as background tasks under the specified user= in the conf file settings. 
These .conf files will by default not autostart run on boot but will attempt a restart if there is a program issue. 
Eg problem with camera.

The shell script install option creates a symlink at ***/etc/supervisor/conf.d*** folder back 
to the speed-camera/supervisor folder .conf files.  Use ./speed-cam.sh and/or speed-web.sh to manage options.
  
Note: Start on boot defaults to false, but can be enabled by editing the appropriate .conf file

For more details run 
    
    ./speed-cam.sh help
	
or

    ./speed-web.sh help	
    
and/or
    
    ./speed-web.sh help.

example .    
./speed-cam.sh help

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

Note:

The supervisor folder .conf files default to user=pi. The .sh scripts will modify the appropriate .conf file
per the logged in user (using sed).



    