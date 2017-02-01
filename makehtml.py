#!/usr/bin/env python

# makehtml.py written by Claude Pageau
# Create html pages from csv log file entries
# for viewing speed images and data on a web server

ver = "3.00"

import glob, os
import csv
import time
import datetime
import shutil

verbose = True

source_csv = "speed-cam.csv"
web_root_dir = "html"
web_root_image_dir = "images"
image_ext = ".jpg"

# contour width to height ratio
guess_person = .55
guess_cart = 1.1 

#-----------------------------------------------------------------------------------------------

def make_web_page(up_html, row_data, dn_html):
    YYYYMMDD=row_data[0]
    HH=row_data[1]
    MM=row_data[2]
    Speed=row_data[3]
    Unit=row_data[4]
    img_path=row_data[5]
    W=row_data[6]
    H=row_data[7]
    aspect_ratio = float(W)/int(H)
    if (aspect_ratio < .73) :
        Guess = "Person Walking"
    elif ( aspect_ratio < 1.1 ) :
        Guess = "Golf Cart or Person on Bike"
    else:
        Guess = "Vehicle"
    Area=row_data[8]
    
    pageTemplate = ('''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <html>
    <head>
    <meta "Content-Type" content="txt/html; charset=ISO-8859-1" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    </head><html>
    <title>Web Title</title>
    <body>
    <table style="border-spacing: 15px;" cellspacing="10">
    <tr>
    <td>
      <a href="%s" alt="Previous Speed Record" >UP</a>  
      <img src="%s" width="640" height="480" alt="Speed Image" >
      <a href="%s" alt="Next Speed Record" >DN</a>         
    </td>      
      <td valign="top" align="center">
        <h1>Speed Camera Data</h1>
        OpenCV Motion Tracking         
        <hr>
        <h3>Taken on %s at %s:%s</h3>
        <h3>Speed was %s %s</h3>
        <h4>Image %s</h4>
        <h4>Size w = %s x h = %s px  Area %s sq px</h4>
        <h3>Aspect Ratio w/h = %.3f</h3>
        <h3>Guess</h3>
        <h3>%s</h3>
      </td>
    </tr>
    </table>
    </body>
    </html>''' % ( dn_html ,img_path , up_html, YYYYMMDD, HH, MM, Speed, Unit, 
                  img_path, W, H, Area, aspect_ratio, Guess))

    # Write the html file
    base_filename = os.path.splitext(os.path.basename(img_path))[0]
    web_html_path = os.path.join(web_root_dir, base_filename+'.html')

    if os.path.isfile(img_path):
        f = open(web_html_path, "w")
        f.write(pageTemplate)
        f.close()
        # Sync file stat dates of html with jpg file
        shutil.copystat(img_path, web_html_path)
        if verbose:
            print("Saved  %s<- %s ->%s" % ( dn_html, web_html_path , up_html ))
    else:
        if os.path.isfile(web_html_path):
            if verbose:
                print("Remove File %s" % web_html_path)
            os.remove(web_html_path)

def check_row(row_data):
    found = False
    web_html_path = ""
    img_path = row_data[5]
    if os.path.isfile(img_path):
        base_filename = os.path.splitext(os.path.basename(img_path))[0]
        web_html_path = base_filename+'.html'
        found = True
    return found, web_html_path

def read_from_csv(filename):
    this_is_first_row = True
    this_is_third_row = True
    second_row = []
    next_row = []
    cur_row  = []
    prev_row = []

    f = open(filename, 'rt')
    cnt=0
    try:
        reader = csv.reader(f)
        for row in reader: 
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

read_from_csv(source_csv)

