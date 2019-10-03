#!/bin/bash
# speed-install.sh script written by Claude Pageau 1-Jul-2016

ver="9.99"
SPEED_DIR='speed-camera'  # Default folder install location
# Make sure ver below matches latest rclone ver on https://downloads.rclone.org/rclone-current-linux-arm.zip
rclone_cur_ver="rclone v1.49.4"

cd ~
is_upgrade=false
if [ -d "$SPEED_DIR" ] ; then
  STATUS="Upgrade"
  is_upgrade=true
else
  STATUS="New Install"
  mkdir -p $SPEED_DIR
  echo "$STATUS Created Folder $SPEED_DIR"
fi

# Remember where this script was launched from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $SPEED_DIR
INSTALL_PATH=$( pwd )
mkdir -p media
echo "-----------------------------------------------"
echo "$STATUS speed-camera speed-install.sh ver $ver"
echo "-----------------------------------------------"
echo "$STATUS Download GitHub Files"
if $is_upgrade ; then
    echo "Note: config.py will not be overwritten. Updated settings are in config.py.new"
    speedFiles=("menubox.sh" "speed-cam.py" \
"speed-cam.sh" "search-speed.py" "search_config.py" "Readme.md" "makehtml.py" "webserver.py" \
"webserver.sh" "sql_speed_gt.py" "alpr-speed.py")
else
    speedFiles=("config.py" "menubox.sh" "speed-cam.py" \
"speed-cam.sh" "search-speed.py" "search_config.py" "Readme.md" "makehtml.py" "webserver.py" \
"webserver.sh" "rclone-security-sync-recent.sh" "remote-run.sh" "watch-app.sh" "alpr-speed.py" \
"sql_speed_gt.py" )
fi

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

if [ ! -f remote-run.sh ] ; then
    wget -O watch-app.sh -q --show-progress https://raw.github.com/pageauc/speed-camera/master/watch-app.sh
fi

if [ ! -f remote-run.sh ] ; then
    wget -O remote-run.sh -q --show-progress https://raw.github.com/pageauc/speed-camera/master/remote-run.sh
fi

if [ ! -f rclone-security-sync-recent.sh ] ; then
    wget -O rclone-security-sync-recent.sh -q --show-progress https://raw.github.com/pageauc/speed-camera/master/rclone-security-sync-recent.sh
fi

# Install plugins if not already installed.  You must delete a plugin file to force reinstall.
echo "INFO  : $STATUS Check/Install pi-timolo/plugins    Wait ..."
PLUGINS_DIR='plugins'  # Default folder install location
# List of plugin Files to Check
pluginFiles=("__init__.py" "picam240.py" "webcam240.py" "picam480.py" "webcam480.py" \
"picam720.py" "webcam720.py" "picam1080.py" "secpicam480.py" "secwebcam480.py")

mkdir -p $PLUGINS_DIR
cd $PLUGINS_DIR
for fname in "${pluginFiles[@]}" ; do
  if [ -f $fname ]; then     # check if local file exists.
    echo "INFO  : $fname plugin Found.  Skip Download ..."
  else
    wget_output=$(wget -O $fname -q --show-progress https://raw.github.com/pageauc/speed-camera/master/plugins/$fname)
    if [ $? -ne 0 ]; then
        wget_output=$(wget -O $fname -q https://raw.github.com/pageauc/speed-camera/master/plugins/$fname)
        if [ $? -ne 0 ]; then
            echo "ERROR : $fname wget Download Failed. Possible Cause Internet Problem."
        else
            wget -O $fname "https://raw.github.com/pageauc/speed-camera/master/plugins/$fname"
        fi
    fi
  fi
done
cd ..

# Install rclone samples
echo "INFO  : $STATUS Check/Install speed-camera/rclone-samples    Wait ..."
RCLONE_DIR='rclone-samples'  # Default folder install location
# List of plugin Files to Check
rcloneFiles=("rclone-security-copy.sh" "rclone-security-sync.sh" "rclone-security-sync-recent.sh" "rclone-cleanup.sh")

mkdir -p $RCLONE_DIR
cd $RCLONE_DIR
for fname in "${rcloneFiles[@]}" ; do
    wget_output=$(wget -O $fname -q --show-progress https://raw.github.com/pageauc/speed-camera/master/rclone-samples/$fname)
    if [ $? -ne 0 ]; then
        wget_output=$(wget -O $fname -q https://raw.github.com/pageauc/speed-camera/master/rclone-samples/$fname)
        if [ $? -ne 0 ]; then
            echo "ERROR : $fname wget Download Failed. Possible Cause Internet Problem."
        else
            wget -O $fname "https://raw.github.com/pageauc/speed-camera/master/rclone-samples/$fname"
        fi
    fi
done
cd ..

rclone_install=true
if [ -f /usr/bin/rclone ]; then
    /usr/bin/rclone version
    rclone_ins_ver=$( /usr/bin/rclone version | grep rclone )
    if [ "$rclone_ins_ver" == "$rclone_cur_ver" ]; then
        rclone_install=false
    fi
fi

if "$rclone_install" = true ; then
    # Install rclone with latest version
    echo "INFO  : Install Latest Rclone from https://downloads.rclone.org/rclone-current-linux-arm.zip"
    wget -O rclone.zip -q --show-progress https://downloads.rclone.org/rclone-current-linux-arm.zip
    echo "INFO  : unzip rclone.zip to folder rclone-tmp"
    unzip -o -j -d rclone-tmp rclone.zip
    echo "INFO  : Install files and man pages"
    cd rclone-tmp
    sudo cp rclone /usr/bin/
    sudo chown root:root /usr/bin/rclone
    sudo chmod 755 /usr/bin/rclone
    sudo mkdir -p /usr/local/share/man/man1
    sudo cp rclone.1 /usr/local/share/man/man1/
    sudo mandb
    cd ..
    echo "INFO  : Deleting rclone.zip and Folder rclone-tmp"
    rm rclone.zip
    rm -r rclone-tmp
    echo "INFO  : /usr/bin/rclone Install Complete"
fi

echo "$STATUS Make required Files Executable"
chmod +x *.py
chmod +x *.sh
chmod -x config*

echo "$STATUS Installing speed-cam.py Dependencies"
sudo apt-get install -yq python-opencv
sudo apt-get install -yq dos2unix
sudo apt-get install -yq python-picamera
sudo apt-get install -yq python3-picamera
sudo apt-get install -yq python-imaging
sudo apt-get install -yq sqlite3

sudo apt-get install -yq gnuplot
if [ $? -ne 0 ]; then
   sudo apt-get install -yq Gnuplot
fi

sudo apt-get install -yq python-gnuplot
if [ $? -ne 0 ]; then
   sudo apt-get install -yq python-Gnuplot
fi

sudo apt-get install -yq libgl1-mesa-dri
sudo apt-get install -yq fonts-freefont-ttf # Required for Jessie Lite Only
sudo apt-get install -yq pandoc  # convert markdown to plain text for Readme.md
dos2unix -q *

cd $DIR
echo "
-----------------------------------------------
$STATUS Complete
-----------------------------------------------
1. Reboot RPI if there are significant Raspbian system updates
2. Raspberry pi optionally needs a monitor/TV attached to display openCV window
3. Run speed-cam.py in SSH Terminal (default) or optional GUI Desktop
   Review and modify the config.py settings as required using nano editor
4. To start speed-cam open SSH or a GUI desktop Terminal session
   and change to speed-camera folder and launch per commands below

   cd ~/speed-camera
   ./speed-cam.py

Calibrate speed camera per wiki instructions.  After Calibration is complete
set config.py variable calibrate = False

Run from Admin menu per

   ./menubox.sh

IMPORTANT: speed-cam.py ver 8.x Requires Updated config.py and plugins

    cd ~/speed-camera
    cp config.py config.py.bak
    cp config.py.new config.py

To replace plugins rename plugins folder per below

    cd ~/speed-camera
    mv plugins pluginsold

Then run menubox.sh UPGRADE menu pick.

-----------------------------------------------
For Detailed Instructions See https://github.com/pageauc/speed-camera/wiki
$SPEED_DIR version $ver
Good Luck Claude ...
Bye"
