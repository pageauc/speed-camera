#!/bin/bash
ver="7.10"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # get cur dir of this script
progName=$(basename -- "$0")
cd $DIR
echo "$progName $ver  written by Claude Pageau"

#==================================
#   watch-app.sh User Settings
#==================================

watch_config_on=false    # true= Remotely Manage Files from Remote Storage  false=off
watch_app_on=false       # true= Monitor watch_app_fname and attempt restart false=off
watch_reboot_on=false    # true= Reboot RPI If watch_app_fname Down false=0ff

watch_app_fname="speed-cam.py"  # Filename of Program to Monitor for Run Status

rclone_name="gdmedia"           # Name you gave remote storage service

sync_dir="speedcam-config-sync"      # Name of folder to manage when watch_config_on=true

# List of file names to monitor for updates
sync_files=("config.py" "speed-cam.py" "rclone-security-sync-recent.sh" \
"search-config.py" "watch-app-err.log" "reboot.force" "remote-run.sh")

# Note: It is not recommended to set reboot.force and remote-run.sh at same time

#====== End User Setting Edits ======

fList=""
for fname in "${sync_files[@]}" ; do
    fList=$fList' '$fname
done
# Display watch-app Settings
echo "--------------- SETTINGS -----------------

watch_config_on  : $watch_config_on       # manage config true=on false=off
watch_app_on     : $watch_app_on          # restart true=on false=off
watch_reboot_on  : $watch_reboot_on       # reboot true=on false=off
watch_app_fname  : $watch_app_fname

rclone_name      : $rclone_name  # Name you gave remote storage service

sync_dir         : $sync_dir   # Will be created if does not exist
sync_files       :$fList

------------------------------------------"

progDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # folder location of this script
cd $progDir

# ------------------------------------------------------
function do_watch_restart ()
{
    now=$(/bin/date +%Y-%m-%d-%H:%M:%S)
    if ! [ -z "$( pgrep -f $watch_app_fname )" ]; then
        progPID=$( pgrep -f "$watch_app_fname" )
        echo "$now INFO  : Stop $watch_app_fname PID $progPID"
        sudo kill $progPID >/dev/null 2>&1
        sleep 3
    fi
    # restart the app
    ./$watch_app_fname  >/dev/null 2>&1 &
    echo "$now INFO  : Wait 10 seconds for $watch_app_fname to restart"
    sleep 10
    if [ -z "$(pgrep -f $watch_app_fname)" ] ; then
        # pi-timolo did not start
        echo "$now INFO  : Restart Failed $watch_app_fname"
        do_watch_reboot        
    else
        progPID=$( pgrep -f $watch_app_fname )
        echo "$now INFO  : Restart OK $watch_app_fname PID $progPID"
    fi
}

# ------------------------------------------------------
function do_remote_config ()
{
    found_update=false
    reboot_on=false
    now=$(/bin/date +%Y-%m-%d-%H:%M:%S)
    if [ ! -d $sync_dir ] ; then  # If local sync dir does not exist then create one
        echo "$now INFO  : Create New Dir $sync_dir"
        mkdir $sync_dir
        for fname in "${sync_files[@]}" ; do
            if [[ "$fname" == "reboot.force" ]]; then
                # initialize reboot.force.done file
                echo "$now INFO  : Creating $sync_dir/$fname.log Entry"
                echo "$progName  written by Claude Pageau
=========================================================
  To Force RPI Reboot. Rename this File to reboot.force
  On the remote storage name $rclone_name:
================ Reboot History =========================
$now $sync_dir/$fname.log History File Initialized." > $sync_dir/$fname.log
            else
                if [ -f $fname ] ; then
                    echo "$now INFO  : Copy $fname to $sync_dir"
                    cp $fname $sync_dir/$fname.orig
                    cp $fname $sync_dir/$fname.done
                else
                    echo "$now WARN  : $fname File Not Found"
                fi
            fi
        done
        # sync new sync_dir files to remote storage
        /usr/bin/rclone sync -v $sync_dir $rclone_name:$sync_dir  # sync to remote storage drive
        if [ ! $? -eq 0 ]; then
            /usr/bin/rclone sync -v --log-file watch-app-err.log $sync_dir $rclone_name:$sync_dir
            echo "$now EPROR - Problem with rclone. Check rclone_name $rclone_name"
        fi
    else
        now=$(/bin/date +%Y-%m-%d-%H:%M:%S)
        echo "$now INFO  : Found Local Dir $sync_dir"
        # Update local sync_dir from remote
        echo "$now INFO  : rclone sync -v $rclone_name:$sync_dir $sync_dir"
        /usr/bin/rclone sync -v $rclone_name:$sync_dir $sync_dir  # sync remote with local sync dir
        if [ ! $? -eq 0 ]; then  # Try to fix problem if local dir or some other error occurred
            now=$(/bin/date +%Y-%m-%d-%H:%M:%S)
            echo "$now INFO  : rclone sync -v $sync_dir $rclone_name:$sync_dir"
            /usr/bin/rclone sync $sync_dir $rclone_name:$sync_dir  # sync to remote storage drive
            /usr/bin/rclone sync -v $rclone_name:$sync_dir $sync_dir  # sync remote with local sync dir
            if [ ! $? -eq 0 ]; then  # Create an error log of problem until next update cycle works.
                now=$(/bin/date +%Y-%m-%d-%H:%M:%S)
                /usr/bin/rclone sync -v --log-file watch-app-err.log $rclone_name:$sync_dir $sync_dir
                echo "$now ERROR : Problem with rclone. Check rclone_name $rclone_name"
            fi
        fi

        # Process sync_files list to see if anything is on list
        for fname in "${sync_files[@]}" ; do     # check if new config files are present
            now=$(/bin/date +%Y-%m-%d-%H:%M:%S)
            if [[ "${fname}" == "reboot.force" ]]; then
                if [[ -f $sync_dir/$fname ]] ; then
                    found_update=true
                    reboot_on=true
                    echo "$now INFO  : Found $fname. Reboot Scheduled."
                    echo "$now INFO  : Found $fname. Reboot Scheduled." >> $sync_dir/$fname
                    cp $sync_dir/$fname $sync_dir/$fname.log
                    rm $sync_dir/$fname
                fi
            elif [[ "${fname}" == "remote-run.sh" ]]; then
                echo "$now INFO  : Found $fname entry in sync_files"
                if [ -f $sync_dir/$fname ] ; then
                    echo "$now INFO  : Found $sync_dir/$fname"
                    if [ -f $fname ] ; then
                        echo "$now INFO  : Check if $fname Already Running"
                        found_update=true
                        if [ -z "$( pgrep -f $fname )" ] ; then
                            echo "$now INFO  : $fname is Not Running"
                        else
                            progPID=$( pgrep -f "$fname" )
                            echo "$now WARN  : Stop $fname PID $progPID"
                            echo "$now WARN  : Stop $fname PID $progPID" >> $sync_dir/$fname.log
                            sudo kill $progPID >/dev/null 2>&1
                        fi
                        cp $fname $sync_dir/$fname.prev
                        cp $sync_dir/$fname $fname       # update working file
                        cp $fname $sync_dir/$fname.done
                        rm $sync_dir/$fname
                        echo "$now INFO  : Run $fname as Background Task"
                        echo "$now INFO  : Run $fname as Background Task" >> $sync_dir/$fname.log
                        ./$fname >> $sync_dir/$fname.log &
                    else
                        echo "$now WARN  : Run Failed. $fname File Not Found."
                        echo "$now WARN  : Run Failed. $fname File Not Found."  >> $sync_dir/$fname.log
                    fi
                else
                    echo "$now WARN  : $sync_dir/$fname File Not Found."
                    echo "$now WARN  : $sync_dir/$fname File Not Found."  >> $sync_dir/$fname.log
                fi
            elif [[ "${fname}" == "watch-app-err.log" ]]; then
                if [ -f $fname ] ; then
                    echo "$now INFO  : Found $fname"
                    found_update=true
                    cp $fname $sync_dir/
                    rm $fname
                fi
            elif [ -f $sync_dir/$fname ] ; then
                found_update=true
                change_files+=("$fname")
                echo "$now INFO  : Found Update for File $fname"
                cp $fname $sync_dir/$fname.prev  # save copy with .prev extension
                echo "$now INFO  : Copy $sync_dir/$fname to $fname"
                cp $sync_dir/$fname $fname       # update working file
            fi
        done

        # echo "$now INFO  : Changed Files ${change_files[*]}"
        if $found_update ; then
            echo "$now INFO  : Found Changes.  Restarting $watch_app_fname"
            do_watch_restart
            if [ -z "$(pgrep -f $watch_app_fname)" ] ; then
                # Roll back changes since pi-timolo did not start
                for fname in "${$change_files[@]}" ; do
                    if [ -f $sync_dir/$fname ] ; then
                        echo "$now WARN  : Undo Update Copy $fname to $sync_dir/$fname.err"
                        cp $fname $sync_dir/$fname.bad
                        cp $sync_dir/$fname.prev $fname
                        rm $sync_dir/$fname
                    fi
                done
                change_files=()
                do_watch_restart
            fi
            for fname in "${change_files[@]}" ; do
                now=$(/bin/date +%Y-%m-%d-%H:%M:%S)
                if [ -f $sync_dir/$fname ] ; then
                    echo "$now INFO  : Confirm Update Copy $fname to $sync_dir/$fname.done"
                    cp $fname $sync_dir/$fname.done
                    rm $sync_dir/$fname
                fi
            done
            # update remote storage with status
            echo "$now INFO  : rclone sync -v $sync_dir $rclone_name:$sync_dir"
            /usr/bin/rclone sync -v $sync_dir $rclone_name:$sync_dir
        else
            echo "$now INFO  : No File Changes Found in $sync_dir"
        fi

        if $reboot_on ; then   # Reboot after all the other updates done
            echo "Found File reboot.force in $sync_dir"
            echo "     Reboot in 15 seconds Waiting ...."
            echo "        ctrl-c to Abort Reboot."
            sleep 10
            echo "       Rebooting in 5 seconds"
            sleep 5
            sudo reboot
        fi
    fi
}

# ------------------------------------------------------
function do_watch_app()
{
    if [ -z "$( pgrep -f $watch_app_fname )" ]; then
        do_watch_restart
    else
        progPID=$( pgrep -f $watch_app_fname )
        echo "$now INFO  : $watch_app_fname is Running PID $progPID"
    fi
}

# ------------------------------------------------------
function do_watch_reboot ()
{
    if [ -z "$(pgrep -f $watch_app_fname)" ] ; then
        if $watch_reboot_on ; then
            now=$(/bin/date +%Y-%m-%d-%H:%M:%S)
            echo "$now INFO  : $watch_app_fname is NOT Running so reboot"
            echo "$now INFO  : Reboot in 15 seconds Waiting ...."
            echo "                     ctrl-c to Abort Reboot."
            sleep 10
            echo "$now INFO :          Rebooting in 5 seconds"
            sleep 5
            sudo reboot
        fi
    else
        APP_PID=$(pgrep -f $watch_app_fname)
        echo "$now INFO  : $watch_app_fname is Running PID $APP_PID"
    fi
}

# ------------------------------------------------------
# Main script processing
now=$(/bin/date +%Y-%m-%d-%H:%M:%S)
if pidof -o %PPID -x "$progName"; then
    echo "$now WARN  : $progName Already Running. Only One Allowed."
else
    reboot_on=false  # If a reboot file is found in $sync_dir then set to true
    if $watch_app_on ; then # Restart app if not running
        echo "$now INFO  : Watch App is On per watch_app_on=$watch_app_on"
        do_watch_app
    else
        echo "$now WARN  : Watch App is Off per watch_app_on=$watch_app_on"
    fi

    if $watch_config_on ; then  # Check if remote configuration feature is on
        echo "$now INFO  : Remote Configuration is On per watch_config_on=$watch_config_on"
        if [ -f /usr/bin/rclone ]; then
            echo " List Remote Names"
            echo "==================="
            /usr/bin/rclone listremotes
            echo "==================="
            do_remote_config
        else
            echo "$now ERROR : /usr/bin/rclone File Not Found. Please Investigate."
        fi
    else
        echo "$now WARN  : Remote Configuration is Off per watch_config_on=$watch_config_on"
    fi

    if $watch_reboot_on ; then # check if watch app feature is on
        echo "$now INFO  : Watch Reboot is On per watch_reboot_on=$watch_reboot_on"
        do_watch_reboot
    else
       echo "$now WARN  : Watch Reboot is Off per watch_reboot_on=$watch_reboot_on"
    fi

    if [ -f "watch-app-new.sh" ] ; then
        echo "$now WARN  : Found Newer Version of watch-app.sh"
        echo "------------------------------------------
        Check If You Already Have New Version. To Upgrade if Required.
        1  nano watch-app-new.sh
        2  Edit settings to transfer any customization from existing watch-app.sh
        3  cp watch-app.sh watch-app-old.sh
        4  rm watch-app.sh
        5  mv watch-app-new.sh watch-app.sh
        6  Test changes"
    fi
fi
echo "------------------------------------------
$progName Done ..."
exit

