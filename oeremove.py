#!/usr/bin/env python

import os
import sys
from glob import glob

input = sys.argv[1]
if not os.path.isdir(input):
    print 'Error - Not a directory - Please provide a directory as input. Exiting...'
    sys.exit()
else:
    os.chdir(input)

    tiff_check = glob('*.tiff')
    dpx_check = glob('*.dpx')
    if len(dpx_check) > 0:
        images = dpx_check

    elif len(tiff_check) > 0:
        images = tiff_check
    else:
        print 'no images found'


permission = ''
for i in images:
    new_filename = ''
    split_names = i.split('_')
    if 'oe' in split_names[0]:
        for x in split_names[1:-1]:
            new_filename += x + '_'
        new_filename += split_names[-1]
        if not permission == 'y' or permission == 'Y':
            permission =  raw_input('\n**** Original filename = %s\n**** New filename =  %s\n**** If this looks ok, please press Y, otherwise, type N\n' % ( i, new_filename))
            while permission not in ('Y','y','N','n'):
                permission =  raw_input('\n**** Original filename = %s\n**** New filename =  %s\n**** If this looks ok, please press Y, otherwise, type N\n' % ( i, new_filename))
            if permission == 'n' or permission == 'N':
                print 'Exiting at your command'
                sys.exit()
            elif permission =='y' or permission == 'Y':
                os.rename(i, new_filename)
                print '**** Renaming %s with %s' % (i, new_filename)
        elif permission == 'y' or permission == 'Y':
            os.rename(i, new_filename)
            print '**** Renaming %s with %s' % (i, new_filename)   
    else:
        print 'This does not need to be renamed - exiting...'
        sys.exit()
            
  