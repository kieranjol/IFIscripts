#!/usr/bin/env python3
'''
Validates md5 or sha512 sidecar checksum manifests.
'''
import sys
import os
import argparse
import time
import unicodedata
import ififuncs
from ififuncs import make_desktop_logs_dir


def get_input(manifest):
    '''
    Figures out what kind of input is passed to the script.
    '''
    if not manifest.endswith(('.txt', '.md5', '.exf')):
        print('Usage: validate.py manifest \nManifests can be a .txt or a .md5 or an ExactFile .exf file.')
        sys.exit()
    elif manifest.endswith('.exf'):
        print('ExactFile manifests have 5 lines of extra info which will confuse validate.py until I get around to fixing this. It will list some missing files but will validate checksums as usual.')
        return manifest
    else:
        return manifest

def parse_manifest(manifest, log_name_source, args):
    '''
    Analyses the manifest to see if any files are missing.
    Returns a list of missing files and a dictionary containing checksums
    and paths.
    '''
    if manifest.endswith('md5'):
        source_dir = os.path.join(
            os.path.dirname(manifest), os.path.basename(manifest).replace('_manifest.md5','')
        )
    elif manifest.endswith('sha512.txt'):
        source_dir = os.path.join(
            os.path.dirname(manifest), os.path.basename(manifest).replace('_manifest-sha512.txt','')
        )
    source_count, file_list = ififuncs.count_stuff(source_dir)
    missing_files_list = []
    manifest_dict = {}
    paths = []
    proceed = 'Y'
    os.chdir(os.path.dirname(manifest))
    with open(manifest, 'r', encoding='utf-8') as manifest_object:
        try:
            manifest_list = manifest_object.readlines()
        except UnicodeDecodeError:
            with open(manifest, 'r', encoding='cp1252') as manifest_object:
                manifest_list = manifest_object.readlines()
        for entries in manifest_list:
            checksum = entries.split(' ')[0]
            if 'manifest-sha512.txt' in manifest:
                path = entries[130:].replace('\r', '').replace('\n', '')
            else:
                path = entries[34:].replace('\r', '').replace('\n', '')
            path = unicodedata.normalize('NFC', path).replace('\\', '/')
            if not os.path.isfile(path):
                path = unicodedata.normalize('NFD', path)
            if not os.path.isfile(path):
                ififuncs.generate_log(
                    log_name_source,
                    '%s is missing' % path
                )
                print(('%s is missing' % path))
                missing_files_list.append(path)
            elif os.path.isfile(path):
                manifest_dict[path] = checksum
                paths.append(path)
    manifest_file_count = len(manifest_list)
    if source_count != manifest_file_count:
        print(' - There is mismatch between your file count and the manifest file count')
        print(' - checking which files are different')
        for i in file_list:
            if i not in paths:
                print((i, 'is present in your source directory but not in the source manifest'))
        if not args.y:
            proceed = ififuncs.ask_yes_no('Do you want to proceed regardless?')
    if proceed == 'N':
        print('Exiting')
        sys.exit()
    else:
        if len(missing_files_list) > 0:
            print(('The number of missing files: %s' % len(missing_files_list)))
            ififuncs.generate_log(
                log_name_source,
                'The number of missing files is: %s' % len(missing_files_list)
            )
        elif len(missing_files_list) == 0:
            print('All files present')
            ififuncs.generate_log(
                log_name_source,
                'All files present'
            )
    return manifest_dict, missing_files_list

def validate(manifest_dict, manifest, log_name_source, missing_files_list):
    '''
    Validates the files listed in the checksum manifest.
    '''
    ififuncs.generate_log(
        log_name_source,
        'Validating %s ' % manifest
    )
    error_counter = 0
    manifest_directory = os.path.dirname(manifest)
    os.chdir(manifest_directory)
    error_list = []
    for i in sorted(manifest_dict.keys()):
        print(('Validating %s' % i))
        if 'manifest-sha512.txt' in manifest:
            current_hash = ififuncs.hashlib_sha512(i)
        else:
            current_hash = ififuncs.hashlib_md5(i)
        if current_hash == manifest_dict[i]:
            print(('%s has validated' % i))
        else:
            print(('%s has mismatched checksum - %s expected - %s hashed' % (i, manifest_dict[i], current_hash)))
            ififuncs.generate_log(
                log_name_source,
                '%s has mismatched checksum - %s expected - %s hashed' % (i, manifest_dict[i], current_hash)
            )
            error_list.append('%s has mismatched checksum - %s expected - %s hashed' % (i, manifest_dict[i], current_hash))
            error_counter += 1
    if error_counter > 0:
        print(('\n\n*****ERRORS***********!!!!\n***********\nThe number of mismatched checksums is: %s\n***********\n' % error_counter))
        ififuncs.generate_log(
            log_name_source,
            'The number of mismatched checksums is: %s' % error_counter
        )
        print('***** List of mismatched files*****')
        for i in error_list:
            print(i)
    elif len(missing_files_list) == 0:
        print('All checksums have validated')
        ififuncs.generate_log(
            log_name_source,
            'All checksums have validated'
        )
    if len(missing_files_list) > 0:
        print(('ERRORS - The number of missing files: %s' % len(missing_files_list)))
        ififuncs.generate_log(
            log_name_source,
            'ERRORS - The number of mismatched checksums is: %s' % len(missing_files_list)
        )
        for i in missing_files_list:
            print((('%s is missing') % i))
    return error_counter + len(missing_files_list)


def make_parser(args_):
    '''
    Creates command line arguments and help.
    '''
    parser = argparse.ArgumentParser(description='MD5 checksum manifest validator. Currently this script expects an md5 checksum, followed by two spaces, followed by a file path.'
                                     ' Written by Kieran O\'Leary.')
    parser.add_argument('input', help='file path of md5 checksum file')
    parser.add_argument('-update_log', help='updates the package log file with the fixity check information', action='store_true')
    parser.add_argument('-y', help='answer Y to user input questions regarding manifest issues', action='store_true')
    parsed_args = parser.parse_args(args_)
    return parsed_args


def check_manifest(args, log_name_source):
    '''
    Launches other functions.
    '''
    manifest = get_input(args.input)
    manifest_dict, missing_files_list = parse_manifest(manifest, log_name_source, args)
    error_counter = validate(manifest_dict, manifest, log_name_source, missing_files_list)
    return manifest, error_counter


def log_results(manifest, log, args):
    '''
    If a sipcreator type log is found,validate will update the log with the
    results.
    '''
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
        with open(logfile, 'a') as ba:
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
                with open(possible_manifest, 'w') as fo:
                    for lines in updated_manifest:
                        fo.write(lines)
                updated_manifest = []


def main(args_):
    '''
    Launches all other functions when called from the command line.
    '''
    args = make_parser(args_)
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
    manifest, error_counter = check_manifest(args, log_name_source)
    if args.update_log:
        log_results(manifest, log_name_source, args)
    return error_counter

if __name__ == '__main__':
    main(sys.argv[1:])
