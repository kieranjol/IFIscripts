#!/usr/bin/env python
'''
Requires ClamAV to be installed
'''

import sys
import subprocess
import argparse

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Runs a virus scan using ClamAV on your input directory'
        ' Written by Eoin O\'Donohoe.'
    )
    parser.add_argument(
        'input', help='Input directory'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def clamscan(input_dir):
    '''
    Calls ClamAV.
    '''
    scan = subprocess.call([
        'clamscan',
        '-r',
        '-v',
        input_dir
    ])

def main(args_):
    '''
    Launches functions that performs a virus check.
    '''
    args = parse_args(args_)
    input_dir = args.input
    print "Running scan.........."
    clamscan(input_dir)


if __name__ == '__main__':
    main(sys.argv[1:]) 



