#!/bin/bash
# This is a simple report generator for the speed camera sqlite3 database
# written by Claude Pageau
# speed-cam.py release ver 8.91 or higher
# If you get database errors then delete or rename data/speed_cam.db
# Then stop and restart speed-cam.py. Note you may have to upgrade.
# sqlite3 database will be recreated

ver="8.91"

if [ -z "$1" ]; then
    clear
    echo "----------------- Speed Camera Report ----------------------"
    echo "This Report will Display all Records with Speeds Above"
    echo "Specified Value. Specify an Integer Number for Speed Over. 0=all"
    read -p "Speed Over: " speed
else
    speed="$1"
fi

if ! [[ "$speed" =~ ^[0-9]+$ ]] ;
   then exec >&2; echo "ERROR: $speed speed is Not an Integer Number. Try Again."
   exit 1
fi

report_filename="sql_speed_gt"
report_dir="media/reports"
if [ ! -d $report_dir ] ; then
    mkdir "$report_dir"
fi

report_path="$report_dir/$report_filename$speed.txt"
#  Schema for speed-camera sqlite3 speed table on speed_cam.db database file
echo ""
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

echo "sqlite3 Report for speed over $speed" | tee $report_path
echo "" | tee -a $report_path
sqlite3 data/speed_cam.db \
  -header -column \
  "select idx,ave_speed,speed_units,image_path,direction \
  from speed \
  where ave_speed > $speed" | tee -a $report_path
echo "" | tee -a $report_path
echo "Saved sqlite3 Report Query to $report_path" | tee -a $report_path

# Generate a png graph using speed value
graph_path="$report_dir/$report_filename$speed.png"
echo "Generating Graph  Wait ..."
sqlite3 data/speed_cam.db -column \
"select log_date, log_hour, count(*) \
 from speed \
 where ave_speed > $speed \
 group by log_date, log_hour \
 order by log_date;" > hour_count.txt

gnuplot <<- EOF
    reset
    set autoscale
    set key off
    set grid
    set terminal png size 900,600
    set output "$graph_path"
    set title "Speed Camera Count by Hour where speed gt $speed"
    set xtics rotate
    set xdata time
    set timefmt "%Y%m%d %H"
    set format x "%Y-%m-%d"
    set xlabel "Date"
    set ylabel "Count"
    plot "hour_count.txt" using 1:3 with boxes fill solid
EOF
rm hour_count.txt

if [ -z "$1" ]; then
   clear
   more -d $report_path
fi
echo "Saved Bar Graph to $graph_path

$0 $ver Processing Complete
Bye
"