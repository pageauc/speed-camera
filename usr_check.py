#!/usr/bin/env python3.4

import cgi, cgitb
import os
import sqlite3

cgitb.enable()

form = cgi.FieldStorage()
register_no = form.getvalue('register_no')
username = form.getvalue('username')
passwd = form.getvalue('password')

print("Content-type:text/html\r\n\r\n")
print("<html>")
print("<head>")
print("<center><h2>Welcome to SPEED CAMERA</h2></center>")
print("</head>")
print("<body>")
print('<div style = "text-align:center ; "')
# print("</div>")
print("")
DB = '/home/pi/speed-camera/data/speed_cam.db'
if os.path.isfile(DB):
    print("<p>INFO  : Connecting to sqlite3 Database %s</p>" % DB)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
else:
    print("<p>ERROR : Could Not Find DB %s</p>" % DB)

## now to check whether the entered data is for
## -> new user 
## -> an old user

cur.execute('SELECT user_name FROM users WHERE reg_no=?', (register_no,))
rows = cur.fetchall()
print("<br><br>")
if len(rows) == 0:  
    print("<p>User  : <b>", username , "</b> Does Not Exist.</p>")
    print('<p>Creating New User %s %s %s</p>' % (username, register_no, passwd))
    conn.execute('INSERT INTO users VALUES(?,?,?)', (register_no,username,passwd))
    conn.commit()
    cur.execute('SELECT user_name FROM users WHERE reg_no=?', (register_no,))
    rows = cur.fetchall()
    print("<br><br>")
    if len(rows) == 0:
        print("<p>ERROR : Failed to Create User ?</p>", username)    
        conn.commit()
    else:
        print("<p>User was Created Successfully</p>")
        print("<p>Done</p>")
else:
    print("<p>Welcome<b>", username ,"</b>. Good to have you back")
    print("<br><p>Your account details</p>")
    print("<ul>")
    print("<li>Register number : ", register_no, " </li>")
    print("<li>Username : " , username, "</li>")
    print("</ul>")
print("<p>Close Database %s</p>" % DB)
print("<p>Bye</p>")
cur.close()
conn.close()
print("</body></html>")    