### supervisor folder
speed-cam.sh and speed-web.sh use supervisorctl service to start, stop, status, Etc. speed-cam.py and speed-web.py per the configuration files in the supervisor folder. 
This will run the programs as background tasks under the specified user. 
These processes will Not autostart=false on boot but will attempt a restart=true if there is a program issue. Eg temporary communication timeout eg RTSP camera stream.

For more details see [How to Use run.sh wiki](https://github.com/pageauc/speed-camera/wiki/How-to-use-run.sh)