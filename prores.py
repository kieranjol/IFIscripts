#!/usr/bin/env python

import argparse
import subprocess
import sys
import os
from glob import glob
import pdb

parser = argparse.ArgumentParser(description='IFI Pro Res 4:2:2 ffmpeg Encoder.'
                                 ' Written by Kieran O\'Leary.')
parser.add_argument('input')
parser.add_argument(
                    '-hq', 
                    action='store_true',help='-profile:v 3 aka Prores HQ')
parser.add_argument(
                    '-yadif', 
                    action='store_true',help='Yet Another DeInterlace Filter')
parser.add_argument(
                    '-scale',
                    help='Rescale video.'
                    ' Usage: -scale 1920x1080 or -scale 720x576 etc')
parser.add_argument(
                    '-md5',
                    action='store_true',
                    help='Get md5 sidecar for your output file')
parser.add_argument(
                    '-map',
                    action='store_true',
                    help='Force default mapping, eg. 1 audio/video stream')
args = parser.parse_args()
prores_options = []
    
if args.yadif:
    prores_options.append('-yadif')
    
if args.scale:
    prores_options.append('-scale')
    width_height = args.scale

number_of_effects =  len(prores_options)

 # Input, either file or firectory, that we want to process.
input = args.input

# Store the directory containing the input file/directory.
wd = os.path.dirname(input)

# Change current working directory to the value stored as "wd"
os.chdir(wd)

# Store the actual file/directory name without the full path.
file_without_path = os.path.basename(input)

# Check if input is a file.
# AFAIK, os.path.isfile only works if full path isn't present.
if os.path.isfile(file_without_path):      
    video_files = []                       # Create empty list 
    video_files.append(file_without_path)  # Add filename to list

# Check if input is a directory. 
elif os.path.isdir(file_without_path):  
    os.chdir(file_without_path)
    video_files = (
        glob('*.mov') +
        glob('*.mp4') +
        glob('*.mxf') +
        glob('*.mkv') +
        glob('*.avi')
    )

# Prints some stuff if input isn't a file or directory.
else: 
    print "Your input isn't a file or a directory."
    
                      
for filename in video_files:
    #pdb.set_trace()
    output = filename + "_prores.mov"
    
    ffmpeg_args =   ['ffmpeg',
            '-i', filename,
            '-c:a', 'copy',
            '-c:v', 'prores',]
    if not args.map:
        ffmpeg_args.append('-map')
        ffmpeg_args.append('0:a?')
        ffmpeg_args.append('-map')
        ffmpeg_args.append('0:v')
        
                
    if args.hq:
        ffmpeg_args.append('-profile:v')
        ffmpeg_args.append('3')
        
    if args.yadif or args.scale:
        
        filter_options = '-vf'
        
        if args.yadif:
            print 'YADIF'
            filter_options += ' yadif'         
              
        if args.scale:
            print 'scale'
            if number_of_effects > 1:
                filter_options += (',scale=%s' % width_height)                        
            else:
                filter_options += (' scale=%s' % width_height)
            
        filter_options = filter_options.split()
        for item in filter_options:
            ffmpeg_args.append(item)    
    ffmpeg_args.append(output)
    print ffmpeg_args
    subprocess.call(ffmpeg_args)
