#!/bin/bash
# Convenient speed-install.sh script written by Claude Pageau 1-Jul-2016
ver="6.40"
SPEED_DIR='speed-camera'  # Default folder install location

cd ~
if [ -d "$SPEED_DIR" ] ; then
  STATUS="Upgrade"
  echo "Upgrade"
else
  echo "speed camera Install"
  STATUS="New Install"
  mkdir -p $SPEED_DIR
  echo "$SPEED_DIR Folder Created"
fi

# Remember where this script was launched from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $SPEED_DIR
INSTALL_PATH=$( pwd )
mkdir -p media

echo "-----------------------------------------------"
echo "  speed-camera speed-install.sh script ver $ver"
echo "  $STATUS speed-cam.py Object speed tracking"
echo "-----------------------------------------------"
echo "1 - Downloading github repo files"
echo ""

speedFiles=("menubox.sh" "speed-install.sh" "speed-cam.py" \
"speed-cam.sh" "search-speed.py" "search_config.py" "Readme.md" "makehtml.py" \
"webserver.py" "webserver.sh" "config.py.240" "config.py.480" "config.py.720" "config.py.1080")

for fname in "${speedFiles[@]}" ; do
    wget_output=$(wget -O $fname -q --show-progress https://raw.github.com/pageauc/speed-camera/master/$fname)
    if [ $? -ne 0 ]; then
        if [ $? -ne 0 ]; then
            echo "ERROR - $fname wget Download Failed. Possible Cause Internet Problem."
        else
            wget -O $fname https://raw.github.com/pageauc/speed-camera/master/$fname
        fi
    fi
done

wget -O media/webserver.txt -q --show-progress https://raw.github.com/pageauc/speed-camera/master/webserver.txt
wget -O config.py.new -q --show-progress https://raw.github.com/pageauc/speed-camera/master/config.py

if [ -e config.py ]; then
  echo "Backup config.py to config.py.prev"
  cp config.py config.py.prev
else
  wget -O config.py -q --show-progress https://raw.github.com/pageauc/speed-camera/master/config.py
fi


echo "Done Download"
echo "------------------------------------------------"
echo "2 - Make required Files Executable"
echo ""
chmod +x *.py
chmod +x *.sh
chmod -x config*
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
echo "5 - Installing speed-cam.py Dependencies"
echo ""
sudo apt-get install -y python-opencv dos2unix python-picamera python-imaging libgl1-mesa-dri
sudo apt-get install -y fonts-freefont-ttf # Required for Jessie Lite Only
echo "Done Dependencies"
dos2unix *sh
dos2unix *py
cd $DIR
# Check if speed-install.sh was launched from speed-cam folder
if [ "$DIR" != "$INSTALL_PATH" ]; then
  if [ -e 'speed-install.sh' ]; then
    echo "$STATUS Cleanup speed-install.sh"
    rm speed-install.sh
  fi
fi
echo "
-----------------------------------------------
6 - $STATUS Complete
-----------------------------------------------

1. Reboot RPI if there are significant Raspbian system updates
2. Raspberry pi optionally needs a monitor/TV attached to display openCV window
3. Run speed-cam.py in SSH Terminal (default) or optional GUI Desktop
   Review and modify the config.py settings as required using nano editor
4. To start speed-cam open SSH or a GUI desktop Terminal session
   and change to speed-camera folder and launch per commands below

   cd ~/speed-camera
   ./speed-cam.py

or Run from Admin menu

   ./menubox.sh

-----------------------------------------------
For Detailed Instructions See https://github.com/pageauc/speed-camera/wiki

$SPEED_DIR Good Luck Claude ...
Bye"










