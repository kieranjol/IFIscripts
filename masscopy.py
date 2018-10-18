#!/usr/bin/env python
'''
Launches copyit.py for subfolders that have md5 anifests.
'''
import os
import argparse
import copyit
from ififuncs import make_desktop_logs_dir


def analyze_log(logfile):
    '''
    Analyzes logfiles on the desktop and summarises the outcome.
    '''
    outcome = ''
    with open(logfile, 'r') as fo:
        log_lines = fo.readlines()
        for line in log_lines:
            if 'EVENT = File Transfer Judgement - Success' in line:
                outcome = 'success'
            if 'EVENT = File Transfer Outcome - Failure' in line:
                outcome = 'failure'
            if 'EVENT = Existing source manifest check - Failure' in line:
                outcome = 'failure - might be outdated manifests in use'
        return outcome

def parse_args():
    '''
    Accepts command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Performs moveit.py in a batch'
        ' Written by Kieran O\'Leary.')
    parser.add_argument(
        'input',
        help='full path of input directory'
    )
    parser.add_argument(
        '-o',
        help='full path of output directory',
        required=True)
    parser.add_argument(
        '-l', '-lto',
        action='store_true',
        help='use gcp instead of rsync on osx for SPEED on LTO')
    parser.add_argument(
        '-y',
        action='store_true',
        help='Answers YES to the question: Not enough free space, would you like to continue?'
    )
    args = parser.parse_args()
    return args


def find_manifest(args):
    '''
    This function tries to find a manifest.
    It looks one folder beneath the input folder for a checksum manifest
    with a folder that has a matching name.
    '''
    # Creates an empty list called dirlist.
    dirlist = []
    # Creates a list of items in your input called directory_contents.
    directory_contents = sorted(os.listdir(args.input))
    # lists all contents of your input and analyzes each one in a `for loop`.
    for item in directory_contents:
        full_path = os.path.join(args.input, item)
        manifest = os.path.join(
            args.input, item
        ) + '_manifest.md5'
        # checks if the manifest exists
        if os.path.isfile(manifest):
            #if the manifest exists, add to dirlist
            dirlist.append(full_path)
        # checks if each item is a directory.
        if os.path.isdir(full_path):
            directories = os.listdir(full_path)
            for subdirectories in directories:
                full_subdirectory_path = os.path.join(
                    full_path, subdirectories
                )
                if os.path.isdir(full_subdirectory_path):
                    manifest = os.path.join(
                        os.path.dirname(
                            full_subdirectory_path
                        ), subdirectories + '_manifest.md5'
                        )
                    if os.path.isfile(manifest):
                        dirlist.append(os.path.dirname(full_subdirectory_path))
    print dirlist
    return dirlist # the dirlist is sent back out to the rest of the script.


def analyze_reports(log_names, desktop_logs_dir):
    '''
    Tries to locate copyit.py logs on the desktop and analyzes them.
    '''
    print 'SUMMARY REPORT'
    for i in log_names:
        if os.path.isfile(i):
            print "%-*s   : %s" % (50, os.path.basename(i)[:-24], analyze_log(i))
        else:
            print i, 'can\'t find log file, trying again...'
            for logs in os.listdir(desktop_logs_dir):
                # look at log filename minus the seconds and '.log'
                if os.path.basename(i)[:-7] in logs:
                    # make sure that the alternate log filename is more recent
                    if int(
                        os.path.basename(logs)[-12:-4].replace('_', '')) > int(os.path.basename(i)[-12:-4].replace('_', '')):
                        print 'trying to analyze %s' % logs
                        print "%-*s   : %s" % (50, os.path.basename(logs)[:-24], analyze_log(os.path.join(desktop_logs_dir, logs)))


def main():
    '''
    Launches the other functions wihch attempt to run multiple copyit.py
    instances if manifests and matching sidecar directories are found
    inside of the input directory.
    '''
    args = parse_args()
    all_files = find_manifest(args)
    processed_dirs = []
    log_names = []
    print '\n\n**** All of these folders will be copied to %s\n' % args.o
    for i in all_files:
        print i
    for i in all_files:
        absolute_path = os.path.join(args.o, os.path.basename(i))
        if os.path.isdir(absolute_path):
            print('%s already exists, skipping') % (absolute_path)
        else:
            desktop_logs_dir = make_desktop_logs_dir()
            copyit_cmd = [os.path.join(args.input, i), args.o]
            if args.l:
                copyit_cmd.append('-l')
            elif args.y:
                copyit_cmd.append('-y')
            log_name = copyit.main(copyit_cmd)
            log_names.append(log_name)
            processed_dirs.append(os.path.basename(os.path.join(args.input, i)))
            print '********\nWARNING - Please check the ifiscripts_logs directory on your Desktop to verify if ALL of your transfers were successful'
            analyze_reports(log_names, desktop_logs_dir)


if __name__ == '__main__':
    main()
