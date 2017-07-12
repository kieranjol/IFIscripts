#!/usr/bin/env python
'''
Specific workflow for the IFI Irish Film Archive's Special Collections.
'''
import argparse
import os
import shutil
from ififuncs import hashlib_manifest
from ififuncs import generate_log

def count_files(source):
    '''
    Counts the files to be processed.
    '''
    file_count = 1
    for _, directories, filenames in os.walk(source):
        filenames = [f for f in filenames if f[0] != '.']
        directories[:] = [d for d in directories if d[0] != '.']
        # Surely just len() would suffice here?
        for files in filenames:
            print "Calculating number of files in all subdirectories -  %s files        \r"% file_count,
            file_count += 1
    return file_count


def make_parser():
    '''
    Accepts command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Batch MD5 checksum generator.'
        'Accepts a parent folder as input and will generate manifest for each subfolder.'
        ' Designed for a specific IFI Irish Film Archive workflow. '
        'Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'input', help='file path of parent directory'
    )
    parser.add_argument(
        '-v', action='store_true',
        help='verbose mode - some extra information such as overall file count.'
    )
    return parser


def create_manifest(source):
    '''
    Generates a master log and creates checksum manifests for all subdirectories.
    '''
    master_log = os.path.expanduser('~/Desktop/batchfixity_errors.log')
    os.chdir(source)
    for dirname in os.walk('.').next()[1]:
        full_path = os.path.join(source, dirname)
        manifest_textfile = '%s/%s_manifest.md5' % (full_path, dirname)
        if not os.path.isfile(manifest_textfile):
            log_name = '%s/%s_fixity.log' % (
                os.path.dirname(full_path), dirname
            )
            generate_log(log_name, 'batchfixity started')
            generate_log(log_name, '%s created' % manifest_textfile)
            try:
                hashlib_manifest(full_path, manifest_textfile, full_path)
                generate_log(log_name, 'manifest creation complete')
                shutil.move(log_name, full_path)
            except IOError:
                with open(master_log, 'ab') as log:
                    log.write(
                        '%s has failed probably because of special characters like a fada\n' % full_path
                    )
                    generate_log(
                        log_name, 'manifest has failed probably because of special characters like a fada'
                        )


def main():
    '''
    Launches the main functions.
    '''
    parser = make_parser()
    args = parser.parse_args()
    if args.v:
        count_files(args.input)
    create_manifest(args.input)


if __name__ == '__main__':
    main()

