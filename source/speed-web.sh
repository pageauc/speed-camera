#!/bin/bash
# This script will run the speed-web.py as a background task
# You will then be able close the terminal session.
# use the edit option and change autostart=true

# initialize script variables
login_id=$( whoami )
speed_dir=$( pwd )
service_name="speed-web"
conf_file_dir="/home/$login_id/speed-camera/supervisor"
conf_file_name="speed-web.conf"

# change supervisor conf file for current logged in user
sed -i s,^user=.*,login=$login_id, $conf_file_dir/$conf_file_name
sed -i s,^directory=.*,directory=$speed_dir, $conf_file_dir/$conf_file_name

# speed-web.sh ver 13.15 written by Claude Pageau
echo "-----------------------------------------------"
echo "$0 supervisorctl $1"

if [ "$1" = "start" ]; then
    sudo supervisorctl start $service_name
    if [ $? -ne 0 ]; then
       echo "ERROR: Try running install Option."
	   echo "  Also run ./speed-web.py to check if web port is in use."
	   echo "  If so try changing WEB_SERVER_PORT in config.py"
    fi
    exit 0

elif [ "$1" = "stop" ]; then
    sudo supervisorctl stop $service_name
    if [ $? -ne 0 ]; then
       echo "ERROR: Run install Option."
    fi
    exit 0

elif [ "$1" = "restart" ]; then
    sudo supervisorctl restart $service_name

elif [ "$1" = "status" ]; then
    sudo supervisorctl status all
    exit 0

elif [ "$1" = "edit" ]; then
    sudo nano $conf_file_dir/$conf_file_name
    sudo supervisorctl reread
    sudo supervisorctl update
    echo "Wait ..."
    sleep 4
    sudo supervisorctl status $service_name
    exit 1

elif [ "$1" = "log" ]; then
    tail -n 200 /var/log/$service_name.log
    echo "----------------------------------------"
    echo "tail -n 200 /var/log/$service_name.log"
    exit 1

elif [ "$1" = "install" ]; then
    # Run this option to initialize supervisor.service
    echo "install: ln -s $conf_file_dir/$conf_file_name /etc/supervisor/conf.d/$conf_file_name"
    sudo ln -s $conf_file_dir/$conf_file_name /etc/supervisor/conf.d/$conf_file_name
    if [ $? -ne 0 ]; then
       echo "$service_name Already Installed"
       exit 1
    fi
    ls -al /etc/supervisor/conf.d
    sudo supervisorctl reread
    sleep 4
    sudo supervisorctl update

elif [ "$1" = "uninstall" ]; then
    sudo supervisorctl stop $service_name
    if [ $? -ne 0 ]; then
       echo "$service_name already STOPPED"
    fi
    sleep 4
    sudo rm /etc/supervisor/conf.d/$conf_file_name
    if [ $? -ne 0 ]; then
       echo "$service_name Not Installed"
       echo "Run install option."
       exit 1
    fi
    sudo supervisorctl reread
    sleep 4
    sudo supervisorctl update

elif [ "$1" = "upgrade" ]; then
    curl -L https://raw.github.com/pageauc/speed-camera/master/source/speed-install.sh | bash
    exit 0
else
   echo "
Usage: ./$(basename "$0") [Option]

  Options:
  start        Start supervisor service
  stop         Stop supervisor service
  restart      restart supervisor service
  status       Status of supervisor service
  edit         nano edit $conf_file_dir
  log          tail -n 200 /var/log/$service_name.log
  install      Install symbolic link for speed-web supervisor service
  uninstall    Uninstall symbolic link for speed-web supervisor service
  upgrade      Upgrade speed-camera files from GitHub
  help         Display Usage message and Status

  Example:  ./$(basename "$0") status
"
fi
echo "Wait ...
"
sudo supervisorctl status all
echo "Done
"
