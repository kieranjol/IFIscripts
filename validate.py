#!/bin/env python
import sys
import hashlib
import os
import logging
import argparse

root = logging.getLogger()
logging.basicConfig(filename='myapp.log', filemode='a',level=logging.INFO)
#root.setLevel(logging.DEBUG)

def hashlib_md5(filename):
   m = hashlib.md5()
   with open(str(filename), 'rb') as f:
       while True:
           buf = f.read(2**20)
           if not buf:
               break
           m.update(buf)
   md5_output = m.hexdigest()
   return md5_output
   
def get_input(manifest):
    if not manifest.endswith(('.txt', '.md5' )):
        print 'Usage: validate.py manifest \nManifests can be a .txt or a .md5 file'
        sys.exit()
    else:
        return manifest
    

def parse_manifest(manifest):
    missing_files = 0
    manifest_dict = {}
    os.chdir(os.path.dirname(manifest))
    with open(manifest, 'rb') as manifest_object:
        manifest_list = manifest_object.readlines()
        for entries in manifest_list:
            checksum = entries.split(' ')[0]
            path = entries[34:].rstrip()
            if not os.path.isfile(path):
                logging.info('%s is missing' % path )
                print '%s is missing' % path
                missing_files += 1
            elif os.path.isfile(path):
                logging.debug('%s %s' % (checksum, path))
                manifest_dict[path] = checksum
                logging.debug(manifest_dict)
    if missing_files > 0:
        print 'The number of missing files: %s' % missing_files
        logging.info('The number of missing files is: %s' %  missing_files)
    elif missing_files == 0:
        print 'All files present'
        logging.info('All files present')
    return manifest_dict, missing_files

def validate(manifest_dict, manifest,missing_files):
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logging.info('Validating %s ' % manifest)
    error_counter = 0
    logging.info('Started')
    manifest_directory = os.path.dirname(manifest)
    os.chdir(manifest_directory)
    for i in manifest_dict:
        print 'Validating %s' % i
        current_hash = hashlib_md5(i)
        if current_hash == manifest_dict[i]:
            print '%s has validated' % i
        else:
            print '%s has mismatched checksum - %s expected - %s hashed' % (i, manifest_dict[i], current_hash)
            logging.info('%s has mismatched checksum - %s expected - %s hashed' % (i, manifest_dict[i], current_hash))
            error_counter += 1
    if error_counter > 0:
        print 'The number of mismatched checksums is: %s' % error_counter
        logging.info('The number of mismatched checksums is: %s' %  error_counter)
    elif error_counter == 0:
        if missing_files > 0:
            print 'The number of missing files: %s' % missing_files
            logging.info('The number of mismatched checksums is: %s' %  missing_files)
        elif missing_files == 0:
            print 'All checksums have validated'
            logging.info('All checksums have validated')

def make_parser():
    parser = argparse.ArgumentParser(description='MD5 checksum manifest validator. Currently this script expects an md5 checksum, followed by two spaces, followed by a file path.'
                                 ' Written by Kieran O\'Leary.')
    parser.add_argument('input', help='file path of md5 checksum file')
    return parser

def check_manifest(input):
    manifest = get_input(input)
    manifest_dict, missing_files = parse_manifest(manifest)
    validate(manifest_dict, manifest, missing_files)
def main():
    parser = make_parser()
    args = parser.parse_args()
    check_manifest(args.input)
if __name__ == '__main__':
   main()