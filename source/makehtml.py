#!/usr/bin/env python

# makehtml.py written by Claude Pageau
# Create linked html pages from csv log file entries
# for easier viewing speed camera images and data on a web server

from __future__ import print_function
progVer = "11.08"
print('Loading ...')
import glob
import os
import sys
import csv
import time
import datetime
import shutil

# Find the full path of this python script
progName = os.path.abspath(__file__)
# get the path location only (excluding script name)
baseDir = os.path.dirname(progName)
# Change to Folder that this script is run from
os.chdir(baseDir)

# User Variable Settings for this script
# --------------------------------------

VERBOSE = True  # produce addition log information
HTML_MAX_FILES = 100  # Default= 100 Set mazimum html files to create 0=All
DELETE_PREVIOUS_HTML = True
SOURCE_CSV_PATH = "./speed-cam.csv"  # location of the speed camera csv file
WEB_HTML_DIR = "media/html"  # Dir path to html folder to store html files

# Guess contour width to height ratio.  Added this Just for fun
PERSON_GUESS_RATIO = .73
PERSON_BIKE_RATIO = 1.1

# ------- End of User Variable Settings -------

if not os.path.exists(SOURCE_CSV_PATH):
    print('%s File Does Not Exist.  Please set' % SOURCE_CSV_PATH)
    print('config.py variable log_data_to_CSV = True')
    print('Restart speed-cam.py and allow time to collect data,')
    print('then rerun makehtml.py')
    sys.exit(1)

if not os.path.isdir(WEB_HTML_DIR):
    print("Creating html Folder %s" % WEB_HTML_DIR)
    os.makedirs(WEB_HTML_DIR)

#------------------------------------------------------------------------------
def make_web_page(up_html, row_data, dn_html):
    timestamp=datetime.datetime.strptime(row_data[0], "%Y-%m-%d %H:%M:%S")
    YYYYMMDD=timestamp.strftime("%Y%m%d")
    HH=timestamp.strftime("%H")
    MM=timestamp.strftime("%M")
    Speed=row_data[1]
    Unit=row_data[2]
    img_path=row_data[3]
    img_filename=os.path.basename(img_path)
    img_html_path = os.path.join(os.path.relpath(
                    os.path.abspath(os.path.dirname(img_path)),
                    os.path.abspath(WEB_HTML_DIR)),
                    img_filename)
    X=row_data[4]
    Y=row_data[5]
    W=row_data[6]
    H=row_data[7]
    aspect_ratio = float(W)/int(H)
    if aspect_ratio < PERSON_GUESS_RATIO:
        Guess = "Person Walking"
    elif aspect_ratio < PERSON_BIKE_RATIO:
        Guess = "Person on Bike or Golf Cart"
    else:
        Guess = "Vehicle"
    Area=int(W)*int(H)

    pageTemplate = ('''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <html>
    <head>
    <meta "Content-Type" content="txt/html; charset=ISO-8859-1" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    </head><html>
    <title>Speed Camera by Claude Pageau</title>
    <body>
    <table style="border-spacing: 15px;" cellspacing="10">
    <tr>
        <td>
          <span style="float: left">
          <a href="%s" target="_blank" ><img src="%s" width="640" height="480"  hspace="20" ALIGN="left" alt="Speed Image"/></a>
          </span>
          <span style="float: right">
          <div>
            <h4><center>Object Motion Speed Tracker</center></h4>
            <h2><center>Speed Camera Data</center></h2>
            <hr>
            <h3>Taken: %s at %s:%s</h3>
            <h3>Speed: %s %s</h3>
            <h3>Contour: %s x %s = %s sq px</h3>
            <h3>Aspect Ratio: %.3f w/h</h3>
            <h3>Guess: %s</h3>
            <hr>
            <center>
              <h4><a href="%s" target="_blank" >%s</a></h4>
              <h1>
                <a href="%s" style="text-decoration:none;" >UP</a>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <a href="%s" style="text-decoration:none";>DOWN</a>
              </h1>
              Click image to enlarge in new browser tab
            </center>
          </div>
          </span>
        </td>
    </tr>
    </table>
    </body>
    </html>''' % (img_html_path, img_html_path,
                  YYYYMMDD, HH, MM, Speed, Unit,
                  W, H, Area, aspect_ratio,
                  Guess, img_html_path,
                  img_filename, dn_html, up_html))
    # Write the html file
    base_filename = os.path.splitext(os.path.basename(img_path))[0]
    web_html_path = os.path.join(WEB_HTML_DIR, base_filename + '.html')

    if os.path.isfile(img_path):
        f = open(web_html_path, "w")
        f.write(pageTemplate)
        f.close()
        # Sync file stat dates of html with jpg file
        shutil.copystat(img_path, web_html_path)
        if VERBOSE:
            print("Saved %s<- %s ->%s" % (dn_html, web_html_path , up_html))
    else:
        if os.path.isfile(web_html_path):
            if VERBOSE:
                print("Remove File %s" % web_html_path)
            os.remove(web_html_path)

#------------------------------------------------------------------------------
def check_row(row_data):
    found = False
    web_html_path = ""
    img_path = row_data[3]
    if os.path.isfile(img_path):
        base_filename = os.path.splitext(os.path.basename(img_path))[0]
        web_html_path = base_filename + '.html'
        found = True
    return found, web_html_path

#------------------------------------------------------------------------------
def csv_line_count(filename):
    with open(filename) as f:
        return sum(1 for line in f)

#------------------------------------------------------------------------------
def file_last_mod_datetime(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

#------------------------------------------------------------------------------
def read_from_csv(filename):
    csv_last_mod_time = file_last_mod_datetime(filename)
    this_is_first_row = True
    this_is_third_row = True
    cur_link = ""
    next_link = ""
    new_link = ""
    second_row = []
    next_row = []
    cur_row  = []
    prev_row = []

    if DELETE_PREVIOUS_HTML:
        print('Remove html files in %s since DELETE_PREVIOUS_HTML = %s' %
              (WEB_HTML_DIR, DELETE_PREVIOUS_HTML))
        html_dir_list = glob.glob(WEB_HTML_DIR + "/*html")
        for file in html_dir_list:
            os.remove(file)

    csv_rows = csv_line_count(filename)
    print('csv file %s contains %i rows' % (filename, csv_rows))
    skip_rows = 0
    if csv_rows > HTML_MAX_FILES and not HTML_MAX_FILES == 0:
        skip_rows = csv_rows - HTML_MAX_FILES
        print('Skipping %s rows in %s since HTML_MAX_FILES = %i' %
              (skip_rows, filename, HTML_MAX_FILES))
    f = open(filename, 'rt')
    cnt=0
    workStart = time.time()
    workCount = 0
    try:
        reader = csv.reader(f)
        for row in reader:
            workCount += 1
            if workCount <= skip_rows:
                continue
            if not next_row:
                jpg_exists, next_link = check_row(row)
                if jpg_exists:
                    next_row = row
                    first_row = row
                    first_link = next_link
            elif not cur_row:
                jpg_exists, cur_link = check_row(row)
                if jpg_exists:
                    cur_row = row
                    second_row = row
                    second_link = cur_link
            else:
                jpg_exists, new_link = check_row(row)
                if jpg_exists:
                    temp_link = new_link
                    prev_row = cur_row
                    prev_link = cur_link
                    cur_row = next_row
                    cur_link = next_link
                    next_row = row
                    save_next_link = next_link
                    next_link = new_link
                    if this_is_first_row:
                        make_web_page(first_link, first_row, second_link)
                        make_web_page(first_link, second_row, temp_link)
                        this_is_first_row = False
                    else:
                        if this_is_third_row:
                            make_web_page(second_link, cur_row, next_link)
                            this_is_third_row = False
                        else:
                            make_web_page(prev_link, cur_row, next_link)
        make_web_page(cur_link, next_row, next_link)

    finally:
        f.close()
        workEnd = time.time()
        outDir = os.path.abspath(WEB_HTML_DIR)
        print("-----------------")
        print("%s ver %s - written by Claude Pageau" % (progName, progVer))
        print('Process speed camera csv file and create linked html files')
        print('for the most recent CSV entries if HTML_MAX_FILES > 0')
        print("%s last modified on %s\n" % (filename, csv_last_mod_time))
        print('HTML_MAX_FILES= %i  DELETE_PREVIOUS_HTML= %s' %
              (HTML_MAX_FILES, DELETE_PREVIOUS_HTML ))
        print("Processed %i web pages in %.2f seconds into Folder %s" %
              (workCount-skip_rows, workEnd - workStart, outDir))
        print("Done ...")

# Start program
read_from_csv(SOURCE_CSV_PATH)
