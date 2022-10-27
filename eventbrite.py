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
import subprocess

BADGESIZE = "80x50"
DEFAULTBACKGROUND = "background_default.png"
BLANKS = 40
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
    "Pyladies" : DEFAULTBACKGROUND,
    "Personal - invoiced" : "background_personal.png",
    "Wait list" : DEFAULTBACKGROUND
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

def shellExec(command):
    return subprocess.check_output(command.split(), stderr=subprocess.STDOUT, shell=False)

class BadgePrinter:
    def __init__(self):
        with open("badges/4BadgesOnA4.svg", encoding="UTF-8") as fileDescr:
            self.badgesPage = fileDescr.read()

        createDirs(OUTPUTDIR)

    def generateBadges(self, participants, pageNumber, background=None):
        print(f"-= PageNumber: {pageNumber} =-")
        badgesPage = self.badgesPage
        mainBackground = None
        if background is not None:
            mainBackground = background
        for position, entry in enumerate(participants):
            try:
                fullName, ticketType, company, jobTitle = entry
                # some companies are too wide
                if len(company) > 45:
                    company = company[:45]
            except ValueError as e:
                print("Error in: ", entry)
                raise Exception(e)
            if (position % 2) == 0:
                print("\t", position, fullName, end='')
            else:
                print("\t", position, fullName)
            nameBlks = fullName.split(" ")
            if len(nameBlks) >= 2:
                firstName = nameBlks[0]
                lastName = nameBlks[1]
            else:
                firstName = ""
                lastName = ""
            badgesPage = badgesPage.replace("person_{}_line_1".format(position + 1), firstName)
            badgesPage = badgesPage.replace("person_{}_line_2".format(position + 1), lastName)
            badgesPage = badgesPage.replace("person_{}_line_3".format(position + 1), jobTitle)
            badgesPage = badgesPage.replace("person_{}_line_4".format(position + 1), company)
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
        shellExec(f"inkscape --pipe --export-dpi=300 --export-filename={pdf} {svg}")

def getBackGround(ticketCode):
    if ticketCode in BADGES:
        return BADGES[ticketCode]
    raise Exception(f"Unknown ticket code: {ticketCode}")

def groupBackGrounds(array_ticketCodes):
    result = []
    for ticketCode in array_ticketCodes:
        result.append(getBackGround(ticketCode))

    return result

def getUserDataFormatted(fullName=None, ticketType=None, company=None, jobTitle=None):
    if fullName is None:
        fullName = ""
    if ticketType is None:
        ticketType = ""
    if company is None:
        company = ""
    if jobTitle is None:
        jobTitle = ""

    return [ fullName, ticketType, company, jobTitle]
    

def resetParticipantsData():
    return []

def numberOfParticipants(participantsList):
    return len(participantsList)

def main(args):
    with open(args.csvfile, encoding='utf-8') as csvFile:
        bdgp = BadgePrinter()
        reader = csv.DictReader(csvFile)
        counter = 0
        pages = 1
        participants = []

        for row in reader:
            if row["Attendee Status"] != "Attending":
                continue
            # limit to 50 characters for company and job title
            fullName = html.escape(row['Name'])
            company = html.escape(row['Company'])[:48]
            ticketType = html.escape(row['Ticket Type'])
            jobTitle = html.escape(row['Job title'])[:48]
            print(f"{counter}) {fullName} from {company} at {ticketType} as {jobTitle}")
            background = getBackGround(ticketType)
            participants.append(getUserDataFormatted(fullName, ticketType, company, jobTitle))
            if numberOfParticipants(participants) >= BADGES_PER_PAGE:
                bdgp.generateBadges(participants, pages)
                participants = resetParticipantsData()
                pages += 1
            counter += 1

        # it ended in nr different than 4
        if len(participants) > 0: 
            for dummy in range(4 - len(participants)):
                participants.append(getUserDataFormatted(ticketType="Business"))
            bdgp.generateBadges(participants, pages)
            pages += 1

        # generating blanks
        #for bg in groupBackGrounds(["Business", "Student", "Speakers", "Volunteers and board", "Last call"]):
        for bg in groupBackGrounds(["Last call"]):
            blanks = resetParticipantsData()
            for x in range(BLANKS):
                print("Blank: ", x)
                blanks.append(getUserDataFormatted())
                if len(blanks) >= BADGES_PER_PAGE:
                    bdgp.generateBadges(blanks, pages, background=bg)
                    blanks = resetParticipantsData()
                    pages += 1
                counter += 1
    print("Total pages:", pages)
    print("Total badges:", counter)
    pdfFiles = []
    for p in range(1, pages):
        pdfFiles.append(f"{OUTPUTDIR}/badge-{p}.pdf")
    #os.system("pdfunite %s all_badges.pdf" % " ".join(pdfFiles))
    # ghostscript just because there is no pdfunit in macos
    shellExec("gs -dNOPAUSE -sDEVICE=pdfwrite -sOUTPUTFILE=all_badges.pdf -dBATCH %s" % " ".join(pdfFiles))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create badges for PyCon Sweden 2022.')
    parser.add_argument('--csvfile', help='CSV file with input data')

    args = parser.parse_args()
    main(args)
