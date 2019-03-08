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
                    ' agentName=rearrange.py,'
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
    start = datetime.datetime.now()
    print args
    if args.user:
        user = args.user
    else:
        user = ififuncs.get_user()
    new_log_textfile = os.path.join(sip_path, 'logs' + '/' + uuid + '_sip_log.log')
    ififuncs.generate_log(
        new_log_textfile,
        'EVENT = rearrange.py started'
    )
    ififuncs.generate_log(
        new_log_textfile,
        'eventDetail=rearrange.py %s' % ififuncs.get_script_version('rearrange.py')
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
    for filename in args.i:
        # add test to see if it actually deleted - what if read only?
        shutil.move(filename, args.new_folder)
        print '%s has been moved into %s' % (filename, args.new_folder)
        ififuncs.generate_log(
            new_log_textfile,
            'EVENT = eventType=file movement,'
            ' eventOutcomeDetailNote=%s has been moved into %s'
            ' agentName=shutil.move()'
            % (filename, args.new_folder)
        )
        relative_filename = filename.replace(args.input + '/', '')
        relative_new_folder = args.new_folder.replace(args.input + '/', '')
        update_manifest(
            sip_manifest,
            relative_filename,
            os.path.join(relative_new_folder, os.path.basename(relative_filename)),
            new_log_textfile
        )
    ififuncs.generate_log(
        new_log_textfile,
        'EVENT = rearrange.py finished'
    )
    ififuncs.checksum_replace(sip_manifest, new_log_textfile, 'md5')
    finish = datetime.datetime.now()
    print('\n- %s ran this script at %s and it finished at %s' % (user, start, finish))


if __name__ == '__main__':
    main(sys.argv[1:])
