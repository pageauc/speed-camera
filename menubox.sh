#!/bin/bash

ver="7.5"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

progname="speed-cam.py"
speedconfig="config.py"
searchconfig="search_config.py"
imagedir="media/images"
searchdir="media/search"

# Setup search target variables
imagedir="$DIR/$imagedir"   # Setup full path to images directory
searchdir="$DIR/$searchdir"  # Setup full path to search directory
searchconfig="$DIR/$searchconfig"

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
     myip=$(ifconfig | grep 'inet ' | grep -v 127.0.0 | cut -d " " -f 12 | cut -d ":" -f 2 )
     myport=$( grep "web_server_port" config.py | cut -d "=" -f 2 | cut -d "#" -f 1 | awk '{$1=$1};1' )
     WEB_1="STOP"
     WEB_2="webserver.py - PID is $webserver_pid http://$myip:$myport"
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

#------------------------------------------------------------------------------
function do_makehtml_menu ()
{
  SET_SEL=$( whiptail --title "makehtml Menu" \
                      --menu "Arrow/Enter Selects or Tab Key" 0 0 0 \
                      --ok-button Select \
                      --cancel-button Back \
  "a RUN" "makehtml.py Create speed cam html files" \
  "b CLEAN" "Delete all html Files then RUN makehtml.py" \
  "c ABOUT" "How to View speed-cam html Files" \
  "q BACK" "To Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SET_SEL" in
      a\ *) clear
            ./makehtml.py
            do_anykey
            do_makehtml_about
            do_makehtml_menu ;;
      b\ *) clear
            echo "Deleting all html files in media/html"
            rm media/html/*html
            ./makehtml.py
            do_anykey
            do_makehtml_about
            do_makehtml_menu ;;
      c\ *) do_makehtml_about
            do_makehtml_menu ;;
      q\ *) clear
            do_main_menu ;;
      *) whiptail --msgbox "Programmer error: un recognized option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SET_SEL" 20 60 1
  fi
}

#--------------------------------------------------------------------
function do_makehtml_about ()
{
  whiptail --title "About makehtml.py" --msgbox " \

  makehtml.py will combine speed-cam.csv data with the
  associated images into a formatted html page.  You
  can view pages from the webserver using a web browser
  and can easily navigate up and down the pages.

  You must have several speed images in media/images
  and an associated speed-cam.csv file.

  To View html files
  1. Run makehtml.py from menu pick or console
     This will create html files in media/html folder
  2. Start webserver.sh and note ip and port
  3. From a web browser connect to speed-cam web server
     using RPI IP:PORT url
  4. View html files in media/html folder
\
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
}

#------------------------------------------------------------------------------
function do_nano_main ()
{
  cp $config_file $filename_conf
  nano $filename_conf
  if (whiptail --title "Save Nano Edits" --yesno "Save nano changes to $config_file\n or cancel all changes" 0 0 \
                                         --yes-button "Save" \
                                         --no-button "Cancel" ); then
    cp $filename_conf $config_file
  fi
}

#------------------------------------------------------------------------------
function do_settings_menu ()
{
  config_file=$speedconfig
  SET_SEL=$( whiptail --title "Settings Menu" \
                      --menu "Arrow/Enter Selects or Tab Key" 0 0 0 \
                      --ok-button Select \
                      --cancel-button Back \
  "a EDIT" "nano $config_file for speed_cam & webserver" \
  "b VIEW" "config.py for speed_cam & webserver" \
  "q BACK" "To Main Menu" 3>&1 1>&2 2>&3 )

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
      *) whiptail --msgbox "Programmer error: un recognized option" 0 0 0 ;;
    esac || whiptail --msgbox "There was an error running menu item $SET_SEL" 0 0 0
  fi
}

#------------------------------------------------------------------------------
function Filebrowser()
{
# first parameter is Menu Title
# second parameter is optional dir path to starting folder
# otherwise current folder is selected

    if [ -z $2 ] ; then
        dir_list=$(ls -lhp  | awk -F ' ' ' { print $9 " " $5 } ')
    else
        cd "$2"
        dir_list=$(ls -lhp  | awk -F ' ' ' { print $9 " " $5 } ')
    fi

    curdir=$(pwd)
    if [ "$curdir" == "/" ] ; then  # Check if you are at root folder
        selection=$(whiptail --title "$1" \
                              --menu "PgUp/PgDn/Arrow Enter Selects File/Folder\nor Tab Key\n$curdir" 0 0 0 \
                              --cancel-button Cancel \
                              --ok-button Select $dir_list 3>&1 1>&2 2>&3)
    else   # Not Root Dir so show ../ BACK Selection in Menu
        selection=$(whiptail --title "$1" \
                              --menu "PgUp/PgDn/Arrow Enter Selects File/Folder\nor Tab Key\n$curdir" 0 0 0 \
                              --cancel-button Cancel \
                              --ok-button Select ../ BACK $dir_list 3>&1 1>&2 2>&3)
    fi

    RET=$?
    if [ $RET -eq 1 ]; then  # Check if User Selected Cancel
       return 1
    elif [ $RET -eq 0 ]; then
       if [[ -d "$selection" ]]; then  # Check if Directory Selected
          Filebrowser "$1" "$selection"
       elif [[ -f "$selection" ]]; then  # Check if File Selected
          if [[ $selection == *$filext ]]; then   # Check if selected File has .jpg extension
            if (whiptail --title "Confirm Selection" --yesno "DirPath : $curdir\nFileName: $selection" 0 0 \
                         --yes-button "Confirm" \
                         --no-button "Retry"); then
                filename="$selection"
                filepath="$curdir"    # Return full filepath  and filename as selection variables
            else
                Filebrowser "$1" "$curdir"
            fi
          else   # Not jpg so Inform User and restart
             whiptail --title "ERROR: File Must have .jpg Extension" \
                      --msgbox "$selection\nYou Must Select a jpg Image File" 0 0
             Filebrowser "$1" "$curdir"
          fi
       else
          # Could not detect a file or folder so Try Again
          whiptail --title "ERROR: Selection Error" \
                   --msgbox "Error Changing to Path $selection" 0 0
          Filebrowser "$1" "$curdir"
       fi
    fi
}

#------------------------------------------------------------------------------
function do_plugins_edit ()
{
    menutitle="Select File to Edit"
    startdir="plugins"
    filext='py'

    Filebrowser "$menutitle" "$startdir"

    exitstatus=$?
    if [ $exitstatus -eq 0 ]; then
        if [ "$selection" == "" ]; then
            echo "User Pressed Esc with No File Selection"
        else
            nano $filepath/$filename
        fi
    else
        echo "User Pressed Cancel. with No File Selected"
    fi
    cd $DIR
}
#------------------------------------------------------------------------------
function do_plugins_menu ()
{
  SET_SEL=$( whiptail --title "Edit Plugins Menu" --menu "Arrow/Enter Selects or Tab Key" 0 0 0 --ok-button Select --cancel-button Back \
  "a CONFIG" "Edit config.py NOTE:plugin vars override" \
  "b PLUGIN" "Select and Edit plugin File to Edit" \
  "q BACK" "To Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SET_SEL" in
      a\ *) rm -f $filename_temp
            rm -f $filename_conf
            do_nano_main
            do_plugins_menu ;;
      b\ *) do_plugins_edit
            do_plugins_menu ;;
      q\ *) clear
            do_main_menu ;;
      *) whiptail --msgbox "Programmer error: unrecognised option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SELECTION" 20 60 1
  fi
}

#------------------------------------------------------------------------------
function do_nano_edit ()
{
    menutitle="Select File to Edit"
    startdir="/home/pi/speed-camera"
    filext='sh'

    Filebrowser "$menutitle" "$startdir"

    exitstatus=$?
    if [ $exitstatus -eq 0 ]; then
        if [ "$selection" == "" ]; then
            echo "User Pressed Esc with No File Selection"
        else
            nano $filepath/$filename
        fi
    else
        echo "User Pressed Cancel. with No File Selected"
    fi
}

#------------------------------------------------------------------------------
function do_sync_run ()
{
    menutitle="Select rclone sync Script to Run"
    startdir="/home/pi/speed-camera"
    filext='sh'

    Filebrowser "$menutitle" "$startdir"

    exitstatus=$?
    if [ $exitstatus -eq 0 ]; then
        if [ "$selection" == "" ]; then
            echo "User Pressed Esc with No File Selection"
        else
            if [ ! -x "$filepath/$filename" ]; then
                chmod +x $filepath/$filename
            fi
            $filepath/$filename
            do_anykey
            clear
        fi
    else
        echo "User Pressed Cancel. with No File Selected"
    fi
}

#------------------------------------------------------------------------------
function do_sync_menu ()
{
  SET_SEL=$( whiptail --title "Rclone Menu" --menu "Arrow/Enter Selects or Tab Key" 0 0 0 --ok-button Select --cancel-button Back \
  "a EDIT" "Select rclone- sh File to Edit with nano" \
  "b RUN" "Run Selected Rclone sh Script" \
  "c CONFIG" "Run rclone config See GitHub Wiki for Details" \
  "d LIST" "Names of Configured Remote Storage Services" \
  "e HELP" "Rclone Man Pages" \
  "f ABOUT" "Rclone Remote Storage Sync" \
  "q BACK" "To Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SET_SEL" in
      a\ *) do_nano_edit
            do_sync_menu ;;
      b\ *) do_sync_run
            do_sync_menu ;;
      c\ *) clear
            rclone config
            do_anykey
            clear
            do_sync_menu ;;
      d\ *) clear
            echo "Avail Remote Names"
            echo ""
            /usr/bin/rclone -v listremotes
            do_anykey
            clear
            do_sync_menu ;;
      e\ *) man rclone
            do_sync_menu ;;
      f\ *) do_sync_about
            do_sync_menu ;;
      q\ *) clear
            do_main_menu ;;
      *) whiptail --msgbox "Programmer error: unrecognised option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SELECTION" 20 60 1
  fi
}

function do_sync_about
{
  whiptail --title "About Sync" --msgbox "\
Rclone is the default speed-camera remote storage sync utility.
You Must Configure a Remote Storage Service before using.

For More Details See Wiki per link below
https://github.com/pageauc/speed-camera/wiki

Select RCLONE, EDIT menu to change rclone- bash script variables.
ctrl-x y to save changes and exit nano otherwise respond n.

Select CONFIG menu to run rclone config menu.
You will need details about your remote Storage Service.

Select RCLONE, RUN menu to Test rclone- bash script changes.
or manually Run an rclone- bash script from a console session.

    ./rclone-script-name.sh

If you want to Run Rclone install separately for another project.
See my GitHub Project https://github.com/pageauc/rclone4pi

                           -----
\
" 0 0 0

}

#------------------------------------------------------------------------------
function do_search_file_select ()
{
    menutitle="Select Target Image for Template Search"
    startdir="media/images"
    filext='jpg'

    Filebrowser "$menutitle" "$startdir"

    exitstatus=$?
    if [ $exitstatus -eq 0 ]; then
        if [ "$selection" == "" ]; then
            echo "User Pressed Esc with No File Selection"
        else
            whiptail --title "Copy Search Target File" --msgbox " \

Copy Search Target File

File: $filename
From: $filepath
 To : $searchdir
\
" 0 0 0
            cp "$filepath/$filename" "$searchdir"
        fi
    else
        echo "User Pressed Cancel. with No File Selected"
    fi
}

#------------------------------------------------------------------------------
function do_search_file_view ()
{
search_list=$(ls -lhp $searchdir/*jpg | awk -F ' ' ' { print $9 " " $5 } ')
whiptail --title "View Search Target File(s)" --msgbox " \

List of Current Search Target Files
in folder $searchdir
-----------------------------------
$search_list
-----------------------------------
\
" 0 0 0
}

#------------------------------------------------------------------------------
function do_search_about ()
{
whiptail --title "About Search" --msgbox " \

 1. Use SELECT menu pick from Search Images Menu
    You can select one or more image files that will
    be copied to $searchdir
 2. Use EDIT menu pick from Search Images Menu
    This will edit search_config.py using nano editor
    ctrl-x y to exit nano then save changes
 3. Use RUN menu pick from Search Images Menu
    This will search for matches for each target search file
    All specific target search file results will be put in a
    folder named after the search target file name minus the extension.
    NOTE To activate copy, Make sure search_config.py variable
    search_copy_on=True
    If False then no copy will occur (use for testing value settings)
 4. Use Webserver and browser to view match result files
    in /media/search folder
\
" 0 0 0
}

#------------------------------------------------------------------------------
function do_speed_search_menu ()
{
  cd $DIR
  config_file=$searchconfig
  SET_SEL=$( whiptail --title "Search Images Menu" \
                      --menu "Arrow/Enter Selects or Tab Key" 0 0 0 \
                      --ok-button Select \
                      --cancel-button Back \
  "a SELECT" "Image Target Files for Search" \
  "b VIEW" "Current Search Target Files" \
  "c EDIT" "nano $config_file Settings" \
  "d SEARCH" "Speed Images for Matches" \
  "e ABOUT" "Images Search" \
  "q BACK" "To Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SET_SEL" in
      a\ *) do_search_file_select
            cd $DIR
            do_speed_search_menu ;;
      b\ *) do_search_file_view
            do_speed_search_menu ;;
      c\ *) /bin/nano "$searchconfig"
            do_speed_search_menu ;;
      d\ *) clear
            ./search-speed.py
            do_anykey
            do_speed_search_menu ;;
      e\ *) do_search_about
            do_speed_search_menu ;;
      q\ *) cd $DIR
            do_main_menu ;;
      *) whiptail --msgbox "Programmer error: unrecognized option" 0 0 0 ;;
    esac || whiptail --msgbox "There was an error running menu item $SET_SEL" 0 0 0
  fi
}

#------------------------------------------------------------------------------
function do_report_menu ()
{
  SET_SEL=$( whiptail --title "sqlite3 Report Menu" \
                      --menu "Arrow/Enter Selects or Tab Key" 0 0 0 \
                      --ok-button Select \
                      --cancel-button Back \
  "a SPEED" "Greater Than Specified Listing" \
  "b HOUR" "Speed Greater Than 17 (Exclude bikes, people)" \
  "c DELETE" "All Reports in media/reports" \
  "d ABOUT" "This Report Menu" \
  "q BACK" "To Main Menu" 3>&1 1>&2 2>&3 )

  RET=$?
  if [ $RET -eq 1 ]; then
    do_main_menu
  elif [ $RET -eq 0 ]; then
    case "$SET_SEL" in
      a\ *) clear
            ./sql_speed_gt.py
            echo ""
            echo "View this report in html format"
            echo "From Speed-Camera Web Page in media/reports folder"
            echo "Web browser url is http://$myip:$myport"
            do_anykey
            do_report_menu ;;
      b\ *) clear
            sqlite3 data/speed_cam.db \
              -header -column \
              "select idx, log_hour, ave_speed, speed_units,image_path,direction \
              from speed \
              where ave_speed > 17"  | more -d
            echo ""
            echo "Updating Speed Camera media/reports web files  Wait..."
            ./sql_speed_gt.py 17
            echo ""
            echo "This report should eliminate bikes/pedestrians and other slower objects"
            echo "View this report in html format"
            echo "From Speed-Camera Web Page in media/reports folder"
            echo "Web browser url is http://$myip:$myport"
            do_anykey
            do_report_menu ;;
      c\ *) clear
            echo "Dir Listing for media/reports"
            ls -l media/reports
            read -p "Delete All Files? (y/n) " choice
            case "$choice" in
                y|Y ) read -p "Are you Sure? (y/n) " choice
                case "$choice" in
                    y|Y ) echo ""
                      rm media/reports/*
                      ls -l media/reports
                      echo "Files Deleted"
                      do_anykey
                      ;;
                    * ) do_report_menu
                      ;;
                esac
            esac
            do_report_menu ;;
      d\ *) do_report_about
            do_report_menu ;;
      q\ *) clear
            do_main_menu ;;
      *) whiptail --msgbox "Programmer error: un recognized option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running selection $SET_SEL" 20 60 1
  fi
}

#------------------------------------------------------------------------------
function do_report_about()
{
  whiptail --title "About SQL Reports Menu" --msgbox " \
       speed camera - SQL Reports Menu

Reports use the sqlite3 speed camera database located at
   /home/pi/speed-cam/data/speed_cam.db

The reports runs sql queries for displaying formatted
reports.

\
" 0 0 0
}

#------------------------------------------------------------------------------
function do_upgrade()
{
  if (whiptail --title "GitHub Upgrade speed-cam" \
               --yesno "Upgrade speed-cam Files from GitHub.\n Some config Files Will be Updated" 0 0 0 \
               --yes-button "upgrade" \
               --no-button "Cancel" ); then
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
 menubox.sh manages speed-cam operation, settings and utilities

 1. Start speed-cam.py and Calibrate the camera distance settings
    using calib images.
 2. Edit config.py and set calibrate=False
 3. Start speed-cam.py and create speed images.  These can
    be viewed from a web browser using the web server url.
 4. Speed Cam Data will be in speed-cam.csv file
 5. If you want to search speed images for similar image matches.
    Select the SEARCH Menu Pick then follow instructions
    in ABOUT menu pick
 6. You can also create html files that combine csv and image data
    into formatted html pages. Output will be put in media/html folder
    Run makehtml.py. check that webserver is running.  View html files
    on a network pc web browser by accessing rpi IP address and port.
    eg 192.168.1.100:8080 (replace ip with your rpi ip)

 For more see  https://github.com/pageauc/rpi-speed-camera

 To Exit this About Press TAB key then Enter on OK
 Good Luck and Enjoy .... Claude
\
" 0 0 0
}

#------------------------------------------------------------------------------
function do_main_menu ()
{
  cd $DIR
  init_status
  temp="$(/opt/vc/bin/vcgencmd measure_temp)"

  cd $DIR
  SELECTION=$(whiptail --title "Speed Camera Main Menu" \
                       --menu "Arrow/Enter Selects or Tab Key" 0 0 0 \
                       --cancel-button Quit \
                       --ok-button Select \
  "a $SPEED_1" "$SPEED_2" \
  "b $WEB_1" "$WEB_2" \
  "c SETTINGS" "Change speed_cam and webserver settings" \
  "d PLUGINS" "Change plugins Settings" \
  "e RCLONE" "Manage File Transfers to Remote Storage" \
  "f HTML" "Make html pages from speed-cam.csv & jpgs" \
  "g VIEW" "View speed-cam.csv File" \
  "h SEARCH" "Images Search Menu (openCV Template Match)" \
  "i UPGRADE" "Program Files from GitHub.com" \
  "j STATUS" "CPU $temp   Select to Refresh" \
  "k REPORTS" "Run Various sqlite3 Reports" \
  "l HELP" "View Readme.md" \
  "m ABOUT" "Information about this program" \
  "q QUIT" "Exit This Program"  3>&1 1>&2 2>&3)

  RET=$?
  if [ $RET -eq 1 ]; then
    exit 0
  elif [ $RET -eq 0 ]; then
    case "$SELECTION" in
      a\ *) do_speed_cam ;;
      b\ *) do_webserver ;;
      c\ *) do_settings_menu ;;
      d\ *) do_plugins_menu ;;
      e\ *) do_sync_menu
            do_main_menu ;;
      f\ *) do_makehtml_menu ;;
      g\ *) clear
            more ./speed-cam.csv
            do_anykey ;;
      h\ *) do_speed_search_menu ;;
      i\ *) clear
            do_upgrade ;;
      j\ *) clear
            do_main_menu ;;
      k\ *) do_report_menu ;;
      l\ *) pandoc -f markdown -t plain  Readme.md | more -d
            do_anykey
            do_main_menu ;;
      m\ *) do_about ;;
      q\ *) rm -f $filename_conf $filename_temp
            clear
            exit 0 ;;
         *) whiptail --msgbox "Programmer error: unrecognised option" 20 60 1 ;;
    esac || whiptail --msgbox "There was an error running menu item $SELECTION" 20 60 1
  fi
}

#------------------------------------------------------------------------------
#                                Main Script
#------------------------------------------------------------------------------

while true; do
   do_main_menu
done
