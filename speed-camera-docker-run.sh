#!/bin/bash

# Check if config.py is symlinked to docker volue
if [ ! -L /root/speed-camera/config.py ]; then 
    echo "config.py not symlinked ..."
    if [ ! -f /root/speed-camera/config/config.py ]; then
        echo "config.py does not exist in the docker volume, let's move it there and create a symlink"
        mv /root/speed-camera/config.py /root/speed-camera/config/config.py
        ln -fs /root/speed-camera/config/config.py /root/speed-camera/config.py 
    else
        echo "config.py already exists on docker volume, so let's create a symlink"
        ln -fs /root/speed-camera/config/config.py /root/speed-camera/config.py 
    fi
fi

if [ ! -f /root/speed-camera/media/webserver.txt ]; then
    wget -O /root/speed-camera/media/webserver.txt -q --show-progress https://raw.github.com/mlapaglia/speed-camera/master/webserver.txt
fi

cd /root/speed-camera/

echo "Starting Web Server..."
python /root/speed-camera/webserver.py start >> /root/speed-camera/webserver.log 2>&1 &

echo "Starting Speed Camera..."
python3 /root/speed-camera/speed-cam.py start 