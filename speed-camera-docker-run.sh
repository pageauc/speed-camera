#!/bin/bash

if [ ! -f /root/speed-camera/config/config.py ]; then
    mv /root/speed-camera/config.py /root/speed-camera/config/config.py
    ln -fs /root/speed-camera/config/config.py /root/speed-camera/config.py 
fi

if [ ! -f /root/speed-camera/media/webserver.txt ]; then
    wget -O /root/speed-camera/media/webserver.txt -q --show-progress https://raw.github.com/pageauc/speed-camera/master/webserver.txt
fi

cd /root/speed-camera/

echo "Starting Web Server..."
python /root/speed-camera/webserver.py start >> /root/speed-camera/webserver.log 2>&1 &

echo "Starting Speed Camera..."
python3 /root/speed-camera/speed-cam.py start 