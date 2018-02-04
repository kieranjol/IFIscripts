#!/usr/bin/env python
'''
Generates sidecar MD5 or SHA512 checksum manifest.
'''
import sys
import os
import argparse
import time
import shutil
import ififuncs
from ififuncs import generate_log
from ififuncs import manifest_file_count
from ififuncs import hashlib_manifest
from ififuncs import make_desktop_logs_dir, make_desktop_manifest_dir


def remove_bad_files(root_dir, log_name_source):
    '''
    Removes unwanted files.
    Verify if this is different than the same function in ififuncs.
    '''
    rm_these = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
    for root, _, files in os.walk(root_dir):
        for name in files:
            path = os.path.join(root, name)
            for i in rm_these:
                if name == i:
                    print '***********************' + 'removing: ' + path
                    generate_log(
                        log_name_source,
                        'EVENT = Unwanted file removal - %s was removed' % path
                    )
                    try:
                        os.remove(path)
                    except OSError:
                        print 'can\'t delete as source is read-only'
def main(args_):
    '''
    Overly long main function that makes a sidecar manifest.
    This needs to get broken up into smaller functions.
    '''
    parser = argparse.ArgumentParser(description='Generate manifest with'
                                     ' checksums for a directory'
                                     ' Written by Kieran O\'Leary.')
    parser.add_argument(
        'source',
        help='Input directory'
    )
    parser.add_argument(
        '-s', '-sidecar',
        action='store_true',
        help='Generates Sidecar'
    )
    parser.add_argument(
        '-f', '-felix',
        action='store_true',
        help='Felix Meehan workflow - places manifest inside of source directory'
    )
    parser.add_argument(
        '-sha512',
        action='store_true',
        help='Generates sha512 checksums instead of md5'
    )
    args = parser.parse_args(args_)
    source = args.source
    source_parent_dir = os.path.dirname(source)
    normpath = os.path.normpath(source)
    relative_path = normpath.split(os.sep)[-1]
    log_name_source_ = os.path.basename(
        args.source
    )  + time.strftime("_%Y_%m_%dT%H_%M_%S")
    if args.s:
        if args.sha512:
            manifest = source_parent_dir + '/%s_manifest-sha512.txt' % relative_path
        else:
            manifest = source_parent_dir + '/%s_manifest.md5' % relative_path
        log_name_source = source_parent_dir + '/%s.log' % log_name_source_
    elif args.f:
        if args.sha512:
            manifest = source_parent_dir + '/%s_manifest-sha512.txt' % relative_path
        else:
            manifest = source + '/%s_manifest.md5' % relative_path
        log_name_source = source_parent_dir + '/%s.log' % log_name_source_
    else:
        if args.sha512:
            manifest_ = manifest_ = '/%s_manifest-sha512.txt' % relative_path
        else:
            manifest_ = '/%s_manifest.md5' % relative_path
        desktop_manifest_dir = make_desktop_manifest_dir()
        manifest = "%s/%s" % (desktop_manifest_dir, manifest_)
        desktop_logs_dir = make_desktop_logs_dir()
        log_name_source = "%s/%s.log" % (desktop_logs_dir, log_name_source_)
    if args.sha512:
        module = 'hashlib.sha512'
    else:
        module = 'hashlib.md5'
    generate_log(log_name_source, 'manifest.py started.')
    if sys.platform == "win32":
            generate_log(
                log_name_source,
                'EVENT = Generating manifest: status=started, eventType=message digest calculation, module=%s, agent=Windows' % module
            )
    if sys.platform == "darwin":
            generate_log(
                log_name_source,
                'EVENT = Generating manifest: status=started, eventType=message digest calculation, module=%s, agent=OSX' % module
            )
    elif sys.platform == "linux2":
        generate_log(
                log_name_source,
                'EVENT = Generating manifest: status=started, eventType=message digest calculation, module=%s, agent=Linux' % module
            )
    ififuncs.generate_log(
        log_name_source,
        'eventDetail=manifest.py %s' % ififuncs.get_script_version('manifest.py'))
    generate_log(log_name_source, 'Source: %s' % source)
    if os.path.isfile(source):
        print '\nFile checksum is not currently supported, only directories.\n'
        generate_log(log_name_source, 'Error: Attempted to generate manifest for file. Only Directories/Folders are currently supported')
        generate_log(log_name_source, 'manifest.py exit')
        sys.exit()
    elif not os.path.isdir(source):
        print ' %s is either not a directory or it does not exist' % source
        generate_log(log_name_source, ' %s is either not a directory or it does not exist' % source)
        generate_log(log_name_source, 'manifest.py exit')
        sys.exit()
    remove_bad_files(source, log_name_source)
    source_count = 0
    for _, _, filenames in os.walk(source):
        # There has to be a better way to count the files..
        for _ in filenames:
            source_count += 1 #works in windows at least
    if os.path.isfile(manifest):
        count_in_manifest = manifest_file_count(manifest)
        if source_count != count_in_manifest:
            print 'This manifest may be outdated as the number of files in your directory does not match the number of files in the manifest'
            generate_log(log_name_source, 'EVENT = Existing source manifest check - Failure - The number of files in the source directory is not equal to the number of files in the source manifest ')
            sys.exit()
    if not os.path.isfile(manifest):
        try:
            print 'Generating source manifest'
            generate_log(log_name_source, 'EVENT = Generating source manifest')
            if args.f:
                if args.sha512:
                    ififuncs.sha512_manifest(source, manifest, source)
                else:
                    hashlib_manifest(source, manifest, source)
                shutil.move(log_name_source, source)
            else:
                if args.sha512:
                    ififuncs.sha512_manifest(source, manifest, source_parent_dir)
                else:
                    hashlib_manifest(source, manifest, source_parent_dir)
        except OSError:
            print 'You do not have access to this directory. Perhaps it is read only, or the wrong file system\n'
            sys.exit()
    else:
        generate_log(log_name_source, 'EVENT = Existing source manifest check - Source manifest already exists. Script will exit. ')
    print 'Manifest created in %s' % manifest
    generate_log(log_name_source, 'Manifest created in %s' % manifest)
    return log_name_source

if __name__ == '__main__':
    main(sys.argv[1:])
