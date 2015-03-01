#!/usr/bin/python
import csv, sys

reader = csv.reader(open(sys.argv[1], "r"), dialect="excel")
for row in reader:
    index = 0
    for r in row:
        print r.upper().replace(" ", "_").replace(".", "_").replace("-", "_") + " = " + str(index)
        index += 1
    break

