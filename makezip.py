#!/usr/bin/env python
from zipfile import ZipFile
import zipfile
import sys
import os
import time
import argparse
import datetime


def parse_args():
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Compress folders with ZIP and verifies the process'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'input', help='Input directory'
    )
    parser.add_argument(
        'destination', help='Output directory'
    )
    parsed_args = parser.parse_args()
    return parsed_args

def main():
    args = parse_args()
    pwd = os.getcwd()
    source = args.input
    destination = args.destination
    # destination = sys.argv[2]
    start = datetime.datetime.now()
    name = os.path.basename(source) + '.zip'
    full_zip = os.path.join(destination, name)
    with ZipFile(full_zip, 'w',zipfile.ZIP_STORED, allowZip64 = True) as myzip:
        os.chdir(source)
        for root, dirnames, filenames in os.walk(source):
            for filename in filenames:
                full_path = os.path.relpath(os.path.join(root, filename))
                print('zipping %s' % full_path)
                myzip.write(full_path)
    finish = datetime.datetime.now()
    print start, finish           
    os.chdir(pwd)
    start = datetime.datetime.now()
    time.sleep(5)
    with zipfile.ZipFile(full_zip, 'r') as myzip:
        print 'verifying..'
        result =  myzip.testzip()
        if result is None:
            print('Python has not detected any errors in your zipfile')
        else:
            print('ERROR DETECTED IN %s '% result)
    finish = datetime.datetime.now()
    # print start, finish           
    
if __name__ == '__main__':
    main()