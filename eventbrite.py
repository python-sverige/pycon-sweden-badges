#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import argparse
import csv
import math
import os
import subprocess
import textwrap
import sys

BADGESIZE = "80x50"
DEFAULTBACKGROUND = "background.png"
BLANKS = 30
BADGES = {
	"Business" : "background.png",
	"Business - Invoiced" : "background.png",
	"Early Bird" : "background.png",
	"Personal" : "background.png",
	"Speakers" : "background_speaker.png",
	"Student" : "background_student.png",
	"Volunteers and board" : "background_organization.png"
}

class BadgePrinter:

	def __init__(self):

		# sizes in mm

		self.badge_width = int(BADGESIZE.split("x")[0]) + 4
		self.badge_height= int(BADGESIZE.split("x")[1]) + 4
		self.badge_padding = 2

		self.paper_width = 210 # A4 paper

		self.page_leftmargin = 20
		self.page_topmargin = 13

		# duplex printer tend to shift content horizontally when duplexing
		# this offset can be corrected here
		self.printer_leftmargin_offset_flipside = 0

		self.header_height = 18.3

		self.tex_document = ''
		self.badge_counter = 0
		self.backside = []

		self._tex_header = textwrap.dedent(r'''			\documentclass[a4paper]{article}
			\usepackage[a4paper, margin=0pt]{geometry}
			\usepackage[utf8]{inputenc}
			%\usepackage[dvips]{geometry}
			\usepackage[texcoord]{eso-pic}
			\usepackage{picture}
			%\usepackage{parskip}
			\usepackage{graphicx}
			%\usepackage{array}
			\usepackage{xcolor}

			\usepackage[default]{raleway}

			%\setlength{\oddsidemargin}{-15mm}
			\pagestyle{empty}

			\begin{document}
		''')

		self._tex_footer = textwrap.dedent(r'''	      \end{document}''')

		self._tex_newpage = textwrap.dedent(r'''			\vspace*{\fill}
			\newpage
		''')

	def tex_header(self):
		self.tex_document += self._tex_header

	def tex_footer(self):
		self.tex_document += self._tex_footer

	def tex_newpage(self):
		self.tex_document += self._tex_newpage

	def add_badge(self, position, name, affiliation, background, flipside=False):
		# left or right badge, x=0 -> left, x=1 -> right
		x = position % 2
		# badge number from top
		y = int(math.ceil((position + 1)/2.0))

		badge_inner_width = self.badge_width - 2*self.badge_padding
		badge_inner_height = self.badge_height - 2*self.badge_padding

		left_margin = self.page_leftmargin + x*self.badge_width

		if flipside:
			left_margin = self.paper_width - self.page_leftmargin - 2*self.badge_width + x*self.badge_width + self.printer_leftmargin_offset_flipside

		self.tex_document += textwrap.dedent(r'''			\AddToShipoutPictureBG*{
				%%\put(%smm,%smm){\framebox(%smm,%smm){}}
				\put(%smm,%smm){\framebox(%smm,%smm){}}
				\put(%smm,%smm){\includegraphics[width=81mm,height=50mm]{%s}}
				\put(%smm,%smm){\makebox(%smm,%smm){\parbox{80mm}{\centering{\fontsize{20}{20}\selectfont\textbf{%s}\\\vspace{2mm}\fontsize{12}{12}\selectfont\textit{%s}}}}}
			}
		''' % (
			left_margin, -(self.page_topmargin + y*self.badge_height), self.badge_width, self.badge_height,
			left_margin + self.badge_padding, -(self.page_topmargin + y*self.badge_height - self.badge_padding), badge_inner_width, badge_inner_height,
			left_margin + self.badge_padding, -(self.page_topmargin + (y-1)*self.badge_height + self.badge_padding+50), background,
			left_margin + self.badge_padding, -(self.page_topmargin + y*self.badge_height - self.badge_padding), badge_inner_width, badge_inner_height - self.header_height, name, affiliation)
		)

	def next_badge(self, name, affiliation, background):
		affiliation = affiliation.replace('&', '\\&')
		self.add_badge(self.badge_counter % 10, name, affiliation, background)

		self.backside.append((name, affiliation))

		self.badge_counter += 1

		if self.badge_counter % 10 == 0:
			self.tex_newpage()
			self.flush_backside(background)

	def flush_backside(self, background):
		return
		# skip everything
		backsideSize = int(len(self.backside)/2)
		for i in range(backsideSize):
			tmp = self.backside[2*i]
			self.backside[2*i] = self.backside[2*i+1]
			self.backside[2*i+1] = tmp

		if len(self.backside) % 2:
			self.backside.append(self.backside[-1])
			self.backside[-2] = None

		for i, r in enumerate(self.backside):
			if r is not None:
				self.add_badge(i, r[0], r[1], background, flipside=True)

		self.backside = []
		self.tex_newpage()

	def flush_badges(self, background):
		if self.backside:
			self.tex_newpage()
			self.flush_backside(background)

def main(args):
	with open(args.csv_file, encoding='utf-8') as f:

		b = BadgePrinter()
		b.tex_header()
		reader = csv.DictReader(f)
		counter = 0
		for row in reader:
			#if (args.limit and row['Order #'] in args.limit) or not args.limit:
			#	b.next_badge(row['First Name'], row['Last Name'])

			if row["Attendee Status"] != "Attending":
				continue
			fullName = row['First Name'] + " " + row['Last Name']
			company = row['Company']
			ticketType = row['Ticket Type']
			jobTitle = row['Job Title']
			if len(company) > 0:
				if len(jobTitle) > 0:
					jobTitle += " at " + company
				else:
					jobTitle = company
			print(counter, fullName, company, ticketType, jobTitle)
			if not ticketType in BADGES:
				background = DEFAULTBACKGROUND
			else:
				background = BADGES[ticketType]
			b.next_badge(fullName, jobTitle, background)
			counter += 1
		for x in range(BLANKS):
			print("Blank: ", x)
			b.next_badge("", "", DEFAULTBACKGROUND)

	#b.flush_badges(DEFAULTBACKGROUND)
	b.tex_footer()

	p = subprocess.Popen(['pdflatex', '-jobname=badges'],
			stdin=subprocess.PIPE,
			stdout=subprocess.DEVNULL,
			encoding='utf8')

	with open('debug.tex', 'w', encoding="utf-8") as f:
		f.write(b.tex_document)

	p.communicate(input=b.tex_document)

	os.remove('badges.aux')
	os.remove('badges.log')

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Create badges for IMC2017.')
	parser.add_argument('csv_file', help='CSV file with input data')

	args = parser.parse_args()

	main(args)
