#!/usr/bin/env python
'''
Very quickly written script to rename part of an image sequence's filenames.
'''

import os
import sys
from glob import glob


def main():
    '''
    Asks user what they'd like their image sequence renamed to.
    '''
    source = sys.argv[1]
    os.chdir(source)
    print 'Please wait - gathering filelist...'
    tiffs = glob('*.tiff') + glob('*.dpx')
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


if __name__ == '__main__':
    main()
