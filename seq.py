#!/usr/bin/env python

import subprocess
import sys
import os
from glob import glob

first_file = sys.argv[1]
os.chdir(first_file)
images = (
        glob('*.tif') +
        glob('*.tiff') +
        glob('*.dpx') 
        )

       
rejigged_name = images[0].split("_")[0:-1]
print rejigged_name
test = ''
counter = 0
while  counter <len(rejigged_name) :
    test += rejigged_name[counter] + '_'
    counter += 1
dirname = os.path.dirname(first_file)    
output = dirname + '/%s_consolidate.mov' % os.path.split(first_file)[-1]
test += '%06d.tiff'
cmd = ['ffmpeg','-f','image2','-framerate','24', '-i',test,'-c:v','v210',output]
print cmd

subprocess.call(cmd)
