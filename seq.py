#!/usr/bin/env python

import subprocess
import sys
import os

first_file = sys.argv[1]
rejigged_name = first_file.split("_")[0:-1]
test = ''
counter = 0
while  counter <len(rejigged_name) :
    test += rejigged_name[counter] + '_'
    counter += 1
dirname = os.path.dirname(first_file)    
output = os.path.dirname(dirname) + '/%s_consolidate.mov' % os.path.split(dirname)[-1]
test += '%06d.tiff'
cmd = ['ffmpeg','-f','image2','-framerate','24', '-i',test,'-c:v','v210',output]
print cmd
subprocess.call(cmd)

