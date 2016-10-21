#!/bin/env python
import sys
import hashlib
import os
import logging
import argparse

'''
accept manifest as input
parse manifest as list
check which algorithm
for each file:
locate file, calculate fresh hash, print value to screen and log, add to premis file if exists, create premis if not

'''
root = logging.getLogger()
logging.basicConfig(filename='myapp.log', filemode='w',level=logging.INFO)
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
    manifest_dict = {}
    with open(manifest, 'rb') as manifest_object:
        manifest_list = manifest_object.readlines()
        for entries in manifest_list:
            checksum = entries.split(' ')[0]
            path = entries[34:].replace('\n', '')
            logging.debug('%s %s' % (checksum, path))
            manifest_dict[path] = checksum
        logging.debug(manifest_dict)
    return manifest_dict 

def validate(manifest_dict, manifest):
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logging.info('Started')
    manifest_directory = os.path.dirname(manifest)
    os.chdir(manifest_directory)
    for i in manifest_dict:
        logging.debug(i)
        print 'Validating %s' % i
        current_hash = hashlib_md5(i)
        if current_hash == manifest_dict[i]:
            print '%s has validated' % i
        else:
            print '%s has mismatched checksum - %s expected - %s hashed' % (i, manifest_dict[i], current_hash)
            logging.info('%s has mismatched checksum - %s expected - %s hashed' % (i, manifest_dict[i], current_hash))
def make_parser():
    parser = argparse.ArgumentParser(description='MD5 checksum manifest validator. Currently this script expects an md5 checksum, followed by two spaces, followed by a file path.'
                                 ' Written by Kieran O\'Leary. On a train home to Cork. 2016-10-22. R.I.P Anthony  \'Axel\'  Foley.')
    parser.add_argument('input')
    return parser
def main():
    parser = make_parser()
    args = parser.parse_args()
    manifest = get_input(sys.argv[1])
    manifest_dict = parse_manifest(manifest)
    validate(manifest_dict, manifest)
    
if __name__ == '__main__':
   main()