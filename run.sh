#!/bin/bash
# run.sh is a systemctl script to control webserver.py and writer.py
# written by Claude Pageau  https://github.com/pageauc/speed-camera
version="2.0"
programs="speed-cam.py webserver.py"
params="start, stop, restart, status, install, uninstall"

echo "$0 ver $version  written by Claude Pageau"
echo "Control $programs"
echo ""

if [ "$1" = "start" ]; then
    echo "sudo supervisorctl start speed-cam speed-web"
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl start speed-cam speed-web
    echo "Wait 10 seconds for supervisor services to start $programs"
    sleep 10
    sudo supervisorctl status all
elif [ "$1" = "stop" ]; then
    echo "STOP: sudo supervisorctl stop $programs"
    sudo supervisorctl stop speed-cam speed-web
    sudo supervisorctl status all
    exit 0
elif [ "$1" = "status" ]; then
    echo "STATUS: sudo supervisorctl status all"
    echo "supervisorctl status for $programs"
    sudo supervisorctl status all
    exit 0
elif [ "$1" = "install" ]; then
    # Run this option to initialize supervisor.service
    echo "INSTALL: sudo ln -s /home/pi/speed-camera/supervisor/* /etc/supervisor/conf.d/"
    sudo ln -s /home/pi/speed-camera/supervisor/* /etc/supervisor/conf.d/
    if [ $? == 0 ]; then
        echo "INFO  - Done Install supervisorctl for $programs"
    else
        echo "WARN  - suprvisorctl for $programs Already Installed."
        exit 0
    fi
elif [ "$1" = "uninstall" ]; then
    echo "Uninstall supervisorctl for $programs"
    sudo supervisorctl stop speed-cam speed-web
    sudo rm /etc/supervisor/conf.d/speed-cam.conf /etc/supervisor/conf.d/speed-web.conf
    exit 0
elif [ "$1" = "upgrade" ]; then
    echo "Upgrade program files from github repo"
    echo " curl -L https://raw.github.com/pageauc/speed-camera/master/speed-install.sh | bash "
    curl -L https://raw.github.com/pageauc/speed-camera/master/speed-install.sh | bash
    echo "Upgrade Finished"
    exit 0
else
   echo "Usage: ./run.sh [Option]"
   echo ""
   echo "Options:"
   echo "  start        Start supervisor service"
   echo "  stop         Stop supervisor service"
   echo "  status       Status of supervisor service"
   echo "  install      Install symbolic links for supervisor service"
   echo "  uninstall    Uninstall symbolic links for supervisor service"
   echo "  upgrade      Upgrade files from Github Repo"
   echo "  help         Display Usage message and Status"
   echo ""
   echo "Example:  ./run.sh status"
   exit 0
fi

echo ""
myip1=$(hostname -I | cut -d " " -f 1)
myip2=$(hostname -I | cut -d " " -f 2)
echo ""
echo " To Access RUNNING speed-camera websever interface"
echo "    Type or copy/paste url link below"
echo "    into web browser url window. Normally near top of browser app."
echo ""
echo "    Example: http://$myip1:8080"
echo ""
echo "Bye"
