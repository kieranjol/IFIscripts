#!/usr/bin/env python

import sys
import subprocess
import os
import pdb
import filecmp
import tempfile
import time
import argparse
import getpass
import hashlib
from sys import platform as _platform
from ififuncs import make_desktop_logs_dir, make_desktop_manifest_dir, generate_log


def hashlib_md5(filename, manifest):
   read_size = 0
   last_percent_done = 0
   m = hashlib.md5()
   total_size = os.path.getsize(filename)
   with open(str(filename), 'rb') as f:
       while True:
           buf = f.read(2**20)
           if not buf:
               break
           read_size += len(buf)
           m.update(buf)
           percent_done = 100 * read_size / total_size
           if percent_done > last_percent_done:
               sys.stdout.write('[%d%%]\r' % percent_done)
               sys.stdout.flush()
               last_percent_done = percent_done
   md5_output = m.hexdigest()
   return md5_output + '  ' + os.path.abspath(filename) +  '\n'

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
                    try:
                        os.remove(path)
                    except OSError:
                        print 'can\'t delete as source is read-only'

def make_manifest(manifest_dir, relative_manifest_path, manifest_textfile, path_to_remove):
    global manifest_generator
    source_counter = 0
    for root, directories, filenames in os.walk(source):
        directories[:] = [d for d in directories if not d[0] == '.']
        directories[:] = [d for d in directories if not d[0] == 'System Volume Information']
        filenames = [f for f in filenames if not os.path.basename(root) == 'System Volume Information']
        filenames = [f for f in filenames if not f[0] == '.']

        for files in filenames:
                source_counter +=1
    counter2 = 1
    os.chdir(manifest_dir)
    if os.path.isfile(manifest_destination):
        print 'Destination manifest already exists'

    for root, directories, filenames in os.walk(manifest_dir):
            directories[:] = [d for d in directories if not d[0] == '.']
            directories[:] = [d for d in directories if not d[0] == 'System Volume Information']
            filenames = [f for f in filenames if not os.path.basename(root) == 'System Volume Information']
            filenames = [f for f in filenames if not f[0] == '.']
            for files in filenames:
                print 'Generating MD5 for %s - %d of %d' % (files, counter2, source_counter)
                md5 = hashlib_md5(os.path.join(root, files), manifest)
                root2 = root.replace(path_to_remove, '')
                try:
                    if root2[0] == '/':
                        root2 = root2[1:]
                    if root2[0] == '\\':
                        root2 = root2[1:]
                except: IndexError
                manifest_generator +=    md5[:32] + '  ' + os.path.join(root2,files).replace("\\", "/") + '\n'
                counter2 += 1
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
        subprocess.call(['robocopy',source, destination_final_path, '/E', '/XA:SH', '/XD', '.*', '/XD', '*System Volume Information*', '/XD', '$Recycle.bin', '/a-:SH', '/a+:R'])
        generate_log(log_name_source, 'EVENT = File Transfer - Windows O.S - Software=Robocopy')
    elif _platform == "darwin":
        if args.l:
           cmd = [ 'gcp','--preserve=mode,timestamps', '-nRv', source, destination_final_path]
           generate_log(log_name_source, 'EVENT = File Transfer - OSX - Software=gcp')
           subprocess.call(cmd) 
        # https://github.com/amiaopensource/ltopers/blob/master/writelto#L51
        else:
            if rootpos == 'y':
                if not os.path.isdir(destination + '/' + dirname):
                    os.makedirs(destination + '/' + dirname)
                cmd = ['rsync','-rtv', '--exclude=.*', '--exclude=.*/', '--stats','--progress', source, destination + '/' + dirname]
            else:
                cmd = ['rsync','-rtv', '--exclude=.*', '--exclude=.*/', '--stats','--progress', source, destination]
            generate_log(log_name_source, 'EVENT = File Transfer - OSX - Software=rsync')
            print cmd
            subprocess.call(cmd)
    elif _platform == "linux2":
        # https://github.com/amiaopensource/ltopers/blob/master/writelto#L51
        cmd = [ 'cp','--preserve=mode,timestamps', '-nRv',source, destination_final_path]
        generate_log(log_name_source, 'EVENT = File Transfer - Linux- Software=cp')
        subprocess.call(cmd)


def diff_report(file1, file2, log_name_source):
    with open(file1, 'r') as fo:
        sourcelist = fo.readlines()

    with open(file2, 'r') as ba:
        destlist = ba.readlines()

    for i in sourcelist:
        if i not in destlist:
            print '%s was expected, but a different value was found in destination manifest' % i.rstrip()
            generate_log(log_name_source, 'ERROR = %s was expected, but a different value was found in destination manifest' % i.rstrip())


def check_extra_files(file1, file2, log_name_source):
    with open(file1, 'r') as fo:
        sourcelist = fo.readlines()

    with open(file2, 'r') as ba:
        destlist = ba.readlines()
    destlist_files = []
    sourcelist_files = []
    for x in destlist:
        destlist_files.append(x[32:])
    for y in sourcelist:
        sourcelist_files.append(y[32:])

    for i in destlist_files:
        if i not in sourcelist_files:
            print '%s is in your destination manifest but is not in the source manifest' % i.rstrip()
            generate_log(log_name_source, 'ERROR = %s is in your destination manifest but is not in the source manifest' % i.rstrip())


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
        print 'A manifest already exists - Checking if manifest is up to date'
        with open(manifest2check, "r") as fo:
            manifest_files = []
            manifest_lines = [line.split(',') for line in fo.readlines()]
            for line in manifest_lines:
                for a in line:
                    a = a.split('\\')
                    manifest_files.append(a[-1].rsplit()[0])
            count_in_manifest =  len(manifest_lines)
            manifest_info = [count_in_manifest, manifest_files]
    return manifest_info

def check_overwrite_dir(dir2check):
    if os.path.isdir(dir2check):
        print 'A directory already exists at your destination. Overwrite? Y/N?'
        overwrite_destination_dir = ''
        while overwrite_destination_dir not in ('Y','y','N','n'):
            overwrite_destination_dir = raw_input()
            if overwrite_destination_dir not in ('Y','y','N','n'):
                print 'Incorrect input. Please enter Y or N'
        return overwrite_destination_dir
# Currently, destination manifest will be overwritten. user input should be required. source manifest will not be overwritten, it will be read.
parser = argparse.ArgumentParser(description='Copy directory with checksum comparison and manifest generation.'
                                 ' Written by Kieran O\'Leary.')
parser.add_argument('source', help='Input directory')
parser.add_argument('destination', help='Destination directory')
parser.add_argument('-b', '-benchmark', action='store_true', help='display benchmark')
parser.add_argument('-l', '-lto', action='store_true', help='use gcp instead of rsync on osx for SPEED on LTO')
#parser.add_argument('-sha', '-sha512', action='store_true', help='use sha512 instead of md5')

global rootpos
rootpos = ''
args = parser.parse_args()
source               = args.source
source_parent_dir    = os.path.dirname(source)
normpath             = os.path.normpath(source)
dirname              = os.path.split(os.path.basename(source))[1]
if dirname == '':
    rootpos = 'y'
    dirname = raw_input('What do you want your destination folder to be called?\n')
relative_path        = normpath.split(os.sep)[-1]
destination                    = args.destination # or hardcode
destination_final_path         = destination + '/%s' % dirname
manifest_destination = destination + '/%s_manifest.md5' % dirname
manifest_ =  '/%s_manifest.md5' % dirname
desktop_manifest_dir = make_desktop_manifest_dir()
manifest = "%s/%s" % (desktop_manifest_dir, manifest_)
manifest_sidecar                = source_parent_dir + '/%s_manifest.md5' % relative_path
manifest_root = source + '/%s_manifest.md5' % os.path.basename(source)
log_name_source_                = dirname + time.strftime("_%Y_%m_%dT%H_%M_%S")
desktop_logs_dir = make_desktop_logs_dir()
log_name_source = "%s/%s.log" % (desktop_logs_dir, log_name_source_)
log_name_destination           = destination + '/%s_ifi_events_log.log' % dirname
generate_log(log_name_source, 'move.py started.')
generate_log(log_name_source, 'Source: %s' % source)
generate_log(log_name_source, 'Destination: %s'  % destination)

manifest_generator = ''

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
file_list = []
for root, directories, filenames in os.walk(source):
    filenames = [f for f in filenames if not f[0] == '.']
    directories[:] = [d for d in directories if not d[0] == '.']
    for files in filenames:
            source_count +=1
            file_list.append(files)
proceed = 'n'
if os.path.isfile(manifest_root):
    print '1'
    proceed = 'y'
    manifest_info = manifest_file_count(manifest_root)
    count_in_manifest = manifest_info[0]
    manifest_files = manifest_info[1]
elif os.path.isfile(manifest_sidecar):
    print '2'
    manifest_info = manifest_file_count(manifest_sidecar)
    proceed = 'y'
    count_in_manifest = manifest_info[0]
    manifest_files = manifest_info[1]
elif os.path.isfile(manifest):
    print '3'
    manifest_info = manifest_file_count(manifest)
    count_in_manifest = manifest_info[0]
    manifest_files = manifest_info[1]
    proceed = 'y'
if proceed == 'y':
    if source_count != count_in_manifest:
        print 'checking which files are different'
        for i in file_list:
           if i not in manifest_files:
               print i, 'is present in your source directory but not in the source manifest'
        for i in manifest_files:
            if i not in file_list:
                print i, 'is present in manifest but is missing in your source files'
        print 'This manifest may be outdated as the number of files in your directory does not match the number of files in the manifest'
        print 'There are',source_count,'files in your source directory',  count_in_manifest, 'in the manifest'
        generate_log(log_name_source, 'EVENT = Existing source manifest check - Failure - The number of files in the source directory is not equal to the number of files in the source manifest ')
        sys.exit()
source_manifest_start_time = time.time()

if os.path.isfile(manifest_sidecar):
    print 'Manifest Sidecar exists - Source manifest Generation will be skipped.'
    manifest = manifest_sidecar
elif not os.path.isfile(manifest):
    try:
        print 'Generating source manifest'
        generate_log(log_name_source, 'EVENT = Generating source manifest')
        if rootpos == 'y':
            make_manifest(source, relative_path,manifest, source)
        else:
            make_manifest(source, relative_path,manifest, os.path.dirname(source))
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
    manifest_generator = ''
    if rootpos == 'y':
        files_in_manifest = make_manifest(destination_final_path,dirname, manifest_destination, destination)
    else:
        files_in_manifest = make_manifest(destination_final_path,dirname, manifest_destination, destination)
else:
    generate_log(log_name_source, 'EVENT = File Transfer Overwrite - Destination directory already exists - Not Overwriting.')
remove_bad_files(destination_final_path)

destination_manifest_time = time.time() - start_destination_manifest_time
destination_count = 0

for root, directories, filenames in os.walk(destination_final_path):
    for files in filenames:
            destination_count +=1 #works in windows at least


if rootpos == 'y':
    manifest_temp = tempfile.mkstemp(dir=desktop_manifest_dir, suffix='.md5')
    os.close(manifest_temp[0]) # Needed for windows.
    with open(manifest, 'r') as fo:
        dest_manifest_list = fo.readlines()
        with open(manifest_temp[1], 'wb') as temp_object:
            for i in dest_manifest_list:
                temp_object.write(i[:33] + ' ' + dirname + '/' +  i[34:])
        manifest = manifest_temp[1]

if filecmp.cmp(manifest, manifest_destination, shallow=False):
    print "Your files have reached their destination and the checksums match"
    generate_log(log_name_source, 'EVENT = File Transfer Judgement - Success')
else:
    print "***********YOUR CHECKSUMS DO NOT MATCH*************"
    if overwrite_destination_manifest not in ('N','n'):
        generate_log(log_name_source, 'EVENT = File Transfer Outcome - Failure')
        print ' There are: \n %s files in your destination manifest \n' % files_in_manifest
        print ' %s files in your destination \n %s files at source' % (destination_count, source_count)
        diff_report(manifest, manifest_destination, log_name_source)
        check_extra_files(manifest, manifest_destination, log_name_source)
        generate_log(log_name_source, 'EVENT = File Transfer Failure Explanation -  %s files in your destination,  %s files at source' % (destination_count, source_count))
    else:
        print ' %s files in your destination \n %s files at source' % (destination_count, source_count)

if args.b:
    display_benchmark()
