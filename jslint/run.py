#!/usr/bin/python

import os, sys

for f in sorted(os.listdir("../src/static/js")):
    if f.startswith("jquery"): continue
    if f.startswith("."): continue
    if os.path.isdir("../src/static/js/%s" % f): continue
    print f
    #output = os.popen("cat ../src/static/js/%s | nodejs runjslint.js" % f).read()
    output = os.popen("nodejs runjslint.js ../src/static/js/%s" % f).read()
    if output.find("ERROR") != -1:
        print output
        sys.exit(1)
    if output.find("WARN") != -1:
        print output

