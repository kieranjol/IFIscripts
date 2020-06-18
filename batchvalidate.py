#!/usr/bin/env python3
import sys
import os
import subprocess
import argparse
import validate

def parse_args():
    '''
    Parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Recursively launch validate.py')
    parser.add_argument('input', help='full path to manifest file')
    parser.add_argument('-y', help ='invokes -y option in validate.py, answers Y to manifest issues', action='store_true')
    parsed_args = parser.parse_args()
    return parsed_args

def main():
    args = parse_args()
    source = args.input
    results = []
    for root, dirname, filenames in os.walk(source):
        error_counter = 0
        for files in filenames:
            if files.endswith('_manifest.md5'):
                if  os.path.basename(root) != 'logs':
                    manifest = os.path.join(root, files)
                    print(manifest)
                    if os.path.isfile(manifest):
                        if args.y:
                            error_counter = validate.main([manifest, '-y'])
                        else:
                            error_counter = validate.main([manifest])
                        if error_counter == 0:
                            results.append([root, 'success'])
                        else:
                            results.append([root, 'failure'])
                        for result in results:
                            print(result)
                else:
                    continue
    for result in results:
        print(result)

if __name__ == '__main__':
    main()
