#!/usr/bin/env python
"""
written by Claude Pageau
Speed Camera Utility to create html and graph png files from
the sqlite3 database data/speed_cam.db

"""

from __future__ import print_function
print("Loading ...")
import sqlite3
import Gnuplot
import os
import time
import logging
import argparse
import sys

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--speed", required=False, type=int, nargs=1,
	help="Speed Over Value")
if not len(sys.argv) > 1:
    print("----------------- Speed Camera Report ----------------------")
    print("This Report will Display all Records with Speeds Over")
    print("Specified Value. SPEED_OVER Must be Integer. 0=all")
    SPEED_OVER = raw_input("Enter SPEED_OVER: ")
else:
    SPEED_OVER = sys.argv[1]
try:
    test = int(SPEED_OVER)
except ValueError:
    logging.error("%s SPEED_OVER Must be Integer. 0=all", SPEED_OVER)
    logging.info("If No Parameter is Supplied, You Will be Prompted for SPEED_OVER Value")
    sys.exit(1)

DB_PATH = 'data/speed_cam.db'
DB_TABLE = 'speed'
REPORTS_DIR = 'media/reports'
if not os.path.isdir(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)   
REPORTS_FILENAME = "hour_count_gt"
REPORTS_PATH = os.path.join(REPORTS_DIR, REPORTS_FILENAME + SPEED_OVER + "_list.html")
COUNT_PATH = os.path.join(REPORTS_DIR, REPORTS_FILENAME + SPEED_OVER + "_totals.html")
GRAPH_PATH = os.path.join(REPORTS_DIR, REPORTS_FILENAME + SPEED_OVER + "_graph.jpg")
GRAPH_DATA_PATH = os.path.join(REPORTS_FILENAME + SPEED_OVER + ".txt")

REPORT_QUERY = ('''
select
    log_date,
    log_hour,
    ave_speed,
    speed_units,
    image_path,
    direction
from %s
where ave_speed > %s
order by
    idx desc''' % (DB_TABLE, SPEED_OVER))

GRAPH_QUERY = ('''
select
    log_date,
    log_hour,
    count(*)
from %s
where
    ave_speed > %s
group by
    log_date,
    log_hour
order by
    idx asc
''' % (DB_TABLE, SPEED_OVER))

HTML_HEADER_1 = (''' <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <html>
    <head>
    <meta "Content-Type" content="txt/html; charset=ISO-8859-1" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Speed Camera by Claude Pageau</title>
    <style>
    table {
        width:100%
    }
    table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    table#t01 tr:nth-child(even) {
    background-color: #eee;
    }
    table#t01 tr:nth-child(odd) {
    background-color: #fff;
    }
    </style>
    </head>
    <body>''')
HTML_HEADER_2 = ('''<center><h2>Speed Camera Report Listing for Speeds gt %s</h2>
    <h4>Click Image Path to View Image. Use Browser Back Button to Return to This List</h4>'''% (SPEED_OVER))
HTML_HEADER_2C = ('''<center><h2>Speed Camera Hourly Count Summary Report for Speeds gt %s</h2>
   <img src="%s" alt="Hourly Bar Graph" </center>''' % (SPEED_OVER, os.path.basename(GRAPH_PATH)))
HTML_HEADER_3 = ('''
    <table id="t01">
    <tr>
    <th>Date</th>
    <th>Hour</th>
    <th>Speed</th>
    <th>Image Path</th>
    <th>Direction</th>
    </tr>''')
HTML_HEADER_3C = ('''
    <table id="t01">
    <tr>
    <th>Date</th>
    <th>Hour</th>
    <th>Count/Hr Totals</th>
    </tr>''')
# HTML_HEADER = HTML_HEADER_1 + HTML_HEADER_2 + HTML_HEADER_3
HTML_FOOTER = "</table></body></html>"

def make_graph_data():
    logging.info("Working.  Please Wait ...")
    graph_data = []
    graph_html = []
    start_time = time.time()
    logging.info("Connect to Database %s", DB_PATH)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(GRAPH_QUERY)
    f = open(GRAPH_DATA_PATH, "w")
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        log_date = (row["log_date"])
        log_hour = (row["log_hour"])
        count = (row[cursor.rowcount])
        row_html = ('''<tr><td>%s</td><td>%s</td><td>%s</td></tr>''' %(log_date, log_hour, count))
        graph_html.append(row_html)
        row_data = ("%s %s %s \n" %(log_date, log_hour, count))
        f.write(row_data)
       # graph_data.append(row)
    f.close()
    cursor.close()
    connection.close()
    # Write count report html file with graph on top
    f = open(COUNT_PATH, "w")
    f.write(HTML_HEADER_1)
    f.write(HTML_HEADER_2C)
    f.write(HTML_HEADER_3C)
    for item in graph_html:
        f.write(item)
    f.write(HTML_FOOTER)
    f.close()
    del graph_html
    logging.info("Saved html File to %s", COUNT_PATH)

def make_graph_image():
    make_graph_data()
    g = Gnuplot.Gnuplot()
    g.reset()
    graph_title = ('Speed Camera Count by Hour where speed gt %s' % SPEED_OVER)
    g.title(graph_title)
    png_file_path = ('set output "%s"' % GRAPH_PATH)
    g(png_file_path)
    g.xlabel('Date')
    g.ylabel('Count')
    g("set autoscale")
    g("set key off")
    g("set grid")
    g("set terminal png size 900,600")
    g("set xtics rotate")
    g("set xdata time")
    g('set timefmt "%Y%m%d %H"')
    g('set format x "%Y-%m-%d"')
    databuff = Gnuplot.File(GRAPH_DATA_PATH, using='1:3', with_='boxes fill solid')
    g.plot(databuff)
    logging.info("Saved Graph File To %s", GRAPH_PATH)

def make_html():
    logging.info("Working.  Please Wait ...")
    html_table = []   # List to hold html table rows
    start_time = time.time()
    logging.info("Connect to Database %s", DB_PATH)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(REPORT_QUERY)
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        log_date = (row["log_date"])
        log_hour = (row["log_hour"])
        ave_speed = (row["ave_speed"])
        speed_units = (row["speed_units"])
        image_path = (row["image_path"])
        image_filename=os.path.basename(image_path)
        direction = (row["direction"])
        link_path = os.path.join(os.path.relpath(
                        os.path.abspath(os.path.dirname(image_path)),
                        os.path.abspath(REPORTS_DIR)),
                        image_filename)
        table_row = ('<tr><td>%s</td><td>%s</td><td>%s %s</td><td><a href="%s">%s</a></td><td>%s</td></tr>' %
                    (log_date,
                     log_hour,
                     ave_speed,
                     speed_units,
                     link_path,
                     image_path,
                     direction))
        html_table.append(table_row)
    connection.close()
    f = open(REPORTS_PATH, "w")
    f.write(HTML_HEADER_1)
    f.write(HTML_HEADER_2)
    f.write(HTML_HEADER_3)
    for item in html_table:
        f.write(item)
    f.write(HTML_FOOTER)
    f.close()
    del html_table
    logging.info("Saved html File to %s", REPORTS_PATH)

if __name__ == '__main__':
    start_time = time.time()
    make_html()
    make_graph_image()
    os.remove(GRAPH_DATA_PATH)
    duration = time.time() - start_time
    logging.info("Processing Took %.2f s.", duration)
    logging.info("View Reports from Speed Camera Web Page under media/reports")
