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
    "Business" : DEFAULTBACKGROUND,
    "Business - Invoiced" : DEFAULTBACKGROUND,
    "Early Bird" : DEFAULTBACKGROUND,
    "Personal" : DEFAULTBACKGROUND,
    "Speakers" : "background_speaker.png",
    "Student" : "background_student.png",
    "Volunteers and board" : "background_organization.png"
}

OUTPUTDIR = "generated"

# it doesn't work...
os.environ["PYTHONIOENCODING"] = "utf-8"

class BadgePrinter:

    def __init__(self):
        with open("badges/4BadgesOnA4.svg", encoding="UTF-8") as fileDescr:
            self.badgesPage = fileDescr.read()

        if not os.path.exists(OUTPUTDIR):
            os.makedirs(OUTPUTDIR)
            for fileName in os.listdir("badges"):
                if not re.search(".png", fileName):
                    continue
                shutil.copy("badges/%s" % fileName, "%s/%s" %
                    (OUTPUTDIR, fileName))

    def generateBadges(self, participants, pageNumber, background=None):
        badgesPage = self.badgesPage
        mainBackground = None
        if background is not None:
            mainBackground = background
        for position, entry in enumerate(participants):
            fullName, company, ticketType, jobTitle = entry
            if (position % 2) == 0:
                print("\t", position, fullName, end='')
            else:
                print("\t", position, fullName)
            badgesPage = badgesPage.replace("person_{}_line_1".format(position + 1), fullName[:15])
            badgesPage = badgesPage.replace("person_{}_line_2".format(position + 1), company[:16])
            badgesPage = badgesPage.replace("person_{}_line_3".format(position + 1), jobTitle[:16])
            badgesPage = badgesPage.replace("person_{}_line_4".format(position + 1), "")
            if mainBackground:
                background = mainBackground
                pass
            elif not ticketType in BADGES:
                background = DEFAULTBACKGROUND
            else:
                background = BADGES[ticketType]
            badgesPage = badgesPage.replace("background_{}.png".format(position + 1), background)
        target = "%s/badge-%02d.svg" % (OUTPUTDIR, pageNumber)
        pdf = "%s/badge-%02d.pdf" % (OUTPUTDIR, pageNumber)
        with open(target, "w", encoding="UTF-8") as output:
            output.write(badgesPage)
        print("Generating page:", pageNumber)
        os.system("rsvg-convert -f pdf -o %s %s" % (pdf, target))

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
            fullName = html.escape(row['First Name'] + " " + row['Last Name'])
            company = html.escape(row['Company'])
            ticketType = row['Ticket Type']
            jobTitle = html.escape(row['Job Title'])
            print(u"%d) %s from %s at %s as %s" % \
                (counter, fullName, company, ticketType, jobTitle))
            participants.append([fullName, company, ticketType, jobTitle])
            if len(participants) >= BADGES_PER_PAGE:
                bdg.generateBadges(participants, pages)
                participants = []
                pages += 1
            counter += 1
        for bg in [DEFAULTBACKGROUND,  BADGES["Student"], BADGES["Speakers"], BADGES["Volunteers and board"]]:
            blanks = []
            for x in range(BLANKS):
                print("Blank: ", x)
                blanks.append(["", "", "", ""])
                if len(blanks) >= BADGES_PER_PAGE:
                    bdg.generateBadges(blanks, pages, background=bg)
                    blanks = []
                    pages += 1
                counter += 1
    print("Total pages:", pages)
    print("Total badges:", counter)
    pdfFiles = []
    for p in range(1, pages):
        pdfFiles.append("%s/badge-%02d.pdf" % (OUTPUTDIR, p))
    #os.system("pdfunite %s all_badges.pdf" % " ".join(pdfFiles))
    # ghostscript just because there is no pdfunit in macos
    os.system("gs -dNOPAUSE -sDEVICE=pdfwrite -sOUTPUTFILE=all_badges.pdf -dBATCH %s" % " ".join(pdfFiles))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create badges for IMC2017.')
    parser.add_argument('csv_file', help='CSV file with input data')

    args = parser.parse_args()

    main(args)
