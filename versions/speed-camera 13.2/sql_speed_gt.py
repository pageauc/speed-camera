#!/usr/bin/env python
"""
written by Claude Pageau
Speed Camera Utility to create html report files from
the sqlite3 database default data/speed_cam.db

"""

from __future__ import print_function
print("Loading ...")
import os
import time
import logging
import sys
import sqlite3

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Import Variable constants from config.py
from config import DB_DIR
from config import DB_NAME
from config import DB_TABLE

# Setup variables
DB_PATH = os.path.join(DB_DIR, DB_NAME)
REPORTS_DIR = 'media/reports'
if not os.path.isdir(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

help_msg=('''
     ------------ Report Help ------------
Creates a formatted html report listing from the sqlite3 database
based on vales for speeds gt and days previous.

If No Parameters provided, You will be prompted for Report values

parameter usage

-h Show this Help Page

or specify parameters per
param 1: speed_over integer
param 2: days_prev integer

eg

%s 50 5

Bye ...

''' % sys.argv[0])

if not len(sys.argv) > 1:
    print("----------------- Speed Camera Report ----------------------")
    print("This Report will Display all Database Records with")
    print("specified Speeds Over and specified days previous.\n")
    print("Value Must be Integer 0=all")
    try:
        speed_over = raw_input("Enter speed_over: ")
    except NameError:
        speed_over = input("Enter speed_over: ")
    print("\nValue Must be Integer > 0")
    try:
        days_prev = raw_input("Enter days_prev: ")
    except NameError:
        days_prev = input("Enter days_prev: ")
else:
    # check if first parameter is -h
    if (sys.argv[1]).lower() == '-h':
        print(help_msg)
        sys.exit(0)

    speed_over = sys.argv[1]
    days_prev = sys.argv[2]
try:
    test = int(speed_over)
except ValueError:
    logging.error("%s speed_over Must be Integer. 0=all", speed_over)
    sys.exit(1)
try:
    test = int(days_prev)
except ValueError:
    logging.error("%s days_prev Must be Integer > 0", days_prev)
    sys.exit(1)

REPORT_FILENAME = ("speed_gt" + speed_over + "_prev_" + days_prev + "days.html")
REPORT_PATH = os.path.join(REPORTS_DIR, REPORT_FILENAME)

html_list_query = ('''
select
    substr(log_timestamp, 2, 16) log_date,
    ave_speed,
    speed_units,
    direction,
    image_path
from %s
where
    ave_speed >= %s and
    substr(log_timestamp, 2, 11) >= DATE('now', '-%s days')  and
    substr(log_timestamp, 2, 11) <= DATE('now', '+1 day')
order by
    ave_speed DESC''' % (DB_TABLE, speed_over, days_prev))

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
HTML_HEADER_2 = ('''<center><h3>Speed Camera Report for Previous %s Days and Speeds >= %s  Sort by Speed desc</h3>
                 <h4>Click Image Path to View Image. Use Browser Back Button to Return to This Report</h4>''' %
                 (days_prev, speed_over))
HTML_HEADER_3 = ('''
    <table id="t01">
    <tr>
    <th>timestamp</th>
    <th>Speed</th>
    <th>Direction</th>
    <th>Image Path</th>
    </tr>''')
HTML_HEADER_3C = ('''
    <table id="t01">
    <tr>
    <th>Date</th>
    <th>Hour</th>
    <th>Count/Hr Totals</th>
    </tr>''')
# HTML_HEADER = HTML_HEADER_1 + HTML_HEADER_2 + HTML_HEADER_3
HTML_FOOTER = "</table><center>End of Report</center></body></html>"

#------------------------------------------------------------------------------
def make_html_report_list():
    logging.info("Working.  Please Wait ...")
    html_table = []   # List to hold html table rows
    start_time = time.time()
    logging.info("Connect to Database %s", DB_PATH)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(html_list_query)
    logging.info("Start Report %s", REPORT_PATH)
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        log_date = (row["log_date"])
        ave_speed = (row["ave_speed"])
        speed_units = (row["speed_units"])
        image_path = (row["image_path"])
        image_filename=os.path.basename(image_path)
        direction = (row["direction"])
        link_path = os.path.join(os.path.relpath(
                        os.path.abspath(os.path.dirname(image_path)),
                        os.path.abspath(REPORTS_DIR)),
                        image_filename)
        table_row = ('<tr><td>%s</td><td>%s %s</td><td>%s</td><td><a href="../%s">%s</a></td></tr>' %
                    (log_date,
                     ave_speed,
                     speed_units,
                     direction,
                     link_path,
                     image_path))
        html_table.append(table_row)

    connection.close()
    f = open(REPORT_PATH, "w")
    f.write(HTML_HEADER_1)
    f.write(HTML_HEADER_2)
    f.write(HTML_HEADER_3)
    for item in html_table:
        f.write(item)
    f.write(HTML_FOOTER)
    f.close()
    del html_table

if __name__ == '__main__':
    start_time = time.time()
    make_html_report_list()
    duration = time.time() - start_time
    logging.info("Processing Took %.2f s.", duration)
    logging.info("View Reports from Speed Camera Web Page")
    logging.info("At %s", REPORT_PATH)