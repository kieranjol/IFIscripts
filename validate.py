#!/usr/bin/env python
import sys
import hashlib
import os
import argparse
import time
import ififuncs
from ififuncs import make_desktop_logs_dir


def hashlib_md5(filename):
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
   return md5_output

def get_input(manifest):
    if not manifest.endswith(('.txt', '.md5', '.exf' )):
        print 'Usage: validate.py manifest \nManifests can be a .txt or a .md5 or an ExactFile .exf file.'
        sys.exit()
    elif manifest.endswith('.exf'):
        print 'ExactFile manifests have 5 lines of extra info which will confuse validate.py until I get around to fixing this.  It will list some missing files but will validate checksums as usual.'
        return manifest
    else:
        return manifest

def parse_manifest(manifest, log_name_source):
    missing_files_list = []
    manifest_dict = {}
    os.chdir(os.path.dirname(manifest))
    with open(manifest, 'rb') as manifest_object:
        manifest_list = manifest_object.readlines()
        for entries in manifest_list:
            checksum = entries.split(' ')[0]
            if 'manifest-sha512.txt' in manifest:
                path = entries[130:].replace('\r', '').replace('\n', '')
            else:
                path = entries[34:].replace('\r', '').replace('\n', '')
            path = path.replace('\\', '/')
            if not os.path.isfile(path):
                ififuncs.generate_log(
                    log_name_source,
                    '%s is missing' % path 
                )
                print '%s is missing' % path
                missing_files_list.append(path)
            elif os.path.isfile(path):
                manifest_dict[path] = checksum
    if len(missing_files_list) > 0:
        print 'The number of missing files: %s' % len(missing_files_list)
        ififuncs.generate_log(
            log_name_source,
            'The number of missing files is: %s' %  len(missing_files_list)
        )
    elif len(missing_files_list) == 0:
        print 'All files present'
        ififuncs.generate_log(
            log_name_source,
            'All files present'
        )
    return manifest_dict, missing_files_list

def validate(manifest_dict, manifest, log_name_source, missing_files_list):
    ififuncs.generate_log(
        log_name_source,
        'Validating %s ' % manifest
    )
    error_counter = 0
    manifest_directory = os.path.dirname(manifest)
    os.chdir(manifest_directory)
    error_list = []

    for i in sorted(manifest_dict.keys()):
        print 'Validating %s' % i
        if 'manifest-sha512.txt' in manifest:
            current_hash = ififuncs.hashlib_sha512(i)
        else:
            current_hash = hashlib_md5(i)
        if current_hash == manifest_dict[i]:
            print '%s has validated' % i
        else:
            print '%s has mismatched checksum - %s expected - %s hashed' % (i, manifest_dict[i], current_hash)
            ififuncs.generate_log(
                log_name_source,
                '%s has mismatched checksum - %s expected - %s hashed' % (i, manifest_dict[i], current_hash)
            )
            error_list.append('%s has mismatched checksum - %s expected - %s hashed' % (i, manifest_dict[i], current_hash))
            error_counter += 1
    if error_counter > 0:
        print '\n\n*****ERRORS***********!!!!\n***********\nThe number of mismatched checksums is: %s\n***********\n' % error_counter
        ififuncs.generate_log(
        log_name_source,
        'The number of mismatched checksums is: %s' %  error_counter
    )
        print '***** List of mismatched files*****'
        for i in error_list:
            print i
    elif len(missing_files_list) == 0:
        print 'All checksums have validated'
        ififuncs.generate_log(
            log_name_source,
            'All checksums have validated'
        )
    if len(missing_files_list) > 0:
        print 'ERRORS - The number of missing files: %s' % len(missing_files_list)
        ififuncs.generate_log(
            log_name_source,
            'ERRORS - The number of mismatched checksums is: %s' %  len(missing_files_list)
        )
        for i in missing_files_list:
            print('%s is missing') % i


def make_parser():
    parser = argparse.ArgumentParser(description='MD5 checksum manifest validator. Currently this script expects an md5 checksum, followed by two spaces, followed by a file path.'
                                 ' Written by Kieran O\'Leary.')
    parser.add_argument('input', help='file path of md5 checksum file')
    return parser

def check_manifest(input, log_name_source):
    manifest = get_input(input)
    manifest_dict, missing_files_list = parse_manifest(manifest, log_name_source)
    validate(manifest_dict, manifest, log_name_source, missing_files_list)
    return manifest
def log_results(manifest, log, args):
    updated_manifest = []
    if 'manifest-sha512.txt' in manifest:
        basename = os.path.basename(manifest).replace('_manifest-sha512.txt', '')
    else:
        basename = os.path.basename(manifest).replace('_manifest.md5', '')
    possible_manifests = [basename + '_manifest-sha512.txt', basename + '_manifest.md5']
    logname = basename + '_sip_log.log'
    sip_dir = os.path.join(
        os.path.dirname(args.input), basename)
    logs_dir = os.path.join(sip_dir, 'logs')
    logfile = os.path.join(logs_dir, logname)
    if os.path.isfile(logfile):
        with open(log, 'r') as fo:
            validate_log = fo.readlines()
        with open(logfile, 'ab') as ba:
            for lines in validate_log:
                ba.write(lines)
        for possible_manifest in possible_manifests:
            if os.path.isfile(possible_manifest):
                with open(possible_manifest, 'r') as manifesto:
                    manifest_lines = manifesto.readlines()
                    for lines in manifest_lines:
                        if logname in lines:
                            if 'manifest-sha512.txt' in possible_manifest:
                                lines = lines[:127].replace(lines[:127], ififuncs.hashlib_sha512(logfile)) + lines[128:]
                            elif '_manifest.md5' in possible_manifest:
                                lines = lines[:31].replace(lines[:31], ififuncs.hashlib_md5(logfile)) + lines[32:]
                        updated_manifest.append(lines)
                with open(possible_manifest, 'wb') as fo:
                    for lines in updated_manifest:
                        fo.write(lines)
                updated_manifest = []


def main():
    parser = make_parser()
    args = parser.parse_args()
    desktop_logs_dir = make_desktop_logs_dir()
    log_name_source_ = os.path.basename(args.input) + time.strftime("_%Y_%m_%dT%H_%M_%S")
    log_name_source = "%s/%s_fixity_validation.log" % (desktop_logs_dir, log_name_source_)
    ififuncs.generate_log(
        log_name_source,
        'EVENT = validate.py started'
    )
    ififuncs.generate_log(
        log_name_source,
        'eventDetail=validate.py %s' % ififuncs.get_script_version('validate.py')
    )
    ififuncs.generate_log(
        log_name_source,
        'Command line arguments: %s' % args
    )
    manifest = check_manifest(args.input, log_name_source)
    log_results(manifest, log_name_source, args)
if __name__ == '__main__':
   main()
