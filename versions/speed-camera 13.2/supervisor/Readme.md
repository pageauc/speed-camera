### supervisor folder
run.sh uses supervisorctl service to start, stop, status, Etc. speed-cam.py and webserver.py per the configuration files in the supervisor folder. 
This will run the programs as background tasks under the specified user. 
These processes will auto start on boot and/or attempt a restart if there is a program issue. Eg temporary communication timeout eg RTSP camera stream.

For more details see [How to Use run.sh wiki](https://github.com/pageauc/speed-camera/wiki/How-to-use-run.sh)