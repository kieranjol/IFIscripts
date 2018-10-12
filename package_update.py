#!/usr/bin/env python
'''
Moves files into subfolders, updates logfiles and manifests.
'''
import os
import argparse
import sys
import datetime
import shutil
import ififuncs
import copyit
import sipcreator


def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Moves files into subfolders, updates logfiles and manifests.'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        '-i', nargs='+',
        help='full path of files to be moved', required=True
    )
    parser.add_argument(
        '-new_folder',
        help='full path of the new destination folder', required=True
    )
    parser.add_argument(
        'input',
        help='full path of \'sipcreator\' Object Entry package'
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.')
    parser.add_argument(
        '-copy', action='store_true',
        help='Copies a file into a package instead of moving it. This should be used when adding files that originate outside of the package.')
    parsed_args = parser.parse_args(args_)
    return parsed_args


def update_manifest(manifest, old_path, new_path, new_log_textfile):
    '''
    Updates the path in a checksum manifest to reflect the new location.
    '''
    updated_lines = []
    with open(manifest, 'r') as file_object:
        checksums = file_object.readlines()
        for line in checksums:
            if old_path in line:
                line = line.replace(old_path, new_path)
                print 'the following path: %s has been updated with %s in the package manifest' % (old_path, new_path)
                ififuncs.generate_log(
                    new_log_textfile,
                    'EVENT = eventType=metadata modification,'
                    ' agentName=package_update.py,'
                    ' eventDetail=the following path: %s has been updated with %s in the package manifest' % (old_path, new_path)
                )
                updated_lines.append(line)
            else:
                updated_lines.append(line)
    with open(manifest, 'w') as updated_manifest:
        for updated_line in updated_lines:
            updated_manifest.write(updated_line)


def main(args_):
    '''
    Launch all the functions for creating an IFI SIP.
    '''
    args = parse_args(args_)
    source = args.input
    sip_path = ififuncs.check_for_sip([source])
    if sip_path is not None:
        oe_path = os.path.dirname(sip_path)
        uuid = os.path.basename(sip_path)
        sip_manifest = os.path.join(
            oe_path, uuid
            ) + '_manifest.md5'
    else:
        # this is assuming that the other workflow will be the 
        # special collections workflow that has the uuid as the parent.
        # some real checks should exist for this whole if/else flow.
        sip_path = args.input
        oe_path = os.path.dirname(args.input)
        uuid = os.path.basename(sip_path)
        sip_manifest = os.path.join(
            oe_path, uuid + '_manifest.md5'
            )
    start = datetime.datetime.now()
    print args
    if args.user:
        user = args.user
    else:
        user = ififuncs.get_user()
    new_log_textfile = os.path.join(sip_path, 'logs' + '/' + uuid + '_sip_log.log')
    ififuncs.generate_log(
        new_log_textfile,
        'EVENT = package_update.py started'
    )
    ififuncs.generate_log(
        new_log_textfile,
        'eventDetail=package_update.py %s' % ififuncs.get_script_version('package_update.py')
    )
    ififuncs.generate_log(
        new_log_textfile,
        'Command line arguments: %s' % args
    )
    ififuncs.generate_log(
        new_log_textfile,
        'EVENT = agentName=%s' % user
    )
    if not os.path.isdir(args.new_folder):
        os.makedirs(args.new_folder)
    if isinstance(args.i[0], (list,)):
        args.i = args.i[0]
    for filenames in args.i:
        if args.copy:
            copyit.main([filenames, args.new_folder])
            ififuncs.generate_log(
                new_log_textfile,
                'EVENT = eventType=file movement,'
                ' eventOutcomeDetailNote=%s has been moved into %s'
                ' agentName=copyit.py'
                % (filenames, args.new_folder)
            )
            # this is hardcoded - pick this apart so that any folder can be added to.
            # this must be fixed in normalise.py as well.
            relative_new_path = args.new_folder.replace(sip_path, '')
            print relative_new_path, 'relative'
            if (relative_new_path[0] == '/') or relative_new_path[0] == '\\':
                relative_new_path = relative_new_path[1:]
            sipcreator.consolidate_manifests(sip_path, relative_new_path, new_log_textfile)
            log_manifest = os.path.join(os.path.dirname(new_log_textfile), os.path.basename(filenames) + '_manifest.md5')
            ififuncs.manifest_update(sip_manifest, log_manifest)
            ififuncs.sort_manifest(sip_manifest)
        else:
            # add test to see if it actually deleted - what if read only?
            shutil.move(filenames, args.new_folder)
            ififuncs.generate_log(
                new_log_textfile,
                'EVENT = eventType=file movement,'
                ' eventOutcomeDetailNote=%s has been moved into %s'
                ' agentName=shutil.move()'
                % (filenames, args.new_folder)
            )
            print '%s has been moved into %s' % (filenames, args.new_folder)
            relative_filename = filenames.replace(os.path.dirname(args.input) + '/', '').replace('\\', '/')
            relative_filename = filenames.replace(os.path.dirname(args.input) + '\\', '').replace('\\', '/')
            relative_new_folder = args.new_folder.replace(os.path.dirname(args.input) + '/', '').replace('\\', '/')
            relative_new_folder = args.new_folder.replace(os.path.dirname(args.input) + '\\', '').replace('\\', '/')
            update_manifest(
                sip_manifest,
                relative_filename,
                os.path.join(relative_new_folder, os.path.basename(relative_filename)).replace('\\', '/'),
                new_log_textfile
            )
    ififuncs.generate_log(
        new_log_textfile,
        'EVENT = package_update.py finished'
    )
    ififuncs.checksum_replace(sip_manifest, new_log_textfile, 'md5')
    finish = datetime.datetime.now()
    print '\n', user, 'ran this script at %s and it finished at %s' % (start, finish)


if __name__ == '__main__':
    main(sys.argv[1:])
