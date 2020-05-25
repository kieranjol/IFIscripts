#!/usr/bin/env python3
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
import ififuncs

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

    # check if input folder size is greater than 100 gigs 100000000000
    if ififuncs.get_folder_size(source) > 100000000000:
        subprocess.call(['7za', 'a', '-tzip', '-v100g', '-mm=LZMA', '-mx=3', full_zip, os.path.basename(source)])
        full_zip = full_zip + '.001'
    else:
        subprocess.call(['7za', 'a', '-tzip', '-mm=LZMA', '-mx=3', full_zip, os.path.basename(source)])
    zip_finish = datetime.datetime.now()
    os.chdir(pwd)
    verify_start = datetime.datetime.now()
    print(' - Verifying the CRC32 checksums within the ZIP file..')
    if full_zip.endswith('.001'):
        try:
            result = subprocess.check_output(['7za', 't', full_zip,], stderr=subprocess.STDOUT).decode(sys.stdout.encoding)
        except subprocess.CalledProcessError as e:
            if 'Error' in e.output:
                result = 'FAILURE - Error Detected'
                print(e.output)
                print(result)
        if 'Everything is Ok' in result:
            print('Python has not detected any errors in your zipfile')
    else:
        with zipfile.ZipFile(full_zip, 'r') as myzip:
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
    ififuncs.check_existence(['7za'])
    main(sys.argv[1:])
