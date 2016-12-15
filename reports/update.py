#!/usr/bin/python

"""
Creates the single "report.txt" file and uploads it to the sheltermanager.com
server for users of the program to access and get new reports
"""

HOST = "wwwdx.sheltermanager.com"

import os

de = os.listdir(".")
s = ""

for d in de:
    if d.endswith(".txt"):
        f = open(d, "r")
        if s != "": s += "&&&\n"
        s += f.read()
        f.close()

print "Found %d reports" % s.count("&&&")

f = open("reports.txt", "w")
f.write(s)
f.flush()
f.close()
print "reports.txt written"

# Upload to the server
os.system("scp -C reports.txt root@%s:/var/www/sheltermanager.com/repo/" % HOST)
print "reports.txt uploaded to root@%s:/var/www/sheltermanager.com/repo/" % HOST

# Remove the temp file
os.system("rm -f reports.txt")
print "cleaning up."
