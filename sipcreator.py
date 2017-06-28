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


def consolidate_manifests(path):
    '''
    Consolidates all manifests in the objects folder
    moves old manifests into logs
    renames manifest with uuid and updates paths in manifest textfile.
    '''
    uuid = os.path.basename(path)
    objects_dir = os.path.join(path, 'objects')
    new_manifest_textfile = os.path.join(
        os.path.dirname(path), uuid + '_manifest.md5'
    )
    collective_manifest = []
    for manifest in os.listdir(objects_dir):
        if manifest.endswith('.md5'):
            if not manifest[0] == '.':
                with open(os.path.join(objects_dir, manifest), 'r') as fo:
                    manifest_lines = fo.readlines()
                    for i in manifest_lines:
                        # This is what appends the new path to existing paths.
                        new_manifest_path = uuid + '/objects/' + i[34:]
                        collective_manifest.append(
                            i[:32] + '  ' + new_manifest_path
                        )
                # Cut and paste old manifests into the log directory
                shutil.move(objects_dir + '/' +  manifest, os.path.join(path, 'logs'))
    with open(new_manifest_textfile, 'ab') as manifest_object:
        for checksums in collective_manifest:
            manifest_object.write(checksums)


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
        log_name_source_ = os.path.basename(
            item,
        ) + time.strftime("_%Y_%m_%dT%H_%M_%S")
        desktop_logs_dir = ififuncs.make_desktop_logs_dir()
        log_name_source = "%s/%s.log" % (desktop_logs_dir, log_name_source_)
        log_names.append(log_name_source)
        subprocess.check_call(moveit_cmd)
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
    consolidate_manifests(sip_path)
    consolidate_logs(log_names, sip_path)

def get_metadata(path):
    '''
    Recursively create mediainfos and mediatraces for AV files.
    This should probably go in ififuncs as it could be used by other scripts.
    '''
    for root, dirnames, filenames in os.walk(path):
        for av_file in filenames:
            if av_file.endswith(('.mov', 'MP4', '.mp4', '.MXF', '.dv', '.DV')):
                if not av_file[0] == '.':
                    inputxml = "%s/%s_mediainfo.xml" % (
                        os.path.join(path, 'metadata'), os.path.basename(av_file)
                        )
                    inputtracexml = "%s/%s_mediatrace.xml" % (
                        os.path.join(path, 'metadata'), os.path.basename(av_file)
                        )
                    print 'Generating mediainfo xml of input file and saving it in %s' % inputxml
                    ififuncs.make_mediainfo(inputxml, 'mediaxmlinput', os.path.join(root, av_file))
                    print 'Generating mediatrace xml of input file and saving it in %s' % inputtracexml
                    ififuncs.make_mediatrace(inputtracexml, 'mediatracexmlinput', os.path.join(root, av_file))


def main():
    '''
    Generates SIPS by calling various microservices and functions.
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
    args = parser.parse_args()
    inputs = args.i
    sip_path = make_folder_path(os.path.join(args.o))
    uuid = os.path.basename(sip_path)
    new_log_textfile = os.path.join(sip_path, 'logs' + '/' + uuid + '_log.log')
    ififuncs.generate_log(
        new_log_textfile,
        'EVENT = sipcreator.py started'
    )

    ififuncs.generate_log(
        new_log_textfile,
        'EVENT = Identifier assignement - type=UUID, value=%s, module=uuid.uuid4' % uuid
    )

    move_files(inputs, sip_path)
    get_metadata(sip_path)
if __name__ == '__main__':
    main()
