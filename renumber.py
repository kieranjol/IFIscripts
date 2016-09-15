#!/usr/bin/env python

import os
import sys
from glob import glob

input = sys.argv[1]

os.chdir(input)
tiffs = glob('*.tiff')
counter = 0

for i in tiffs:
    numbo = '%06d' % counter
    filename = i
    # create new variable which trims the first 18 characters.
    head_good_filename = filename[:-11] 
    filename_fix = head_good_filename + str(numbo) + '.tiff'
    counter += 1
    os.rename(filename, filename_fix)