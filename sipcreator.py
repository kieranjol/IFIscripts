#!/usr/bin/env python
'''
Generates SIPS by calling various microservices and functions.
'''
import os
import argparse
import sys
import shutil
import subprocess
import time
import datetime
import ififuncs
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


def consolidate_manifests(path, directory):
    '''
    Consolidates all manifests in the objects folder
    moves old manifests into logs
    renames manifest with uuid and updates paths in manifest textfile.
    '''
    uuid = os.path.basename(path)
    objects_dir = os.path.join(path, directory)
    new_manifest_textfile = os.path.join(
        os.path.dirname(path), uuid + '_manifest.md5'
    )
    collective_manifest = []
    for manifest in os.listdir(objects_dir):
        if manifest.endswith('.md5'):
            if manifest[0] != '.':
                with open(os.path.join(objects_dir, manifest), 'r') as fo:
                    manifest_lines = fo.readlines()
                    for i in manifest_lines:
                        # This is what appends the new path to existing paths.
                        new_manifest_path = uuid + '/%s/' % directory + i[34:]
                        collective_manifest.append(
                            i[:32] + '  ' + new_manifest_path
                        )
                # Cut and paste old manifests into the log directory

                shutil.move(
                    objects_dir + '/' +  manifest, os.path.join(path, 'logs')
                )
    with open(new_manifest_textfile, 'ab') as manifest_object:
        for checksums in collective_manifest:
            manifest_object.write(checksums)
    return new_manifest_textfile


def consolidate_logs(lognames, path):
    '''
    Finds moveit.py logs on the desktop
    Copies all text into a single log file
    Saves it in the SIP
    '''
    uuid = os.path.basename(path)
    new_log_textfile = os.path.join(path, 'logs' + '/' + uuid + '_log.log')
    for log in lognames:
        with open(log, 'r') as fo:
            log_lines = fo.readlines()
        with open(new_log_textfile, 'ab') as log_object:
            for lines in log_lines:
                log_object.write(lines)


def move_files(inputs, sip_path):
    '''
    Runs moveit.py on all inputs
    '''
    log_names = []
    for item in inputs:
        moveit_cmd = [
            sys.executable,
            os.path.expanduser("~/ifigit/ifiscripts/moveit.py"),
            item, os.path.join(sip_path, 'objects')
        ]
        desktop_logs_dir = ififuncs.make_desktop_logs_dir()
        log_name_source_ = os.path.basename(
            item,
        ) + time.strftime("_%Y_%m_%dT%H_%M_%S")
        log_name_source = "%s/%s.log" % (desktop_logs_dir, log_name_source_)
        log_names.append(log_name_source)
        subprocess.check_call(moveit_cmd)
    consolidate_logs(log_names, sip_path)
    return log_names


def log_report(log_names):
    '''
    Analyzes all the moveit.py logs on the desktop and print a report.
    '''
    desktop_logs_dir = ififuncs.make_desktop_logs_dir()
    for i in log_names:
        if os.path.isfile(i):
            print "%-*s   : %s" % (50, os.path.basename(i)[:-24], analyze_log(i))
        else:
            print i, 'can\'t find log file, trying again...'
            log_names.remove(i)
            for logs in os.listdir(desktop_logs_dir):
                # look at log filename minus the seconds and '.log'
                if os.path.basename(i)[:-7] in logs:
                    # make sure that the alternate log filename is more recent
                    if int(
                            os.path.basename(logs)[-12:-4].replace('_', '')
                    ) > int(
                        os.path.basename(i)[-12:-4].replace('_', '')):
                        print 'trying to analyze %s' % logs
                        print "%-*s   : %s" % (
                            50, os.path.basename(logs)[:-24], analyze_log(
                                os.path.join(desktop_logs_dir, logs))
                            )
                        log_names.append(os.path.join(desktop_logs_dir, logs))

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Wraps objects into an Irish Film Institute SIP'
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
    parsed_args = parser.parse_args(args_)
    return parsed_args


def get_metadata(path):
    '''
    Recursively create mediainfos and mediatraces for AV files.
    This should probably go in ififuncs as it could be used by other scripts.
    '''
    for root, _, filenames in os.walk(path):
        for av_file in filenames:
            if av_file.endswith(
                    ('.mov', 'MP4', '.mp4', '.mkv', '.MXF', '.dv', '.DV')
            ):
                if av_file[0] != '.':
                    inputxml = "%s/%s_mediainfo.xml" % (
                        os.path.join(path, 'metadata'), os.path.basename(av_file)
                        )
                    inputtracexml = "%s/%s_mediatrace.xml" % (
                        os.path.join(path, 'metadata'), os.path.basename(av_file)
                        )
                    print 'Generating mediainfo xml of input file and saving it in %s' % inputxml
                    ififuncs.make_mediainfo(
                        inputxml, 'mediaxmlinput', os.path.join(root, av_file)
                    )
                    print 'Generating mediatrace xml of input file and saving it in %s' % inputtracexml
                    ififuncs.make_mediatrace(
                        inputtracexml,
                        'mediatracexmlinput',
                        os.path.join(root, av_file)
                    )


def main(args_):
    '''
    Launch all the functions for creating an IFI SIP.
    '''
    args = parse_args(args_)
    start = datetime.datetime.now()
    inputs = args.i
    user = ififuncs.get_user()
    sip_path = make_folder_path(os.path.join(args.o))
    uuid = os.path.basename(sip_path)
    new_log_textfile = os.path.join(sip_path, 'logs' + '/' + uuid + '_log.log')
    ififuncs.generate_log(
        new_log_textfile,
        'EVENT = sipcreator.py started'
    )
    ififuncs.generate_log(
        new_log_textfile,
        'EVENT = User=%s' % user
    )
    uuid_event = (
        'EVENT = eventType=Identifier assignement,'
        ' eventIdentifierType=UUID, value=%s, module=uuid.uuid4'
    ) % uuid
    ififuncs.generate_log(
        new_log_textfile,
        uuid_event
    )
    metadata_dir = os.path.join(sip_path, 'metadata')
    logs_dir = os.path.join(sip_path, 'logs')
    log_names = move_files(inputs, sip_path)
    get_metadata(sip_path)
    ififuncs.hashlib_manifest(
        metadata_dir, metadata_dir + '/metadata_manifest.md5', metadata_dir
    )
    new_manifest_textfile = consolidate_manifests(sip_path, 'objects')
    consolidate_manifests(sip_path, 'metadata')
    ififuncs.hashlib_append(
        logs_dir, new_manifest_textfile,
        os.path.dirname(os.path.dirname(logs_dir))
    )
    ififuncs.sort_manifest(new_manifest_textfile)
    log_report(log_names)
    finish = datetime.datetime.now()
    print '\n', user, 'ran this script at %s and it finished at %s' % (start, finish)


if __name__ == '__main__':
    main(sys.argv[1:])
