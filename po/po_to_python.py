#!/usr/bin/python

# Converts all .po files in the current directory to 
# python modules for use with asm

import os

def chopvalue(s):
    return s[s.find("\"")+1:s.rfind("\"")]

dirlist = os.listdir(".")
for pofile in dirlist:
    if pofile.endswith(".po"):

        print "Processing: " + pofile
        f = open(pofile, "r")
        lines = f.readlines()
        f.close()
       
        # Parse the po file into a dictionary
        strings = {}
        mode = "k"
        k = ""
        v = ""
        for l in lines:
            # if we have msgid go into key mode
            if l.startswith("msgid"):
                mode = "k"
                k = ""
                v = ""
            # we saw a msgstr, go into value mode
            if l.startswith("msgstr"):
                mode = "v"
                v = ""
            # we had a blank line, store the last k/v and go into skip mode
            if l.strip() == "":
                strings[k] = v
                mode = "s"
            # Build up the key or value
            if mode == "k":
                k += chopvalue(l)
            elif mode == "v":
                l = l.decode("utf-8")
                v += chopvalue(l.encode("ascii", "xmlcharrefreplace"))
        
        # Build up the python representation of it and write it out
        s = "# " + pofile + "\n\n"
        s += "val = {"
        first = True
        for k, v in strings.iteritems():
                if not first: s += ",\n"
                first = False
                s += "\"%s\" : \"%s\"" % (k, v)
        s += "\n}\n"
        outfile = "locale_" + pofile.replace(".po", ".py")
        f = open(outfile, "w")
        f.write(s)
        f.flush()
        f.close()

