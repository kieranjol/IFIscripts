#!/usr/bin/env python
import sys
import os
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description='Performs moveit.py in a batch'
                                ' Written by Kieran O\'Leary.')
    parser.add_argument(
                    'input',
                    help='full path of input directory'
                    )
    parser.add_argument(
                    '-o',
                    help='full path of output directory', required=True)
    args = parser.parse_args()
    dirlist = []
    permission = ''
    for source_directory in os.listdir(args.input):
        if os.path.isdir(os.path.join(args.input,source_directory)):
            manifest = os.path.join(args.input,source_directory) + '_manifest.md5'
            if os.path.isfile(manifest):
                dirlist.append(os.path.join(args.input, source_directory))
    all_files = dirlist
    if not permission == 'y' or permission == 'Y':
        print '\n\n**** All of these folders will be copied to %s\n' % args.o
        for i in all_files:
            print i
        permission =  raw_input('\n**** These are the directories that will be copied. \n**** If this looks ok, please press Y, otherwise, type N\n' )
        while permission not in ('Y','y','N','n'):
            permission =  raw_input('\n**** These are the directories that will be copied. \n**** If this looks ok, please press Y, otherwise, type N\n')
        if permission == 'n' or permission == 'N':
            print 'Exiting at your command- Cheerio for now'
            sys.exit()
        elif permission =='y' or permission == 'Y':
            print 'Ok so!'
    for i in all_files:
            if os.path.isdir(os.path.join(args.o, os.path.basename(i))):
                print('%s already exists, skipping') % (os.path.join(args.o, os.path.basename(i)))
            else:
                subprocess.check_call([sys.executable,os.path.expanduser("~/ifigit/ifiscripts/moveit.py"),
                os.path.join(args.input,i), args.o])
                print '********\nWARNING - Please check the ifiscripts_logs directory on your Desktop to verify if ALL of your transfers were successful'


if __name__ == '__main__':
    main()
