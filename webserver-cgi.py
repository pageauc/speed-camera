#!/usr/bin/python
'''
This is a cgi web server interface for processing python cgi scripts.  Default is to
run in www web root. By default python scripts are run from www/cgi-bin folder.
These scripts need to be written in cgi syntax to support html form pages.
This server is used for processing sqlite reports and speed camera admin web pages.
I chose to create a second server so cgi-bin folder is not visible from
the speed camera webserver.py directory browser at default media folder.
'''
import os
import socket
import CGIHTTPServer
import BaseHTTPServer

PROG_NAME = os.path.basename(__file__)
PROG_VER = "0.1"
PORT = 8081
WEB_ROOT = "www"
CGI_DIR = "/cgi-bin"

os.chdir(WEB_ROOT)
try:
    my_ip = ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1],
                         [[(s.connect(('8.8.8.8', 53)),
                            s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET,
                                                                     socket.SOCK_DGRAM)]][0][1]]) if l][0][0])

except:
    print("ERROR - Can't Find a Network IP Address on this Raspberry Pi")
    print("        Configure Network and Try Again")
    sys.exit(1)

class Handler(CGIHTTPServer.CGIHTTPRequestHandler):
    cgi_directories = [CGI_DIR]

httpd = BaseHTTPServer.HTTPServer(("", PORT), Handler)

print("%s ver %s   written by Claude Pageau" % (PROG_NAME, PROG_VER))
print("This server will process speed-camera cgi scripts at")
print("http://%s:%i" % ( my_ip, PORT))

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("")
    print("User Pressed ctrl-c")
    print("%s %s" % (PROG_NAME, PROG_VER))
    print("Exiting Bye ...")
    httpd.shutdown()

except IOError as e:
    print("I/O error({0}): {1}".format(e.errno, e.strerror))
