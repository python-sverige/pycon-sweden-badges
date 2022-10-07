#!/usr/bin/env python3
# coding=utf-8
import argparse
import csv
import math
import os
import subprocess
import textwrap
import sys
import html
import sys
import re
import shutil

BADGESIZE = "80x50"
DEFAULTBACKGROUND = "background_default.png"
BLANKS = 12
BADGES_PER_PAGE = 4
BADGES_TEMPLATE = "badges/4BadgesOnA4.svg"
BADGES = {
    "Early Bird" : DEFAULTBACKGROUND,
    "Early Bird Special" : DEFAULTBACKGROUND,
    "Authors Thank You Ticket" : DEFAULTBACKGROUND,
    "Business" : DEFAULTBACKGROUND,
    "Personal" : "background_personal.png",
    "Student" : "background_student.png",
    "Business - Invoiced" : DEFAULTBACKGROUND,
    "Volunteers and board" : "background_organization.png",
    "Speakers" : "background_speaker.png",
    "Last call" : "background_lastcall.png",
    "Business 50%" : DEFAULTBACKGROUND,
    "Sponsors" : DEFAULTBACKGROUND,
    "Pyladies" : DEFAULTBACKGROUND
}

OUTPUTDIR = "generated"

# it doesn't work...
os.environ["PYTHONIOENCODING"] = "utf-8"

def createDirs(directory):
    '''
    It creates the need directory if it isn't there yet.
    '''
    if not os.path.exists(directory):
        os.makedirs(directory)

class BadgePrinter:
    def __init__(self):
        with open("badges/4BadgesOnA4.svg", encoding="UTF-8") as fileDescr:
            self.badgesPage = fileDescr.read()

        createDirs(OUTPUTDIR)

        #for fileName in os.listdir("badges"):
        #    if not re.search(".png", fileName):
        #        continue
        #    shutil.copy(f"badges/{fileName}", f"{OUTPUTDIR}/{fileName}")

    def generateBadges(self, participants, pageNumber, background=None):
        print(f"-= PageNumber: {pageNumber} =-")
        badgesPage = self.badgesPage
        mainBackground = None
        if background is not None:
            mainBackground = background
        for position, entry in enumerate(participants):
            try:
                fullName, ticketType = entry
            except ValueError as e:
                print("Error in: ", entry)
                raise Exception(e)
            if (position % 2) == 0:
                print("\t", position, fullName, end='')
            else:
                print("\t", position, fullName)
            namePieces = fullName.split(" ")
            badgesPage = badgesPage.replace("person_{}_line_1".format(position + 1), namePieces[0])
            badgesPage = badgesPage.replace("person_{}_line_2".format(position + 1), namePieces[-1])
            badgesPage = badgesPage.replace("person_{}_line_3".format(position + 1), "")
            badgesPage = badgesPage.replace("person_{}_line_4".format(position + 1), "")
            if mainBackground:
                background = mainBackground
                pass
            elif not ticketType in BADGES:
                background = DEFAULTBACKGROUND
            else:
                background = BADGES[ticketType]
            if not os.path.exists("badges/" + background):
                raise Exception(f"{background} not found")
            badgesPage = badgesPage.replace("background_{}.png".format(position + 1), background)
            cwd = os.path.abspath(os.path.curdir)
            badgesPage = badgesPage.replace("$PWD", cwd)

        svg = f"{OUTPUTDIR}/badge-{pageNumber}.svg"
        pdf = f"{OUTPUTDIR}/badge-{pageNumber}.pdf"
        with open(svg, "w", encoding="UTF-8") as output:
            output.write(badgesPage)
        print("Generating page:", pageNumber)
        #os.system(f"rsvg-convert -f pdf -o {pdf} {target}")
        ### using inkscape directly
        os.system(f"cat {svg}  | inkscape --pipe --export-filename={pdf}")

def getBackGround(ticketCode):
    if ticketCode in BADGES:
        return BADGES[ticketCode]
    raise Exception(f"Unknown ticket code: {ticketCode}")

def groupBackGrounds(array_ticketCodes):
    result = []
    for ticketCode in array_ticketCodes:
        result.append(getBackGround(ticketCode))

    return result

def main(args):
    with open(args.csv_file, encoding='utf-8') as csvFile:
        bdg = BadgePrinter()
        reader = csv.DictReader(csvFile)
        counter = 0
        pages = 1
        participants = []

        for row in reader:
            if row["Attendee Status"] != "Attending":
                continue
            fullName = html.escape(row['Name'])
            #company = html.escape(row['Company'])
            ticketType = row['Ticket Type']
            #jobTitle = html.escape(row['Jmeob Title'])
            #print(f"{counter}) {fullName} from {company} at {ticketType} as {jobTitle}")
            background = getBackGround(ticketType)
            print(f"{counter}) {fullName} from at {ticketType} using bg {background}")
            participants.append([fullName, ticketType])
            if len(participants) >= BADGES_PER_PAGE:
                bdg.generateBadges(participants, pages)
                participants = []
                pages += 1
            counter += 1

        # it ended in nr different than 4
        if len(participants) > 0: 
            for dummy in range(4 - len(participants)):
                participants.append(["", "Business"])
            bdg.generateBadges(participants, pages)
            pages += 1

        # generating blanks
        #for bg in groupBackGrounds(["Business", "Student", "Speakers", "Volunteers and board", "Last call"]):
        for bg in groupBackGrounds(["Last call"]):
            blanks = []
            for x in range(BLANKS):
                print("Blank: ", x)
                blanks.append(["",  ""])
                if len(blanks) >= BADGES_PER_PAGE:
                    bdg.generateBadges(blanks, pages, background=bg)
                    blanks = []
                    pages += 1
                counter += 1
    print("Total pages:", pages)
    print("Total badges:", counter)
    pdfFiles = []
    for p in range(1, pages):
        pdfFiles.append(f"{OUTPUTDIR}/badge-{p}.pdf")
    #os.system("pdfunite %s all_badges.pdf" % " ".join(pdfFiles))
    # ghostscript just because there is no pdfunit in macos
    os.system("gs -dNOPAUSE -sDEVICE=pdfwrite -sOUTPUTFILE=all_badges.pdf -dBATCH %s" % " ".join(pdfFiles))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create badges for IMC2017.')
    parser.add_argument('csv_file', help='CSV file with input data')

    args = parser.parse_args()

    main(args)
