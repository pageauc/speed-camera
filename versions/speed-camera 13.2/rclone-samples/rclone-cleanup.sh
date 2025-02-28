#!/bin/bash
ver="10.00"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # get cur dir of this script
progName=$(basename -- "$0")
cd $DIR

echo "$progName $ver  written by Claude Pageau"

# Customize rclone sync variables Below
# ---------------------------------------
rcloneName="gdmedia"
# ---------------------------------------

# Display Users Settings
echo "
---------- SETTINGS -------------
rcloneName   : $rcloneName
---------------------------------"
if pidof -o %PPID -x "$progName"; then
    echo "WARN  : $progName Already Running. Only One Allowed."
else
    if [ -f /usr/bin/rclone ]; then
        echo "INFO  : rclone is installed at /usr/bin/rclone"
        rclone version   # display rclone version
        rclone listremotes        
        echo "INFO  : /usr/bin/rclone cleanup -v $rcloneName:"
        echo "        One Moment Please ..."
        /usr/bin/rclone cleanup -v $rcloneName:
        echo "Done Cleanup of $rcloneName:"
    else
        echo "WARN  : /usr/bin/rclone Not Installed."
    fi
fi
echo "$progName Bye ..."

