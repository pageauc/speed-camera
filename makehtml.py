#!/usr/bin/env python

# makehtml.py written by Claude Pageau
# Create html pages from csv log file entries
# for viewing speed images and data on a web server

progVer = "6.70"

import glob
import os
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
verbose = True
image_ext = ".jpg"
source_csv = "speed-cam.csv"
web_html_dir = "media/html"  # Dir path to html files
web_image_dir = "media/images/"   # Dir path of images
# contour width to height ratio
guess_person = .73
guess_cart = 1.1
# End of Variable Settings

if not os.path.isdir(web_html_dir):
    print("Creating html Folder %s" % web_html_dir)
    os.makedirs(web_html_dir)

#------------------------------------------------------------------------------
def make_web_page(up_html, row_data, dn_html):
    YYYYMMDD=row_data[0]
    HH=row_data[1]
    MM=row_data[2]
    Speed=row_data[3]
    Unit=row_data[4]
    img_path=row_data[5]
    img_filename=os.path.basename(img_path)
    img_html_path = os.path.join(os.path.relpath(
                    os.path.abspath(os.path.dirname(img_path)),
                    os.path.abspath(web_html_dir)),
                    img_filename)
    X=row_data[6]
    Y=row_data[7]
    W=row_data[8]
    H=row_data[9]
    aspect_ratio = float(W)/int(H)
    if aspect_ratio < guess_person:
        Guess = "Person Walking"
    elif aspect_ratio < guess_cart:
        Guess = "Person on Bike or Golf Cart"
    else:
        Guess = "Vehicle"
    Area=row_data[10]

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
    web_html_path = os.path.join(web_html_dir, base_filename + '.html')

    if os.path.isfile(img_path):
        f = open(web_html_path, "w")
        f.write(pageTemplate)
        f.close()
        # Sync file stat dates of html with jpg file
        shutil.copystat(img_path, web_html_path)
        if verbose:
            print("Saved %s<- %s ->%s" % (dn_html, web_html_path , up_html))
    else:
        if os.path.isfile(web_html_path):
            if verbose:
                print("Remove File %s" % web_html_path)
            os.remove(web_html_path)

#------------------------------------------------------------------------------
def check_row(row_data):
    found = False
    web_html_path = ""
    img_path = row_data[5]
    if os.path.isfile(img_path):
        base_filename = os.path.splitext(os.path.basename(img_path))[0]
        web_html_path = base_filename+'.html'
        found = True
    return found, web_html_path

#------------------------------------------------------------------------------
def read_from_csv(filename):
    this_is_first_row = True
    this_is_third_row = True
    cur_link = ""
    next_link = ""
    new_link = ""
    second_row = []
    next_row = []
    cur_row  = []
    prev_row = []

    f = open(filename, 'rt')
    cnt=0
    workStart = time.time()
    workCount = 0
    try:
        reader = csv.reader(f)
        for row in reader:
            workCount += 1
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
        outDir = os.path.abspath(web_html_dir)
        print("-----------------")
        print("%s ver %s - written by Claude Pageau" % (progName, progVer))
        print("Processed %i web pages in %i seconds into Folder %s" %
              (workCount, workEnd - workStart, outDir))
        print("Done ...")
read_from_csv(source_csv)
