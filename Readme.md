# SPEED CAMERA - Object Motion Tracker [![Mentioned in Awesome <INSERT LIST NAME>](https://awesome.re/mentioned-badge.svg)](https://github.com/thibmaek/awesome-raspberry-pi)
### RPI, Unix and Windows Speed Camera Using python, openCV, USB Cam or RPI camera module
## For Details See [Program Features](https://github.com/pageauc/speed-camera/wiki/Program-Description#program-features) and [Wiki Instructions](https://github.com/pageauc/speed-camera/wiki) and [YouTube Videos](https://github.com/pageauc/speed-camera#links)

## RPI Quick Install or Upgrade   
***IMPORTANT*** - A raspbian **sudo apt-get update** and **sudo apt-get upgrade** will
**NOT** be performed as part of   
**speed-install.sh** so it is recommended you run these prior to install
to ensure your system is up-to-date.     

***Step 1*** With mouse left button highlight curl command in code box below. Right click mouse in **highlighted** area and Copy.     
***Step 2*** On RPI putty SSH or terminal session right click, select paste then Enter to download and run script.  

    curl -L https://raw.github.com/pageauc/speed-camera/master/speed-install.sh | bash

This will download and run the **speed-install.sh** script. If running under python3 you will need opencv3 installed.
See my Github [menu driven compile opencv3 from source](https://github.com/pageauc/opencv3-setup) project

## Program Description   
This is a raspberry pi, Windows, Unix Distro computer openCV object speed camera demo program.
It is written in python and uses openCV to detect and track the x,y coordinates of the 
largest moving object in the camera view above a minimum pixel area.
User variables are stored in the [***config.py***](https://github.com/pageauc/speed-camera/blob/master/config.py) file.
Motion detection is restricted between ***y_upper***, ***y_lower***, ***x_left***, ***x_right*** variables  (road or area of interest).
If a track is longer than ***track_len_trig*** variable then average speed will be 
calculated based on ***cal_obj_px*** and ***cal_obj_mm*** variables and a speed photo will be
taken and saved in ***media/images*** dated subfolders per variable ***imageSubDirMaxFiles*** = ***1000*** 
(see config.py). 

If ***log_data_to_CSV*** = ***True*** then a ***speed-cam.csv*** file will be created/updated with event data stored in
CSV (Comma Separated Values) format. This can be imported into a spreadsheet, database, Etc program for further processing.
Release 8.9 adds a **sqlite3** database to store speed data. Default is ***data/speed_cam.db*** with data in the ***speed*** table .
there is a simple report ***sql_speed_gt.sh*** that can query for records with greater than a specified speed.
I plan on doing more but this should be a good start. Take a look at the code for details.

Also included are 
  
* [***menubox.sh***](https://github.com/pageauc/speed-camera/wiki/Admin-and-Settings#manage-settings-using-menuboxsh)
script is a whiptail menu system to allow easier management of program settings and operation. 
* [***rclone***](https://github.com/pageauc/speed-camera/wiki/Manage-rclone-Remote-Storage-File-Transfer)
for optional remote file sync to a remote storage service like google drive, DropBox and many others. 
* [***watch-app.sh***](https://github.com/pageauc/speed-camera/wiki/watch-app.sh-Remote-Manage-Config)
for administration of settings from a remote storage service. Plus application monitoring.
* [***speed-search.py***](https://github.com/pageauc/rpi-speed-camera/wiki/How-to-Run-speed-search.py)
allows searching for similar target object images using opencv template matching. 
* [***makehtml.py***](https://github.com/pageauc/speed-camera/wiki/How-to-View-Data#view-combined-imagedata-html-pages-on-a-web-browser)
creates html files that combine csv and image data for easier viewing from a web browser.
(Does not work with ***secpicam480.py*** or ***secwebcam480.py*** plugins enabled.
* [***webserver.py***](https://github.com/pageauc/speed-camera/wiki/How-to-View-Data#how-to-view-images-and-or-data-from-a-web-browser)
Allows viewing images and/or data from a web browser (see config.py for webserver settings)
* [***sql_speed_gt.sh***](https://github.com/pageauc/speed-camera/blob/master/sql_speed_gt.sh) Prompts for a speed value and runs a simple
sqlite3 query to show all record that exceed the specified speed. Output can be found in media/reports folder and is available from browser. 
* [***sql_hour_count.py***](https://github.com/pageauc/speed-camera/blob/master/sql_hour_count.py) Run report for count by hour.
also produces a graph using gnuplot. Query output html report and .png graph can be found in media/reports folder and is available from browser.

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
up-to-date python version. For Downloads visit https://www.python.org/downloads    

The latest python versions includes numpy and recent opencv version that is required to run this code. 
You will also need a USB web cam installed and working. 
To install this program access the GitHub project page at https://github.com/pageauc/speed-camera
Select the ***green Clone or download*** button. The files will be cloned or zipped
to a speed-camera folder. You can run the code from python IDLE application (recommended), GUI desktop
or command prompt terminal window. Note bash .sh shell scripts will not work with windows unless 
special support for bash is installed for windows Eg http://win-bash.sourceforge.net/  http://www.cygwin.com/
Note I have Not tested these.   

***IMPORTANT*** speed-cam.py ver 8.x or greater Requires Updated config.py and plugins.

    cd ~/speed-camera
    cp config.py config.py.bak
    cp config.py.new config.py
    
To replace plugins rename (or delete) plugins folder per below

    cd ~/speed-camera
    mv plugins pluginsold   # renames plugins folder
    rm -r plugins           # deletes plugins folder

Then run ***menubox.sh*** UPGRADE menu pick.
 
## Manual Install or Upgrade   
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
You will need to perform a calibration to set the correct value for config.py ***cal_obj_px*** and ***cal_obj_mm*** 
variables based on the distance from camera to objects being measured for speed.
See [***Calibration Procedure***](https://github.com/pageauc/speed-camera/wiki/Calibrate-Camera-for-Distance) for more details.     

The config.py motion tracking variable called track_counter = can be adjusted for your system and opencv version.
default is 5 but a quad core RPI3 and latest opencv version eg 3.4.2 can be 10-15 or possibly greater. 
    
## Run menubox.sh 

    cd ~/speed-camera
    ./menubox.sh

Admin speed-cam Easier using menubox.sh (Once calibrated and/or testing complete)  
![menubox main menu](https://github.com/pageauc/speed-camera/blob/master/menubox.png)     

View speed-cam data and trends from web browser per sample screen shots

![Speed Camera Web Recent View](https://github.com/pageauc/speed-camera/blob/master/speed_web_recent.png)   
![Speed Camera Web html speed list Report](https://github.com/pageauc/speed-camera/blob/master/speed_web_sqlite.png)   
![Speed Camera Web Recent View](https://github.com/pageauc/speed-camera/blob/master/speed_web_gnuplot.png)   

## Links
* YouTube Speed Lapse Video https://youtu.be/-xdB_x_CbC8
* YouTube Speed Camera Video https://youtu.be/eRi50BbJUro
* YouTube motion-track video https://youtu.be/09JS7twPBsQ
* Speed Camera RPI Forum post https://www.raspberrypi.org/forums/viewtopic.php?p=1004150#p1004150
* YouTube Channel https://www.youtube.com/user/pageaucp 
* Speed Camera GitHub Repo https://github.com/pageauc/speed-camera      

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
