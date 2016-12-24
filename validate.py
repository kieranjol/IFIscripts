#!/usr/bin/env python
import sys
import hashlib
import os
import logging
import argparse
import time
import getpass
from ififuncs import make_desktop_logs_dir


def hashlib_md5(filename):
   read_size = 0
   last_percent_done = 0
   m = hashlib.md5()
   total_size = os.path.getsize(filename)
   with open(str(filename), 'rb') as f:
       while True:
           buf = f.read(2**20)
           if not buf:
               break
           read_size += len(buf)
           m.update(buf)
           percent_done = 100 * read_size / total_size
           if percent_done > last_percent_done:
               sys.stdout.write('[%d%%]\r' % percent_done)
               sys.stdout.flush()
               last_percent_done = percent_done
   md5_output = m.hexdigest()
   return md5_output

def get_input(manifest):
    if not manifest.endswith(('.txt', '.md5', '.exf' )):
        print 'Usage: validate.py manifest \nManifests can be a .txt or a .md5 or an ExactFile .exf file.'
        sys.exit()
    elif manifest.endswith('.exf'):
        print 'ExactFile manifests have 5 lines of extra info which will confuse validate.py until I get around to fixing this.  It will list some missing files but will validate checksums as usual.'
        return manifest
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
            path = path.replace('\\', '/')
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
    logging.info('Validating %s ' % manifest)
    error_counter = 0
    manifest_directory = os.path.dirname(manifest)
    os.chdir(manifest_directory)
    error_list = []

    for i in sorted(manifest_dict.keys()):
        print 'Validating %s' % i
        current_hash = hashlib_md5(i)
        if current_hash == manifest_dict[i]:
            print '%s has validated' % i
        else:
            print '%s has mismatched checksum - %s expected - %s hashed' % (i, manifest_dict[i], current_hash)
            logging.info('%s has mismatched checksum - %s expected - %s hashed' % (i, manifest_dict[i], current_hash))
            error_list.append('%s has mismatched checksum - %s expected - %s hashed' % (i, manifest_dict[i], current_hash))
            error_counter += 1
    if error_counter > 0:
        print '\n\n*****ERRORS***********!!!!\n***********\nThe number of mismatched checksums is: %s\n***********\n' % error_counter
        logging.info('The number of mismatched checksums is: %s' %  error_counter)
        print '***** List of mismatched files*****'
        for i in error_list:
            print i
    elif error_counter == 0:
        if missing_files > 0:
            print '\n*****ERRORS!!!!***********\nThe number of missing files: %s\n***********\n' % missing_files
            logging.info('\n***********ERRORS!!!!*****\nThe number of mismatched checksums is: %s\n***********\n' %  missing_files)
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
    desktop_logs_dir = make_desktop_logs_dir()
    log_name_source_ = os.path.basename(args.input) + time.strftime("_%Y_%m_%dT%H_%M_%S")
    log = "%s/%s_fixity_validation.log" % (desktop_logs_dir, log_name_source_)
    root = logging.getLogger()
    logging.basicConfig(filename=log, filemode='a',level=logging.INFO)
    logging.info('Started at %s using the following workstation: %s' % (time.strftime("%Y-%m-%dT%H:%M:%S "), getpass.getuser()))

    #root.setLevel(logging.DEBUG)
    check_manifest(args.input)
if __name__ == '__main__':
   main()