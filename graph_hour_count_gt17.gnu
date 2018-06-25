# graph_hour_count_gt17.gnu   written by Claude Pageau
# gnuplot script to generate a .png graph of
# hourly speed count.  This should eliminate slower objects
# like bikes, pedestrians etc.

reset
set autoscale
set key off
set grid
set terminal png size 900,600
set output "media/reports/sql_hour_count_gr17.png"
set title "Speed Camera Count by Hour where speed gt 17"
set xtics rotate
set xdata time
set timefmt "%Y%m%d %H"
set format x "%Y-%m-%d"
set xlabel "Date"
set ylabel "Count"
plot "hour_count.txt" using 1:3 with boxes fill solid

#plot "hour.txt" using 1:3 with lines
