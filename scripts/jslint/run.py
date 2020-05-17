#!/usr/bin/env python3

import os, sys, subprocess

JSLINT_BIN = "node_modules/jshint/bin/jshint"
CFG = "jshint.conf"

if not os.path.exists(JSLINT_BIN):
    print("jshint does not exist, installing from npm")
    os.system("npm install jshint")

files = sorted(os.listdir("../../src/static/js"))
if len(sys.argv) == 2: 
    files = [ sys.argv[1] ]

for f in files:
    if f.startswith("jquery"): continue
    if f.startswith("."): continue
    if os.path.isdir("../../src/static/js/%s" % f): continue
    print(f)
    filepath = "../../src/static/js/%s" % f
    try:
        output = subprocess.run([JSLINT_BIN, "--config", CFG, filepath], check=True, capture_output=True)
        output = output.stdout.decode("utf-8")
        if output.find("OK") == -1 and output.strip() != "": 
            print(output)
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        output = e.stdout.decode("utf-8")
        print(output)
        sys.exit(1)

