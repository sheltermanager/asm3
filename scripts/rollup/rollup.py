#!/usr/bin/env python3

# Rolls up all of the minified python js files into one file 
# in the correct order and dumps it to stdout.

# Assumes cwd is the root of the source tree

import os

jsfiles = [ "common.min.js", "common_map.min.js", "common_widgets.min.js", "common_animalchooser.min.js",
    "common_animalchoosermulti.min.js", "common_personchooser.min.js", "common_tableform.min.js", "header.min.js",
    "header_additional.min.js", "header_edit_header.min.js" ]

exclude = [ "animal_view_adoptable.min.js", "document_edit.min.js", "mobile.min.js", "mobile_sign.min.js", 
    "onlineform_extra.min.js", "rollup.min.js" ]

for i in os.listdir("src/static/js/min"):
    if i not in jsfiles and i not in exclude and not i.startswith(".") and i.endswith(".min.js"):
        jsfiles.append(i)

for i in jsfiles:
    with open("src/static/js/min/%s" % i, "r") as f:
        print(f.read())


