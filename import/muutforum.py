#!/usr/bin/env python3

import datetime, time
import json

def unix2display(t):
    """ Convert UNIX date to display date"""
    p = datetime.datetime.fromtimestamp(float(t))
    return time.strftime("%Y-%m-%d %H:%M:%S", p.timetuple())

def escapeHTML(s):
    return s.replace("<", "&lt;").replace(">", "&gt;")

with open("/home/robin/Downloads/20230819_muut_backup.json", "r") as f:
    s = f.read()

d = json.loads(s)

print("<!DOCTYPE html>" \
    "<html>" \
    "<head>" \
    "<meta charset=\"utf-8\">" \
    "<style>" \
    "* { font-family: sans-serif }" \
    "</style>" \
    "</head>" \
    "<body>")
print("<h1>Forum Archive</h1>")
print("<p>Below are all the posts from the sheltermanager forum that was previously hosted on muut.com. As of 6th November 2023, we have switched to github discussions.</p>")
print("<p>Use the find facility in your browser (usually CTRL+F) to search this page.</p>")
threads = d["threads"]["/asm3"] + d["threads"]["/general"] + d["threads"]["/asm2"]
threads = sorted(threads, key=lambda x: x["seed"]["date"], reverse=True)
for item in threads:
    t = item["seed"]
    title = t["title"]
    body = escapeHTML(t["body"])
    dt = unix2display(t["date"])
    author = t["author"]["path"]
    img = t["author"]["img"]
    print(f"<h2>{title}</h2>")
    print(f"<p><img style='height: 50px; vertical-align: middle' src='https:{img}'/> <b>{author}</b>: <i>{dt}</i><br>{body}</p>")
    for r in sorted(item["replies"], key=lambda x: x["date"]):
        body = escapeHTML(r["body"])
        author = r["author"]["path"]
        img = r["author"]["img"]
        dt = unix2display(r["date"])
        print(f"<p style='margin-left: 40px'><img style='height: 50px; vertical-align: middle' src='https:{img}'/> <b>{author}</b>: <i>{dt}</i><br>{body}</p>")
    print("<hr>")

print("</body></html>")
