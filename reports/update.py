#!/usr/bin/env python3

"""
Creates the single "report.txt" file and uploads it to the sheltermanager.com
server for users of the program to access and get new reports
"""

import os, sys

s = []
for fname in os.listdir("."):
    if fname.endswith(".txt") and fname != "reports.txt":
        with open(fname, "r") as f:
            s.append(f.read())

rcount = "&&&".join(s).count("&&&")
print(f"Processed {len(s)} files containing {rcount} reports")

with open("reports.txt", "w") as f:
    f.write("&&&\n".join(s))
print("reports.txt written")


