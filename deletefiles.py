#!/usr/bin/env python
'''
Deletes files after sipcreator has been run, but before accession.py has been run.
Manifests are updated and metadata is deleted.
'''
import os
import argparse
import sys
import datetime
import ififuncs


def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Deletes files from Object Entry packages'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        '-i', nargs='+',
        help='full path of files to be deleted', required=True
    )
    parser.add_argument(
        '-uuid_path',
        help='full path of \'sipcreator\' Object Entry package'
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.')
    parsed_args = parser.parse_args(args_)
    return parsed_args


def remove_from_manifest(manifest, old_oe, new_log_textfile):
    '''
    Removes a file from a manifest and logs the result in the logfile.
    '''
    updated_lines = []
    with open(manifest, 'r') as file_object:
        checksums = file_object.readlines()
        for line in checksums:
            if old_oe in line:
                print '%s has been removed from the package manifest' % line
                ififuncs.generate_log(
                    new_log_textfile,
                    'EVENT = eventType=metadata modification,'
                    ' agentName=deletefiles.py,'
                    ' eventDetail=%s has been removed from the package manifest' % line)
                continue
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
    source = args.uuid_path
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
        sip_path = args.uuid_path
        oe_path = os.path.dirname(args.uuid_path)
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
        'EVENT = deletefiles.py started'
    )
    ififuncs.generate_log(
        new_log_textfile,
        'eventDetail=deletefiles.py %s' % ififuncs.get_script_version('deletefiles.py')
    )
    ififuncs.generate_log(
        new_log_textfile,
        'Command line arguments: %s' % args
    )
    ififuncs.generate_log(
        new_log_textfile,
        'EVENT = agentName=%s' % user
    )
    metadata_dir = os.path.join(sip_path, 'metadata')
    for filename in args.i:
        # add test to see if it actually deleted - what if read only?
        os.remove(filename)
        print '%s has been deleted' % filename
        ififuncs.generate_log(
            new_log_textfile,
            'EVENT = eventType=deletion,'
            ' eventOutcomeDetailNote=%s has been deleted,'
            ' agentName=os.remove()'
            % filename
        )
        for metadata in os.listdir(metadata_dir):
            if os.path.basename(filename) in metadata:
                os.remove(os.path.join(metadata_dir, metadata))
                print '%s has been deleted' %  os.path.join(metadata_dir, metadata)
                ififuncs.generate_log(
                    new_log_textfile,
                    'EVENT = eventType=deletion,'
                    ' eventOutcomeDetailNote=%s has been deleted,'
                    ' agentName=os.remove()'
                    % os.path.join(metadata_dir, metadata)
                )
        remove_from_manifest(sip_manifest, os.path.basename(filename), new_log_textfile)
        ififuncs.sort_manifest(sip_manifest)
    ififuncs.generate_log(
        new_log_textfile,
        'EVENT = deletefiles.py finished'
    )    
    ififuncs.checksum_replace(sip_manifest, new_log_textfile, 'md5')
    finish = datetime.datetime.now()
    print '\n', user, 'ran this script at %s and it finished at %s' % (start, finish)


if __name__ == '__main__':
    main(sys.argv[1:])
