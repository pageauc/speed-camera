#!/bin/bash
ver="7.00"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # get cur dir of this script
progName=$(basename -- "$0")
cd $DIR
echo "INFO  : $progName $ver  written by Claude Pageau"

echo "           Instructions

 This is a sample script that will be
 replaced by watch-app.sh if watch_config-On=true
 This will enable remote configuration from a remote storage service

 Upload a script called remote-run.sh to the folder pointed to by
 watch-app.sh variable sync_dir.  watch-app.sh will
 download and execute the script if it is named remote-run.sh

 See speed-camera GitHub Wiki for more details

$progName Bye ...
"
