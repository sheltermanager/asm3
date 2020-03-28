#!/usr/bin/python

"""
Extract all strings from our python code and js/templates
and generate a pot file. xgettext can't handle functions in quoted
strings.
This means ASM doesn't actually have any dependency on gettext 
since none of it is helpful to us, but still reads and writes 
pot/po files for launchpad. Thanks for nothing gettext team!
"""

import os, re, textwrap, datetime

src = os.listdir("src")
js = os.listdir("src/static/js")

strings = {}

def extract_strings(fname, s):
    for x in re.findall("\\_\\(['\"](.+?)['\"],? ?l?\\)", s):
        if x in strings:
            if strings[x].find(fname) == -1:
                strings[x] += " " + fname
        else:
            strings[x] = fname

def output_msgid(s):
    m = "msgid \""
    if len(s) <= 76:
        m += s + "\"\n"
        return m
    else:
        m += "\"\n"
        bits = textwrap.wrap(s, width=76)
        for i in range(0, len(bits)):
            if i == len(bits) -1:
                m += "\"%s\"\n" % bits[i]
            else:
                m += "\"%s \"\n" % bits[i]
        return m

for j in js:
    if j.endswith(".js") and not j.startswith("jquery"):
        f = open("src/static/js/" + j, "r")
        s = f.read()
        f.close()
        extract_strings(j, s)

for p in src:
    if p.endswith(".py"):
        f = open("src/" + p, "r")
        s = f.read()
        f.close()
        extract_strings(p, s)

pot = """
# ASM Translation Strings
# Copyright (C) 2013-2020 Robin Rawson-Tetley
# This file is distributed under the same license as the ASM3 package.
# Robin Rawson-Tetley <robin@sheltermanager.com>, 2020.

msgid ""
msgstr ""
"Project-Id-Version: ASM3\\n"
"Report-Msgid-Bugs-To: robin@sheltermanager.com\\n"
"POT-Creation-Date: %s+0000\\n"
"Last-Translator: Robin Rawson-Tetley <robin@sheltermanager.com>\\n"
"Language-Team: en <robin@sheltermanager.com>\\n"
"Language: en\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

""" % ( datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d %H:%M") )

for string, fname in iter(sorted(strings.items())):
    locs = textwrap.wrap(fname, width=76)
    for l in locs:
        pot += "#: %s\n" % l
    pot += output_msgid(string)
    pot += "msgstr \"\"\n\n"

print(pot)


