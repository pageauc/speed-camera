#!/usr/bin/python3

import cgi
import html
import os
import subprocess
import socket
import fcntl
import struct
import socketserver
import sys
import time
import urllib
from http.server import SimpleHTTPRequestHandler
from io import BytesIO

PROG_VER = "ver 12.02 written by Claude Pageau modified by Alexandre Strube for python3 compatibility"
'''
 SimpleHTTPServer python program to allow selection of images from right panel and display in an iframe left panel
 Use for local network use only since this is not guaranteed to be a secure web server.
 based on original code by zeekay and modified by Claude Pageau Nov-2015 for use with pi-timolo.py on a Raspberry Pi
 from http://stackoverflow.com/questions/8044873/python-how-to-override-simplehttpserver-to-show-timestamp-in-directory-listing
 1 - Use nano editor to change webserver.py web_server_root and other variables to suit at bottom of config.py
     nano config.py         # Webserver settings are near the end of the file
     ctrl-x y to save changes
 2 - On Terminal session execute command below.  This will display file access information
     ./webserver.py    # ctrl-c to stop web server.  Note if you close terminal session webserver.py will stop.
 3 - To Run this script as a background daemon execute the command below.
     Once running you can close the terminal session and webserver will continue to run.
     ./webserver.sh start
     To check status of webserver type command below with no parameter
     ./webserver.sh
 4 - On a LAN computer web browser url bar, input this RPI ip address and port number per below
     example    http://192.168.1.110:8080
 Variable Settings are imported from config.py
 To implement this version edit webserver.sh
'''

SCRIPT_PATH = os.path.abspath(__file__)   # Find the full path of this python script
BASE_DIR = os.path.dirname(SCRIPT_PATH)   # Get the path location only (excluding script name)
PROG_NAME = os.path.basename(__file__)    # Name of this program
# Check for variable file to import and error out if not found.
CONFIG_FILE_PATH = os.path.join(BASE_DIR, "config.py")
# Check if config file found and import variable settings.
if not os.path.exists(CONFIG_FILE_PATH):
    print("ERROR - Cannot Import Configuration Variables.")
    print("        Missing Configuration File %s" % CONFIG_FILE_PATH)
    sys.exit(1)
else:
    # Read Configuration variables from config.py file
    print("Importing Configuration Variables from File %s" % CONFIG_FILE_PATH)
    from config import *

os.chdir(web_server_root)
web_root = os.getcwd()
os.chdir(BASE_DIR)
MNT_POINT = "./"

if web_list_by_datetime:
    dir_sort = 'Sort DateTime'
else:
    dir_sort = 'Sort Filename'

if web_list_sort_descending:
    dir_order = 'Desc'
else:
    dir_order = 'Asc'

list_title = "%s %s" % (dir_sort, dir_order)

#-------------------------------------------------------------------------------
def get_ip_address(ifname):
    '''
    Function to Check network interface name to see if an ip address is bound to it
    ifname is a byte string name of interface eg eth0, wlan0, lo Etc
	returns None if there is an IO error.  This function works with python2 and python3
    '''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
    except IOError:
        return None

#-------------------------------------------------------------------------------
def df(drive_mnt):
    '''
       function to read disk drive data using unix df command
       for the specified mount point.
       Returns a formatted string of Disk Status
    '''
    try:
        df = subprocess.Popen(["df", "-h", drive_mnt], stdout=subprocess.PIPE)
        output = df.communicate()[0].decode('utf-8')
        device, size, used, available, percent, mountpoint = output.split("\n")[1].split()
        drive_status = ("Drive [ %s ] Mount_Point [ %s ] Space_Used [ %s %s of %s ] Space_Avail [ %s ]" %
                        (device, mountpoint, percent, used, size, available))
    except:
        drive_status = "df command Error. No drive status avail"
    return drive_status

#-------------------------------------------------------------------------------
class DirectoryHandler(SimpleHTTPRequestHandler):

    def list_directory(self, path):
        try:
            list = os.listdir(path)
            all_entries = len(list)
        except os.error:
            self.send_error(404, b"No permission to list directory")
            return None

        if web_list_by_datetime:
            # Sort by most recent modified date/time first
            list.sort(key=lambda x: os.stat(os.path.join(path, x)).st_mtime, reverse=web_list_sort_descending)
        else:
            # Sort by File Name
            list.sort(key=lambda a: a.lower(), reverse=web_list_sort_descending)
        f = BytesIO()
        displaypath = html.escape(urllib.parse.unquote(self.path))
        # find index of first file or hyperlink

        file_found = False
        cnt = 0
        for entry in list:  # See if there is a file for initializing iframe
            fullname = os.path.join(path, entry)
            if os.path.islink(fullname) or os.path.isfile(fullname):
                file_found = True
                break
            cnt += 1
        print("here")
        # Start HTML formatting code
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(b'<head>')
        # Setup Meta Tags and better viewing on small screen devices
        f.write(b'<meta "Content-Type" content="txt/html; charset=ISO-8859-1" />')
        f.write(b'<meta name="viewport" content="width=device-width, initial-scale=1.0" />')
        if web_page_refresh_on:
            f.write(b'<meta http-equiv="refresh" content="%s" />' % web_page_refresh_sec.encode('utf-8'))
        f.write(b'</head>')

        tpath, cur_folder = os.path.split(self.path)
        f.write(b"<html><title>%s %s</title>" % (web_page_title.encode('utf-8'), self.path.encode('utf-8')))
        f.write(b"<body>")
        # Start Left iframe Image Panel
        f.write(b'<iframe width="%s" height="%s" align="left"'
                % (web_iframe_width_usage.encode('utf-8'), web_image_height.encode('utf-8')))
        if file_found:  # file was display it in left pane
            f.write(b'src="%s" name="imgbox" id="imgbox" alt="%s">'
                    % (list[cnt].encode('utf-8'), web_page_title.encode('utf-8')))
        else:  # No files found so blank left pane
            f.write(b'src="%s" name="imgbox" id="imgbox" alt="%s">'
                    % (b"about:blank", web_page_title.encode('utf-8')))

        f.write(b'<p>iframes are not supported by your browser.</p></iframe>')
        # Start Right File selection List Panel
        list_style = b'<div style="height: ' + web_list_height.encode('utf-8') + b'px; overflow: auto; white-space: nowrap;">'
        f.write(list_style)
        # f.write(b'<center><b>%s</b></center>' % (self.path.encode('utf-8')))
        # Show a refresh button at top of right pane listing
        refresh_button = ('''<FORM>&nbsp;&nbsp;<INPUT TYPE="button" onClick="history.go(0)"
VALUE="Refresh">&nbsp;&nbsp;<b>%s</b></FORM>''' % list_title)
        f.write(b'%s' % refresh_button.encode('utf-8'))
        f.write(b'<ul name="menu" id="menu" style="list-style-type:none; padding-left: 4px">')
        # Create the formatted list of right panel hyper-links to files in the specified directory
        if self.path != "/":   # Display folder Back arrow navigation if not in web root
            f.write(b'<li><a href="%s" >%s</a></li>\n'
                    % (urllib.parse.quote("..").encode('utf-8'), html.escape("< BACK").encode('utf-8')))
        display_entries = 0
        file_found = False
        for name in list:
            display_entries += 1
            if web_max_list_entries > 1:
                if display_entries >= web_max_list_entries:
                    break
            fullname = os.path.join(path, name)
            displayname = linkname = name
            date_modified = time.strftime('%H:%M:%S %d-%b-%Y', time.localtime(os.path.getmtime(fullname)))
            # Append / for directories or @ for symbolic links
            if os.path.islink(fullname):
                displayname = name + "@"  # symbolic link found
            if os.path.isdir(fullname):   # check if entry is a directory
                displayname = name + "/"
                linkname = os.path.join(displaypath, displayname)
                f.write(b'<li><a href="%s" >%s</a></li>\n'
                        % (urllib.parse.quote(linkname).encode('utf-8'), html.escape(displayname).encode('utf-8')))
            else:
                f.write(b'<li><a href="%s" target="imgbox">%s</a> - %s</li>\n'
                        % (urllib.parse.quote(linkname).encode('utf-8'), html.escape(displayname).encode('utf-8'), date_modified.encode('utf-8')))

        if (self.path != "/") and display_entries > 35:   # Display folder Back arrow navigation if not in web root
            f.write(b'<li><a href="%s" >%s</a></li>\n' % (urllib.parse.quote("..").encode('utf-8'), html.escape("< BACK").encode('utf-8')))
        f.write(b'</ul></div><p><b>')
        drive_status = df(MNT_POINT)
        f.write(b'<div style="float: left; padding-left: 40px;">Web Root is [ %s ]  %s</div>' %
                (web_server_root.encode('utf-8'), drive_status.encode('utf-8')))
        f.write(b'<div style="text-align: center;">%s</div>' % web_page_title.encode('utf-8'))

        if web_page_refresh_on:
            f.write(b'<div style="float: left; padding-left: 40px;">Auto Refresh = %s sec</div>' % web_page_refresh_sec.encode('utf-8'))

        if web_max_list_entries > 1:
            f.write(b'<div style="text-align: right; padding-right: 40px;">Listing Only %i of %i Files in %s</div>'
                    % (display_entries.encode('utf-8'), all_entries.encode('utf-8'), self.path.encode('utf-8')))
        else:
            f.write(b'<div style="text-align: right; padding-right: 50px;">Listing All %i Files in %s</div>'
                    % (all_entries, self.path.encode('utf-8')))
        # Display web refresh info only if setting is turned on
        f.write(b'</b></p>')
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header(b"Content-type", b"text/html; charset=%s" % encoding.encode('utf-8'))
        self.send_header("Content-Length".encode('utf-8'), str(length))
        self.end_headers()
        return f

# Start Web Server Processing
os.chdir(web_server_root)
socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(("", web_server_port), DirectoryHandler)

net_interface_names = [ b'eth0', b'wlan0' ]   # byte string list of interface names to check
ip_list = []
for my_if in net_interface_names:
    my_ip = get_ip_address(my_if)
    if my_ip is not None:
        ip_list.append(my_ip)

print("----------------------------------------------------------------")
print("%s %s" % (PROG_NAME, PROG_VER))
print("---------------------------- Settings --------------------------")
print("Server  - web_page_title   = %s" % web_page_title)
print("          web_server_root  = %s/%s" % (BASE_DIR, web_server_root))
print("          web_server_port  = %i " % web_server_port)
print("Content - web_image_height = %s px (height of content)" % web_image_height)
print("          web_iframe_width = %s  web_iframe_height = %s" % (web_iframe_width, web_iframe_height))
print("          web_iframe_width_usage = %s (of avail screen)" % (web_iframe_width_usage))
print("          web_page_refresh_sec = %s  (default=180 sec)" % web_page_refresh_sec)
print("          web_page_blank = %s ( True=blank left pane until item selected)" % web_page_blank)
print("Listing - web_max_list_entries = %s ( 0=all )" % web_max_list_entries)
print("          web_list_by_datetime = %s  sort_decending = %s" % (web_list_by_datetime, web_list_sort_descending))
print("----------------------------------------------------------------")
print("From a computer on the same LAN. Use a Web Browser to access this server at")
print("Type the URL below into the browser url bar then hit enter key.")
print("")
if not ip_list:
    print("ERROR - Can't Find a Network IP Address on this Raspberry Pi")
    print("        Check Network Interfaces and Try Again")
else:
    for myip in ip_list:
        print("                 http://%s:%i"  % (myip, web_server_port))
print("")
print("IMPORTANT: If You Get - socket.error: [Errno 98] Address already in use")
print("           Check for Another app using port or Wait a minute for webserver to timeout and Retry.")
print("              ctrl-c to exit this webserver script")
print("----------------------------------------------------------------")
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("")
    print("User Pressed ctrl-c")
    print("%s %s" % (PROG_NAME, PROG_VER))
    print("Exiting Bye ...")
    httpd.shutdown()
    httpd.socket.close()
except IOError as e:
    print("I/O error({0}): {1}".format(e.errno, e.strerror))