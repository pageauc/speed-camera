#!/usr/bin/env python

ver = "version 5.20"  # Original issue on 26-Jul-2017 by Claude Pageau

"""
speed-search.py written by Claude Pageau pageauc@gmail.com
Raspberry (Pi) - python opencv2 find images matching search image using cv2 template matching
GitHub Repo here https://github.com/pageauc/rpi-speed-camera/tree/master/

This is program works in conjunction with speed-cam.py data output images and csv file.
It needs a speed camera csv file and related images.  To initiate a search make sure
there is sufficient images (suggest > 100).  Find a single speed image that you want
to find matches for.  Copy this image into the search folder (default media/search)
Start speed-search.py

    cd ~/rpi-speed-camera
    ./speed-search.py
    
If config.py variable copy_results_on = True then copies of the matching image files 
will be put in a subfolder named the same as the search image filename minus the extension.
The search file will be copied to the subfolder as well.
If copy_results = False then no copying will take place.  This can be used for testing
various config.py search_value settings.  higher will get more results lower more results
This setting is used to determine how close the original image matches other speed images.
Note Only the cropped rectangle area is used for this search.

This is still under development.  If you have suggestions or issues post a GitHub issue
to the Repo.  The search will generate false positives but can reduce the amount of 
searching if you are looking for a specific image match. I have not implemented logging
results at this time.  Also the code still needs more work but thought it was
good enough to release.
 
Claude  ...   

"""
print("Loading  Please Wait .....")
import time
import cv2
import csv
import glob
import shutil
import os

# Create some system variables
mypath=os.path.abspath(__file__)       # Find the full path of this python script
baseDir=mypath[0:mypath.rfind("/")+1]  # get the path location only (excluding script name)
baseFileName=mypath[mypath.rfind("/")+1:mypath.rfind(".")]
progName = os.path.basename(__file__)  # Get name of this script with no path

configFilePath = baseDir + "config.py"
if not os.path.exists(configFilePath):  # check if config.py file exist if not wget github copy
    print("ERROR - Missing config.py file - Could not find Configuration file %s" % (configFilePath))
    import urllib2
    config_url = "https://raw.github.com/pageauc/rpi-speed-camera/master/config.py"
    print("   Attempting to Download config.py file from %s" % ( config_url ))
    try:
        wgetfile = urllib2.urlopen(config_url)
    except:
        print("ERROR: Download of config.py Failed")
        print("   Try Rerunning the speed-install.sh Again.")
        print("   or")
        print("   Perform GitHub curl install per Readme.md")
        print("   and Try Again")
        print("Exiting %s" % ( progName ))
        quit()
    f = open('config.py','wb')
    f.write(wgetfile.read())
    f.close()
from config import *  # Read Configuration variables from config.py file

# Initialize size of rectangle to crop for search matches
sw = 100 * image_bigger  # default search rectangle Width
sh = 45 * image_bigger  # default search rectangle height
crop_x_L = (x_left + 10) * image_bigger
crop_x_R = (x_right - 10) * image_bigger
crop_y_U = (y_upper + 10) * image_bigger
crop_y_D = (y_lower - 10) * image_bigger

#-----------------------------------------------------------------------------------------------
def check_image_match(full_image, small_image):
    # Look for small_image in full_image and return best and worst results
    # Try other MATCH_METHOD settings per config.py comments
    # For More Info See http://docs.opencv.org/3.1.0/d4/dc6/tutorial_py_template_matching.html
    result = cv2.matchTemplate( full_image, small_image, MATCH_METHOD)
    # Process result to return probabilities and Location of best and worst image match
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)  # find search rect match in new image
    return maxVal

#-----------------------------------------------------------------------------------------------
def get_search_rect(search_filepath):
    if os.path.isfile(search_filepath):   # check if file exists
        print("Loading Search Image %s" % (search_filepath))
        search_image = cv2.imread(search_filepath)  # read color image in BGR format
        try:
            search_rect = search_image[crop_y_U:crop_y_D,crop_x_L:crop_x_R]
        except:
            print("ERROR: Problem Extracting search_rect from %s" % search_filepath)
            quit()
    else:
        print("ERROR: File Not Found %s" % search_filepath)
        quit()
    print("Successfully Created Search Rectangle from %s" % search_filepath)
    return search_rect

#-----------------------------------------------------------------------------------------------
def search_csv(search_image, search_rect, csv_filename):
    cnt = 0             # Initialize csv file row counter
    work_count = 0      # initialize number of images processed
    result_count = 0    # initialize search result counter
    result_list = []    # initialize blank result list
    # Construct a results folder name based on original search filename minus extension
    results_dir_path = os.path.join(search_path,
                       os.path.splitext(os.path.basename(search_image))[0])
    if copy_results_on:  # Create a results destination folder if required otherwise results is view only
        if not os.path.exists(results_dir_path):
            try:
                os.makedirs(results_dir_path)
            except OSError as err:
                print('ERROR: Cannot Create Directory %s - %s, using default location.' % ( results_dir_path, err))
                quit()
            else:
                print('Created Search Results Dir %s' % (results_dir_path))
    # Construct path of search file in original images folder
    search_image_path = os.path.join(image_path,
                                     os.path.basename(search_image))
    work_start = time.time()      # Start a timer for processing duration
    f = open(csv_filename, 'rt')  # Open csv file for reading
    try:
        reader = csv.reader(f)    # Read csv file into reader list
        print("Searching for Matches with search_value > %f  Please Wait ...." % ( search_value ))
        print("-------------------------------------")
        for row in reader:  # row is a list of one row of data
            cnt += 1  # Increment Row Counter
            work_count += 1  # increment counter for number of images processed
            img_path = row[5]  # Get target image filename
            if os.path.isfile(img_path):   # check if file exists
                target_image = cv2.imread(img_path)  # read color image in BGR format
                target_rect = target_image[crop_y_U:crop_y_D,crop_x_L:crop_x_R]
                search_val = check_image_match(target_rect, search_rect)  # get search result

                if search_val >= search_value and not (img_path == search_image_path):   # Check if result is OK and not itself
                    result_count += 1   # increment valid search result counter
                    result_list.append([search_val,img_path])  # Update search result_list
                    print("%i Result val=%.4f/%.4f  MATCH=%s" %( cnt, search_val, search_value, img_path))
                    if copy_results_on:
                        # Put a copy of search match file into results subfolder (named with search file name without ext)
                        try:
                            shutil.copy(img_path, results_dir_path)  # put a copy of file in results folder
                        except OSError as err:
                            print('ERROR: Copy Failed from %s to %s - %s' % (img_path, results_dir_path, err))
                    if gui_window_on:
                        cv2.imshow("Searching", search_rect)
                        cv2.imshow("Target", target_rect)
                        cv2.waitKey(3000)  # pause for 3 seconds if match found
                else:
                    print("%i Result val=%.4f/%.4f  SKIP=%s" %( cnt, search_val, search_value, img_path))
                    if gui_window_on:
                        cv2.imshow("Searching", search_rect)
                        cv2.imshow("Target", target_rect)
                        cv2.waitKey(20)  # Not a match so display for a short time
        try:
            if copy_results_on:
                # At end of search Copy search file to search results folder
                shutil.copy(search_image, results_dir_path)
                if os.path.exists(search_image):
                    os.remove(search_image)
        except OSError as err:
            print('ERROR: Copy Failed from %s to %s - %s' % (search_file, results_dir_path, err))
    finally:
        f.close()   # close csv file    
        work_end = time.time()  # stop work timer
        print("------------------------------------------------")
        print("Search Results Matching %s" % search_image)
        print("with search_value >= %.4f" % search_value)
        print("------------------------------------------------")
        if result_list:  # Check if results_list has search file entries
            for filename in result_list:
                print(filename)
            if copy_results_on:
                print("Search Match Files Copied to Folder: %s " % results_dir_path)
        else:
            print("------------- Instructions ---------------------")
            print("")
            print("No Search Matches Found.")
            print("You May Need to Reduce config.py variable search_value = %.4f" % search_value)
            print("From %.4f to a lower value." % search_value)
            print("Then Try Again")
            print("")
        print("------------------------------------------------")
        print("Processed %i Images in %i seconds Found %i Matches" %
                       (work_count, work_end - work_start, result_count))

# Start Main
csv_filename = 'speed-cam.csv'
search_list = glob.glob(search_path + '/*jpg')
if search_list:
    print("Found Search Files in Folder: %s" % search_path)
    for files in search_list:
        print(files)
    print("------------------------------------------------")
    for filePath in search_list:
        print("Searching for Matches with %s" % filePath)
        search_rect = get_search_rect(filePath)
        search_csv(filePath, search_rect, csv_filename)
else:
    print("------------- Instructions ---------------------")
    print("")
    print("No Search Files Found in Folder %s" % search_path)
    print("To enable a search")
    print("1 Copy one or more Speed Image File(s) to Folder: %s" % search_path)
    print("2 Restart this script.")
    print("")
    print("Note: config.py variable copy_results_on = %s" % copy_results_on)
    print("if True Then a copy of all search match files will be copied")
    print("To a search subfolder named after the search image name minus extension")
    print("Otherwise search results will be displayed with no copying (useful for testing)")
    print("")
print("------------------------------------------------")
print("%s %s  written by Claude Pageau" % (progName, ver))
print("Done ...")