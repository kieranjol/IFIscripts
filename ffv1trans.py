# Written by Kieran O'Leary, with a major review and overhaul/cleanup by Zach Kelling aka @Zeekay

import subprocess
import sys
import filecmp
from glob import glob
import os
import pdb
from Tkinter import *
import tkFileDialog
root = Tk()

# Create file-open dialog.
root.update()
# Directory with files that we want to transcode losslessly and generate metadata for
filename = tkFileDialog.askopenfilename(parent=root)
output = filename + 'transcoded.mov'
inputxml = filename + '.xml'
outputxml = output + '.xml'
# Transcode video file writing frame md5 and output appropriately
def transcode(inputfile, video_codec,audio_options, output):
    subprocess.call(['ffmpeg',
                '-i',inputfile, 
                '-c:v',video_codec,
                
                '-c:a',audio_options,         
                output])	

#pdb.set_trace()
codec = raw_input("Pick a codec: (1) ProRes, (2) v210 or (3) h264 ")
if codec== "1":
     transcode(filename, 'prores','copy',output)   
elif codec == "2":
     transcode(filename, 'v210','copy',output)   
elif codec == "3":
    
     transcode(filename, "libx264 -pix_fmt yuv420p" ,'copy',output)  



#transcode(filename, video_options,'copy',output)            
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
	

