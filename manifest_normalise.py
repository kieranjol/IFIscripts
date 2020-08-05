#!/usr/bin/env python3
'''
Normalises manifests so that they adhere to ifiscripts manifest.
This includes removing lines with hashes.
Removing lines with just whitespace.
Creating a new sidecar called _modified_manifest.md5
The goal is to allow batchaccession to run on the new manifests.
'''
import argparse
import os
import sys
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)

def parse_args():
    '''
    Parse command line arguments
    '''
    parser = argparse.ArgumentParser(
        description='Normalises manifests so that batchvalidate can run. '
        'New sidecar is generated called with _modified_manifest.md5 at end of filename.'
    )
    parser.add_argument(
        'input',
        help='full path of input directory. All md5 files will be processed'
    )
    parsed_args = parser.parse_args()
    return parsed_args

def main():
    '''
    Launches the functions that will normalise your manifests
    '''
    args = parse_args()
    source_dir = args.input
    if os.path.isdir(source_dir):
        for root, _, filenames in os.walk(source_dir):
            for filename in filenames:
                if filename[0] != '.' and filename.endswith('.md5'):
                    old_manifest_file = os.path.join(root, filename)
                    new_manifest_file = old_manifest_file + '_modified_manifest.md5'
                    # i'm sure there's a better way to detect if the script already ran..
                    if not '_modified_manifest.md5_modified_manifest.md5' in new_manifest_file:
                        with open(old_manifest_file, 'r') as old_manifest:
                            with open(new_manifest_file, 'w') as new_manifest:
                                for line in old_manifest.readlines():
                                    if not (line[0] == '#' or line == '\n'):
                                        logging.info('changing %s' % filename)
                                        new_manifest.write(line)
                    else:
                        logging.info('Modified manifests already exist in %s' % root)
    else:
        logging.info('Input must be a directory')
        sys.exit()
if __name__ == '__main__':
    main()
