#!/usr/bin/env python

# Take a subset of the TNA catalog (selected by record group, series, and string match)
# parse and pretty-print.

import os
import sys
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--rg", help="Record group", type=int, required=True)
parser.add_argument(
    "--subgroup", help="Record group file", type=int, required=False, default=None
)
parser.add_argument("--match", help="Filter", type=str, required=False, default=None)
parser.add_argument(
    "--startl", help="First line to print", type=int, required=False, default=0
)
parser.add_argument(
    "--endl", help="Last line to print", type=int, required=False, default=None
)
args = parser.parse_args()

# Write to stdout
fw = sys.stdout

# Input files
fileN = []
filed = "%s/WW2_US_logs/US_TNA_Catalog/record-groups/rg_%03d/" % (
    os.getenv("SCRATCH"),
    args.rg,
)
if args.subgroup is not None:
    fileN.append("%s/rg_%03d-%03d.json" % (filed, args.rg, args.subgroup))
else:
    files = os.listdir(filed)
    for fn in files:
        fileN.append("%s/%s" % (filed, fn))

count = 0
for filen in fileN:
    fd = open(filen, "r")
    while True:
        line = fd.readline()
        if not line:
            break
        if args.match is not None and args.match not in line:
            continue
        if line[0] == ",":
            continue
        count += 1
        if count < args.startl:
            continue
        if args.endl is not None and count > args.endl:
            break
        if line[:2] == "{[":
            line = line[2:]
        if line[-3:-1] == "]}":
            line = line[:-3] + "\n"
        try:
            fj = json.loads(line)
        except:
            print(line)
            break
        fw.write(json.dumps(fj, indent=4))
    fd.close()
