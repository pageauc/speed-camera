# speed2.py - RPI OpenCV2 Object Speed Tracker
####  A Raspberry Pi Speed Camera using python, Video Stream Thread, pi-camera

For Easy speed2 install onto raspbian RPI. 

    curl -L https://raw.github.com/pageauc/motion-track/master/speed-track-2/install.sh | bash

From a computer logged into the RPI via ssh(Putty) session use mouse to highlight command above, right click, copy.  
Then select ssh(Putty) window, mouse right click, paste.  The command should 
download and execute the github install.sh script for speed2 object(vehicle) speed tracker.  Note a raspbian
apt-get update and upgrade will be performed as part of install so it may take some time if these are not 
up-to-date

How to Run speed2 https://github.com/pageauc/motion-track/wiki/Running-Program

### Links
* speed-track YouTube video here https://youtu.be/eRi50BbJUro
* speed2 RPI forum post here https://www.raspberrypi.org/forums/viewtopic.php?p=1004150#p1004150
* motion-track YouTube video here using RPI B2 https://youtu.be/09JS7twPBsQ
* YouTube Channel https://www.youtube.com/user/pageaucp   
* GitHub Repo https://github.com/pageauc

### Release History
* ver 2.03 16-May-2016 - Enhanced streaming speed by using threading

### Program Description
This is a raspberry pi computer openCV2 object speed camera demo program.
It is written in python and uses openCV2 to detect and track object motion.
The results are recorded on speed photos and data in a CSV file that can be
imported to a spreadsheet or other program for additiona processing.  
The program will detect motion in the field of view and use opencv to calculate
the largest contour and return its x,y coordinate. Motion detection is
restricted between y_upper and y_lower variables (road area).  If a track
is longer than track_len_trig variable then average speed will be 
calculated (based on IMAGE_VIEW_FT variable) and a speed photo will be
taken and saved in an images folder. If log_data_to_file=True then a
speed2.csv file will be created/updated with event data stored in
CSV (Comma Separated Values) format. This can be imported into a spreadsheet.

#### Credits
Some of this code is based on a YouTube tutorial by
Kyle Hounslow using C here https://www.youtube.com/watch?v=X6rPdRZzgjg

Thanks to Adrian Rosebrock jrosebr1 at http://www.pyimagesearch.com 
for the PiVideoStream Class code available on github at
https://github.com/jrosebr1/imutils/blob/master/imutils/video/pivideostream.py

### Quick Setup
Requires a Raspberry Pi computer with a RPI camera module installed, configured
and tested to verify it is working. I used a RPI model B2 but a B+ , 3 or 
earlier will work OK. A quad core processor will greatly improve performance
due to threading

For Easy speed2 install onto raspbian RPI. 

    curl -L https://raw.github.com/pageauc/motion-track/master/speed-track-2/install.sh | bash

From a computer logged into the RPI via ssh(Putty) session use mouse to highlight command above, right click, copy.  
Then select ssh(Putty) window, mouse right click, paste.  The command should 
download and execute the github install.sh script for speed2 object(vehicle) speed tracker.

### or

From logged in RPI SSH session or console terminal perform the following.

    wget https://raw.github.com/pageauc/motion-track/master/speed-track-2/install.sh
    chmod +x install.sh
    ./install.sh
    ./speed2.py

Run install.sh again to upgrade to latest version of speed2 code.
    
IMPORTANT - Review settings in config.py file and edit variables with nano as required.
You will need to perform a calibration to set the correct value for IMAGE_VIEW_FT 
variable based on the distance from camera to objects being measured for speed.  
See video and this Readme.md below for more details.

### Running Speed2
    
if wish to run speed2.py in background or on boot from /etc/rc.local then

    ./speed2.sh
    
or edit /etc/rc.local file using nano editor per command below

    sudo nano /etc/rc.local

Then add line below before the exit line then ctrl-x y to save and reboot to test

    /home/pi/speed2/speed2.sh
    exit 0    
    
Edit the speed2.sh script to suit your needs per comments.  
Note you may need to change the sleep delay time if rc.local does not run script
successfully at boot, since services may need more time to start.  
        
To Run using python3 perform the following (Note you must have opencv for python3 already installed)
NOTE: operation under python3 is not very good compared to python2 IMO. I recommend you run under python2

    sudo apt-get install -y python3-pip  
    sudo pip-3.2 install -y Pillow
    python3 ./speed2.py
    
if you get opengl error then install support library per following command then reboot.

    sudo apt-get install libgl1-mesa-dri  
    
also on raspberry pi 3's activate opengl support using 
 
    sudo raspi-config,

From 9 Advanced Options select AA GL Driver then enable driver and reboot 
    
You can also use git clone to copy the files to your RPI.

    cd ~
    git clone https://github.com/pageauc/motion-track.git
 
The speed-track-2 files will be in the motion-track/speed-track-2 subfolder. You can
then move them to another location if you wish.
 
Note A default images folder will be created to store jpg speed photos. There is an
image_path variable in the config.py file.  Use nano editor to change path and/or
other variables as desired.

Use the calibrate option and follow instructions below to calculate an accurate
value for IMAGE_VIEW_FT variable in the speed_settings.py
    
### Calibrate IMAGE_VIEW_FT variable
  
speed2.py needs to be calibrated in order to display a correct speed.

#### Calibration Procedure

* Setup the RPI camera to point to the view to be monitored.
* Login to RPI using SSH or desktop terminal session and cd to speed-track folder
* Use nano to edit speed_settings.py. Edit variable calibrate=True  ctl-x y to save
* Start speed_track.py eg python ./speed_track.py
* Motion will automatically be detected and calibration images will be
  put in images folder with prefix calib-
* Monitor progress and calibration images. Press ctrl-c to Quit when done. 
* Adjust the y_upper and y_lower variables to cover the road area.  Note
  image 0,0 is the top left hand corner and values are in pixels.  Do not
  exceed the CAMERA_HEIGHT default 240 value  
* Open calibration images with an image viewer program and use hash marks to
  record pixels for vehicle length
  Note each division is 10 pixels.  I use filezilla to transfer files to/from
  my PC and the RPI using sftp protocol and the RPI IP address.
* Use formula below to calculate a value for IMAGE_VIEW_FT variable   
  You should use several photos to confirm and average results.
* Use nano to edit the speed_settings.py and change IMAGE_VIEW_FT variable value
  to new calculated value.  Also change variable calibrate = False
* Restart speed_track.py and monitor console messages.
  Perform a test using a vehicle at a known speed to verify calibration.
* Make sure y_upper and y_lower variables are correctly set for the area to
  monitor. This will restrict motion detection to area between these variable
  values.  Make sure top of vehicles is included.
  
Please note that if road is too close and/or vehicles are moving too quickly then
the camera may not capture motion and/or record vehicle in speed photo.
  
#### Calibration formula
Use this formula to calculate a value for IMAGE_VIEW_FT
 
IMAGE_VIEW_FT = (CAMERA_WIDTH * Ref_Obj_ft) / num_px_for_Ref_Object

eg (320 * 18) / 80 = 72
  
### Settings

Variable values are stored in the config.py file and are imported
when speed2.py is run.  Use the nano editor to modify these settings
per the comments.  Most settings should be OK and should not need to be
changed. Others may need to be fine tuned.  The openCV settings most
likely won't need to be changed unless you are familiar with them.

Note if log_data_to_file is set it will save a data to a .csv file
in the same folder as speed2.py  eg speed2.csv 

Have Fun   
Claude Pageau

YouTube Channel https://www.youtube.com/user/pageaucp   
GitHub Repo https://github.com/pageauc
