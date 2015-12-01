import sys
import subprocess
import os
import time
from easygui import multenterbox, choicebox

# Store the filename without extension.
filename_without_path = os.path.basename(sys.argv[1])

# Store the current time in ISO8601 format.
time = time.strftime("%Y-%m-%dT%H:%M:%S")

# Begin Interview using Easygui.
msg ="Which Workflow?"
title = "Workflows"
choices = ["Telecine One Light", "bestlight", "Telecine Grade", "Tape Ingest 1", "Tape Ingest 2", "Tape Edit Suite 1", "Tape Edit Suite 2"]
choice = choicebox(msg, title, choices)

msg ="Preperation?"
title = "Workflows"
choices = ["Splice and perforation check", "Splice and perforation check & repairs", "Splice and perferation check & repairs & leader added", "Splice and perforation check and leader added", ]
preperation = choicebox(msg, title, choices)

# Forking path in order to get more accurate info depending on workflow
if choice not in ("Telecine One Light", "bestlight", "Telecine Grade"):
    msg ="Tape Deck?"
    title = "Pick a name yo!"
    choices = ["DVW-A500p", "MiniDV-Something", "UVW-1800P", "J-30", "J-H1", "Another Beta gizmo", "Unknown"]
    deck = choicebox(msg, title, choices)
# Currently unused, but I'll get around to it :[
else:
    msg ="Telecine Machine"
    title = "Pick a name yo!"
    choices = ["Flashtransfer", "Flashscan",]
    scanner = choicebox(msg, title, choices)

#More interviews    
msg ="User?"
title = "Pick a name yo!"
choices = ["Kieran O'Leary", "Gavin Martin", "Dean Kavanagh", "Raelene Casey", "Anja Mahler", "Eoin O'Donohoe", "Unknown"]
user = choicebox(msg, title, choices)

msg = "Fill out these things please"
title = "blablablabl"
fieldNames = ["Source Accession Number","Notes","Filmographic Reference Number"]
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
        
# Prints info to screen. Make this actually useful! 
print "Reply was:", fieldValues

# Generate filename for the reVTMD xmlfile
revtmd_xmlfile = sys.argv[1] + '.xml'


# Store md5 checksum.
print 'generating md5 checksum, this may take some time'
md5 = subprocess.check_output(['md5deep', '-e', sys.argv[1]])
# Begin creating functions for repetitive tasks:
# Generate xml elements for coding process history.
def revtmd_coding_process_history():
    fo.write('<revtmd:codingProcessHistory>\n')
    fo.write('<revtmd:role/>\n')
    fo.write('<revtmd:description/>\n')
    fo.write('<revtmd:manufacturer/>\n')
    fo.write('<revtmd:modelName/>\n')
    fo.write('<revtmd:version/>\n')
    fo.write('<revtmd:serialNumber/>\n')
    fo.write('<revtmd:signal/>\n')
    fo.write('<revtmd:settings/>\n')
    fo.write('<revtmd:videoEncoding/>\n')
    fo.write('</revtmd:codingProcessHistory>\n')

# Create mostly blank reVTMD template which we'll gradually fill up with info.
with open(revtmd_xmlfile, "w+") as fo:

    fo.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    fo.write('<revtmd xmlns:revtmd="http://nwtssite.nwts.nara/schema/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://nwtssite.nwts.nara/schema/  http://www.archives.gov/preservation/products/reVTMD.xsd">\n')
    fo.write('<revtmd:reVTMD>\n')
    fo.write('<revtmd:object>\n')
    fo.write('<revtmd:filename/>\n')
    fo.write('<revtmd:organization>\n')
    fo.write('<revtmd:organization_main>\n')
    fo.write('<revtmd:name>Irish Film Institute</revtmd:name>\n')
    fo.write('<revtmd:role/>\n')
    fo.write('</revtmd:organization_main>\n')
    fo.write('<revtmd:organization_division>\n')
    fo.write('<revtmd:name>Irish Film Archive</revtmd:name>\n')
    fo.write('</revtmd:organization_division>\n')
    fo.write('</revtmd:organization>\n')
    fo.write('<!-- Use for custodian of the content item -->\n')
    fo.write('<revtmd:organization>\n')
    fo.write('<revtmd:organization_main>\n')
    fo.write('<revtmd:name/>\n')
    fo.write('<revtmd:role/>\n')
    fo.write('<revtmd:role_note/>\n')
    fo.write('</revtmd:organization_main>\n')
    fo.write('</revtmd:organization>\n')
    fo.write('<revtmd:identifier/>\n')
    fo.write('<revtmd:mimetype/>\n')
    fo.write('<revtmd:checksum algorithm="md5" dateTime="%s">%s</revtmd:checksum>\n' % (time,md5.split()[0])) 
    fo.write('<!-- Checksum as generated immediately after the digitization process. -->\n')
    fo.write('<revtmd:use/>\n')
    fo.write('<revtmd:captureHistory>\n')
    fo.write('<revtmd:digitizationDate/>\n')
    fo.write('<revtmd:digitizationEngineer/>\n')
    fo.write('<revtmd:preparationActions/>\n')
    fo.write('<revtmd:preparationActions/>\n')
    revtmd_coding_process_history()
    revtmd_coding_process_history()
    revtmd_coding_process_history()
    revtmd_coding_process_history()
    revtmd_coding_process_history()
    revtmd_coding_process_history()
    revtmd_coding_process_history()
    fo.write('</revtmd:captureHistory>\n')
    fo.write('</revtmd:object>\n')
    fo.write('</revtmd:reVTMD>\n')
    fo.write('</revtmd>\n')
    
# This function actually adds value to a specified xml element.    
def add_to_revtmd(element, value, xmlfile):
    subprocess.call(['xml', 'ed', '--inplace', '-N', 'x=http://nwtssite.nwts.nara/schema/', '-u', element, '-v', value, xmlfile])
    
# What follows are a lot of functions that can be reused. Titles should be self explanatory.
def ffmpeg_revtmd(numbo):
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:role', 'Transcode', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:description', 'Transcode to FFv1 in Matroska wrapper', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:manufacturer', 'ffmpeg', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:modelName', '2.8.2', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:videoEncoding', "FFv1", revtmd_xmlfile)
    
def avid_capture_revtmd(numbo):
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:role', 'Capture', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:description', 'SDI bitstream capture', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:manufacturer', 'Avid', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:modelName', 'Media Composer', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:version', '8.3.0', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:serialNumber', 'ABC123', revtmd_xmlfile)
def telecine_mac_pro_revtmd(numbo):
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:role', 'Host Computer', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:description', 'Provides computing environment', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:manufacturer', 'Apple', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:modelName', 'Mac Pro', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:version', 'dunno', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:serialNumber', 'ABC123', revtmd_xmlfile)
def telecine_mac_pro_os_revtmd(numbo):
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:role', 'Host Computer Operating System', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:description', 'Provides computing environment operating system', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:manufacturer', 'Apple', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:modelName', 'Mavericks', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:version', 'dunno', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:serialNumber', 'ABC123', revtmd_xmlfile)
def avid_export_revtmd(numbo):
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:role', 'Transcode', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:description', 'Transcode to v210 in quicktime wrapper', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:manufacturer', 'Avid', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:modelName', 'Media Composer', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:version', '8.3.0', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:videoEncoding', "v210", revtmd_xmlfile)
def avid_consolidate_revtmd(numbo):
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:role', 'File Editing', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:description', 'Add plate, consolidate multiple clips', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:manufacturer', 'Avid', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:modelName', 'Media Composer', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:version', '8.3.0', revtmd_xmlfile)
def flashtransfer(numbo):
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:role', 'Telecine', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:description', '16mm Film Digitisation', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:manufacturer', 'MWA', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:modelName', 'Flashtransfer', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:signal', 'SDI', revtmd_xmlfile)
    add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '/revtmd:serialNumber', 'ABC123', revtmd_xmlfile)

# Combine previous functions for the bestlight workflow  
def bestlight():
        
    add_to_revtmd('//revtmd:filename', filename_without_path, revtmd_xmlfile)
    add_to_revtmd('//revtmd:identifier', fieldValues[0], revtmd_xmlfile)
    flashtransfer(1)
    avid_capture_revtmd(4)
    add_to_revtmd('//revtmd:digitizationEngineer[1]', user, revtmd_xmlfile)
    avid_consolidate_revtmd(5)
    avid_export_revtmd(6)
    ffmpeg_revtmd(7)
    telecine_mac_pro_revtmd(2)
    telecine_mac_pro_os_revtmd(3)
    
# Currently just a test. Not useful yet.
# def ingest1():
#
#     add_to_revtmd('//revtmd:filename', filename_without_path, revtmd_xmlfile)
#     add_to_revtmd('//revtmd:identifier', fieldValues[0], revtmd_xmlfile)
#     add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '1]/revtmd:role', 'Playback', revtmd_xmlfile)
#     add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '1]/revtmd:description', '16mm Film Digitisation', revtmd_xmlfile)
#     add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '1]/revtmd:manufacturer', 'MWA', revtmd_xmlfile)
#     add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '1]/revtmd:modelName', 'Flashtransfer', revtmd_xmlfile)
#     add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '1]/revtmd:signal', 'SDI', revtmd_xmlfile)
#     add_to_revtmd('//revtmd:codingProcessHistory' + str([numbo]) + '1]/revtmd:serialNumber', 'ABC123', revtmd_xmlfile)
#     add_to_revtmd('//revtmd:digitizationEngineer[1]', user, revtmd_xmlfile)
#
#     avid_export_revtmd()
#     ffmpeg_revtmd()

# This launches the xml creation based on your selections  
if choice == "bestlight":
    bestlight()
elif choice =="Tape Ingest 1":
    ingest1()

