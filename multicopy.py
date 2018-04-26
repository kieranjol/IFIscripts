#!/usr/bin/env python
'''
Launches multiple copyit jobs. This is different to masscopy.py,
which takes a single directory as input and launches multiple copyit jobs.
This script takes multiple inputs and copies them to the output directory.
Make God have mercy on us all
'''

import argparse
import copyit
import masscopy
import ififuncs

def parse_args():
    '''
    Accepts command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Performs copyit.py in a batch'
        'Launches multiple copyit jobs. This is different to masscopy.py,'
        'which takes a single directory as input and launches multiple copyit jobs.'
        'This script takes multiple inputs and copies them to the output directory.'
        ' Written by Kieran O\'Leary.')
    parser.add_argument(
        '-i', nargs='+',
        help='full path of input directory',
        required=True
    )
    parser.add_argument(
        '-o',
        help='full path of output directory',
        required=True)
    parser.add_argument(
        '-l', '-lto',
        action='store_true',
        help='use gcp instead of rsync on osx for SPEED on LTO')
    args = parser.parse_args()
    return args


def main():
    '''
    Launches functions
    '''
    log_names = []
    args = parse_args()
    desktop_logs_dir = ififuncs.make_desktop_logs_dir()
    for i in args.i:
        log_names.append(copyit.main([i, args.o]))
    print '********\nWARNING - Please check the ifiscripts_logs directory on your Desktop to verify if ALL of your transfers were successful'
    masscopy.analyze_reports(log_names, desktop_logs_dir)



if __name__ == '__main__':
    main()
