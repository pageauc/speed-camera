#!/usr/bin/env python
"""
This sample script will read speed-cam.py images from sqlite3 database entries.
It will then use openalpr to search for license plate numbers.

You will need to configure openalpr to suit your needs eg
country and regions Etc.  As each image is processed the speed_cam.db speed table
status field will be updated to 'none' or plate infor. image is only processed once.

Note
----
When using speed camera for openalpr purposes the speed settings will
most likely not be needed and motion tracking will only be used for triggering
image for license plate capture.  It is suggested you set speed-cam.py config.py
image resolution WIDTH and HEIGHT to 640x480 with image_bigger = 1.0

This script will only print out the license plates info so you will need to modify
code to save results to a sqlite database table, csv or other file.

Good Luck Claude ....

Installation
------------
I installed openalpr on RPI's per

    sudo apt-get install python-openalpr
    sudo apt-get install openalpr install openalpr-daemon
    sudo apt-get openalpr-utils libopenalpr-dev

    sudo apt-get install sqlite3

I Also needed to create symbolic link per below but this may be due to version that was loaded

sudo ln -s /usr/share/openalpr/runtime_data/ocr/tessdata/lus.traineddata /usr/share/openalpr/runtime_data/ocr/lus.traineddata

"""
from __future__ import print_function
import sys
import os
import time
try:
    from openalpr import Alpr
except ImportError:
    print("ERROR : Problem loading openalpr.  Try Installing per")
    print("        sudo apt-get install python-openalpr")
    print("        sudo apt-get install openalpr")
    print("        sudo apt-get install openalpr-daemon")
    print("        sudo apt-get install openalpr-utils libopenalpr-dev")
    sys.exit(1)

try:
    import sqlite3
except ImportError:
    print("ERROR: Problem loading sqlite3. Try Installing per")
    print("       sudo apt-get install sqlite3")
    sys.exit(1)

# User Variables
# --------------
PROG_VER = "ver 1.5"

VERBOSE_ON = True
DB_FILE = '/home/pi/speed-camera/data/speed_cam.db'
SPEED_DIR = '/home/pi/speed-camera'   # path to speed-camera folder
WAIT_SECS = 30  # seconds to wait between queries for images to process

# System Variables
# ----------------
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
    print(HORZ_LINE)
    print("Connecting to %s  Wait ..." % DB_FILE)

ALPR = Alpr("us", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
if not ALPR.is_loaded():
    print('ERROR : Problem loading OpenALPR')
    sys.exit(1)

ALPR.set_top_n(3)      # Set max plates expected per image
ALPR.set_default_region('on')  # Ontario Canada

# Connect to sqlite3 file database file speed_cam.db
try:
    DB_CONN = sqlite3.connect(DB_FILE)
except sqlite3.Error as err_msg:
    print("ERROR: Failed sqlite3 Connect to DB %s" % DB_FILE)
    print("       %s" % err_msg)
    sys.exit(1)

# setup CURSOR for processing db query rows
DB_CONN.row_factory = sqlite3.Row
CURSOR = DB_CONN.cursor()
try:
    while True:
        NO_DATA = ""
        # run sql query to select unprocessed images from speed_cam.db
        ROW_TOTAL = CURSOR.execute("SELECT COUNT(*) FROM speed WHERE status=''").fetchone()[0]
        CURSOR.execute("SELECT idx, image_path FROM speed WHERE status=''")
        ROW_COUNTER = 0
        while True:
            ROW = CURSOR.fetchone()
            if ROW is None:
                NO_DATA = "No Data to Process"
                break
            ROW_COUNTER += 1
            ROW_INDEX = (ROW["idx"])
            ROW_PATH = (ROW["image_path"])
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

            # update speed_cam.db speed, status column with 'none' or plate info
            if FOUND_PLATE:
                if VERBOSE_ON:
                    print("%i/%i SQLITE Add %s to %s" %
                          (ROW_COUNTER, ROW_TOTAL, PLATE_DATA, IMAGE_PATH))
                SQL_CMD = ('''UPDATE speed SET status="{}" WHERE idx="{}"'''
                           .format(PLATE_DATA, ROW_INDEX))
                DB_CONN.execute(SQL_CMD)
                DB_CONN.commit()
            else:
                if VERBOSE_ON:
                    print("%i/%i No Plate %s" %
                          (ROW_COUNTER, ROW_TOTAL, IMAGE_PATH))
                # set speed table status field to NULL
                SQL_CMD = ('''UPDATE speed SET status=NULL WHERE idx="{}"'''
                           .format(ROW_INDEX))
                DB_CONN.execute(SQL_CMD)
                DB_CONN.commit()
        if VERBOSE_ON:
            print('%s  Wait %is ...' % (NO_DATA, WAIT_SECS))
            time.sleep(WAIT_SECS)

except KeyboardInterrupt:
    print("")
    print("%s %s User Exited with ctr-c" %(PROG_NAME, PROG_VER))
finally:
    print("DB_CONN.close %s" % DB_FILE)
    DB_CONN.close()
    print("ALRP.unload")
    ALPR.unload()
    print("Bye ...")
