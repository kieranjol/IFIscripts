#!/usr/bin/env python
'''
This script will ask mediainfo to get all durations with a folder
'''
import os
import sys
from ififuncs import get_milliseconds


def main():
    '''
    Recursively search for AV files and print duration in seconds
    '''
    all_files = sys.argv[1:]
    duration = 0
    for parent_directory in all_files:
        for root, dirnames, filenames in os.walk(parent_directory):
            for filename in filenames:
                if filename.endswith(('.MP4', '.mov', '.mkv')):
                    milliseconds = get_milliseconds(
                        os.path.join(root, filename)
                    )
                    duration += float(milliseconds)
    print '\nDuration of', all_files, ',', duration / 1000 / 60, 'minutes\n'


if __name__ == '__main__':
    main()
