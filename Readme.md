# SPEED CAMERA - Object Motion Tracker [![Mentioned in Awesome <INSERT LIST NAME>](https://awesome.re/mentioned-badge.svg)](https://github.com/thibmaek/awesome-raspberry-pi)
### RPI, Unix and Windows Speed Camera Using python, openCV, RPI camera module, USB Cam or IP Cam
## For Details See [Program Features](https://github.com/pageauc/speed-camera/wiki/Program-Description#program-features), [Wiki Instructions](https://github.com/pageauc/speed-camera/wiki) and [YouTube Videos](https://github.com/pageauc/speed-camera#reference-links).

## Note re Bullseye: 
Speed-cam.py ver 11.26 will now run under the latest Raspberry Pi OS Bullseye with a pi camera module as well as webcam and IP cameras. 
For picamera support Run ***sudo raspi-config***, Interface Options, then enable Legacy Camera option and reboot.

## RPI Quick curl Install or Upgrade   
***IMPORTANT*** - A raspbian **sudo apt-get update** and **sudo apt-get upgrade** will
**NOT** be performed as part of   
**speed-install.sh** so it is highly recommended you run these prior to install
to ensure your system is up-to-date.     

***Step 1*** With mouse left button highlight curl command in code box below. Right click mouse in **highlighted** area and Copy.     
***Step 2*** On RPI putty SSH or terminal session right click, select paste then Enter to download and run script.  

    curl -L https://raw.github.com/pageauc/speed-camera/master/speed-install.sh | bash

This will download and run the **speed-install.sh** script. If running under python3 you will need opencv3 installed.
See my Github [menu driven compile opencv3 from source](https://github.com/pageauc/opencv3-setup) project

***IMPORTANT*** speed-cam.py ver 8.x or greater Requires Updated config.py and plugins.

    cd ~/speed-camera
    cp config.py config.py.bak
    cp config.py.new config.py
    
To replace plugins rename (or delete) plugins folder per below

    cd ~/speed-camera
    mv plugins pluginsold   # renames plugins folder
    rm -r plugins           # deletes plugins folder

Then run ***menubox.sh*** UPGRADE menu pick.

## Mac or Windows Systems
See [Windows 10/11 or Apple Mac Docker Install Quick Start](https://github.com/pageauc/speed-camera#docker-install-quick-start)    
or [Windows or Unix Distro Installs without Docker](https://github.com/pageauc/speed-camera#windows-or-non-rpi-unix-installs)

## Program Description   
This is a raspberry pi, Windows, Unix Distro computer openCV object speed camera demo program.
It is written in python and uses openCV to detect and track the x,y coordinates of the 
largest moving object in the camera view above a minimum pixel area.

User variables are stored in the [***config.py***](https://github.com/pageauc/speed-camera/blob/master/config.py) file.
Motion detection is restricted between ***y_upper***, ***y_lower***, ***x_left***, ***x_right*** variables  (road or area of interest).
Auto calculated but can be overridden in config.py by uncommenting desired variable settings.
Motion Tracking is controlled by the ***track_counter*** variable in config.py.  This sets the number of track events and 
the track length in pixels.  This may need to be tuned for camera view, cpu speed, etc. 
Speed is calculated based on ***cal_obj_px*** and ***cal_obj_mm*** variables for L2R and R2L motion direction. A video stream frame image will be
captured and saved in ***media/images*** dated subfolders (optional) per variable ***imageSubDirMaxFiles*** = ***2000*** 
For variable settings details see [config.py file](https://github.com/pageauc/speed-camera/blob/master/config.py). 

If ***log_data_to_CSV*** = ***True*** then a ***speed-cam.csv*** file will be created/updated with event data stored in
CSV (Comma Separated Values) format. This can be imported into a spreadsheet, database, Etc program for further processing.
Release 8.9 adds a **sqlite3** database to store speed data. Default is ***data/speed_cam.db*** with data in the ***speed*** table.
Database setting can be managed from config.py.  Database is automatically created from config.py settings. For more
details see [How to Manage Sqlite3 Database](https://github.com/pageauc/speed-camera/wiki/How-to-Manage-Sqlite3-Database)

## Admin, Reports, Graphs and Utilities scripts
  
* [***menubox.sh***](https://github.com/pageauc/speed-camera/wiki/Admin-and-Settings#manage-settings-using-menuboxsh)
script is a whiptail menu system to allow easier management of program settings and operation.    
* [***webserver.py***](https://github.com/pageauc/speed-camera/wiki/How-to-View-Data#how-to-view-images-and-or-data-from-a-web-browser)
Allows viewing images and/or data from a web browser (see config.py for webserver settings)
To implement webserver3.py copy webserver3.py to webserver.py  Note and update will undo this change.   
* [***rclone***](https://github.com/pageauc/speed-camera/wiki/Manage-rclone-Remote-Storage-File-Transfer)
Manage settings and setup for optional remote file sync to a remote storage service like google drive, DropBox and many others.   
* [***watch-app.sh***](https://github.com/pageauc/speed-camera/wiki/watch-app.sh-Remote-Manage-Config)
for administration of settings from a remote storage service. Plus application monitoring.  
* [***sql-make-graph-count-totals.py***](https://github.com/pageauc/speed-camera/wiki/How-to-Generate-Speed-Camera-Graphs#sql-make-graph-count-totalspy) Query sqlite database and Generate one or more matplotlib graph images and save to media/graphs folder.
Graphs display counts by hour, day or month for specfied previous days and speed over. Multiple reports can be managed from
the config.py ***GRAPH_RUN_LIST*** variable under matplotlib image settings section.       
* [***sql-make-graph-speed-ave.py***](https://github.com/pageauc/speed-camera/wiki/How-to-Generate-Speed-Camera-Graphs#sql-make-graph-speed-avepy) Query sqlite database and Generate one or more matplotlib graph images and save to media/graphs folder.
Graphs display Average Speed by hour, day or month for specfied previous days and speed over. Multiple reports can be managed from
the config.py ***GRAPH_RUN_LIST*** variable under matplotlib image settings section.    
* [***sql-speed_gt.py***](https://github.com/pageauc/speed-camera/wiki/How-to-Generate-Speed-Camera-Graphs#sql-speed_gtpy) Query sqlite database and Generate html formatted report with links to images and save to media/reports folder.
Can accept parameters or will prompt user if run from console with no parameters
* [***makehtml.py***](https://github.com/pageauc/speed-camera/wiki/How-to-View-Data#view-combined-imagedata-html-pages-on-a-web-browser)
Creates html files that combine csv and image data for easier viewing from a web browser and saved to media/html folder.    
* [***speed-search.py***](https://github.com/pageauc/rpi-speed-camera/wiki/How-to-Run-speed-search.py)
allows searching for similar target object images using opencv template matching.  Results save to media/search folder.    
* [***alpr-speed.py***](https://github.com/pageauc/speed-camera/wiki/alpr-speed.py---Process-speed-images-with-OPENALPR-Automatic-License-Plate-Reader)
This is a demo that processes existing speed camera images with a front or back view of vehicle using [OPENALPR](https://github.com/openalpr/openalpr)
License plate reader. Output is saved to media/alpr folder. For installation, Settings and Run details see
[ALPR Wiki Documentaion](https://github.com/pageauc/speed-camera/wiki/alpr-speed.py---Process-speed-images-with-OPENALPR-Automatic-License-Plate-Reader)       

## Reference Links
* YouTube Speed Lapse Video https://youtu.be/-xdB_x_CbC8
* YouTube Speed Camera Video https://youtu.be/eRi50BbJUro
* YouTube motion-track video https://youtu.be/09JS7twPBsQ  
* [How to Build a Cheap Homemade Speed Camera](https://mass.streetsblog.org/2021/02/26/how-to-build-a-homemade-speed-camera/)  
* Speed Camera RPI Forum post https://www.raspberrypi.org/forums/viewtopic.php?p=1004150#p1004150
* YouTube Channel https://www.youtube.com/user/pageaucp 
* Speed Camera GitHub Repo https://github.com/pageauc/speed-camera      

## Requirements
[***Raspberry Pi computer***](https://www.raspberrypi.org/documentation/setup/) and a [***RPI camera module installed***](https://www.raspberrypi.org/documentation/usage/camera/)
or USB Camera plugged in. Make sure hardware is tested and works. Most [RPI models](https://www.raspberrypi.org/products/) will work OK. 
A quad core RPI will greatly improve performance due to threading. A recent version of 
[Raspbian operating system](https://www.raspberrypi.org/downloads/raspbian/) is Recommended.   
or  
***MS Windows or Unix distro*** computer with a USB Web Camera plugged in and a
[recent version of python installed](https://www.python.org/downloads/)
For Details See [***Wiki details***](https://github.com/pageauc/speed-camera/wiki/Prerequisites-and-Install#windows-or-non-rpi-unix-installs).

It is recommended you upgrade to OpenCV version 3.x.x  For Easy compile of opencv 3.4.2 from source 
See https://github.com/pageauc/opencv3-setup

## Windows or Non RPI Unix Installs
For Windows or Unix computer platforms (non RPI or Debian) ensure you have the most
up-to-date python version. For Download and Install [python](https://www.python.org/downloads) and [Opencv](https://docs.opencv.org/4.x/d5/de5/tutorial_py_setup_in_windows.html)    

The latest python versions includes numpy and recent opencv version that is required to run this code. 
You will also need a USB web cam installed and working. 
To install this program access the GitHub project page at https://github.com/pageauc/speed-camera
Select the ***green Clone or download*** button. The files will be cloned or zipped
to a speed-camera folder. You can run the code from python IDLE application (recommended), GUI desktop
or command prompt terminal window. Note bash .sh shell scripts will not work with windows unless 
special support for bash is installed for windows Eg http://win-bash.sourceforge.net/  http://www.cygwin.com/
***Note:*** I have Not tested these.   

## Docker Install Quick Start
speed camera supports a docker installation on    
Apple Macintosh per [System requirements and Instructions](https://docs.docker.com/desktop/mac/install/)    
and      
Microsoft Windows 10/11 64 bit with BIOS Virtualization enabled
and [Microsoft Windows Subsystem for Linux WSL 2](https://docs.microsoft.com/en-us/windows/wsl/install) 
per [System requirements and Instructions](https://docs.docker.com/desktop/windows/install/).   

1. Download and install [Docker Desktop](https://www.docker.com/get-started) for your System
1. Clone the GitHub [Speed Camera repository](https://github.com/pageauc/speed-camera) using green Clone button (top right)
1. Run [docker-compose up](https://docs.docker.com/compose/reference/up/) from the directory you cloned the repo into.
1. The Docker container will likely exit because it is using a default config.
1. Edit the configuration file @ `config/config.py`
1. Run [docker-compose up](https://docs.docker.com/compose/reference/up/) per documentation
1. Run [docker build](https://docs.docker.com/engine/reference/commandline/build/) command locally to get a fresh image.
 
## Raspberry pi Manual Install or Upgrade   
From logged in RPI SSH session or console terminal perform the following. Allows you to review install code before running

    cd ~
    wget https://raw.github.com/pageauc/speed-camera/master/speed-install.sh
    more speed-install.sh       # You can review code if you wish
    chmod +x speed-install.sh
    ./speed-install.sh  # runs install script.
    
## Run to view verbose logging 

    cd ~/speed-camera    
    ./speed-cam.py
    
See [***How to Run***](https://github.com/pageauc/speed-camera/wiki/How-to-Run) speed-cam.py wiki section

***IMPORTANT*** Speed Camera will start in ***calibrate*** = ***True*** Mode.    
Review settings in ***config.py*** file and edit variables with nano as required.
You will need to perform a calibration to set the correct value for config.py ***cal_obj_px*** and ***cal_obj_mm*** for
L2R and R2L directions. The variables are based on the distance from camera to objects being measured for speed.
See [***Calibration Procedure***](https://github.com/pageauc/speed-camera/wiki/Calibrate-Camera-for-Distance) for more details.     

The config.py motion tracking variable called ***track_counter*** = can be adjusted for your system and opencv version.
Default is 5 but a quad core RPI3 and latest opencv version eg 3.4.2 can be 10-15 or possibly greater.  This will
require monitoring the verbose log messages in order to fine tune.
    
## Run menubox.sh 

    cd ~/speed-camera
    ./menubox.sh

Admin speed-cam Easier using menubox.sh (Once calibrated and/or testing complete)  
![menubox main menu](https://github.com/pageauc/speed-camera/blob/master/menubox.png)     

View speed-cam data and trends from web browser per sample screen shots. These can be generated 
from Menubox.sh menu pick or by running scripts from console or via crontab schedule.

![Speed Camera GRAPHS Folder Web Page](https://github.com/pageauc/speed-camera/blob/master/speed_web_graphs.png)  
![Speed Camera REPORTS Folder Web Page](https://github.com/pageauc/speed-camera/blob/master/speed_web_reports.png)   
![Speed Camera HTML Folder Web Page](https://github.com/pageauc/speed-camera/blob/master/speed_web_html.png)    

You can view recent or historical images directly from the speed web browser page.  These are dynamically created
and show up-to-date images.  Press the web page refesh button to update display 
![Speed Camera RECENT Folder Web Page](https://github.com/pageauc/speed-camera/blob/master/speed_web_recent.png)   
![Speed Camera IMAGES Folder Web Page](https://github.com/pageauc/speed-camera/blob/master/speed_web_images.png)   

## Credits  
Some of this code is based on a YouTube tutorial by
Kyle Hounslow using C here https://www.youtube.com/watch?v=X6rPdRZzgjg

Thanks to Adrian Rosebrock jrosebr1 at http://www.pyimagesearch.com 
for the PiVideoStream Class code available on github at
https://github.com/jrosebr1/imutils/blob/master/imutils/video/pivideostream.py
  
Have Fun   
Claude Pageau    
YouTube Channel https://www.youtube.com/user/pageaucp   
GitHub Repo https://github.com/pageauc
