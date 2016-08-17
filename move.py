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
import getpass

# Currently, destination manifest will be overwritten. user input should be required. source manifest will not be overwritten, it will be read.
parser = argparse.ArgumentParser(description='Copy directory with checksum comparison and manifest generation.'
                                 ' Written by Kieran O\'Leary.')
parser.add_argument('source', help='Input directory')
parser.add_argument('destination', help='Destination directory')
parser.add_argument('-b', '-benchmark', action='store_true', help='display benchmark')
parser.add_argument('-sha', '-sha512', action='store_true', help='use sha512 instead of md5')
'''
if args.sha:
    crf_value = args.crf
else:
    crf_value = '23'
openssl/ and use archivematica tests for verification
'''
args = parser.parse_args()

source               = args.source
source_parent_dir    = os.path.dirname(source)
normpath             = os.path.normpath(source) 
dirname              = os.path.split(os.path.basename(source))[1]
relative_path        = normpath.split(os.sep)[-1]


destination                    = args.destination # or hardcode
manifest_destination           = destination + '/%s_manifest.md5' % dirname
destination_final_path         = destination + '/%s' % dirname
manifest_ =  '/%s_manifest.md5' % relative_path
manifest = os.path.expanduser("~/Desktop/%s") % manifest_
log_name_source_                = os.path.basename(args.source) + time.strftime("_%Y_%m_%dT%H_%M_%S")
log_name_source = os.path.expanduser("~/Desktop/%s.log") % log_name_source_
log_name_destination           = destination + '/%s_ifi_events_log.log' % dirname

def generate_log(log, what2log):
    if not os.path.isfile(log):
        with open(log,"wb") as fo:
            fo.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + getpass.getuser() + ' ' + what2log + ' \n')
    else:
        with open(log,"ab") as fo:
            fo.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + getpass.getuser() + ' ' + what2log + ' \n')
        
        
generate_log(log_name_source, 'move.py started.') 
generate_log(log_name_source, 'Source: %s' % source)  
generate_log(log_name_source, 'Destination: %s'  % destination)                       
def display_benchmark():
    print 'SOURCE MANIFEST TIME', source_manifest_time
    print 'COPY TIME', copy_time
    print 'DESTINATION MANIFEST TIME', destination_manifest_time

def test_write_capabilities(directory):
    if os.path.isdir(directory):
        temp = tempfile.mkstemp(dir=directory, suffix='.tmp')
        os.close(temp[0]) # Needed for windows.
        os.remove(temp[1])
    elif os.path.isfile(directory):
        print '\nFile transfer is not currently supported, only directories.\n'
        generate_log(log_name_source, 'Error: Attempted file transfer. Source and Destination must be a directory')   
        generate_log(log_name_source, 'move.py exit')   
        sys.exit()
    else:
        print ' %s is either not a directory or it does not exist' % directory
        generate_log(log_name_source, ' %s is either not a directory or it does not exist' % directory)
        generate_log(log_name_source, 'move.py exit')      
        sys.exit()

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
        generate_log(log_name_source, 'EVENT = File Transfer - Windows O.S - Software=Robocopy')  
        print destination_final_path
    elif _platform == "darwin":
        # https://github.com/amiaopensource/ltopers/blob/master/writelto#L51
        cmd = ['gcp','--preserve=mode,timestamps', '-nRv',source, destination_final_path]
        generate_log(log_name_source, 'EVENT = File Transfer - OSX - Software=gcp')  
        
        subprocess.call(cmd)
    elif _platform == "linux2":
        # https://github.com/amiaopensource/ltopers/blob/master/writelto#L51
        cmd = [ 'cp','--preserve=mode,timestamps', '-nRv',source, destination_final_path]
        generate_log(log_name_source, 'EVENT = File Transfer - Linux- Software=cp')  
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
def manifest_file_count(manifest2check):
    if os.path.isfile(manifest2check):
        print 'A manifest already exists'
        with open(manifest2check, "r") as fo:
            manifest_lines = [line.split(',') for line in fo.readlines()]
            count_in_manifest =  len(manifest_lines)
    return count_in_manifest    
  
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
    test_write_capabilities(source_parent_dir)
except OSError:
            print 'You cannot write to your source directory!'
            generate_log(log_name_source, 'EVENT = I/O Test - Failure - No write access to source directory.')      
            sys.exit()
          
try:
    test_write_capabilities(destination)
except OSError:
            print 'You cannot write to your destination!'
            generate_log(log_name_source, 'EVENT = I/O Test - Failure - No write access to destination directory.')  
            sys.exit()
overwrite_destination_manifest = check_overwrite(manifest_destination)
overwrite_destination_dir = check_overwrite_dir(destination_final_path)

remove_bad_files(source)
source_count = 0

for root, directories, filenames in os.walk(source):   
    for files in filenames:   
            source_count +=1 #works in windows at least
print source_count            

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
        make_manifest(source_parent_dir, relative_path,manifest)
        generate_log(log_name_source, 'EVENT = Generating source manifest')  
        
    except OSError:
            print 'You do not have access to this directory. Perhaps it is read only, or the wrong file system\n'
            sys.exit()

source_manifest_time = time.time() - source_manifest_start_time

copy_start_time = time.time()
if overwrite_destination_dir not in ('N','n'):
    if overwrite_destination_dir != None:
        generate_log(log_name_source, 'EVENT = File Transfer Overwrite - Destination directory already exists - Overwriting.')         
    copy_dir()
else:
    generate_log(log_name_source, 'EVENT = File Transfer Overwrite - Destination directory already exists - Not Overwriting.')  
    
copy_time = time.time() - copy_start_time

start_destination_manifest_time = time.time()
if overwrite_destination_manifest not in ('N','n'):
    if overwrite_destination_manifest == None:
        generate_log(log_name_source, 'EVENT = Destination Manifest Generation') 
    else:
        generate_log(log_name_source, 'EVENT = Destination Manifest Overwrite - Destination manifest already exists - Overwriting.') 
    print 'Generating destination manifest'
    files_in_manifest = make_manifest(destination,dirname, manifest_destination)
else:
    generate_log(log_name_source, 'EVENT = File Transfer Overwrite - Destination directory already exists - Not Overwriting.')
remove_bad_files(destination_final_path)

destination_manifest_time = time.time() - start_destination_manifest_time
destination_count = 0

for root, directories, filenames in os.walk(destination_final_path):  
    for files in filenames: 
            destination_count +=1 #works in windows at least
print destination_count  

if filecmp.cmp(manifest, manifest_destination, shallow=False):
    print "Your files have reached their destination and the checksums match"
    generate_log(log_name_source, 'EVENT = File Transfer Judgement - Success')  
else:
    print "***********YOUR CHECKSUMS DO NOT MATCH*************"
    if overwrite_destination_manifest not in ('N','n'):
        generate_log(log_name_source, 'EVENT = File Transfer Outcome - Failure') 
        print ' There are: \n %s files in your destination manifest \n' % files_in_manifest 
        print ' %s files in your destination \n %s files at source' % (destination_count, source_count)
        generate_log(log_name_source, 'EVENT = File Transfer Failure Explanation -  %s files in your destination,  %s files at source' % (destination_count, source_count)) 
    else:
        print ' %s files in your destination \n %s files at source' % (destination_count, source_count)
if args.b:
    display_benchmark()
