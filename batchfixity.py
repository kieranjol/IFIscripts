#!/usr/bin/env python

import argparse
import os
import sys
import time
import shutil
from ififuncs import hashlib_manifest
from ififuncs import generate_log

def count_files(input):
    file_count = 1
    for root, directories, filenames in os.walk(input):
        filenames = [f for f in filenames if not f[0] == '.']
        directories[:] = [d for d in directories if not d[0] == '.']
        for files in filenames:
            print "Calculating number of files in all subdirectories -  %s files        \r"% file_count,
            file_count +=1
    return file_count


def make_parser():
    parser = argparse.ArgumentParser(description='Batch MD5 checksum generator.'
                                'Accepts a parent folder as input and will generate manifest for each subfolder.'
                                ' Designed for a specific IFI Irish Film Archive workflow. '
                                'Written by Kieran O\'Leary.')
    parser.add_argument('input', help='file path of parent directory')
    parser.add_argument('-v', action='store_true', help='verbose mode - some extra information such as overall file count.')
    return parser


def create_manifest(input):
    os.chdir(input)
    for dirname in os.walk('.').next()[1]:
        full_path = os.path.join(input, dirname)
        manifest_textfile = '%s/%s_manifest.md5' % (full_path,dirname)
        log_name = '%s/%s_fixity.log' % (os.path.dirname(full_path),dirname)
        generate_log(log_name, 'batchfixity started')
        generate_log(log_name, '%s created' % manifest_textfile)
        hashlib_manifest(full_path, manifest_textfile, full_path)
        generate_log(log_name, 'manifest creation complete')
        shutil.move(log_name, full_path)


def main():
    parser = make_parser()
    args = parser.parse_args()
    if args.v:
        file_count = count_files(args.input)
    create_manifest(args.input)


if __name__ == '__main__':
   main()

