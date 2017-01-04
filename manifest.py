#!/usr/bin/env python

import sys
import subprocess
import os
import getpass
import argparse
import time
import shutil
from ififuncs import generate_log
from ififuncs import manifest_file_count
from ififuncs import hashlib_manifest
from ififuncs import make_desktop_logs_dir, make_desktop_manifest_dir


def remove_bad_files(root_dir):
    rm_these = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
    for root, dirs, files in os.walk(root_dir):
        for name in files:
            path = os.path.join(root, name)
            for i in rm_these:
                if name == i:
                    print '***********************' + 'removing: ' + path
                    generate_log(log_name_source, 'EVENT = Unwanted file removal - %s was removed' % path)
                    os.remove(path)

parser = argparse.ArgumentParser(description='Generate manifest with checksums for a directory'
                                 ' Written by Kieran O\'Leary.')
parser.add_argument('source', help='Input directory')
parser.add_argument('-s', '-sidecar', action='store_true', help='Generates Sidecar')
parser.add_argument('-f', '-felix', action='store_true', help='Felix Meehan workflow - places manifest inside of source directory')

args = parser.parse_args()

source               = args.source
source_parent_dir    = os.path.dirname(source)
normpath             = os.path.normpath(source)
dirname              = os.path.split(os.path.basename(source))[1]
relative_path        = normpath.split(os.sep)[-1]
log_name_source_                = os.path.basename(args.source)  + time.strftime("_%Y_%m_%dT%H_%M_%S")
if args.s:
    manifest = source_parent_dir + '/%s_manifest.md5' % relative_path
    log_name_source = source_parent_dir + '/%s.log' % log_name_source_
    
elif args.f:
    manifest = source + '/%s_manifest.md5' % relative_path
    log_name_source = source_parent_dir + '/%s.log' % log_name_source_
else:
    manifest_ =  '/%s_manifest.md5' % relative_path
    desktop_manifest_dir = make_desktop_manifest_dir()
    manifest = "%s/%s" % (desktop_manifest_dir, manifest_)


    desktop_logs_dir = make_desktop_logs_dir()
    log_name_source = "%s/%s.log" % (desktop_logs_dir, log_name_source_)


generate_log(log_name_source, 'move.py started.')
generate_log(log_name_source, 'Source: %s' % source)

if os.path.isfile(source):
    print '\nFile checksum is not currently supported, only directories.\n'
    generate_log(log_name_source, 'Error: Attempted to generate manifest for file. Only Directories/Folders are currently supported')
    generate_log(log_name_source, 'move.py exit')
    sys.exit()
elif not os.path.isdir(source):
    print ' %s is either not a directory or it does not exist' % source
    generate_log(log_name_source, ' %s is either not a directory or it does not exist' % source)
    generate_log(log_name_source, 'move.py exit')
    sys.exit()

remove_bad_files(source)
source_count = 0
for root, directories, filenames in os.walk(source):
    for files in filenames:
            source_count +=1 #works in windows at least


if os.path.isfile(manifest):
    count_in_manifest = manifest_file_count(manifest)
    if source_count != count_in_manifest:
        print 'This manifest may be outdated as the number of files in your directory does not match the number of files in the manifest'
        generate_log(log_name_source, 'EVENT = Existing source manifest check - Failure - The number of files in the source directory is not equal to the number of files in the source manifest ')
        sys.exit()
source_manifest_start_time = time.time()

if not os.path.isfile(manifest):
    try:
        print 'Generating source manifest'
        hashlib_manifest(source, manifest,source)
        generate_log(log_name_source, 'EVENT = Generating source manifest')
        shutil.move(log_name_source, source)

    except OSError:
            print 'You do not have access to this directory. Perhaps it is read only, or the wrong file system\n'
            sys.exit()
else:
    generate_log(log_name_source, 'EVENT = Existing source manifest check - Source manifest already exists. Script will exit. ')
source_manifest_time = time.time() - source_manifest_start_time

print 'Manifest created in %s' % manifest