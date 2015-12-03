# Written by Kieran O'Leary, with a major review and overhaul/cleanup by Zach Kelling aka @Zeekay
# Makes a single ffv1.mkv

import subprocess
import sys
import filecmp
from glob import glob
import os
from Tkinter import *
import tkFileDialog
root = Tk()

# Create file-open dialog.
root.update()
# Directory with files that we want to transcode losslessly and generate metadata for
filename = tkFileDialog.askopenfilename(parent=root)
filenoext = os.path.splitext(filename)[0]
# Change directory to directory with video files


print filenoext
# Generate new directory names in AIP
metadata_dir   = "%s/metadata" % filenoext

data_dir   = "%s/data" % filenoext
provenance_dir   = "%s/provenance" % filenoext

# Actually create the directories.
os.makedirs(metadata_dir)
os.makedirs(data_dir)
os.makedirs(provenance_dir)

#Generate filenames for new files in AIP.
inputxml  = "%s/%s.xml" % (metadata_dir,os.path.basename(filename) )
output    = "%s/%s.mkv" % (data_dir, os.path.basename(filename))

# Generate filename of ffv1.mkv without the path.
outputfilename = os.path.basename(output)

outputxml = "%s/%s.xml" % (metadata_dir, outputfilename)
fmd5      = "%s/%s.framemd5" % (provenance_dir, os.path.basename(filename))
fmd5ffv1  = output + ".framemd5"

# Transcode video file writing frame md5 and output appropriately
subprocess.call(['ffmpeg',
                '-i', filename, 
                '-c:v', 'ffv1',        # Use FFv1 codec
                '-g','1',              # Use intra-frame only aka ALL-I aka GOP=1
                '-level','3',          # Use Version 3 of FFv1
                '-c:a','copy',         # Copy and paste audio bitsream with no transcoding
                '-map','0',
                '-dn',
                output,	
                '-f','framemd5','-an'  # Create decoded md5 checksums for every frame of the input. -an ignores audio
                , fmd5 ])
subprocess.call(['ffmpeg',     # Create decoded md5 checksums for every frame of the ffv1 output
                '-i',output,
                '-f','framemd5','-an',
                fmd5ffv1 ])

# Verify that the video really is lossless by comparing the fixity of the two framemd5 files. 
if filecmp.cmp(fmd5, fmd5ffv1, shallow=False): 
	print "YOUR FILES ARE LOSSLESS YOU SHOULD BE SO HAPPY!!!"
else:
	print "YOUR CHECKSUMS DO NOT MATCH, BACK TO THE DRAWING BOARD!!!"
	sys.exit()                 # Script will exit the loop if transcode is not lossless.


# Write metadata for original video file - with open will auto close the file.
def make_mediainfo(xmlfilename, xmlvariable, inputfilename):
  with open(xmlfilename, "w+") as fo:
  	xmlvariable = subprocess.check_output(['mediainfo',
  						'-f',
  						'--language=raw', # Use verbose output.
  						'--output=XML',
  						inputfilename])       #input filename
  	fo.write(xmlvariable)
    
make_mediainfo(inputxml,'mediaxmlinput',filename)
make_mediainfo(outputxml,'mediaxmloutput',output)
	

