#!/usr/bin/env python

# Make a csv file, that matches Kevin's spreadsheet, from the TNA Archive dump

import os
import sys
import json
import argparse
import re
from calendar import monthrange

parser = argparse.ArgumentParser()
parser.add_argument("--rg", help="Record group", type=int, required=True)
parser.add_argument(
    "--subgroup", help="Record group file", type=int, required=False, default=None
)
parser.add_argument("--series", help="Series", type=int, required=True)
parser.add_argument("--match", help="Filter", type=str, required=False, default=None)
parser.add_argument("--title", default=False, action="store_true")
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

# Most of the work is in parsing the 'title' field, which is a string containing
#  the ship name, maybe class and number ('DD-119'), maybe date or date range, and
#  maybe other stuff, in several different formats.
mnames = (
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
)


def getNameFromTitle(title):
    shipName = title
    # If title contains ':' strip everything afterwards
    pIdx = shipName.find(":")
    if pIdx > 0:
        shipName = shipName[: pIdx ]
    # If title contains '(' strip everything afterwards
    pIdx = shipName.find("(")
    if pIdx > 0:
        shipName = shipName[: pIdx ]
    # If title contains a date, strip date and everything afterwards
    rx = re.search("\d+/\d+/", shipName)
    if rx is not None:
        shipName = shipName[: rx.span()[0]]
    rx = re.search("- \w+ \d\d\d\d/", shipName)
    if rx is not None:
        shipName = shipName[: rx.span()[0]]
    # Get rid of 'Log of the' and similar
    pIdx = shipName.find(' of the ')
    if pIdx > 0:
        shipName = shipName[(pIdx+8) : ]
    pIdx = shipName.find(' of ')
    if pIdx > 0:
        shipName = shipName[(pIdx+4) : ]
    # rationalise U.S.S to USS
    pIdx = shipName.find('U.S.S.')
    if pIdx > -1:
        shipName = "USS %s" % shipName[(pIdx+6) : ]
    return shipName


def getClassFromTitle(title):
    rx = re.search("\(\w+-\d+\)", title)
    if rx is not None:
        classN = rx.group()
        return classN
    raise Exception("Class not found")


def getStartDateFromTitle(title):
    rx = re.search("(\d+)/(\d+)/(\d+)\D+(\d+)/(\d+)/(\d+)", title)
    if rx is not None:
        return [int(rx.groups()[2]), int(rx.groups()[0]), int(rx.groups()[1])]
    rx = re.search("- \w+ (\d\d\d\d)/", title)
    if rx is not None:
        mmatch = -1
        for count in range(len(mnames)):
            if title.lower().find(mnames[count]) > -1:
                mmatch = count + 1
                break
        return [int(rx.groups()[0]), mmatch, 1]
    raise Exception("Date not found")


def getEndDateFromTitle(title):
    rx = re.search("(\d+)/(\d+)/(\d+)\D+(\d+)/(\d+)/(\d+)", title)
    if rx is not None:
        return [int(rx.groups()[5]), int(rx.groups()[3]), int(rx.groups()[4])]
    rx = re.search("- \w+ (\d\d\d\d)/", title)
    if rx is not None:
        mmatch = -1
        for count in range(len(mnames)):
            if title.lower().find(mnames[count]) > -1:
                mmatch = count + 1
                break
        return [int(rx.groups()[0]), mmatch, monthrange(rx.groups()[0], mmatch)[1]]
    raise Exception("Date not found")


def getEndDate(record):
    try:
        ed = record["coverageDates"]["coverageEndDate"]
        if "logicalDate" in ed:
            return (
                int(ed["logicalDate"][:4]),
                int(ed["logicalDate"][5:7]),
                int(ed["logicalDate"][8:10]),
            )
        else:
            return (
                int(ed["year"]),
                int(ed["month"]),
                monthrange(int(ed["year"]), int(ed["month"]))[1],
            )
    except Exception:
        return getEndDateFromTitle(record["title"])


def getStartDate(record):
    try:
        ed = record["coverageDates"]["coverageStartDate"]
        if "logicalDate" in ed:
            return (
                int(ed["logicalDate"][:4]),
                int(ed["logicalDate"][5:7]),
                int(ed["logicalDate"][8:10]),
            )
        else:
            return (
                int(ed["year"]),
                int(ed["month"]),
                1,
            )
    except Exception:
        return getStartDateFromTitle(record["title"])


# Add the column titles if requested
if args.title:
    fw.write("%-30s,%-12s,%-12s,%-12s,%-12s,%-20s,%-10s,%-10s,%-50s,%-12s,%s\n" % (
        "Ship Name","Hull No.","Record Group","Series NAID","Record Entry","Container",
        "StartDate","EndDate","Nara URL","#Images","Document URL")
    )


# Get rid of any commas (bad in CSV)
def stripC(inpS):
    opS = inpS
    while opS.find(",") >= 0:
        opS = opS.replace(",", " ")
    return opS


for filen in fileN:
    fd = open(filen, "r")
    while True:
        line = fd.readline()
        if not line:
            break
        if line[0] == ",":
            continue
        if args.match is not None and args.match not in line:
            continue
        if line[:2] == "{[":
            line = line[2:]
        if line[-3:-1] == "]}":
            line = line[:-3] + "\n"
        try:
            fj = json.loads(line)
        except:
            print(line)
            break
        try:
            base = fj["description"]["fileUnit"]
        except Exception:
            continue
        try:
            if int(base["parentSeries"]["naId"]) != args.series:
                continue
        except Exception:
            continue

        try:
            shipName = getNameFromTitle(base["title"])
            fw.write("%-30s," % stripC(shipName))
        except Exception:
            fw.write("%-30s," % " ")

        try:
            hullNo = getClassFromTitle(base["title"])
            fw.write('"%-12s",' % stripC(hullNo))
        except Exception:
            fw.write("%-12s," % " ")

        # Fixed data - record group and parent series
        fw.write("%-12d," % args.rg)
        fw.write("%-12d," % args.series)

        # Record entry?
        try:
            vcn = base["variantControlNumberArray"]["variantControlNumber"]
            for entry in vcn:
                if entry["type"]["naId"] == "10675882":
                    fw.write("%-12s," % stripC(entry["number"]))
                    break
        except Exception as e:
            # sys.stderr.write(repr(e))
            fw.write("%-12s," % " ")

        # Container
        try:
            pFile = base["physicalOccurrenceArray"]["fileUnitPhysicalOccurrence"]
            cid = pFile["mediaOccurrenceArray"]["mediaOccurrence"]["containerId"]
            fw.write("%-20s," % stripC(cid))
        except Exception as e:
            # sys.stderr.write(repr(e))
            fw.write("%-20s," % " ")

        # dates
        try:
            ed = getStartDate(base)
            fw.write("%04d-%02d-%02d," % (ed[0], ed[1], ed[2]))
        except Exception as e:
            fw.write("%10s," % " ")
        try:
            ed = getEndDate(base)
            fw.write("%04d-%02d-%02d," % (ed[0], ed[1], ed[2]))
        except Exception as e:
            fw.write("%10s," % " ")

        # Nara URL
        try:
            fw.write("https://catalog.archives.gov/id/%-18s," % base["naId"])
        except Exception:
            fw.write("%-50s," % " ")

        # Count of images
        try:
            nImages = len(fj["objects"]["object"]) - 1  # Don't count the pdf
            fw.write("%-12d," % nImages)
        except Exception as e:
            # sys.stderr.write(repr(e))
            fw.write("%-12s," % " ")

        # Get the pdf url, if there is one
        try:
            docs = fj["objects"]["object"]
            pdfU = None
            for doc in docs:
                a_url = doc["file"]["@url"]
                ftype = a_url[-3:].lower()
                if ftype == "pdf":
                    pdfU = a_url
                    break
            if pdfU is not None:
                fw.write("%s," % pdfU)
            else:
                fw.write("%12s," % " ")
        except Exception:
            fw.write("%12s," % " ")
        fw.write("\n")
    fd.close()
