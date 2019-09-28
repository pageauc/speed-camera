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

prog_ver = "ver 1.2"

import sys
import time
import os
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
DB_FILE = '/home/pi/speed-camera/data/speed_cam.db'
SPEED_DIR = '/home/pi/speed-camera'   # path to speed-camera folder

# System Variables
my_path = os.path.abspath(__file__)  # Find the full path of this python script
# get the path location only (excluding script name)
base_dir = my_path[0:my_path.rfind("/")+1]
base_file_name = my_path[my_path.rfind("/")+1:my_path.rfind(".")]
prog_name = os.path.basename(__file__)
horz_line = "----------------------------------------------------------------------"
print(horz_line)
print("%s %s   written by Claude Pageau" % (prog_name, prog_ver))
print(horz_line)

alpr = Alpr("us", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
if not alpr.is_loaded():
    print('ERROR : Problem loading OpenALPR')
    sys.exit(1)

alpr.set_top_n(3)      # Set max plates expected per image
alpr.set_default_region('on')  # Ontario Canada

# Connect to sqlite3 file database file speed_cam.db
try:
    db_conn = sqlite3.connect(DB_FILE)
except sqlite3.Error as err_msg:
    print("ERROR: Failed sqlite3 Connect to DB %s" % DB_FILE)
    print("       %s" % err_msg)
    sys.exit(1)

# setup cursor for processing db query rows
db_conn.row_factory = sqlite3.Row
cursor = db_conn.cursor()
try:
    while True:
        # run sql query to select unprocessed images from speed_cam.db
        cursor.execute("SELECT idx, image_path FROM speed WHERE status=''")
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            row_index = (row["idx"])
            row_path = (row["image_path"])
            # create full path to image file to process
            image_path = os.path.join(SPEED_DIR, row_path)
            # This may have to be tweaked since image is from a file.
            # Do ALPR processing on selected image
            print('Processing %s' % image_path)
            results = alpr.recognize_file(image_path)

            # Check for plate data in results
            plate_data = 'none'
            for i, plate in enumerate(results['results']):
                best_candidate = plate['candidates'][0]
                # Could add to a database table eg speed_cam.db plate table image_path, plate columns
                plate_data = ('Plate #{}: {:7s} ({:.2f}%)'.format(i, best_candidate['plate'].upper(),
                       best_candidate['confidence']))
                print(plate_data)
            print(plate_data)
            # Set speed_cam.db speed table status field to 'done'
            sql_cmd = '''UPDATE speed SET status="{}" WHERE idx="{}"'''.format(plate_data, row_index)
            db_conn.execute(sql_cmd)
            db_conn.commit()
        print('Waiting 30 seconds')
        time.sleep(30)

except KeyboardInterrupt:
    print("")
    print("User Exited with ctr-c")
finally:
    db_conn.close()
    alpr.unload()

