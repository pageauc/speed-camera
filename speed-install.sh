#!/bin/bash
# Convenient speed-install.sh script written by Claude Pageau 1-Jul-2016
ver="1.1"
SPEED_DIR='rpi-speed-camera'  # Default folder install location

cd ~
if [ -d "$SPEED_DIR" ] ; then
  STATUS="Upgrade"
  echo "Upgrade rpi-speed-camera files"
else  
  echo "New rpi-speed-camera Install"
  STATUS="New Install"
  mkdir -p $SPEED_DIR
  echo "$SPEED_DIR Folder Created"
fi 

cd $SPEED_DIR
INSTALL_PATH=$( pwd )
  
# Remember where this script was launched from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "-----------------------------------------------"
echo "  rpi-speed-camera speed-install.sh script ver $ver"
echo "  $STATUS speed-cam.py Object speed tracking"
echo "-----------------------------------------------"
echo ""
echo "1 - Downloading github repo files"
wget -O speed-install.sh -q --show-progress https://raw.github.com/pageauc/rpi-speed-camera/master/speed-install.sh
if [ $? -ne 0 ] ;  then
  wget -O speed-install.sh https://raw.github.com/pageauc/rpi-speed-camera/master/speed-install.sh
  wget -O speed-cam.py https://raw.github.com/pageauc/rpi-speed-camera/master/speed-cam.py
  wget -O speed-cam.sh https://raw.github.com/pageauc/rpi-speed-camera/master/speed-cam.sh
  wget -O Readme.md https://raw.github.com/pageauc/rpi-speed-camera/master/Readme.md
  wget -q https://raw.github.com/pageauc/rpi-speed-camera/master/config.py
else
  wget -O speed-cam.py -q --show-progress https://raw.github.com/pageauc/rpi-speed-camera/master/speed-cam.py
  wget -O speed-cam.sh -q --show-progress https://raw.github.com/pageauc/rpi-speed-camera/master/speed-cam.sh  
  wget -O Readme.md -q --show-progress https://raw.github.com/pageauc/rpi-speed-camera/master/Readme.md
  wget -q --show-progress https://raw.github.com/pageauc/rpi-speed-camera/master/config.py
fi
echo "Done Download"
echo "------------------------------------------------"
echo ""
echo "2 - Make required Files Executable"
chmod +x speed-cam.py
chmod +x speed-cam.sh
chmod +x speed-install.sh
echo "Done Permissions"
echo "------------------------------------------------"
echo "3 - Performing Raspbian System Update"
echo "    This Will Take Some Time ...."
echo ""
sudo apt-get -y update
echo "Done update"
echo "------------------------------------------------"
echo "4 - Performing Raspbian System Upgrade"
echo "    This Will Take Some Time ...."
echo ""
sudo apt-get -y upgrade
echo "Done upgrade"
echo "------------------------------------------------"
echo ""
echo "5 - Installing speed-cam.py Dependencies"
sudo apt-get install -y python-opencv python-picamera python-imaging python-pyexiv2 libgl1-mesa-dri
sudo apt-get install -y fonts-freefont-ttf # Required for Jessie Lite Only
echo "Done Dependencies"
cd $DIR
# Check if speed-install.sh was launched from speed-cam folder
if [ "$DIR" != "$INSTALL_PATH" ]; then
  if [ -e 'speed-install.sh' ]; then
    echo "$STATUS Cleanup speed-install.sh"
    rm speed-install.sh
  fi
fi
echo "-----------------------------------------------"
echo "6 - $STATUS Complete"
echo "-----------------------------------------------"
echo ""
echo "1. Reboot RPI if there are significant Raspbian system updates"
echo "2. Raspberry pi optionally needs a monitor/TV attached to display openCV window"
echo "3. Run speed-cam.py in SSH Terminal (default) or optional GUI Desktop"
echo "   Review and modify the config.py settings as required using nano editor"
echo "4. To start speed-cam open SSH or a GUI desktop Terminal session" 
echo "   and change to rpi-speed-camera folder and launch per commands below"
echo ""
echo "   cd ~/rpi-speed-camera"
echo "   ./speed-cam.py"
echo ""
echo "-----------------------------------------------"
echo "See Readme.md for Further Details"
echo $SPEED_DIR "Good Luck Claude ..."
echo "Bye"










