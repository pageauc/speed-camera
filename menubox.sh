#!/bin/bash

ver="3.40"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

progname="speed-cam.py"
speedconfig="config.py"
searchconfig="search_config.py"
filename_conf="work_config.txt"
filename_temp="work_temp.txt"

#------------------------------------------------------------------------------
function do_anykey ()
{
   echo ""
   echo "######################################"
   echo "#          Review Output             #"
   echo "######################################"
   read -p "  Press Enter to Return to Main Menu"
}

#------------------------------------------------------------------------------
function init_status ()
{
  if [ -z "$( pgrep -f speed-cam.py )" ]; then
    SPEED_1="START"
    SPEED_2="speed_cam.py in background"
  else
     speed_cam_pid=$( pgrep -f speed-cam.py )
     SPEED_1="STOP"
     SPEED_2="speed_cam.py - PID is $speed_cam_pid"
  fi

  if [ -z "$( pgrep -f webserver.py )" ]; then
     WEB_1="START"
     WEB_2="webserver.py in background"
  else
     webserver_pid=$( pgrep -f webserver.py )
     WEB_1="STOP"
     WEB_2="webserver.py - PID is $webserver_pid"
  fi
}

#------------------------------------------------------------------------------
function do_speed_cam ()
{
  if [ -z "$( pgrep -f speed-cam.py )" ]; then
     ./speed-cam.sh start
     if [ -z "$( pgrep -f speed-cam.py )" ]; then
         whiptail --msgbox "Failed to Start speed-cam.py   Please Investigate Problem " 20 70
     fi
  else
     speed_cam_pid=$( pgrep -f speed-cam.py )
     sudo ./speed-cam.sh stop
      if [ ! -z "$( pgrep -f speed-cam.py )" ]; then
          whiptail --msgbox "Failed to Stop speed-cam.py   Please Investigate Problem" 20 70
      fi
  fi
  do_main_menu
}

#------------------------------------------------------------------------------
function do_webserver ()
{
  if [ -z "$( pgrep -f webserver.py )" ]; then
     ./webserver.sh start
     if [ -z "$( pgrep -f webserver.py )" ]; then
        whiptail --msgbox "Failed to Start webserver.py   Please Investigate Problem." 20 70
     else
       myip=$(ifconfig | grep 'inet ' | grep -v 127.0.0 | cut -d " " -f 12 | cut -d ":" -f 2 )
       myport=$( grep "web_server_port" config.py | cut -d "=" -f 2 | cut -d "#" -f 1 | awk '{$1=$1};1' )
       whiptail --msgbox --title "Webserver Access" "Access speed-cam web server from another network computer web browser using url http://$myip:$myport" 15 50
     fi
  else
     webserver_pid=$( pgrep -f webserver.py )
     sudo ./webserver.sh stop
     if [ ! -z "$( pgrep -f webserver.py )" ]; then
        whiptail --msgbox "Failed to Stop webserver.py   Please Investigate Problem." 20 70
     fi
  fi
  do_main_menu
}

function do_makehtml ()
{
  SET_SEL=$( whiptail --title "makehtml Menu" --menu "Arrow/Enter Selects or Tab Key" 0 0 0 --ok-button Select --cancel-button Back \
  "a RUN" "makehtml.py nano $config_file for speed_cam & webserver" \
  "b VIEW" "How to View speed HTML Files" \
  "q QUIT" "Back to Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SET_SEL" in
      a\ *) clear
            ./makehtml.py
            do_anykey
            do_makehtml ;;
      b\ *) do_makehtml_about
            do_makehtml ;;
      q\ *) do_main_menu ;;
      *) whiptail --msgbox "Programmer error: un recognized option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SET_SEL" 20 60 1
  fi
}
#--------------------------------------------------------------------
function do_makehtml_about ()
{
  python "./makehtml.py"
  whiptail --title "About makehtml.py" --msgbox " \

  You must have several speed images in media/images
  and an associated speed-cam.csv file.

  To View html files
  1. Run makehtml.py from menu pick or console
     This will create html files in media/html folder
  2. Start webserver.sh and note ip and port
  3. From a web browser connect to speed-cam web server
     using RPI IP:PORT url
  4. View html files in media/html folder

" 0 0 0
}

#--------------------------------------------------------------------
function do_edit_save ()
{
  if (whiptail --title "Save $var=$newvalue" --yesno "$comment\n $var=$newvalue   was $value" 8 65 --yes-button "Save" --no-button "Cancel" ) then
    value=$newvalue

    rm $filename_conf  # Initialize new conf file
    while read configfile ;  do
      if echo "${configfile}" | grep --quiet "${var}" ; then
         echo "$var=$value         #$comment" >> $filename_conf
      else
         echo "$configfile" >> $filename_conf
      fi
    done < $config_file
    cp $filename_conf $config_file
  fi
  rm $filename_temp
  rm $filename_conf
  do_settings_menu
}

#------------------------------------------------------------------------------
function do_nano_main ()
{
  cp $config_file $filename_conf
  nano $filename_conf
  if (whiptail --title "Save Nano Edits" --yesno "Save nano changes to $config_file\n or cancel all changes" 8 65 --yes-button "Save" --no-button "Cancel" ) then
    cp $filename_conf $config_file
  fi
}

#------------------------------------------------------------------------------
function do_settings_menu ()
{
  config_file=$speedconfig
  SET_SEL=$( whiptail --title "Settings Menu" --menu "Arrow/Enter Selects or Tab Key" 0 0 0 --ok-button Select --cancel-button Back \
  "a EDIT" "nano $config_file for speed_cam & webserver" \
  "b VIEW" "config.py for speed_cam & webserver" \
  "q QUIT" "Back to Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SET_SEL" in
      a\ *) do_nano_main
            do_settings_menu ;;
      b\ *) more -d config.py
            do_anykey
            do_settings_menu ;;
      q\ *) do_main_menu ;;
      *) whiptail --msgbox "Programmer error: un recognized option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running menu item $SET_SEL" 20 60 1
  fi
}

#------------------------------------------------------------------------------
function do_search_selections ()
{
    comment="Select File Search Filter"
    var="*"
    value="This is a Value"

    searchvalue=$(whiptail --title "Image Directory Select (Enter Saves or Tab)" \
                           --inputbox "$comment\n $var=$value" 10 65 "$value" \
                           --ok-button "Save" 3>&1 1>&2 2>&3)
    exitstatus=$?
    if [ ! "$newvalue" = "" ] ; then   # Variable was changed
       if [ $exitstatus -eq 1 ] ; then  # Check if Save selected otherwise it was cancelled
          do_edit_save
       elif [ $exitstatus -eq 0 ] ; then
         echo "do_edit_variable - Cancel was pressed"
         if echo "${value}" | grep --quiet "${newvalue}" ; then
            do_settings_menu
         else
            do_edit_save
         fi
       fi
    fi
  do_speed_search_menu
}

#------------------------------------------------------------------------------
function do_search_about ()
{
   whiptail --title "About Search" --msgbox " \

1 From console copy one or more target images
  From: media/images
  To  : media/search
2 Edit Search Settings if required.
  You can use the menubox.sh EDIT Menu Pick
  This will edit search_config.py using nano editor
  ctrl-x y to exit nano then save changes
3 Run search-speed.py using Menu Pick or console command

Note: I will be working on a menu selection for copying
      target files.

" 0 0 0

}

#------------------------------------------------------------------------------
function do_speed_search_menu ()
{
  config_file=$searchconfig
  SET_SEL=$( whiptail --title "Search Images Menu" --menu "Arrow/Enter Selects or Tab Key" 0 0 0 --ok-button Select --cancel-button Back \
  "a SELECT" "Image Target Files for Search" \
  "b EDIT" "nano $config_file Settings" \
  "c SEARCH" "Speed Images for Matches" \
  "d ABOUT" "Images Search" \
  "q QUIT" "Back to Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SET_SEL" in
      a\ *) do_search_about
            do_speed_search_menu ;;
      b\ *) do_nano_main
            do_speed_search_menu ;;
      c\ *) clear
            ./search-speed.py
            do_anykey
            do_speed_search_menu ;;
      d\ *) do_search_about
            do_speed_search_menu ;;
      q\ *) do_main_menu ;;
      *) whiptail --msgbox "Programmer error: unrecognized option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running menu item $SET_SEL" 20 60 1
  fi
}

#------------------------------------------------------------------------------
function do_upgrade()
{
  if (whiptail --title "GitHub Upgrade speed-cam" --yesno "Upgrade speed-cam files from GitHub. Config files will not be changed" 8 65 --yes-button "upgrade" --no-button "Cancel" ) then
    curlcmd=('/usr/bin/curl -L https://raw.github.com/pageauc/rpi-speed-camera/master/speed-install.sh | bash')
    eval $curlcmd
    do_anykey
  fi
}

#------------------------------------------------------------------------------
function do_about()
{
  whiptail --title "About menubox.sh" --msgbox " \
       speed-cam - Object Motion Speed Tracking
        using Raspberry Pi, picamera and openCV
              written by Claude Pageau

 menubox.sh manages speed-cam operation, settings and utilities

 1. Start and Calibrate the camera distance settings using calib images.
 2. Edit config.py and set calibrate=False
 3. Start speed-cam.py and create speed images.  These can
    be viewed using the web server.
 4. Data will be in speed-cam.csv
 5. If you want to search for a image matches run the
    copy target image(s) to media/search then run
    search-speed.py
 6. You can also create html files to combine csv and image data
    run make
 file and images will be in images folder (links to html/images).
 Run makehtml.py and start the webserver.  View html files on a
 network pc web browser by accessing rpi IP address and port.
 eg 192.168.1.100:8080 (replace ip with your rpi ip)

           For more detailed instructions see
       https://github.com/pageauc/rpi-speed-camera

 Good Luck and Enjoy .... Claude
\
" 0 0 0
}

#------------------------------------------------------------------------------
function do_main_menu ()
{
  init_status
  SELECTION=$(whiptail --title "Main Menu" --menu "Arrow/Enter Selects or Tab Key" 0 0 0 --cancel-button Quit --ok-button Select \
  "a $SPEED_1" "$SPEED_2" \
  "b $WEB_1" "$WEB_2" \
  "c SETTINGS" "Change speed_cam and webserver settings" \
  "d HTML" "Make html pages from speed-cam.csv & jpgs" \
  "e VIEW" "View speed-cam.csv File" \
  "f SEARCH" "Images Search Menu (openCV Template Match)" \
  "g UPGRADE" "Program Files from GitHub.com" \
  "h ABOUT" "Information about this program" \
  "q QUIT" "Exit This Program"  3>&1 1>&2 2>&3)

  RET=$?
  if [ $RET -eq 1 ]; then
    exit 0
  elif [ $RET -eq 0 ]; then
    case "$SELECTION" in
      a\ *) do_speed_cam ;;
      b\ *) do_webserver ;;
      c\ *) do_settings_menu ;;
      d\ *) do_makehtml ;;
      e\ *) clear
            more ./speed-cam.csv
            do_anykey ;;
      f\ *) do_speed_search_menu ;;
      g\ *) clear
            do_upgrade ;;
      h\ *) do_about ;;
      q\ *) exit 0 ;;
         *) whiptail --msgbox "Programmer error: unrecognized option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running menu item $SELECTION" 20 60 1
  fi
}

#------------------------------------------------------------------------------
#                                Main Script
#------------------------------------------------------------------------------

while true; do
   do_main_menu
done
