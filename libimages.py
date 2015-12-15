import sys
import subprocess
from glob import glob
import os
from easygui import multenterbox, choicebox
from Tkinter import *
import tkFileDialog
root = Tk()
import pdb

# Create file-open dialog.
root.update()
# Directory with files that we want to transcode losslessly and generate metadata for P.S just as for directory instead, fix later.
video_dir 	= tkFileDialog.askdirectory(parent=root)
inmagic_xmlfile = 'blablabla.xml'

os.chdir(video_dir)

# Find all image files
video_files 	  =  glob('*.tif') + glob('*.jpg') + glob('*.jpeg') + glob('*.JPG')
no_of_emptyfields = len(video_files) # the number of inmagic records based on the number of files

msg = "Fill out these things please"
title = "blablablabl"
fieldNames = ["Year",
	      "Film Title","Copyright", 
              "Donation Date", "Director", "Reference number of first record", "Accession number of first record "]
fieldValues = []  # we start with blanks for the values
fieldValues = multenterbox(msg,title, fieldNames)


# make sure that none of the fields was left blank
while 1:
        if fieldValues == None: break
        errmsg = ""
        for i in range(len(fieldNames)):
            if fieldValues[i].strip() == "":
                errmsg = errmsg + ('"%s" is a required field.' % fieldNames[i])
        if errmsg == "": break # no problems found
        fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)
		
msg ="User?"
title = "Pick a name yo!"
choices = ["Fiona Rigney", "Fleur Finley", "Kasandra O'Connell", "Kieran O'Leary"]
user = choicebox(msg, title, choices)
print fieldValues[5]
ref = fieldValues[5]
acc_number = int(fieldValues[6])
number = 0 #Inmagic lists the first record as number 0. the second record is number 1 and so on.
#print noofemptyfields
with open(inmagic_xmlfile, "w+") as fo:

	fo.write('<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>\n')
	fo.write('<inm:Results xmlns:inm="http://www.inmagic.com/webpublisher/query" productTitle="Inmagic DB/TextWorks for SQL" productVersion="13.00">\n')
	fo.write('<inm:Recordset setCount="%s">\n' % no_of_emptyfields)
	fo.write('<inm:Record setEntry="%s">\n' % number)
	fo.write('<inm:Reference-Number>%s</inm:Reference-Number>\n' % ref)
	fo.write('<inm:Type/>\n')
	fo.write('<inm:Item-Title/>\n')
	fo.write('<inm:Film-Title/>\n')
	fo.write('<inm:Year/>\n')
	fo.write('<inm:Country-of-Origin/>\n')
	fo.write('<inm:Language/>\n')
	fo.write('<inm:Notes/>\n')
	fo.write('<inm:Dimensions/>\n')
	fo.write('<inm:Colour/>\n')
	fo.write('<inm:Location-Number/>\n')
	fo.write('<inm:Conservation/>\n')
	fo.write('<inm:Copyright/>\n')
	fo.write('<inm:Access-Restrictions/>\n')
	fo.write('<inm:Acquisition-Source/>\n')
	fo.write('<inm:Acquisition-Method/>\n')
	fo.write('<inm:Date-Created/>\n')
	fo.write('<inm:Edited-By/>\n')
	fo.write('<inm:Date-Last-Modified/>\n')
	fo.write('<inm:Number-Of-Copies/>\n')
	fo.write('<inm:Description/>\n')
	fo.write('<inm:Subject-Headings/>\n')
	fo.write('<inm:Date-Of-Donation/>\n')
	fo.write('<inm:Accession-Number>15/%s</inm:Accession-Number>\n' % str(acc_number).zfill(4) )
	fo.write('<inm:Director/>\n')
	fo.write('<inm:Image/>\n')
	fo.write('<inm:Collection-Name/>\n')
	fo.write('<inm:Collection-Level-Des/>\n')
	fo.write('<inm:Level-of-Description>File</inm:Level-of-Description>\n')
	fo.write('<inm:Digital-or-Hardcopy>Digital</inm:Digital-or-Hardcopy>\n')
	fo.write('<inm:Master-or-Access/>\n')
	fo.write('<inm:Size/>\n')
	fo.write('<inm:Digital-Size/>\n')
	fo.write('<inm:File-Format/>\n')
	fo.write('<inm:Resolution/>\n')
	fo.write('<inm:Depositor-Ref-Number/>\n')
	fo.write('<inm:Movement-Field/>\n')
	fo.write('</inm:Record>\n')
for _ in range(no_of_emptyfields - 1): # -1 because one blank record has already been created
	number += 1
	
	with open(inmagic_xmlfile, "a+") as fo:
		fo.write('<inm:Record setEntry="%s">\n' % number)
		fo.write('<inm:Reference-Number/>\n')
		fo.write('<inm:Type/>\n')
		fo.write('<inm:Item-Title/>\n')
		fo.write('<inm:Film-Title/>\n')
		fo.write('<inm:Year/>\n')
		fo.write('<inm:Country-of-Origin/>\n')
		fo.write('<inm:Language/>\n')
		fo.write('<inm:Notes/>\n')
		fo.write('<inm:Dimensions/>\n')
		fo.write('<inm:Colour/>\n')
		fo.write('<inm:Location-Number/>\n')
		fo.write('<inm:Conservation/>\n')
		fo.write('<inm:Copyright/>\n')
		fo.write('<inm:Access-Restrictions/>\n')
		fo.write('<inm:Acquisition-Source/>\n')
		fo.write('<inm:Acquisition-Method/>\n')
		fo.write('<inm:Date-Created/>\n')
		fo.write('<inm:Edited-By/>\n')
		fo.write('<inm:Date-Last-Modified/>\n')
		fo.write('<inm:Number-Of-Copies/>\n')
		fo.write('<inm:Description/>\n')
		fo.write('<inm:Subject-Headings/>\n')
		fo.write('<inm:Date-Of-Donation/>\n')
		fo.write('<inm:Accession-Number/>\n')
		fo.write('<inm:Director/>\n')
		fo.write('<inm:Image/>\n')
		fo.write('<inm:Collection-Name/>\n')
		fo.write('<inm:Collection-Level-Des/>\n')
		fo.write('<inm:Level-of-Description>File</inm:Level-of-Description>\n')
		fo.write('<inm:Digital-or-Hardcopy>Digital</inm:Digital-or-Hardcopy>\n')
		fo.write('<inm:Master-or-Access/>\n')
		fo.write('<inm:Size/>\n')
		fo.write('<inm:Digital-Size/>\n')
		fo.write('<inm:File-Format/>\n')
		fo.write('<inm:Resolution/>\n')
		fo.write('<inm:Depositor-Ref-Number/>\n')
		fo.write('<inm:Movement-Field/>\n')
		fo.write('</inm:Record>\n')
		
with open(inmagic_xmlfile, "a+") as fo:
		fo.write('</inm:Recordset>\n')
		fo.write('</inm:Results>\n')	
		
numbo = 0
numbo_1 = 1
ref = int(fieldValues[5])

print ref
for filename in video_files: #Begin a loop for all .mov and .mp4 files.
	#pdb.set_trace()
	msg ="User?"
	title = "Depositor?"
	choices = ["IFB", "BAI"]
	#user = choicebox(msg, title, choices)
	print inmagic_xmlfile
	print video_dir
	print video_files
	
	
	ref +=1
	acc_number +=1
	
	print ref
	print fieldValues
	def add_to_inmagic(element, value, xmlfile):
	    subprocess.call(['xmlstarlet', 'ed', '--inplace', '-N', 'x=http://www.inmagic.com/webpublisher/query', '-u', element, '-v', value, xmlfile])
	add_to_inmagic('//inm:Collection-Name', 'BAI',inmagic_xmlfile)
	add_to_inmagic('//inm:Acquisition-Source', 'Broadcasting Authority of Ireland [BAI]',inmagic_xmlfile)
	add_to_inmagic('//inm:Acquisition-Method', 'BAI Delivery',inmagic_xmlfile)
	add_to_inmagic('//inm:Edited-By', user,inmagic_xmlfile)
	add_to_inmagic('//inm:Record' + str([numbo_1 + 1]) +'//inm:Reference-Number',str(ref),inmagic_xmlfile)
	add_to_inmagic('//inm:Record' + str([numbo_1 + 1]) +'//inm:Accession-Number', '15/' + str(acc_number).zfill(4),inmagic_xmlfile)
	numbo_1 += 1
	def get_exiftool(var_type, type, filename):
	    var_type = subprocess.check_output(['exiftool', '-b',
				                 type , filename ])
	    return var_type
	megapixels =  get_exiftool('megapixels', '-Megapixels', filename )
	filesize =  get_exiftool('filesize', '-FileSize', filename )
	codec =  get_exiftool('codec', '-FileType', filename )
	print "processing", filename
	print codec
	print megapixels
	print filesize
	
	numbo +=1
	
	add_to_inmagic('//inm:Record' + str([numbo]) + '//inm:File-Format', codec,inmagic_xmlfile)
	add_to_inmagic('//inm:Record' + str([numbo]) + '//inm:Digital-Size', filesize,inmagic_xmlfile)
	add_to_inmagic('//inm:Record' + str([numbo]) + '//inm:Year', fieldValues[0],inmagic_xmlfile)
	add_to_inmagic('//inm:Record' + str([numbo]) + '//inm:Film-Title', fieldValues[1],inmagic_xmlfile)
	add_to_inmagic('//inm:Record' + str([numbo]) + '//inm:Copyright', fieldValues[2],inmagic_xmlfile)
	add_to_inmagic('//inm:Record' + str([numbo]) + '//inm:Date-Of-Donation', fieldValues[3],inmagic_xmlfile)
	add_to_inmagic('//inm:Record' + str([numbo]) + '//inm:Director', fieldValues[4],inmagic_xmlfile)
	
	
subprocess.call(['xmlstarlet', 'ed', '--inplace','-d',
                '//*[not(./*) and (not(./text()) or normalize-space(./text())="")]',
                 inmagic_xmlfile])
print "You've created", no_of_emptyfields, "Inmagic records. Open the image database, select File ->Import ->select xml file and make sure that ""'check for matching records'"" is not selected" 
