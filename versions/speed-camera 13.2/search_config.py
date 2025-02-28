# ---------------- User Configuration Settings for speed-cam.py ---------------------------------
#               Ver 5.00 search-speed.py Variable Configuration Settings

# ======================================
#    speed-search.py variable settings
# ======================================

# Display and Log settings
# ------------------------
search_verbose = True      # Display basic status information on console
search_log_to_file = False # True = Send logging to file   (not implemented yet)
search_logfile_path = 'speed-search.log'  # Location of log file when search_log_to_file=True

search_gui_on = False      # True = Turn On All desktop GUI openCV windows. False=Don't Show (req'd for SSH) .

search_match_value = 0.97            # Default = 0.97 Accuracy setting for Image Searches 0=Lowest 1=Highest
search_source_images_path = "media/images"  # Source images folder
search_copy_on = True                # Copy matching image files to search_path subfolder (based on search filename minus ext)
search_dest_path = 'media/search'    # Destination for Result images if search_copy_on = True
search_using_csv = True              # False= Use glob  True= Use csv file for source file names
search_csv_path = 'speed-cam.csv'    #
search_data_on_image = True          # default=True show match_value on result images

search_match_method = 3       # Default=3   Valid MatchTemplate COMPARE_METHOD Int Values
                              # 0 = cv2.TM_SQDIFF
                              # 1 = cv2.TM_SQDIFF_NORMED
                              # 2 = cv2.TM_CCORR
                              # 3 = cv2.TM_CCORR_NORMED   Default
                              # 4 = cv2.TM_CCOEFF
                              # 5 = cv2.TM_CCOEFF_NORMED
                              # For comparison methods details
                              # see http://docs.opencv.org/3.1.0/d4/dc6/tutorial_py_template_matching.html

# ---------------------------------------------- End of User Variables -----------------------------------------------------





