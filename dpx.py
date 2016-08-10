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


dirname = os.path.dirname(source_directory)    
output_dirname = dirname + '/' + os.path.basename(source_directory) + '_dpx_transcodes'
os.makedirs(output_dirname)
for tiff in images:
    cmd = ['ffmpeg','-f','image2','-framerate','24', '-i', tiff ,output_dirname + '/' + tiff[:-4] + 'dpx']
    print cmd
    subprocess.call(cmd)
