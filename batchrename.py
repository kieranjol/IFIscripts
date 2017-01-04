#!/usr/bin/env python

import os
import sys
from glob import glob

input = sys.argv[1]

os.chdir(input)
print 'Please wait - gathering filelist...'
tiffs = glob('*.tiff') + glob('*.dpx')
counter = 0

filename = tiffs[0]
# create new variable which trims the first 18 characters.
head_good_filename = filename[:-11]

print 'Current filename without extension and number sequence is: %s' % head_good_filename
new_head = raw_input('what do you want to change this to?\n')
for i in tiffs:
    tail = i[-11:]
    filename_fix = new_head + tail
    print filename_fix
    os.rename(i, filename_fix)
