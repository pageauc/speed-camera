#!/usr/bin/env python

ver = "ver 5.60"  # Original issue on 26-Jul-2017 by Claude Pageau

"""
speed-search.py written by Claude Pageau pageauc@gmail.com
Raspberry (Pi) - python opencv2 find images matching search image using cv2 template matching
GitHub Repo here https://github.com/pageauc/rpi-speed-camera/tree/master/

This is program works in conjunction with speed-cam.py data output images and csv file.
It needs a speed camera csv file and related images.  To initiate a search make sure
there is sufficient images (suggest > 100).  Find a single speed image that you want
to find matches for.  Copy this image into the search folder (default media/search)
Start search-speed.py

    cd ~/rpi-speed-camera
    ./search-speed.py

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

import os
os.system('clear')
# Create some system variables
mypath=os.path.abspath(__file__)       # Find the full path of this python script
baseDir=mypath[0:mypath.rfind("/")+1]  # get the path location only (excluding script name)
baseFileName=mypath[mypath.rfind("/")+1:mypath.rfind(".")]
progName = os.path.basename(__file__)  # Get name of this script with no path

print("%s %s Loading  Please Wait ....." % (progName, ver))
import time
import cv2
import csv
import glob
import shutil
import sys

configFilePath = baseDir + "search_config.py"
if not os.path.exists(configFilePath):  # check if config.py file exist if not wget github copy
    print("ERROR - Could Not Find Configuration File %s" % (configFilePath))
    import urllib2
    config_url = "https://raw.github.com/pageauc/rpi-speed-camera/master/search_config.py"
    print("   Attempting to Download config File from %s" % ( config_url ))
    try:
        wgetfile = urllib2.urlopen(config_url)
    except:
        print("ERROR: Download of config Failed")
        print("   Try Rerunning the speed-install.sh Again.")
        print("   or")
        print("   Perform GitHub curl install per Readme.md")
        print("   and Try Again")
        print("Exiting %s" % ( progName ))
        quit()
    f = open('search_config.py','wb')
    f.write(wgetfile.read())
    f.close()
from search_config import *  # Read Configuration variables from search_config.py file
from config import *

# Initialize size of rectangle to crop for search matches
sw = 100 * image_bigger  # default search rectangle Width
sh = 45 * image_bigger  # default search rectangle height
crop_x_L = (x_left + 10) * image_bigger
crop_x_R = (x_right - 10) * image_bigger
crop_y_U = (y_upper + 10) * image_bigger
crop_y_D = (y_lower - 10) * image_bigger
blank = "                                                              "

#-----------------------------------------------------------------------------------------------
def print_at(x, y, text):
     sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
     sys.stdout.flush()

#-----------------------------------------------------------------------------------------------
def check_image_match(full_image, small_image):
    # Look for small_image in full_image and return best and worst results
    # Try other MATCH_METHOD settings per config.py comments
    # For More Info See http://docs.opencv.org/3.1.0/d4/dc6/tutorial_py_template_matching.html
    result = cv2.matchTemplate( full_image, small_image, search_match_method)
    # Process result to return probabilities and Location of best and worst image match
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)  # find search rect match in new image
    return maxVal

#-----------------------------------------------------------------------------------------------
def get_search_rect(search_filepath):
    if os.path.isfile(search_filepath):   # check if file exists
        print("Loading Target Search Image %s" % (search_filepath))
        image1 = cv2.imread(search_filepath)  # read color image in BGR format
        try:
            search_rect = image1[crop_y_U:crop_y_D,crop_x_L:crop_x_R]
        except:
            print("ERROR: Problem Extracting search_rect from %s" % search_filepath)
            return None
    else:
        print("ERROR: File Not Found %s" % search_filepath)
        return None
    print("Successfully Created Target Search Rectangle from %s" % search_filepath)
    return search_rect

#-----------------------------------------------------------------------------------------------
def search_for_match(search_image, search_rect):
    cnt = 0             # Initialize csv file row counter
    work_count = 0      # initialize number of images processed
    result_count = 0    # initialize search result counter
    result_list = []    # initialize blank result list
    # Construct a results folder name based on original search filename minus extension
    results_dir_path = os.path.join(search_dest_path,
                       os.path.splitext(os.path.basename(search_image))[0])
    print_at(2,1,"Target  : %s with search_match_value>%.4f" % ( search_image, search_match_value ))
    if search_copy_on:  # Create a search results dest folder if required otherwise results is view only
        if not os.path.exists(results_dir_path):
            try:
                os.makedirs(results_dir_path)
            except OSError as err:
                print('ERROR: Cannot Create Directory %s - %s, using default location.' %
                                                 ( results_dir_path, err))
            else:
                print('Created Search Results Dir %s' % (results_dir_path))

    # Construct path of search file in original images folder
    search_image_path = os.path.join(search_source_images_path, os.path.basename(search_image))
    work_start = time.time()      # Start a timer for processing duration
    try:
        if search_using_csv:
            f = open(search_csv_path, 'rt')  # Open csv file for reading
            reader = csv.reader(f)    # Read csv file into reader list
            image_data = list(reader)
        else:
            image_data = glob.glob(os.path.join(search_source_image_path, '/*jpg'))
        search_images_total = len(image_data)

        for row in image_data:  # row is a list of one row of data
            work_count += 1  # increment counter for number of images processed
            if search_using_csv:
                current_image_path = row[5]  # Get target image filename
            else:
                current_image_path = image_data[cnt]
            cnt += 1  # Increment Row Counter
            if os.path.isfile(current_image_path):   # check if file exists
                target_image = cv2.imread(current_image_path)  # read color image in BGR format
                target_rect = target_image[crop_y_U:crop_y_D,crop_x_L:crop_x_R]
                search_result_value = check_image_match(target_rect, search_rect)  # get search result

                if search_result_value >= search_match_value and not (current_image_path == search_image_path):   # Check if result is OK and not itself
                    result_count += 1   # increment valid search result counter
                    result_list.append([search_result_value, current_image_path])  # Update search result_list
                    print_at(4,1,"Matched : %i Last: %i/%i  value: %.4f/%.4f  MATCH=%s       " %
                         ( result_count, cnt, search_images_total, search_result_value, search_match_value, current_image_path))
                    if search_copy_on:
                        # Put a copy of search match file into results subfolder (named with search file name without ext)
                        try:
                            shutil.copy(current_image_path, results_dir_path)  # put a copy of file in results folder
                        except OSError as err:
                            print('ERROR: Copy Failed from %s to %s - %s' % (current_image_path, results_dir_path, err))
                    if gui_window_on:
                        cv2.imshow("Searching", search_rect)
                        cv2.imshow("Target", target_rect)
                        cv2.waitKey(3000)  # pause for 3 seconds if match found
                else:
                    print_at(3,1,"Progress: %i/%i  value: %.4f/%.4f  SKIP=%s    " %
                         ( cnt, search_images_total, search_result_value, search_match_value, current_image_path))
                    if gui_window_on:
                        cv2.imshow("Searching", search_rect)
                        cv2.imshow("Target", target_rect)
                        cv2.waitKey(20)  # Not a match so display for a short time
        try:
            if search_copy_on:
                # At end of search Copy search file to search results folder
                shutil.copy(search_image, results_dir_path)
                if os.path.exists(search_image):
                    os.remove(search_image)
        except OSError as err:
            print('ERROR: Copy Failed from %s to %s - %s' % (search_file, results_dir_path, err))
    finally:
        if search_using_csv:
            f.close()   # close csv file
        work_end = time.time()  # stop work timer
        print("------------------------------------------------")
        print("Search Results Matching %s" % search_image)
        print("with search_match_value >= %.4f" % search_match_value)
        print("------------------------------------------------")
        if result_list:  # Check if results_list has search file entries
            result_list.sort(reverse=True)
            for filename in result_list:
                print(filename)
            print("------------------------------------------------")
            if search_copy_on:
                print("Search Match Files Copied to Folder: %s " % results_dir_path)
            else:
                print("search_copy_on=%s  No Search Match Files Copied to Folder: %s" % (search_copy_on, results_dir_path))
        else:
            print("------------- Instructions ---------------------")
            print("")
            print("No Search Matches Found.")
            print("You May Need to Reduce %s variable search_match_value = %.4f" % (configFilePath, search_match_value))
            print("From %.4f to a lower value." % search_match_value)
            print("Then Try Again")
            print("")
        print("Processed %i Images in %i seconds Found %i Matches" %
                       (work_count, work_end - work_start, result_count))
    return result_list

# ------------------- Start Main --------------------------------

if not os.path.isdir(search_dest_path):
    print("Creating Search Folder %s" % ( search_dest_path))
    os.makedirs(search_dest_path)
    
search_list = glob.glob(search_dest_path + '/*jpg')
target_total = len(search_list)
try:
    if search_list:  # Are there any search files found in search_path
        for filePath in search_list:  # process each search_list entry
            os.system('clear')
            for i in range(1,5):
                print("")
                print_at(1,i,blank)
            print_at(1,1,"%s %s written by Claude Pageau       " % ( progName, ver))
            print("------------------------------------------------")
            print("Found %i Target Search Image Files in %s" %
                                 ( target_total, search_dest_path))
            print("------------------------------------------------")
            for files in search_list:
                current = files
                if current == filePath:
                    print("%s  Current Search" % current)
                else:
                    print(files)
            print("------------------------------------------------")
            search_rect = get_search_rect(filePath)  # Get search_rect of file
            if search_rect == None:  # Check if search_rect created
                print("ERROR: Problem Creating Search Rectangle.")
                print("       Cannot Search Match %s" % filePath)
            else:
                results = search_for_match(filePath, search_rect)  # Look for matches
               # if results:
               #     for rows in results:
               #         print(rows)
    else:
        print("------------- Instructions ---------------------")
        print("")
        print("No Search Files Found in Folder %s" % search_dest_path)
        print("To enable a search")
        print("1 Copy one or more Speed Image File(s) to Folder: %s" % search_dest_path)
        print("2 Restart this script.")
        print("")
        print("Note: search_config.py variable search_copy_on = %s" % search_copy_on)
        print("if True Then a copy of all search match files will be copied")
        print("To a search subfolder named after the search image name minus extension")
        print("Otherwise search results will be displayed with no copying (useful for testing)")
        print("")
    print("------------------------------------------------")
    print("%s %s  written by Claude Pageau" % (progName, ver))
    print("Done ...")
except KeyboardInterrupt:
    print("")
    print("+++++++++++++++++++++++++++++++++++")
    print("User Pressed Keyboard ctrl-c")
    print("%s %s - Exiting ..." % (progName, ver))
    print("+++++++++++++++++++++++++++++++++++")
    print("")
    quit(0)
