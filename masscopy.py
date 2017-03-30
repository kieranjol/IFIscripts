#!/usr/bin/env python
import sys
import os
import subprocess
import argparse
import time
from ififuncs import make_desktop_logs_dir


def analyze_log(logfile):
    outcome = ''
    with open(logfile, 'r') as fo:
        log_lines = fo.readlines()
        for line in log_lines:
            if 'EVENT = File Transfer Judgement - Success ' in line:
                outcome = 'success'
            if 'EVENT = File Transfer Outcome - Failure' in line:
                outcome = 'failure'
        return outcome


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
        if os.path.isdir(
            os.path.join(args.input,source_directory)
            ):
            manifest = os.path.join(
                args.input,source_directory
                ) + '_manifest.md5'
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
    processed_dirs = []
    log_names = []
    for i in all_files:
        if os.path.isdir(
            os.path.join(args.o, os.path.basename(i))
            ):
            print(
                '%s already exists, skipping'
                 ) % (os.path.join(args.o, os.path.basename(i)))
        else:
            log_name_source_ = os.path.basename(
                os.path.join(args.input,i)
                ) + time.strftime("_%Y_%m_%dT%H_%M_%S")
            desktop_logs_dir = make_desktop_logs_dir()
            log_name_source = "%s/%s.log" % (desktop_logs_dir, log_name_source_)
            moveit_cmd = [
                sys.executable,
                os.path.expanduser("~/ifigit/ifiscripts/moveit.py"),
                os.path.join(args.input,i), args.o]
            subprocess.check_call(moveit_cmd)
            processed_dirs.append(os.path.basename(os.path.join(args.input,i)))
            log_names.append(log_name_source)
            print '********\nWARNING - Please check the ifiscripts_logs directory on your Desktop to verify if ALL of your transfers were successful'
    print 'SUMMARY REPORT'
    for i in log_names:
        if os.path.isfile(i):
            print "%-*s   : %s" % (50,os.path.basename(i)[:-24], analyze_log(i))
        else:
            print i, 'can\'t find log file, trying again...'
            for logs in os.listdir(desktop_logs_dir):
                # look at log filename minus the seconds and '.log'
                if os.path.basename(i)[:-7] in logs:
                    # make sure that the alternate log filename is more recent
                    if int(os.path.basename(logs)[-12:-4].replace('_','')) > int(os.path.basename(i)[-12:-4].replace('_','')):
                        print 'trying to analyze %s' % logs
                        print "%-*s   : %s" % (50,os.path.basename(logs)[:-24], analyze_log(os.path.join(desktop_logs_dir,logs)))
if __name__ == '__main__':
    main()
