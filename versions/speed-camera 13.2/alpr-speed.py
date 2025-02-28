#!/usr/bin/env python
"""
This sample script will read speed-cam.py image_path from sqlite3 database entries.
It will then use openalpr to search for license plate numbers.

You will need to configure openalpr to suit your needs eg
country, regions, config, Etc.  As each image is processed the speed_cam.db speed table
status field will be updated to NULL or plate info if found. image is only processed once.

Note
----
When using speed camera for openalpr purposes the speed settings will
most likely not be needed and motion tracking will only be used for triggering
images for license plate capture.  It is suggested you set speed-cam.py config.py
image resolution WIDTH and HEIGHT to 640x480 with image_bigger = 1.0

Example query for licence plate data in the sqlite3 database

   cd ~/speed-camera
   sqlite3 data/speed_cam.db
   SELECT status, image_path FROM speed WHERE status NOT NULL;
   or SELECT status, image_path FROM speed WHERE status LIKE 'Plate%'

ctl-d to exit sqlite3 console
Note query will also display unprocessed images.

Installation
------------
Install openalpr on RPI (stretch/buster) per

    sudo apt-get update
    sudo apt-get install python-openalpr
    sudo apt-get install python3-openalpr
    sudo apt-get install sqlite3

    sudo apt-get install openalpr openalpr-daemon
    sudo apt-get install openalpr-utils libopenalpr-dev

I Also needed to create a symbolic link per below
but this may be due to version that was loaded

sudo ln -s /usr/share/openalpr/runtime_data/ocr/tessdata/lus.traineddata /usr/share/openalpr/runtime_data/ocr/lus.traineddata

See User Variables below to change default settings.

Still a work in progress
Good Luck Claude ....
"""
from __future__ import print_function
import sys
import os
import time

try:
    import sqlite3
except ImportError:
    print("ERROR: Problem importing sqlite3. Try Installing per")
    print("       sudo apt-get install sqlite3")
    sys.exit(1)

try:
    from openalpr import Alpr
except ImportError:
    print("ERROR : Problem importing openalpr. Try Installing per")
    print("        sudo apt-get install python-openalpr")
    print("        sudo apt-get install python3-openalpr")
    print("        sudo apt-get install openalpr")
    print("        sudo apt-get install openalpr-daemon")
    print("        sudo apt-get install openalpr-utils libopenalpr-dev")
    sys.exit(1)

PROG_VER = "ver 1.76"

#=================
# User Variables
#=================
VERBOSE_ON = True
DB_FILE = '/home/pi/speed-camera/data/speed_cam.db' # path to speed cam database
SPEED_DIR = '/home/pi/speed-camera'   # path to speed-camera folder
WAIT_SECS = 30  # seconds to wait between queries for images to process

ALPR_COUNTRY = "us"   # Country Code eg 'us', 'eu' See ALPR Docs
ALPR_REGION = "on"   # State/province Etc  See ALPR Docs
ALPR_TOP_N = 3        # Max Number of plates to search per image

# File path to ALPR configuration file per ALPR docs
ALPR_CONF_PATH = "/etc/openalpr/openalpr.conf"
# Directory path to ALPR runtime_data per ALPR docs
ALPR_RUNTIME_DATA_PATH = "/usr/share/openalpr/runtime_data"

#=================
# System Variables
#=================
# Find the full path of this python script
MY_PATH = os.path.abspath(__file__)
# get the path location only (excluding script name)
BASE_DIR = MY_PATH[0:MY_PATH.rfind("/")+1]
# BASE_FILE_NAME is This script name without extension
BASE_FILE_NAME = MY_PATH[MY_PATH.rfind("/")+1:MY_PATH.rfind(".")]
PROG_NAME = os.path.basename(__file__)

HORZ_LINE = "----------------------------------------------------------------------"
if VERBOSE_ON:
    print(HORZ_LINE)
    print("%s %s   written by Claude Pageau" % (PROG_NAME, PROG_VER))
    print("ALPR license plate search speed_cam.py Images")
    print(HORZ_LINE)
    print("Loading   Wait ...")

ALPR = Alpr(ALPR_COUNTRY, ALPR_CONF_PATH, ALPR_RUNTIME_DATA_PATH)
if not ALPR.is_loaded():
    print('ERROR : Problem loading OpenALPR')
    sys.exit(1)

ALPR.set_top_n(ALPR_TOP_N)      # max plates expected per image
ALPR.set_default_region(ALPR_REGION)  # State/Prov Etc per ALPR docs

try:
    RETRY = 0
    while True:
        try:
            # Connect to sqlite3 database file
            DB_CONN = sqlite3.connect(DB_FILE)
        except sqlite3.Error as err_msg:
            print("ERROR: Failed sqlite3 Connect to DB %s"
                  % DB_FILE)
            print("       %s" % err_msg)
            RETRY += 1
            if RETRY <= 5:
                print('DB_CONN RETRY %i/5  Wait ...' % RETRY)
                time.sleep(5)
                continue  # loop
            else:
                sys.exit(1)

        # setup CURSOR for processing db query rows
        CURSOR = DB_CONN.cursor()
        CURSOR.execute("SELECT idx, image_path FROM speed WHERE status=''")
        ALL_ROWS = CURSOR.fetchall()
        DB_CONN.close() # Close DB to minimize db lock issues
        ROW_TOTAL = len(ALL_ROWS)  # Get total Rows to Process
        ROW_MSG = "%i Rows Found to Process." % ROW_TOTAL
        ROW_COUNTER = 0
        PLATES_DONE = 0
        for row in ALL_ROWS:
            ROW_INDEX = row[0] # get image idx from speed table
            ROW_PATH = row[1]  # get image_path from speed table
            ROW_COUNTER += 1
            # create full path to image file to process
            IMAGE_PATH = os.path.join(SPEED_DIR, ROW_PATH)
            # Do ALPR processing on selected image
            RESULTS = ALPR.recognize_file(IMAGE_PATH)
            PLATE_DATA = 'Plate: '
            FOUND_PLATE = False
            for i, plate in enumerate(RESULTS['results']):
                FOUND_PLATE = True
                best_candidate = plate['candidates'][0]
                ROW_DATA = ('{:7s} ({:.2f}%) '.format
                            (best_candidate['plate'].upper(),
                             best_candidate['confidence']))
                PLATE_DATA = PLATE_DATA + ROW_DATA
                PLATES_DONE += 1

            # UPDATE speed_cam.db speed, status column with PLATE_DATA or NULL
            try:
                DB_CONN = sqlite3.connect(DB_FILE)
                if FOUND_PLATE:
                    if VERBOSE_ON:
                        print("%i/%i SQLITE Add %s to %s" %
                              (ROW_COUNTER, ROW_TOTAL,
                               PLATE_DATA, IMAGE_PATH))
                    SQL_CMD = ('''UPDATE speed SET status="{}" WHERE idx="{}"'''
                               .format(PLATE_DATA, ROW_INDEX))
                else:
                    if VERBOSE_ON:
                        print("%i/%i No Plate %s" %
                              (ROW_COUNTER, ROW_TOTAL, IMAGE_PATH))
                    # set speed table status field to NULL
                    SQL_CMD = ('''UPDATE speed SET status=NULL WHERE idx="{}"'''
                               .format(ROW_INDEX))
                DB_CONN.execute(SQL_CMD)
                DB_CONN.commit()
                DB_CONN.close()
            except sqlite3.OperationalError:
                print("SQLITE3 DB Lock Problem Encountered.")
            ROW_MSG = "Found %i Plates" % PLATES_DONE
        if VERBOSE_ON:
            print('%s  Wait %is ...' % (ROW_MSG, WAIT_SECS))
        time.sleep(WAIT_SECS)

except KeyboardInterrupt:
    print("")
    print("%s %s User Exited with ctr-c" %(PROG_NAME, PROG_VER))
finally:
    print("DB_CONN.close %s" % DB_FILE)
    DB_CONN.close()
    print("ALPR.unload")
    ALPR.unload()
    print("%s %s  Bye ..." % (PROG_NAME, PROG_VER))
