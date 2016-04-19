#!/usr/bin/env python

import argparse
import subprocess
import sys
import os
from glob import glob
import pdb


parser = argparse.ArgumentParser(description="test")
parser.add_argument('input')
parser.add_argument('-hq', action='store_true',help='-profile:v 3 aka Prores HQ')
parser.add_argument('-yadif', action='store_true',help='Yet Another DeInterlace Filter')
parser.add_argument('-scale',help='Rescale video. Usage: -scale 1920x1080 or -scale 720x576')
parser.add_argument('-md5', action='store_true',help='Get md5 sidecar for your output file')

args = parser.parse_args()
prores_options = []

if args.hq:
    print 'Prores HQ'
    
if args.yadif:
    print 'yadif'
    prores_options.append('-yadif')
if args.scale:
    print 'rescale'
    prores_options.append('-scale')
    width_height = args.scale
print prores_options
number_of_effects =  len(prores_options)
if not prores_options:
    print 'Processing your prores with no extra options'
else:    
    prores_options.insert(0, '-vf')

print args.input

 # Input, either file or firectory, that we want to process.
input = args.input
print input

# Store the directory containing the input file/directory.
wd = os.path.dirname(input)

# Change current working directory to the value stored as "wd"
os.chdir(wd)

# Store the actual file/directory name without the full path.
file_without_path = os.path.basename(input)
print file_without_path



# Check if input is a file.
# AFAIK, os.path.isfile only works if full path isn't present.
if os.path.isfile(file_without_path):      
    print os.path.isfile(file_without_path)
    print "single file found"
    video_files = []                       # Create empty list 
    video_files.append(file_without_path)  # Add filename to list
    print video_files

# Check if input is a directory. 
elif os.path.isdir(file_without_path):  
    os.chdir(file_without_path)
    video_files =  glob('*.mov') + glob('*.mp4') + glob('*.mxf') + glob('*.mkv')+ glob('*.avi')

# Prints some stuff if input isn't a file or directory.
else: 
    print "Your input isn't a file or a directory."
    print "What was it? I'm curious."  
print prores_options 

                     
for filename in video_files:
            #pdb.set_trace()
            output = filename + "ffmpeg.mov"
            
            ffmpeg_args =   ['ffmpeg',
                    '-i', filename,
                    '-c:v', 'prores',]
            if args.hq:
                ffmpeg_args.append('-profile:v')
                ffmpeg_args.append('3')
            if args.yadif or args.scale:
                
                optio = '-vf'
                
                if args.yadif:
                    print 'YADIF'
                    optio += ' yadif'
                       
                      
                if args.scale:
                    print 'scale'
                    if number_of_effects > 1:
                    
                        optio += (',scale=%s' % width_height)
                    else:
                        optio += (' scale=%s' % width_height)
                    
                    
            optio = optio.split()
            print optio
            for item in optio:
            
                ffmpeg_args.append(item)    
            ffmpeg_args.append(output)
            print ffmpeg_args
            subprocess.call(ffmpeg_args)

