#!/usr/bin/env python3

"""
Creates the single "report.txt" file and uploads it to the sheltermanager.com
server for users of the program to access and get new reports
"""

HOST = "wwwdx.sheltermanager.com"

import os

s = []
for fname in os.listdir("."):
    if fname.endswith(".txt"):
        with open(fname, "r") as f:
            s.append(f.read())

rcount = "&&&".join(s).count("&&&")
print(f"Processed {len(s)} files containing {rcount} reports")

with open("reports.txt", "w") as f:
    f.write("&&&".join(s))
print("reports.txt written")

# Upload to the server
os.system(f"scp -C reports.txt root@{HOST}:/var/www/sheltermanager.com/repo/")
print(f"reports.txt uploaded to root@{HOST}:/var/www/sheltermanager.com/repo/")

# Remove the temp file
os.system("rm -f reports.txt")
print("reports.txt deleted")

