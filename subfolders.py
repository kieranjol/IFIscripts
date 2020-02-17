#!/usr/bin/env python3
'''
Generates subfolders based on filenames within the input directory
and if -move is used, moves the relevant files into these new directories.
Eg. An input directory contains file1.mkv, file1.xml file2.mkv, file2.xml
This will result in directories called file1 and file2 being created, and
file1.mkv and file1.xml will be moved into the file1 directory, with a similar action
for file2
'''
import os
import sys
import shutil
import argparse

def parse_args():
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Generates subfolders based on filenames within the input directory'
        'and if -move is used, moves the relevant files into these new directories.'
        'Eg. An input directory contains file1.mkv, file1.xml file2.mkv, file2.xml'
        'This will result in directories called file1 and file2 being created, and'
        'file1.mkv and file1.xml will be moved into the file1 directory, with a similar action'
        'for file2'
    )
    parser.add_argument(
        '-i',
        help='full path of input directory', required=True
    )
    parser.add_argument(
        '-move',
        help='Moves files into the newly created subfolders', action='store_true'
    )
    parsed_args = parser.parse_args()
    return parsed_args

def main():
    '''
    Generates subfolders based on filenames within the input directory
    and if -move is used, moves the relevant files into these new directories.
    Eg. An input directory contains file1.mkv, file1.xml file2.mkv, file2.xml
    This will result in directories called file1 and file2 being created, and
    file1.mkv and file1.xml will be moved into the file1 directory, with a similar action
    for file2
    '''
    args = parse_args()
    inputs = args.i
    if not os.path.isdir(inputs):
        print(' - Input must be a directory/folder - exiting!')
        sys.exit()
    for dirs in os.listdir(inputs):
        if dirs[0] != '.':
            full_path = os.path.join(inputs, dirs)
            new_dir, _ = (os.path.splitext(full_path))
            if not os.path.isdir(new_dir):
                os.makedirs(new_dir)
                if os.path.isdir(new_dir):
                    print(' - The following directory has been created: %s' % new_dir)
            else:
                print(' - %s already exists' % new_dir)
            if args.move:
                if new_dir in full_path:
                    if os.path.isfile(full_path):
                        print(' - %s will be moved into %s' % (full_path, new_dir))
                        shutil.move(full_path, new_dir)

if __name__ == '__main__':
    main()