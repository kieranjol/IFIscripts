#!/usr/bin/env python
'''
Generates SIPS by calling various microservices and functions.
'''
import os
import argparse
import ififuncs
import sys
import shutil
import subprocess
import time
from masscopy import analyze_log


def make_folder_path(path):
    '''
    Generates objects/logs/metadata/UUID folder structure in output.
    Returns the path.
    '''
    representation_uuid = ififuncs.create_uuid()
    path = os.path.join(path, representation_uuid)
    ififuncs.make_folder_structure(path)
    return path

def extract_checksums(manifest, path_list, basename):
    new_manifest = []
    manifest_ =  '/%s_manifest.md5' % basename
    desktop_manifest_dir = ififuncs.make_desktop_manifest_dir()
    manifest_textfile = "%s/%s" % (desktop_manifest_dir, manifest_)
    if os.path.isfile(manifest):
        with open(manifest, 'r') as fo:
            manifest_lines = fo.readlines()
            for path in path_list:
                for i in manifest_lines:
                    if path in i:
                        if path[0] == '/':
                            path = path[1:]
                        new_manifest.append(i[:32] + '  ' + path)
    with open(manifest_textfile,"wb") as fo:
        for i in new_manifest:
            fo.write(i + '\n')

def consolidate_manifests(path):
    uuid = os.path.basename(path)
    objects_dir = os.path.join(path, 'objects')
    new_manifest_textfile = os.path.join(os.path.dirname(path), uuid + '_manifest.md5')
    collective_manifest = []
    for manifests in os.listdir(objects_dir):
        if manifests.endswith('.md5'):
             if not manifests[0] == '.':
                 with open(os.path.join(objects_dir, manifests), 'r') as fo:
                     manifest_lines = fo.readlines()
                     for i in manifest_lines:
                         new_manifest_path = uuid + '/objects/' + i[34:]
                         collective_manifest.append(i[:32] + '  ' + new_manifest_path   )
                 shutil.move(objects_dir + '/' +  manifests, os.path.join(path, 'logs'))
    with open(new_manifest_textfile, 'ab') as manifest_object:
        for checksums in collective_manifest:
            manifest_object.write(checksums)


def consolidate_logs(lognames, path):
    uuid = os.path.basename(path)
    collective_manifest = []
    new_log_textfile = os.path.join(path, 'logs' + '/' + uuid + '_log.log')
    for log in lognames:
        with open(log, 'r') as fo:
            log_lines = fo.readlines()
        with open(new_log_textfile, 'ab') as log_object:
            for lines in log_lines:
                log_object.write(lines)


def get_relative_filepaths(inputs):
    path_list = []
    for paths in inputs:
        for root, dirnames, filenames in os.walk(paths):
            for filename in filenames:
                path_list.append(os.path.join(root.replace(paths,''), filename))
    return sorted(path_list)

def main():
    '''
    Generates SIPS by calling various microservices and functions.
    '''
    parser = argparse.ArgumentParser(
        description='Wraps objects into a SIP'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        '-i', nargs='+',
        help='full path of input directory', required=True
    )
    parser.add_argument(
        '-o', '-output',
        help='full path of output directory', required=True
    )
    parser.add_argument(
        '-m', '-manifest',
        help='full path to a pre-existing manifest'
    )
    args = parser.parse_args()
    sip_path = make_folder_path(os.path.join(args.o))
    path_list = get_relative_filepaths(args.i)
    
    '''
    print args.i
    basename = os.path.basename(args.i[0])
    
    print basename
    extract_checksums(args.m, path_list, basename)
    '''
    log_names = []
    for t in args.i:
        print t
        moveit_cmd = [
                        sys.executable,
                        os.path.expanduser("~/ifigit/ifiscripts/moveit.py"),
                        t, os.path.join(sip_path, 'objects')]
        log_name_source_ = os.path.basename(
                t
                ) + time.strftime("_%Y_%m_%dT%H_%M_%S")
        desktop_logs_dir = ififuncs.make_desktop_logs_dir()
        log_name_source = "%s/%s.log" % (desktop_logs_dir, log_name_source_)
        log_names.append(log_name_source)
        subprocess.check_call(moveit_cmd)
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
    new_manifest = consolidate_manifests(sip_path)
    print sip_path
    print log_names
    consolidate_logs(log_names, sip_path)
    '''
    bring ubunutu and macbook to loopline,do transfers there
    take manifests, add uuid, put in correct location, delete orig manifests
    '''

if __name__ == '__main__':
    main()
