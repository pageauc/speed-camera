# speed-cam.py - Speed Camera Object Motion Tracker 
### RPI, Unix and Windows Speed Camera Using python, openCV, pi-camera or USB Cam

### For Details See [Speed Camera GitHub Wiki](https://github.com/pageauc/rpi-speed-camera/wiki)

* 6.50  Rewrote code to simplify image text and make compatible with Non RPI
        Unix or Windows platforms using a Web Cam.  Tested and Works OK.

* 6.00  Added Optional SubDir creation by number of files or by SubDir Age
        Also Added Disk Space Management that deletes oldest file in specified Dir Tree
        to maintain a specified amount of Free disk space (default 500 MB)
        Also added try, except, pass for loading of pi-camera libraries
        This should allow speed-cam.py to work on Non RPI platforms with Web Cam eg Ubuntu or windows       

* 5.00 Added search-speed.py that uses opencv template matching to find similar images.  To use,
       use menubox.sh menuing or command line to copy one or more search image(s) to the
       default media/search folder and run search-speed.py.  
       if the config.py variable copy_results_on=True then image match files including orignal search file 
       are copied to a subfolder with the same name as the search image filename but without the file extension. 
       If you set config.py gui_window_on=True a Searching and Target window will be displayed on the
       RPI desktop.  When a match is found it will be displayed for 4 seconds.
       Results can also be reviewed from a web browser by running ./webserver.py and accessing link for search/subfolder
       (Note: search-speed.py is still under development)
          
* IMPORTANT: speed-cam.py release 5.x or above requires a full install.
It is advised that you rename/delete previous rpi-speed-camera folder
and rerun GitHub Quick Install or Manual Install.  The default config.py is based on the
config.py.240 file and works with single core RPI's. The config.py.720 is designed for quad core RPI's.
Use menubox.sh to change settings or nano config.py

### Quick Install   
Easy Install of speed-cam onto a Raspberry Pi Computer with latest Raspbian. 

    curl -L https://raw.github.com/pageauc/rpi-speed-camera/master/speed-install.sh | bash

From a computer logged into the RPI via ssh(Putty) session use mouse to highlight command above, right click, copy.  
Then select ssh(Putty) window, mouse right click, paste.  The command should 
download and execute the github speed-install.sh script for rpi-speed-camera object(vehicle) speed tracker.  
This install can also be done directly on an Internet connected Raspberry Pi via a console or desktop terminal session and web browser.      
Note - a raspbian apt-get update and upgrade will be performed as part of install 
so it may take some time if these are not up-to-date

#### or Manual Install   
From logged in RPI SSH session or console terminal perform the following.

    wget https://raw.github.com/pageauc/rpi-speed-camera/master/speed-install.sh
    chmod +x speed-install.sh
    ./speed-install.sh
    cd rpi-speed-camera
    ./speed-cam.py
    
or menubox.sh

    cd ~/rpi-speed-camera
    ./menubox.sh

Admin speed-cam Easier using menubox.sh   
![menubox main menu](https://github.com/pageauc/rpi-speed-camera/blob/master/menubox.png)  
    
### Links  

* YouTube Speed Camera Video https://youtu.be/eRi50BbJUro
* YouTube Speed Lapse Video https://youtu.be/-xdB_x_CbC8
* Speed Camera RPI Forum post https://www.raspberrypi.org/forums/viewtopic.php?p=1004150#p1004150
* YouTube motion-track video https://youtu.be/09JS7twPBsQ
* YouTube Channel https://www.youtube.com/user/pageaucp 
* Speed Camera GitHub Repo https://github.com/pageauc/rpi-speed-camera     
    
### Requirements
Requires a Raspberry Pi computer with a RPI camera module or a USB Web Camera installed, configured
and tested to verify it is working. I used a RPI model B2 but a B+ , 3 or 
earlier will work OK. A quad core processor will greatly improve performance
due to threading. A recent version of Raspbian operating system is recommended.
    
IMPORTANT - Review settings in config.py file and edit variables with nano as required.
You will need to perform a calibration to set the correct value for cal_obj_px and cal_obj_mm 
variable based on the distance from camera to objects being measured for speed.  
See video and this Readme.md below for more details.     
    
See How to Run speed-cam.py section below

### Program Description   
This is a raspberry pi computer openCV2 object speed camera demo program.
It is written in python and uses openCV2 to detect and track object motion.
This can be vehicles or any other moving objects.  It tracks the speed of
the largest moving object in the camera view above a minimum pixel area.
The results are recorded on speed photos and in a CSV data file that can be
imported to a spreadsheet or other program for additional processing.  You
can also run makehtml.sh to generate html files that combine csv and image
data.

The program will detect motion in the field of view and use opencv to calculate
the largest contour and return its x,y coordinate. Motion detection is
restricted between y_upper and y_lower variables (road or area of interest).
If a track is longer than track_len_trig variable then average speed will be 
calculated (based on cal_obj_px and cal_obj_mm variables) and a speed photo will be
taken and saved in an images folder. If log_data_to_file=True then a
speed2.csv file will be created/updated with event data stored in
CSV (Comma Separated Values) format. This can be imported into a spreadsheet.

### How to Run    
To run speed-cam.py as a background task or on boot from /etc/rc.local then

    cd ~/rpi-speed-camera
    ./speed-cam.sh start
    
or to run on boot edit /etc/rc.local file using nano editor per command below

    sudo nano /etc/rc.local

Then add line below before the exit line then ctrl-x y to save and reboot to test

    /home/pi/rpi-speed-camera/speed-cam.sh start
    exit 0    
    
Edit the speed-cam.sh script to suit your needs per comments.  
Note you may need to change the sleep delay time if rc.local does not run script
successfully at boot, since services may need more time to start.  
        
To Run using python3 perform the following (Note you must have opencv for python3 already installed)
NOTE: operation under python3 is not faster compared to python2 IMO. I recommend you run under python2

    sudo apt-get install -y python3-pip  
    sudo pip-3.2 install -y Pillow
    python3 ./speed-cam.py
    
if you get opengl error then install support library per following command then reboot.

    sudo apt-get install libgl1-mesa-dri  
    
also on raspberry pi 3's activate opengl support using 
 
    sudo raspi-config,

From 9 Advanced Options select AA GL Driver then enable driver and reboot 
    
You can also use git clone to copy the files to your RPI.

    cd ~
    git clone https://github.com/pageauc/rpi-speed-camera.git
 
The speed-cam files will be in the /home/pi/rpi-speed-camera folder. You can
then move them to another location if you wish.
 
Note A default images folder will be created to store jpg speed photos. There is an
image_path variable in the config.py file.  Use nano editor to change path and/or
other variables as desired.

Use the calibrate option and follow instructions below to calculate an accurate
value for IMAGE_VIEW_FT variable in the speed_settings.py
 

### Calibration Procedure   
speed-cam.py needs to be calibrated in order to display a correct speed.

To Calibrate cal_obj_px and cal_obj_mm variables perform the following

* Setup the RPI camera to point to the view to be monitored.
* Login to RPI using SSH or desktop terminal session and cd to rpi-speed-camera folder
* Use nano to edit config.py. 
* Edit variable calibrate=True
* If required Adjust the y_upper and y_lower variables to cover the road area.  Note
  image 0,0 is the top left hand corner and values are in pixels.  Do not
  exceed the CAMERA_HEIGHT value  
* In nano save changes ( ctl-x y to save )
* Start speed-cam.py eg python ./speed-cam.py
* Motion will automatically be detected and calibration images will be
  put in images folder with prefix calib-
* Monitor progress and calibration images. Press ctrl-c to Quit when done. 
* View calibration images with image viewer program or via webserver
  and use hash marks to record cal_obj_px for vehicle/object length
  Note each division is 10 pixels.  I use filezilla to transfer files to/from
  my PC and the RPI using sftp protocol and the RPI IP address.
* Record cal_obj_mm length of the speed object above in millimeters   
  You should use several photos to confirm and average results.
* Use nano to edit the config.py and change values for variables cal_obj_px and cal_obj_mm
  to new values.  Also change variable calibrate = False
* Exit nano then start speed_cam.py and monitor console messages.
  Perform a test using a vehicle at a known speed to verify calibration.
* Make sure y_upper and y_lower variables are correctly set for the area to
  monitor. This will restrict motion detection to area between these variable
  values.  Make sure top of vehicles/objects is included.
  
Please note that if road is too close and/or vehicles are moving too quickly then
the camera may not capture motion and/or record vehicle in speed photo.
    
### Configuration Settings  
Variable values are stored in the config.py file and are imported
when speed-cam.py is run.  Use the nano editor to modify these settings
per the comments.  Most settings should be OK and should not need to be
changed. Others may need to be fine tuned.  The openCV settings most
likely won't need to be changed unless you are familiar with them.

Note if log_data_to_file is set it will save tracking data to a .csv file
in the same folder as speed-cam.py  eg speed-cam.csv 

### Project Improvements
These are some of the improvements I have been thinking about.  Not sure
when I will actually implement as this is just a personal project challenge done for fun.

* Move project documentation into GitHub wiki for easier maintenance.
* Extract and store vehicle colour from image countour data
* Add ability to set camera time of day schedule. Eg no night or specific time of day
* Implement gdrive feature to sync data and/or images to users google or dropbox cloud storage 
* Adjust Calibration for vehicles travelling in opposite lanes due to different distances from camera
* Auto Calibrate by looking for smaller vehicles.  Small vehicles will usually be very similar in length so that
the distance from camera to road can be calculated and used for any moving objects at a similar distance.
* Modify CSV file to show filename separate from file path and simplify image naming to eliminate speed.
* Create a sql database and/or web interface to store image and tracking data
* Use image match per cam-track app to find similar vehicles in dataset and degree of accuracy. This
could be used to query for vehicles that are the same or very similar. 
* Using image match feature above, implement ability to track only specific objects (colour, shape, contour size, contour h/w ratio Etc.
* Implement gnuplot interface to allow plotting by time of day or other parameters
* Implement creation of profiles for vehicles, pedestrians, bicycles, Birds, Animals, Etc. Tracking

### Credits  
Some of this code is based on a YouTube tutorial by
Kyle Hounslow using C here https://www.youtube.com/watch?v=X6rPdRZzgjg

Thanks to Adrian Rosebrock jrosebr1 at http://www.pyimagesearch.com 
for the PiVideoStream Class code available on github at
https://github.com/jrosebr1/imutils/blob/master/imutils/video/pivideostream.py
  
Have Fun   
Claude Pageau    
YouTube Channel https://www.youtube.com/user/pageaucp   
GitHub Repo https://github.com/pageauc
