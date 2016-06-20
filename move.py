#!/usr/bin/env python

import sys
import subprocess
import os
import pdb
import filecmp
from sys import platform as _platform
import tempfile
import time
import argparse

# Currently, destination manifest will be overwritten. user input should be required. source manifest will not be overwritten, it will be read.
parser = argparse.ArgumentParser(description='Copy directory with checksum comparison and manifest generation.'
                                 ' Written by Kieran O\'Leary.')
parser.add_argument('source', help='Input directory')
parser.add_argument('destination', help='Destination directory')
parser.add_argument('-b', '-benchmark', action='store_true', help='display benchmark')

args = parser.parse_args()

source               = args.source
source_parent_dir    = os.path.dirname(source)
normpath             = os.path.normpath(source) 
dirname              = os.path.splitext(os.path.basename(source))[0]
relative_path        = normpath.split(os.sep)[-1]

destination                    = args.destination # or hardcode
manifest_destination           = destination + '/%s_manifest.md5' % dirname
destination_final_path         = destination + '/%s' % dirname
manifest                       = source_parent_dir + '/%s_manifest.md5' % relative_path
'''
file_list = []

for root, directories, filenames in os.walk(source):
    root_list = os.listdir(root)
    for i in root_list:
        file_list.append(i)
    for directory in directories:
             os.chdir(root)
             dirlist = os.listdir(directory)
             for i in dirlist:
                 file_list.append(i)
'''

def count_files(location):
    file_count = 0
    for dirs,subdir,files in os.walk(location):
        file_count += len(files)
        for subdirs in subdir:
            file_count +=len(files)
        return file_count

def display_benchmark():
    print 'SOURCE MANIFEST TIME', source_manifest_time
    print 'COPY TIME', copy_time
    print 'DESTINATION MANIFEST TIME', destination_manifest_time

def test_write_capabilities(directory):
    if os.path.isdir(directory):
        temp = tempfile.mkstemp(dir=directory)
        os.remove(temp[1])
    elif os.path.isfile(directory):
        print '\nFile transfer is not currently supported, only directories.\n'
        sys.exit()
    else:
        print ' %s is either not a directory or it does not exist' % directory
        sys.exit()

def remove_bad_files(root_dir):
    rm_these = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
    for root, dirs, files in os.walk(root_dir):
        for name in files:
            path = os.path.join(root, name)
            for i in rm_these:
                if name == i:
                    print '***********************' + 'removing: ' + path
                    os.remove(path)

def make_manifest(manifest_dir, relative_manifest_path, manifest_textfile):
    os.chdir(manifest_dir)
    if os.path.isfile(manifest_destination):
        print 'Destination manifest already exists'
    manifest_generator = subprocess.check_output(['md5deep', '-ler', relative_manifest_path])
    manifest_list = manifest_generator.splitlines()
    files_in_manifest = len(manifest_list)
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list,  key=lambda x:(x[34:])) 
    with open(manifest_textfile,"wb") as fo:
        for i in manifest_list:
            fo.write(i + '\n')
    return files_in_manifest

def copy_dir():
    if _platform == "win32":
        subprocess.call(['robocopy',source, destination_final_path, '/E'])
    elif _platform == "darwin":
        # https://github.com/amiaopensource/ltopers/blob/master/writelto#L51
        cmd = ['gcp','--preserve=mode,timestamps', '-nRv',source, destination_final_path]
        subprocess.call(cmd)
    elif _platform == "linux2":
        # https://github.com/amiaopensource/ltopers/blob/master/writelto#L51
        cmd = [ 'cp','--preserve=mode,timestamps', '-nR',source, destination_final_path]
        subprocess.call(cmd)

def check_overwrite(file2check):
    if os.path.isfile(file2check):
        print 'A manifest already exists at your destination. Overwrite? Y/N?'
        overwrite_destination_manifest = ''
        while overwrite_destination_manifest not in ('Y','y','N','n'):
            overwrite_destination_manifest = raw_input()
            if overwrite_destination_manifest not in ('Y','y','N','n'):
                print 'Incorrect input. Please enter Y or N'
        return overwrite_destination_manifest

def check_overwrite_dir(dir2check):
    if os.path.isdir(dir2check):
        print 'A directory already exists at your destination. Overwrite? Y/N?'
        overwrite_destination_dir = ''
        while overwrite_destination_dir not in ('Y','y','N','n'):
            overwrite_destination_dir = raw_input()
            if overwrite_destination_dir not in ('Y','y','N','n'):
                print 'Incorrect input. Please enter Y or N'
        return overwrite_destination_dir

try:
    test_write_capabilities(source)
except OSError:
            print 'You cannot write to your source directory!'
            sys.exit()
try:
    test_write_capabilities(destination)
except OSError:
            print 'You cannot write to your destination!'
            sys.exit()
overwrite_destination_manifest = check_overwrite(manifest_destination)
overwrite_destination_dir = check_overwrite_dir(destination_final_path)

remove_bad_files(source)
files_in_source = count_files(source) 
source_manifest_start_time = time.time()

if not os.path.isfile(manifest):
    try:
        print 'Generating source manifest'
        make_manifest(source_parent_dir, relative_path,manifest)
    except OSError:
            print 'You do not have access to this directory. Perhaps it is read only, or the wrong file system\n'
            sys.exit()

source_manifest_time = time.time() - source_manifest_start_time

copy_start_time = time.time()
if overwrite_destination_dir not in ('N','n'):
    copy_dir()
copy_time = time.time() - copy_start_time

start_destination_manifest_time = time.time()
if overwrite_destination_manifest not in ('N','n'):
    print 'Generating destination manifest'
    files_in_manifest = make_manifest(destination,dirname, manifest_destination)
remove_bad_files(destination_final_path)

destination_manifest_time = time.time() - start_destination_manifest_time
files_in_destination = count_files(destination_final_path)
if filecmp.cmp(manifest, manifest_destination, shallow=False):
	print "Your files have reached their destination and the checksums match"
else:
	print "***********YOUR CHECKSUMS DO NOT MATCH*************"
print ' There are: \n %s files in your destination manifest \n %s files in your destination \n %s files at source' % (files_in_manifest, files_in_destination, files_in_source)
if args.b:
    display_benchmark()

