#!/usr/bin/env python3

# Converts all .po files in the current directory to 
# python and javascript modules

import os

def chopvalue(s):
    return s[s.find("\"")+1:s.rfind("\"")]

dirlist = os.listdir(".")
for pofile in dirlist:
    if pofile.endswith(".po"):

        print("Processing: %s" % pofile)
        with open(pofile, "r") as f:
            lines = f.readlines()
       
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
                v += chopvalue(l)
        
        # Build up the python representation of it and write it out
        s = "# " + pofile + "\n\n"
        s += "val = {"
        first = True
        for k, v in strings.items():
            if k == "": continue
            if not first: s += ",\n"
            first = False
            s += "\"%s\" : \"%s\"" % (k, v)
        s += "\n}\n"
        outfile = "locale_" + pofile.replace(".po", ".py")
        with open(outfile, "wb") as f:
            f.write(s.encode("utf-8"))

        # Now do a javascript version
        s = "// " + pofile + "\n\n"
        s += "i18n_lang = {"
        first = True
        for k, v in strings.items():
            if k == "": continue
            if not first: s += ",\n"
            first = False
            s += "\"%s\" : \"%s\"" % (k, v)
        s += "\n};\n"
        s += """
        _ = function(key) {
            try {
                var v = key;
                if (i18n_lang.hasOwnProperty(key)) {
                    if ($.trim(i18n_lang[key]) != "" && i18n_lang[key].indexOf("??") != 0 && i18n_lang[key].indexOf("(??") != 0) {
                        v = i18n_lang[key];
                    }
                    else {
                        v = key;
                    }
                }
                else {
                    v = key;
                }
                return $("<div></div>").html(v).text();
            }
            catch (err) {
                return "[error]";
            }
        };
        """
        outfile = "locale_" + pofile.replace(".po", ".js")
        with open(outfile, "wb") as f:
            f.write(s.encode("utf-8"))


