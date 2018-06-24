#!/bin/bash
# A simple speed camera query report to display
# hourly statistics.  written by Claude Pageau
#

report_filename="sql_hour_count.txt"
report_dir="media/reports"
if [ ! -d $report_dir ] ; then
    mkdir "$report_dir"
fi
report_path="$report_dir/$report_filename"

echo "     sqlite3 speed camera Report" | tee $report_path
echo "Hourly Count and Average Speed Report" | tee -a $report_path
echo "-------------------------------------" | tee -a $report_path
sqlite3 data/speed_cam.db \
  -header -column \
"select log_date, log_hour, count(*), round(avg(ave_speed),2), speed_units \
 from speed \
 group by log_date, log_hour \
 order by log_date;" | tee -a $report_path
echo "Report Saved to File $report_path" | tee -a $report_path

echo "Generating plot image"
sqlite3 data/speed_cam.db -column \
"select log_date, log_hour, count(*) \
 from speed \
 group by log_date, log_hour \
 order by log_date;" | tee hour_count.txt

gnuplot plot_hour_count.dat
rm hour_count.txt

clear
more -d $report_path
