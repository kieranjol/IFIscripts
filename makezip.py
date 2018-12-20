#!/usr/bin/env python
'''
Zips and verifies all files and folders within your input directory.
'''
from zipfile import ZipFile
import zipfile
import sys
import os
import time
import argparse
import subprocess
import datetime


def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Compress folders with ZIP and verifies the process'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        '-i', help='Input directory', required=True
    )
    parser.add_argument(
        '-o', help='Output directory', required=True
    )
    parser.add_argument(
        '-basename', help='Specify a basename for the output file. A basename is a filename without the full path eg output.zip'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def create_zip(source, destination, name):
    '''
    Creates an uncompressed zipfile for all files in the source directory
    and stores the zipfile in the destination directory
    '''
    pwd = os.getcwd()
    zip_start = datetime.datetime.now()
    full_zip = os.path.join(destination, name)
    os.chdir(os.path.dirname(source))
    subprocess.call(['7za', 'a', '-tzip', '-mx=0', full_zip, os.path.basename(source)])
    zip_finish = datetime.datetime.now()
    os.chdir(pwd)
    verify_start = datetime.datetime.now()
    with zipfile.ZipFile(full_zip, 'r') as myzip:
        print(' - Verifying the CRC32 checksums within the ZIP file..')
        result = myzip.testzip()
        if result is None:
            print('Python has not detected any errors in your zipfile')
        else:
            print('ERROR DETECTED IN %s '% result)
    verify_finish = datetime.datetime.now()
    total_zip = zip_finish - zip_start
    total_verify = verify_finish - verify_start
    print('Zipping duration = %s seconds' % (str(total_zip)))
    print('Verification duration = %s seconds' % (str(total_verify)))
    print('Total duration = %s seconds' % (str(total_zip + total_verify)))
    return result, full_zip

def main(args_):
    '''
    Zips and verifies all files and folders within your input directory.
    '''
    args = parse_args(args_)
    print(args)
    print('makezip.py started')
    source = args.i
    destination = args.o
    if args.basename:
        name = args.basename
    else:
        name = os.path.basename(source) + '.zip'
    result, full_zip = create_zip(source, destination, name)
    return result, full_zip

if __name__ == '__main__':
    main(sys.argv[1:])
