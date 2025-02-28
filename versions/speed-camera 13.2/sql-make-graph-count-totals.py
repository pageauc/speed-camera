#!/usr/bin/env python
'''
written by Claude Pageau
Speed Camera Utility to create graph image files from
the sqlite3 database data/speed_cam.db using matplotlib.

'''
from __future__ import print_function
prog_ver = '13.02'
DEBUG = False
print('Loading ver %s DEBUG= %s ... ' % (prog_ver, DEBUG))
import sqlite3
import os
import time
import datetime as dt
import sys
try:
    import matplotlib
except ImportError:
    print('''
    matplotlib import failed.
    To install run the following commands

    sudo apt update
    sudo apt upgrade
    sudo apt install python-matplotlib python3-matplotlib

    Note these installs will take some time ...
    ''')
    sys.exit(1)
matplotlib.use('Agg')  # Allow graphs to be created without display eg SSH
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger('matplotlib.font_manager').disabled = True
# Import Variable constants from config.py
from config import DB_DIR
from config import DB_NAME
from config import DB_TABLE
from config import MO_SPEED_MPH_ON
from config import GRAPH_PATH
from config import GRAPH_ADD_DATE_TO_FILENAME   # Prefix graph image filename with datetime for uniqueness.
from config import GRAPH_RUN_TIMER_HOURS
from config import GRAPH_RUN_LIST

if not os.path.exists(GRAPH_PATH):  # Check if grpahs directory exists
    os.makedirs(GRAPH_PATH)         # make directory if Not Found

# Create help Message Strings

help_msg_title = ('''
This program will query the speed camera sqlite3 database per config.py settings or command line parameters.
It will then generate matplotlib graph images per selection and grouping values.

Command Line parameters
-----------------------
Selects Records per -s speed over, -d days previous and groups counts by  -t totals eg hour, day, month
matplotlib will then create jpg graph images to auto created filenames.  You can add optional datetime prefix by
setting config.py GRAPH_ADD_DATE_TO_FILENAME boolean variable. Default is False (overwrites previous existing filenames)

Graph will show record count totals for specified speeds over and days previous
totaled by log_timestamp Grouping eg hour, day, month.

No Command Line Parameters
--------------------------
If NO command line parameters are supplied then multiple graphs can be created per the speed camera config.py
GRAPH_RUN_DATA list variable.  This can generate multiple graph image files per specified list data criteria.
See config.py comments for required GRAPH_RUN_DATA list values.

''')

help_msg = ('''
NOTE:
Run a single graph by passing parameters to this script. For details See

    %s -h

or Create Multiple Graphs from config.py

To Edit/Add/Remove Graph Images.
Edit config.py GRAPH_RUN_LIST variable under matplotlib settings.

Graph Images can be viewed from Speed Camera Web Page at %s
''' % (sys.argv[0], GRAPH_PATH))

if len(sys.argv) > 1:
    import argparse
    ap = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=help_msg_title)

    ap.add_argument('-s', required=True, type=int, action='store', dest='speed',
        help='speed over- Integer - Selects Database Records with Speeds >= specified Value')

    ap.add_argument('-d', required=True, type=int, action='store', dest='days',
        help='days prev - Integer - Selects Database Records where log_timestamp is between now and specified number of days previous')

    ap.add_argument('-t', required=True, action='store', dest='totals',
        help='total by  - String  - Groups Count Totals by specified string. Valid Strings are: hour day month')

    args = ap.parse_args()
    if args.totals not in ['hour', 'day', 'month']:
        print('-t option must be a valid string value: hour, day or month')
        sys.exit(1)

    speed_over = args.speed
    days_prev = args.days
    total_by = args.totals

#----------------------------------------------------------------------------------------
def is_int(var):
    ''' Check if variable string can successfully be converted to an integer.
    '''
    try:
        int(var)
    except ValueError:
        return False
    return True

#----------------------------------------------------------------------------------------
def get_timestamp_substr(total_by):
    '''
    Convert hour, day or month string to required
    values for changing the log_timestamp to an appropriate
    substring value.
    '''
    total_by = total_by.upper()
    if total_by == 'HOUR':
        timestamp_subst = '2, 13'
    elif total_by == 'DAY':
        timestamp_subst = '2, 10'
    elif total_by == 'MONTH':
        timestamp_subst = '2, 7'
    else:
        logging.info("total_by variable must be string. Valid values are hour, day, month")
        logging.warning("Defaulting to hour")
        timestamp_subst = '2, 13'
    return timestamp_subst

#----------------------------------------------------------------------------------------
def get_speed_units_str():
    '''
    Convert config.py MO_SPEED_MPH_ON boolean to a string.
    '''
    speed_unit = 'kph'
    if MO_SPEED_MPH_ON:
        speed_unit  = 'mph'
    return speed_unit

#----------------------------------------------------------------------------------------
def get_query_str(total_by, days_prev, speed_over):
    ''' Create Sqlite3 Query to Get Totals for specified days previous and speeds over
    '''
    timestamp_subst = get_timestamp_substr(total_by)
    sql_query_by_count = ('''
    select
        substr(log_timestamp, %s) log_date,
        count(*) count_totals
    from %s
    where
        ave_speed >= %s and
        substr(log_timestamp, 2, 11) >= DATE('now', '-%i days')  and
        substr(log_timestamp, 2, 11) <= DATE('now', '+1 day')
    group by
        log_date
    ''' % (timestamp_subst, DB_TABLE, speed_over, int(days_prev)))

    return sql_query_by_count

#----------------------------------------------------------------------------------------
def make_graph_image(total_by, days_prev, speed_over):
    ''' Extract Data from sql db and generate matplotlib graph showing totals for specified
        hour, day, month
    '''

    if not (is_int(days_prev) and is_int(speed_over)):
        logging.error("days_prev and speed_over must be integer >= 0")
        return

    days_prev = abs(days_prev)  # Make sure they are positive
    speed_over = abs(speed_over)
    speed_units = get_speed_units_str()
    total_by = total_by.upper()
    db_path = os.path.join(DB_DIR, DB_NAME)
    count_sql_query = get_query_str(total_by, days_prev, speed_over)
    right_now = dt.datetime.now()
    now = ("%02d-%02d-%02d-%02d:%02d" % (right_now.year,
                                         right_now.month,
                                         right_now.day,
                                         right_now.hour,
                                         right_now.minute))
    if GRAPH_ADD_DATE_TO_FILENAME:
        file_now = now + '_'     # prefix file name with datetime
    else:
        file_now = ''   # No Datetime on filename
    image_filepath = os.path.join(GRAPH_PATH,
                                  file_now +
                                  'graph_count_' +
                                  'prev' + str(days_prev) +
                                  'days_by' + total_by.lower() +
                                  '_ge' + str(speed_over)+ speed_units +
                                  '.jpg')

    graph_title = ('Previous %s days COUNT by %s for SPEEDS >= %s %s\n%s' %
                   (str(days_prev), total_by, str(speed_over), speed_units, now))
    if DEBUG:
        logging.info("Running: %s", graph_title)
        logging.info("Connect to Database %s", db_path)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    if DEBUG:
        logging.info('Executing Query \n %s', count_sql_query)
    cursor.execute(count_sql_query)
    xd = []   # list for database query date data
    y = []    # list for database query count data
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        if DEBUG:
            print(row)
        xdat, ydat = row
        # Create x,y data lists for matplotlib plt
        if total_by == 'HOUR':
            xd.append(dt.datetime.strptime(xdat, '%Y-%m-%d %H'))
        elif total_by == 'DAY':
            xd.append(dt.datetime.strptime(xdat, '%Y-%m-%d'))
        elif total_by == 'MONTH':
            xd.append(dt.datetime.strptime(xdat, '%Y-%m'))
        y.append(ydat)
    cursor.close()
    connection.close()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gcf().autofmt_xdate()

    plt.figure(figsize=(10.0, 7.0), dpi=100)
    plt.title(graph_title)
    plt.ylabel('COUNT by ' + total_by)
    plt.plot(xd, y)
    plt.xticks(rotation=60)
    plt.tight_layout()
    plt.savefig(image_filepath)
    logging.info('Saved - %s', image_filepath)
    return image_filepath

#----------------------------------------------------------------------------------------
def graph_from_list():
    ''' Generate multiple graph images from config.py GRAPH_RUN_LIST Variable
    '''
    run_cntr = 0
    total_graphs = len(GRAPH_RUN_LIST)
    logging.info("--- Start Generating %i Graph Images from config.py GRAPH_RUN_LIST Variable", total_graphs)
    start_time = time.time() # Start timer for processing duration
    for graph_data in GRAPH_RUN_LIST:
        run_cntr +=1
        total_by = graph_data[0]
        days_prev = graph_data[1]
        speed_over = graph_data[2]
        logging.info("%i of %i - prev %i days, count by %s, speed over %i %s)",
                      run_cntr, total_graphs, days_prev, total_by.upper(), speed_over, get_speed_units_str())
        make_graph_image(total_by, days_prev, speed_over)
    duration = time.time() - start_time
    logging.info("--- Finish. Processing Took %.2f seconds", duration)

if __name__ == '__main__':

    try:
        if len(sys.argv) > 1:
            make_graph_image(total_by, days_prev, speed_over)
        else:
            if GRAPH_RUN_TIMER_HOURS > 0.0:
                while True:
                    graph_from_list()
                    logging.warning('Looping Timer Set per config.py GRAPH_RUN_TIMER_HOURS = %.2f', GRAPH_RUN_TIMER_HOURS)
                    logging.info('Next Run is in %.2f hours', GRAPH_RUN_TIMER_HOURS)
                    print('Waiting ... Ctr-C to Exit')
                    time.sleep(GRAPH_RUN_TIMER_HOURS * 3600)
            else:
                graph_from_list()
    except KeyboardInterrupt:
        print("\nUser Pressed Keyboard Ctrl-C to Exit")
    print(help_msg)
    print('Ver %s Bye ....' % prog_ver)

