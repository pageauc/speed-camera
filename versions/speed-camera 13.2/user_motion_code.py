"""
This module will be imported into speed-cam.py and will
execute the userMotionCode function after
motion tracking image is taken.  The filenamePath will be passed
in case you want to process the file as an attachment
or include in a message, Etc.  If you need to import other
python modules they can be added to the top of this
module and used in the userMotionCode.
You can also include other functions within this module
as long as they are directly or indirectly called
within the userMotionCode function since that is
the only function that is called in the speed-cam.py
program when motion tracking is tiggered.
"""

#------------------------------------------------------------------------------
def userMotionCode(vs, image_width, image_height, filenamePath):
    """
    Users can put code here that needs to be run
    after speed camera motion tracking and image taken
    Eg Notify or activate something.

    Note all functions and variables will be imported.
    speed-cam.py will execute this function userMotionCode(filename)
    in speed-cam.py per example below

        user_motion_code.userMotionCode(filename)

    """
    # Insert User python code Below
    # print("User Code Executing from userMotionCode function")
    # print("file path is %s" % filenamePath)
