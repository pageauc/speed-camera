#!/bin/bash

ver="3.00"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

pyconfigfile="./config.py"
filename_conf="./speed_cam.conf"
filename_temp="./speed_cam.conf.temp"

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
  if [ -z "$( pgrep -f speed_cam.py )" ]; then
    SPEED_1="Start speed_cam"
    SPEED_2="Start speed_cam.py in background"
  else
     SPEED_pid=$( pgrep -f speed-cam.py )
     SPEED_1="Stop speed_cam"
     SPEED_2="Stop speed_cam.py - PID is $SPEED_pid"     
  fi

  if [ -z "$( pgrep -f webserver.py )" ]; then
     WEB_1="Start webserver"
     WEB_2="Start webserver.py in background"    
  else
     webserver_pid=$( pgrep -f webserver.py )    
     WEB_1="Stop webserver"
     WEB_2="Stop webserver.py - PID is $webserver_pid"    
  fi
}

#------------------------------------------------------------------------------
function do_speed_cam ()
{
  if [ -z "$( pgrep -f speed-cam.py )" ]; then 
     ./speed-cam.py >/dev/null 2>&1 & 
     if [ -z "$( pgrep -f speed-cam.py )" ]; then 
         whiptail --msgbox "Failed to Start speed-cam.py   Please Investigate Problem " 20 70     
     fi
  else
     speed-cam_pid=$( pgrep -f speed-cam.py )  
     sudo kill $pi_timolo_pid
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
     ./webserver.py >/dev/null 2>&1 & 
     if [ -z "$( pgrep -f webserver.py )" ]; then 
        whiptail --msgbox "Failed to Start webserver.py   Please Investigate Problem." 20 70     
     fi 
  else  
     webserver_pid=$( pgrep -f webserver.py )   
     sudo kill $webserver_pid
     if [ ! -z "$( pgrep -f webserver.py )" ]; then 
        whiptail --msgbox "Failed to Stop webserver.py   Please Investigate Problem." 20 70     
     fi      
  fi
  do_main_menu
}

#--------------------------------------------------------------------
function do_makehtml ()
{
  python "./makehtml.py" 
  echo "---------------------------------------------"
  echo "           N O T I C E"
  echo "---------------------------------------------"  
  echo "Start webserver and view files in web browser"      
  do_anykey 
  do_main_menu
}

#--------------------------------------------------------------------
function do_edit_variable ()
{
  choice=$(cat $filename_temp | grep $SELECTION)

  var=$(echo $choice | cut -d= -f1)
  value=$(echo $choice | cut -d= -f2)
  comment=$( cat $filename_conf | grep $var | cut -d# -f2 )

  echo "${value}" | grep --quiet "True"
  # Exit status 0 means anotherstring was found
  # Exit status 1 means anotherstring was not found
  if [ $? = 0 ] ; then
     newvalue=" False"
     do_edit_save       
  else
     echo "${value}" | grep --quiet "False"
     if [ $? = 0 ] ; then
        newvalue=" True"
        do_edit_save            
     elif  [ $? = 1 ] ; then       
        newvalue=$(whiptail --title "Edit $var (Enter Saves or Tab)" \
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
     fi
  fi
  do_settings_menu 
}

#--------------------------------------------------------------------
function do_edit_menu ()
{
  clear
  echo "Copy $filename_conf from $pyconfigfile  Please Wait ...."
  cp $pyconfigfile $filename_conf
  echo "Initialize $filename_temp  Please Wait ...."  
  cat $filename_conf | grep = | cut -f1 -d# | tr -s [:space:] >$filename_temp
  echo "Initializing Settings Menu Please Wait ...."    
  menu_options=()
  while read -r number text; do
    menu_options+=( ${number//\"} "${text//\"}" )
  done < $filename_temp
  
  SELECTION=$( whiptail --title "Speed Cam Settings Menu" \
                       --menu "Arrow/Enter Selects or Tab" 0 0 0 "${menu_options[@]}" --ok-button "Edit" 3>&1 1>&2 2>&3 )  
  RET=$?  
  if [ $RET -eq 1 ] ; then
    do_settings_menu
  elif [ $RET -eq 0 ]; then
    cp $pyconfigfile $filename_conf
    cat $filename_conf | grep = | cut -f1 -d# | tr -s [:space:] >$filename_temp  
    do_edit_variable
  fi
}

#------------------------------------------------------------------------------
function do_nano_main ()
{
  cp $pyconfigfile $filename_conf
  nano $filename_conf
  if (whiptail --title "Save Nano Edits" --yesno "Save nano changes to $filename_conf\n or cancel all changes" 8 65 --yes-button "Save" --no-button "Cancel" ) then
    cp $filename_conf $pyconfigfile  
  fi 
}

#------------------------------------------------------------------------------
function do_settings_menu ()
{
  SET_SEL=$( whiptail --title "Settings Menu" --menu "Arrow/Enter Selects or Tab Key" 0 0 0 --ok-button Select --cancel-button Back \
  "a " "Menu Edit config.py for speed_cam & webserver" \
  "b " "Edit nano config.py for speed_cam & webserver" \
  "c " "View config.py for speed_cam & webserver" \
  "d " "Back to Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SET_SEL" in
      a\ *) do_edit_menu ;;
      b\ *) do_nano_main
            do_settings_menu ;;
      c\ *) more -d config.py
            do_anykey
            do_settings_menu ;;
      d\ *) do_main_menu ;;
      *) whiptail --msgbox "Programmer error: unrecognized option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SELECTION" 20 60 1
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
  whiptail --title "About" --msgbox " \
   speed_cam - OpenCV Motion Tracking Object Speed
          written by Claude Pageau

   Manage speed_cam operation, config and utilities

   Start Webserver to view speed_cam html files.
   Note you must run makehtml.py to create or update
   the html files.
\
" 35 70 35
}

#------------------------------------------------------------------------------
function do_main_menu ()
{
  init_status
  SELECTION=$(whiptail --title "Main Menu" --menu "Arrow/Enter Selects or Tab Key" 20 70 10 --cancel-button Quit --ok-button Select \
  "a $SPEED_1" "$SPEED_2" \
  "b $WEB_1" "$WEB_2" \
  "c Web Pages" "Create Web Pages from CSV Log File and Images" \
  "d Settings" "Change speed_cam and webserver settings" \
  "e Upgrade" "Upgrade program files from GitHub.com"  "f About" "Information about this program" \
  "q Quit" "Exit This Program"  3>&1 1>&2 2>&3)

  RET=$?
  if [ $RET -eq 1 ]; then
    exit 0
  elif [ $RET -eq 0 ]; then
    case "$SELECTION" in
      a\ *) do_speed_cam ;;
      b\ *) do_webserver ;;
      c\ *) do_makehtml ;;
      d\ *) do_settings_menu ;;
      e\ *) do_upgrade ;;
      f\ *) do_about ;;
      q\ *) clear
            exit 0 ;;
         *) whiptail --msgbox "Programmer error: unrecognized option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SELECTION" 20 60 1
  fi
}

#------------------------------------------------------------------------------
#                                Main Script
#------------------------------------------------------------------------------

while true; do
   do_main_menu
done
