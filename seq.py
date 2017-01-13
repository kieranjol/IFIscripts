#!/usr/bin/env python

import subprocess
import sys
import os
import argparse
from glob import glob



parser = argparse.ArgumentParser(description='Generate v210/mov file from image sequence.'
                                'Written by Kieran O\'Leary.')
parser.add_argument('input', help='file path of parent directory')
parser.add_argument('-p', action='store_true', help='Use the Apple ProRes 4:2:2 codec instead of v210')
parser.add_argument('-f', action='store_true', help='choose an alternative framerate')
args = parser.parse_args()
source_directory = args.input

if not os.path.isdir(args.input):
    print('Please provide a directory as input, not a file')
    sys.exit()
os.chdir(source_directory)
images = (
        glob('*.tif') +
        glob('*.tiff') +
        glob('*.dpx') 
        )
extension = os.path.splitext(images[0])[1]
numberless_filename = images[0].split("_")[0:-1]

ffmpeg_friendly_name = ''
counter = 0
while  counter <len(numberless_filename) :
    ffmpeg_friendly_name += numberless_filename[counter] + '_'
    counter += 1
dirname = os.path.dirname(source_directory)    
output = dirname + '/%s.mov' % os.path.split(source_directory)[-1]
ffmpeg_friendly_name += '%06d' + extension
codec = 'v210'
if args.p:
    codec = 'prores'
#the sript will choose 24fps as default    
cmd = ['ffmpeg','-f','image2','-framerate','24', '-i', ffmpeg_friendly_name,'-c:v',codec,output]
#adding the choice of an alternative fps here through argsparse
if args.f:
    fps = raw_input('what alternative framerate do you require? 16,18,21,25?')	               
    cmd = ['ffmpeg','-f','image2','-framerate',fps, '-i', ffmpeg_friendly_name,'-c:v',codec,output] 
print cmd
subprocess.call(cmd)
print 'Output file is located in %s' % output
