#!/bin/bash
# This is a simple report generator for the speed camera sqlite3 database
# written by Claude Pageau
clear
echo "----------------- Speed Camera Report ----------------------"
echo "This report will display all records with speed above"
echo "Specified Value. Specify number for speed over. 0=all"
read -p "Speed Over: " speed
if ! [[ "$speed" =~ ^[0-9]+$ ]] ;
   then exec >&2; echo "error: Not a number"; exit 1
fi
echo ""
echo "Running sqlite3 Report for speed over $speed" | tee $0.rep
echo "" | tee -a $0.rep
sqlite3 data/speed_cam.db \
  -header -column \
  "select idx,speed_ave,speed_units,image_path,cx,cy,direction \
  from speed \
  where speed_ave > $speed" | tee -a $0.rep
echo "" | tee -a $0.rep
echo "Report Saved to File $0.rep"
echo "Bye ..."
