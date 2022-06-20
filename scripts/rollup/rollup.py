#!/usr/bin/env python3

# Rolls up all of the js files into one file 
# in the correct order and dumps it to stdout.

# Assumes cwd is the root of the source tree

import os

jsfiles = [ "common.js", "common_map.js", "common_widgets.js", "common_animalchooser.js",
    "common_animalchoosermulti.js", "common_personchooser.js", "common_tableform.js", "header.js",
    "header_additional.js", "header_edit_header.js" ]

exclude = [ "animal_view_adoptable.js", "document_edit.js", 
    "mobile.js", "mobile2.js", "mobile_login.js", "mobile_report.js", "mobile_sign.js", 
    "onlineform_extra.js", "report_toolbar.js", "service_sign_document.js", "service_checkout_adoption.js" ]

for i in os.listdir("src/static/js"):
    if i not in jsfiles and i not in exclude and not i.startswith(".") and i.endswith(".js"):
        jsfiles.append(i)

for i in jsfiles:
    with open("src/static/js/%s" % i, "r") as f:
        print(f.read())


