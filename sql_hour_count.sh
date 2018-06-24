#!/bin/bash
# A simple speed camera query report to display
# hourly statistics.  written by Claude Pageau
#
echo "     sqlite3 speed camera Report" | tee sql_hour_count.txt
echo "Hourly Count and Average Speed Report" | tee -a sql_hour_count.txt
echo "-------------------------------------" | tee -a sql_hour_count.txt
sqlite3 data/speed_cam.db \
  -header -column \
"select log_date, log_hour, count(*), round(avg(ave_speed),2), speed_units \
 from speed \
 group by log_date, log_hour \
 order by log_date;" | tee -a sql_hour_count.txt
echo "Report Saved to File sql_hour_count.txt" | tee -a sql_hour_count.txt
more -d sql_hour_count.txt
