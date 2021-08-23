#!/usr/bin/env python3

# Rolls up all of the compat python js files into one file 
# in the correct order and dumps it to stdout.

# Assumes cwd is the root of the source tree

import os

def readfile_print(fname):
    with open(fname, "r") as f:
        print(f.read())

jsfiles = [ "common.js", "common_map.js", "common_widgets.js", "common_animalchooser.js",
    "common_animalchoosermulti.js", "common_personchooser.js", "common_tableform.js", "header.js",
    "header_additional.js", "header_edit_header.js" ]

exclude = [ "animal_view_adoptable.js", "document_edit.js", "mobile.js", "mobile_sign.js", 
    "onlineform_extra.js", "report_toolbar.js", "service_sign_document.js", "service_checkout_adoption.js" ]

exclude += [ "rollup.js", "rollup_compat.js" ]

# Output extra polyfills first
os.system("cat node_modules/regenerator-runtime/runtime.js | scripts/jsmin/jsmin > node_modules/regenerator-runtime/runtime.min.js")
readfile_print("node_modules/regenerator-runtime/runtime.min.js")
readfile_print("node_modules/promise-polyfill/dist/polyfill.min.js")

for i in os.listdir("src/static/js/compat"):
    if i not in jsfiles and i not in exclude and not i.startswith(".") and i.endswith(".js"):
        jsfiles.append(i)

for i in jsfiles:
    readfile_print("src/static/js/compat/%s" % i)


