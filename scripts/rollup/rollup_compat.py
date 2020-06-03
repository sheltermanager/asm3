#!/usr/bin/env python3

# Rolls up all of the minified compat python js files into one file 
# in the correct order and dumps it to stdout.

# Assumes cwd is the root of the source tree

import os

def readfile_print(fname):
    with open(fname, "r") as f:
        print(f.read())

jsfiles = [ "common.min.js", "common_map.min.js", "common_widgets.min.js", "common_animalchooser.min.js",
    "common_animalchoosermulti.min.js", "common_personchooser.min.js", "common_tableform.min.js", "header.min.js",
    "header_additional.min.js", "header_edit_header.min.js" ]

exclude = [ "animal_view_adoptable.min.js", "document_edit.min.js", "mobile.min.js", "mobile_sign.min.js", 
    "onlineform_extra.min.js", "rollup.min.js", "rollup_compat.min.js" ]

# Output extra polyfills first
os.system("cat node_modules/regenerator-runtime/runtime.js | scripts/jsmin/jsmin > node_modules/regenerator-runtime/runtime.min.js")
readfile_print("node_modules/regenerator-runtime/runtime.min.js")
readfile_print("node_modules/promise-polyfill/dist/polyfill.min.js")

for i in os.listdir("src/static/js/compat"):
    if i not in jsfiles and i not in exclude and not i.startswith(".") and i.endswith(".min.js"):
        jsfiles.append(i)

for i in jsfiles:
    readfile_print("src/static/js/compat/%s" % i)


