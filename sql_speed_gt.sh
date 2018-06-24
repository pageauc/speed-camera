#!/bin/bash
# This is a simple report generator for the speed camera sqlite3 database
# written by Claude Pageau
# speed-cam.py release ver 8.91 or higher
# If you get database errors then delete or rename data/speed-cam.db
# Then stop and restart speed-cam.py.  Note you may have to upgrade.

report_filename="sql_speed_gt.txt"
report_dir="media/reports"
if [ ! -d $report_dir ] ; then
    mkdir "$report_dir"
fi
report_path="$report_dir/$report_filename"

clear
echo "----------------- Speed Camera Report ----------------------"
echo "This report will display all records with speed above"
echo "Specified Value. Specify number for speed over. 0=all"
read -p "Speed Over: " speed
if ! [[ "$speed" =~ ^[0-9]+$ ]] ;
   then exec >&2; echo "error: Not a number"; exit 1
fi

echo ""
#  Schema for speed-camera sqlite3 speed table on speed_cam.db database file
: "
     idx text primary key,
     log_date text, log_hour text, log_minute text,
     camera text,
     ave_speed real, speed_units text, image_path text,
     image_w integer, image_h integer, image_bigger integer,
     direction text, plugin_name text,
     cx integer, cy integer,
     mw integer, mh integer, m_area integer,
     x_left integer, x_right integer,
     y_upper integer, y_lower integer,
     max_speed_over integer,
     min_area integer, track_trig_len integer,
     cal_obj_px integer, cal_obj_mm integer)
"

echo "Running sqlite3 Report for speed over $speed" | tee $report_path
echo "" | tee -a $report_path
sqlite3 data/speed_cam.db \
  -header -column \
  "select idx,ave_speed,speed_units,image_path,direction \
  from speed \
  where ave_speed > $speed" | tee -a $report_path
echo "" | tee -a $report_path
echo "Report Saved to File $report_path" | tee -a $report_path
clear
more -d $report_path