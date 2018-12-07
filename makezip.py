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
    parsed_args = parser.parse_args(args_)
    return parsed_args

def main(args_):
    '''
    Zips and verifies all files and folders within your input directory.
    '''
    args = parse_args(args_)
    pwd = os.getcwd()
    source = args.i
    destination = args.o
    start = datetime.datetime.now()
    name = os.path.basename(source) + '.zip'
    full_zip = os.path.join(destination, name)
    with ZipFile(full_zip, 'w', zipfile.ZIP_STORED, allowZip64=True) as myzip:
        os.chdir(source)
        for root, _, filenames in os.walk(source):
            for filename in filenames:
                full_path = os.path.relpath(os.path.join(root, filename))
                print('zipping %s' % full_path)
                myzip.write(full_path)
    finish = datetime.datetime.now()
    print(start, finish)
    os.chdir(pwd)
    start = datetime.datetime.now()
    time.sleep(5)
    with zipfile.ZipFile(full_zip, 'r') as myzip:
        print('verifying..')
        result = myzip.testzip()
        if result is None:
            print('Python has not detected any errors in your zipfile')
        else:
            print('ERROR DETECTED IN %s '% result)
    finish = datetime.datetime.now()
    print(start, finish)
    return result, full_zip

if __name__ == '__main__':
    main(sys.argv[1:])
