import os
from fpdf import FPDF

DIRECTORY = "IMG"
WIDTH = 80
HEIGHT = 100
XS = [20, 110]
YS = [30, 137]

pdf = FPDF()
pdf.set_auto_page_break(0)

# Save images
imagelist = [file for file in os.listdir(DIRECTORY) if file.endswith('.png')]

# Loop through
for index, image in enumerate(imagelist):
    if index % 4 == 0:
        pdf.add_page()
        pdf.image(os.path.join(DIRECTORY, image), x=XS[0], y=YS[0], w=WIDTH, h=HEIGHT)
    elif index % 4 == 1:
        pdf.image(os.path.join(DIRECTORY, image), x=XS[1], y=YS[0], w=WIDTH, h=HEIGHT)
    elif index % 4 == 2:
        pdf.image(os.path.join(DIRECTORY, image), x=XS[0], y=YS[1], w=WIDTH, h=HEIGHT)
    elif index % 4 == 3:
        pdf.image(os.path.join(DIRECTORY, image), x=XS[1], y=YS[1], w=WIDTH, h=HEIGHT)
        
# Save PDF
pdf.output('Test.pdf', 'F')