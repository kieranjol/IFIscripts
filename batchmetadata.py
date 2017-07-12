#!/usr/bin/env python
'''
'Traverses through subdirectories finding images sequences
and creating mediainfo and medatrace xml reports.
'''
import sys
import os
import argparse
from glob import glob
try:
    from ififuncs import make_mediatrace
    from ififuncs import make_mediainfo
except ImportError:
    print '*** ERROR - IFIFUNCS IS MISSING - *** \nMakeffv1 requires that ififuncs.py is located in the same directory as some functions are located in that script - https://github.com/kieranjol/IFIscripts/blob/master/ififuncs.py'
    sys.exit()


def make_parser():
    '''
    Accepts command line inputs.
    '''
    parser = argparse.ArgumentParser(
        description='Traverses through subdirectories finding images sequences and creating mediainfo and medatrace xml reports.'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument('input', help='file path of parent directory')
    return parser


def create_metadata(source):
    '''
    Recursively finds image sequences and creates mediainfo/mediatrace in parent
    directory.
    '''
    for root, _, _ in os.walk(source):
        os.chdir(root)
        tiff_check = glob('*.tiff')
        dpx_check = glob('*.dpx')
        tif_check = glob('*.tif')
        if len(dpx_check) > 0:
            images = dpx_check
        elif len(tiff_check) > 0:
            images = tiff_check
        elif len(tif_check) > 0:
            images = tif_check
        else:
            continue
        mediainfo_xml = '%s/%s_mediainfo.xml' % (os.path.dirname(root), images[0])
        mediatrace_xml = '%s/%s_mediatrace.xml' % (os.path.dirname(root), images[0])
        print 'Creating mediainfo XML for %s' % images[0]
        make_mediainfo(mediainfo_xml, 'mediaxmloutput', images[0])
        print 'Creating mediatrace XML for %s' % images[0]
        make_mediatrace(mediatrace_xml, 'mediatracexmlinput', images[0])


def main():
    '''
    Launches all the functions.
    '''
    parser = make_parser()
    args = parser.parse_args()
    source = args.input
    if not os.path.isdir(source):
        print 'This script takes a directory/folder as input. Please rerun the script. Exiting.'
        sys.exit()
    create_metadata(source)


if __name__ == '__main__':
    main()
