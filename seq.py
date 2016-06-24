#!/usr/bin/env python

import subprocess
import sys
import os
from glob import glob

source_directory = sys.argv[1]
os.chdir(source_directory)
images = (
        glob('*.tif') +
        glob('*.tiff') +
        glob('*.dpx') 
        )

numberless_filename = images[0].split("_")[0:-1]
ffmpeg_friendly_name = ''
counter = 0
while  counter <len(numberless_filename) :
    test += numberless_filename[counter] + '_'
    counter += 1
dirname = os.path.dirname(source_directory)    
output = dirname + '/%s_consolidate.mov' % os.path.split(source_directory)[-1]
ffmpeg_friendly_name += '%06d.tiff'
cmd = ['ffmpeg','-f','image2','-framerate','24', '-i', ffmpeg_friendly_name,'-c:v','v210',output]
print cmd
subprocess.call(cmd)
