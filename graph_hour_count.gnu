# graph_hour_count.gnu   written by Claude Pageau
# gnuplot script to generate a .png graph of
# hourly speed count.

reset
set autoscale
set key off
set grid
set terminal png size 900,600
set output "media/reports/sql_hour_count.png"
set title "Speed Camera Count by Hour"
set xtics rotate
set xdata time
set timefmt "%Y%m%d %H"
set format x "%Y-%m-%d"
set xlabel "Date"
set ylabel "Count"
plot "hour_count.txt" using 1:3 with boxes fill solid

#plot "hour.txt" using 1:3 with lines
