# import json
# import requests

"""
This module will be imported into speed-cam.py and will
execute the userReportingCode function after collecting data to report.
The filenamePath will be passed in case you want to process the file as an attachment
or include in a message, Etc.  If you need to import other
python modules they can be added to the top of this
module and used in the userReportingCode.
You can also include other functions within this module
as long as they are directly or indirectly called
within the userReportingCode function since that is
the only function that is called in the speed-cam.py
program when reporting is triggered.
"""

#------------------------------------------------------------------------------
def userReportingCode(data, video_stream, filenamePath):
    """
    Users can put code here that needs to be run
    after speed camera reporting tracking and image taken
    Eg Notify or activate something.

    Note all functions and variables will be imported.
    speed-cam.py will execute this function userReportingCode(filename)
    in speed-cam.py per example below

        user reporting_code.userReportingCode(data, filename)

    """
    # Insert User python code Below
    # print("User Code Executing from userReportingCode function")
    # print("file path is %s" % filenamePath)

    # files = {
    #     "json": data,
    #     "file": open(filenamePath, "rb")
    # }

    # headers = {
    #     "Authorization": "Bearer shhh it's a secret"
    # }

    # url = "https://example.com/api/speed"

    # requests.post(url, data=data, files=files, headers=headers)
