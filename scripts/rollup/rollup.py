#!/usr/bin/env python3

# Rolls up all of the js files into one file 
# in the correct order and dumps it to stdout.

# Assumes cwd is the root of the source tree

import os

jsfiles = [ "common.js", "common_validate.js", "common_html.js", "common_map.js", "common_widgets.js", "common_animalchooser.js",
    "common_animalchoosermulti.js", "common_personchooser.js", "common_tableform.js", "common_barcode.js", "common_microchip.js", "header.js",
    "header_additional.js", "header_edit_header.js" ]

exclude = [ "animal_view_adoptable.js", "document_edit.js", "onlineform_extra.js", "report_toolbar.js" ]

for i in os.listdir("src/static/js"):
    if i in exclude: continue
    if i in jsfiles: continue
    if i.startswith("mobile") or i.startswith("service"): continue
    if i.startswith(".") or not i.endswith(".js"): continue
    jsfiles.append(i)

for i in jsfiles:
    with open("src/static/js/%s" % i, "r") as f:
        print(f.read())


