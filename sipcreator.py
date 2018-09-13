#!/usr/bin/env python
'''
Generates SIPS by calling various microservices and functions.
'''
import os
import argparse
import sys
import shutil
import subprocess
import datetime
import copyit
import ififuncs
import package_update
from masscopy import analyze_log


def make_folder_path(path, args, object_entry):
    '''
    Generates objects/logs/metadata/UUID folder structure in output.
    Returns the path.
    '''
    if not args.u:
        representation_uuid = ififuncs.create_uuid()
    else:
        representation_uuid = args.u
    if args.sc:
        oe_path = args.o
    else:
        oe_path = os.path.join(path, object_entry)
    path = os.path.join(oe_path, representation_uuid)
    print path
    ififuncs.make_folder_structure(path)
    return path


def consolidate_manifests(path, directory, new_log_textfile):
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
        if '_manifest' in manifest:
            if manifest.endswith('.md5'):
                if manifest[0] != '.':
                    ififuncs.generate_log(
                        new_log_textfile,
                        'EVENT = Manifest consolidation - Checksums from %s merged into %s' % (os.path.join(objects_dir, manifest), new_manifest_textfile)
                    )
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
                    ififuncs.generate_log(
                        new_log_textfile,
                        'EVENT = Manifest movement - Manifest from %s to %s' % (objects_dir + '/' +  manifest, os.path.join(path, 'logs'))
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
    new_log_textfile = os.path.join(path, 'logs' + '/' + uuid + '_sip_log.log')
    for log in lognames:
        with open(log, 'r') as fo:
            log_lines = fo.readlines()
        with open(new_log_textfile, 'ab') as log_object:
            for lines in log_lines:
                log_object.write(lines)


def move_files(inputs, sip_path, args):
    '''
    Runs moveit.py on all inputs
    '''
    log_names = []
    for item in inputs:
        cmd = [item, os.path.join(sip_path, 'objects')]
        if args.move:
            cmd.append('-move')
        log_name = copyit.main(cmd)
        log_names.append(log_name)
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
    parser.add_argument(
        '-u', '-uuid',
        help='Use a pre-existing UUID instead of a newly generated UUID.'
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.'
    )
    parser.add_argument(
        '-d', '-dcp', action='store_true',
        help='Adds DCP specific processing, like creating objects subfolder with text extracted from <ContentTitleText> in the CPL.'
    )
    parser.add_argument(
        '-quiet', action='store_true',
        help='Quiet mode, suppresses the analyze_logs() report'
    )
    parser.add_argument(
        '-move', action='store_true',
        help='invokes the -move argument in copyit.py - moves instead of copy.'
    )
    parser.add_argument(
        '-sc', action='store_true',
        help='special collections workflow'
    )
    parser.add_argument(
        '-oe',
        help='Enter the Object Entry number for the representation.SIP will be placed in a folder with this name.'
    )
    parser.add_argument(
        '-supplement', nargs='+',
        help='Enter the full path of files or folders that are to be added to the supplemental subfolder within the metadata folder. Use this for information that supplements your preservation objects but is not to be included in the objects folder.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def get_metadata(path, new_log_textfile):
    '''
    Recursively create mediainfos and mediatraces for AV files.
    This should probably go in ififuncs as it could be used by other scripts.
    '''
    mediainfo_version = 'mediainfo'
    try:
        mediainfo_version = subprocess.check_output([
            'mediainfo', '--Version'
        ]).rstrip()
    except subprocess.CalledProcessError as grepexc:
        mediainfo_version = grepexc.output.rstrip().splitlines()[1]
    for root, directories, filenames in os.walk(path):
        directories[:] = [
            d for d in directories if d != 'metadata'
        ]
        for av_file in filenames:
            if av_file.lower().endswith(
                    ('.mov', 'MP4', '.mp4', '.mkv', '.MXF', '.mxf', '.dv', '.DV', '.3gp', '.webm', '.swf', '.avi', '.wav', '.WAV')
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
                    ififuncs.generate_log(
                        new_log_textfile,
                        'EVENT = Metadata extraction - eventDetail=Technical metadata extraction via mediainfo, eventOutcome=%s, agentName=%s' % (inputxml, mediainfo_version)
                    )
                    print 'Generating mediatrace xml of input file and saving it in %s' % inputtracexml
                    ififuncs.make_mediatrace(
                        inputtracexml,
                        'mediatracexmlinput',
                        os.path.join(root, av_file)
                    )
                    ififuncs.generate_log(
                        new_log_textfile,
                        'EVENT = Metadata extraction - eventDetail=Mediatrace technical metadata extraction via mediainfo, eventOutcome=%s, agentName=%s' % (inputtracexml, mediainfo_version)
                    )
            elif av_file.lower().endswith(
                    ('.tif', 'tiff', '.doc', '.txt', '.docx', '.pdf', '.jpg', '.jpeg', '.png', '.rtf', '.xml', '.odt', '.cr2', '.epub', '.ppt', '.pptx', '.xls', '.xlsx', '.gif', '.bmp', '.csv' )
            ):
                if av_file[0] != '.':
                    if not av_file.lower().endswith(('.txt', '.csv')):
                        exiftool_version = 'exiftool'
                        try:
                            exiftool_version = subprocess.check_output([
                                'exiftool', '-ver'
                            ])
                        except subprocess.CalledProcessError as grepexc:
                            exiftool_version = grepexc.output.rstrip().splitlines()[1]
                        inputxml = "%s/%s_exiftool.json" % (
                            os.path.join(path, 'metadata'), os.path.basename(av_file)
                        )
                        ififuncs.generate_log(
                            new_log_textfile,
                            'EVENT = Metadata extraction - eventDetail=Technical metadata extraction via exiftool, eventOutcome=%s, agentName=%s' % (inputxml, exiftool_version)
                        )
                        print 'Generating exiftool json of input file and saving it in %s' % inputxml
                        ififuncs.make_exiftool(
                            inputxml,
                            os.path.join(root, av_file)
                        )
                    siegfried_version = 'siegfried'
                    try:
                        siegfried_version = subprocess.check_output([
                            'sf', '-version'
                        ])
                    except subprocess.CalledProcessError as grepexc:
                        siegfried_version = grepexc.output.rstrip().splitlines()[1]
                    inputtracexml = "%s/%s_siegfried.json" % (
                        os.path.join(path, 'metadata'), os.path.basename(av_file)
                        )
                    print 'Generating Siegfried json of input file and saving it in %s' % inputtracexml
                    ififuncs.make_siegfried(
                        inputtracexml,
                        os.path.join(root, av_file)
                    )
                    ififuncs.generate_log(
                        new_log_textfile,
                        'EVENT = Format identification - eventType=format identification, eventDetail=Format identification via PRONOM signatures using Siegfried, eventOutcome=%s, agentName=%s' % (inputtracexml, siegfried_version)
                    )
def create_content_title_text(sip_path):
    '''
    DCPs are often delivered with inconsistent foldernames.
    This will rename the parent folder with the value recorded in <ContentTitleText>
    For example:
    Original name: CHARBON-SMPTE-24
    New name: CHARBON-SMPTE-24-INTEROP-SUBS_TST_S_XX-EN_FR_XX_2K_CHA-20120613_CHA_OV
    Rename will only occur if user agrees.
    '''
    objects_dir = os.path.join(sip_path, 'objects')
    cpl = ififuncs.find_cpl(objects_dir)
    dcp_dirname = os.path.dirname(cpl)
    content_title_text = ififuncs.get_contenttitletext(cpl)
    dci_foldername = os.path.join(objects_dir, content_title_text)
    if ififuncs.ask_yes_no(
            'Do you want to rename %s with %s ?' % (dcp_dirname, dci_foldername)
    ) == 'Y':
        os.chdir(os.path.dirname(dcp_dirname))
        os.rename(os.path.basename(dcp_dirname), content_title_text)
    return content_title_text

def normalise_objects_manifest(sip_path):
    '''
    For a root copy workflow, the objects manifest is in the
    uuid directory, not the objects directory. This will move it
    into the objects directory.
    '''
    objects_manifest = os.path.join(sip_path, 'objects_manifest.md5')
    if os.path.isfile(objects_manifest):
        updated_manifest_lines = []
        with open(objects_manifest, 'r') as fo:
            manifest_lines = fo.readlines()
            for i in manifest_lines:
                # This is what appends the new path to existing paths.
                replacement = i.replace('  objects/', '  ')
                updated_manifest_lines.append(replacement)
        with open(objects_manifest, 'w') as fo:
            for x in updated_manifest_lines:
                fo.write(x)
        # Cut and paste old manifests into the log directory
        shutil.move(
            objects_manifest, os.path.join(sip_path, 'objects')
        )

def main(args_):
    '''
    Launch all the functions for creating an IFI SIP.
    '''
    args = parse_args(args_)
    start = datetime.datetime.now()
    inputs = args.i
    print args
    if args.user:
        user = args.user
    else:
        user = ififuncs.get_user()
    if not args.sc:
        if args.oe:
            if args.oe[:2] != 'oe':
                print 'First two characters must be \'oe\' and last four characters must be four digits'
                object_entry = ififuncs.get_object_entry()
            elif len(args.oe[2:]) not in range(4, 6):
                print 'First two characters must be \'oe\' and last four characters must be four digits'
                object_entry = ififuncs.get_object_entry()
            elif not args.oe[2:].isdigit():
                object_entry = ififuncs.get_object_entry()
                print 'First two characters must be \'oe\' and last four characters must be four digits'
            else:
                object_entry = args.oe
        else:
            object_entry = ififuncs.get_object_entry()
    else:
        object_entry = 'not_applicable'
    sip_path = make_folder_path(os.path.join(args.o), args, object_entry)
    if args.u:
        if ififuncs.validate_uuid4(args.u) is None:
            uuid = args.u
            uuid_event = (
                'EVENT = eventType=Identifier assignement,'
                ' eventIdentifierType=UUID, value=%s, module=uuid.uuid4'
            ) % uuid
        else:
            print 'exiting due to invalid UUID'
            uuid_event = (
                'EVENT = exiting due to invalid UUID supplied on the commmand line: %s' % uuid
            )
            uuid = False
    else:
        uuid = os.path.basename(sip_path)
        uuid_event = (
            'EVENT = eventType=Identifier assignement,'
            ' eventIdentifierType=UUID, value=%s, module=uuid.uuid4'
        ) % uuid
    new_log_textfile = os.path.join(sip_path, 'logs' + '/' + uuid + '_sip_log.log')
    ififuncs.generate_log(
        new_log_textfile,
        'EVENT = sipcreator.py started'
    )
    ififuncs.generate_log(
        new_log_textfile,
        'eventDetail=sipcreator.py %s' % ififuncs.get_script_version('sipcreator.py')
    )
    ififuncs.generate_log(
        new_log_textfile,
        'Command line arguments: %s' % args
    )
    ififuncs.generate_log(
        new_log_textfile,
        'EVENT = agentName=%s' % user
    )
    ififuncs.generate_log(
        new_log_textfile,
        uuid_event
    )
    if args.u is False:
        sys.exit()
    if not args.sc:
        ififuncs.generate_log(
            new_log_textfile,
            'EVENT = eventType=Identifier assignement,'
            ' eventIdentifierType=object entry, value=%s'
            % object_entry
        )
    metadata_dir = os.path.join(sip_path, 'metadata')
    supplemental_dir = os.path.join(metadata_dir, 'supplemental')
    logs_dir = os.path.join(sip_path, 'logs')
    log_names = move_files(inputs, sip_path, args)
    get_metadata(sip_path, new_log_textfile)
    ififuncs.hashlib_manifest(
        metadata_dir, metadata_dir + '/metadata_manifest.md5', metadata_dir
    )
    if args.sc:
        normalise_objects_manifest(sip_path)
    new_manifest_textfile = consolidate_manifests(sip_path, 'objects', new_log_textfile)
    consolidate_manifests(sip_path, 'metadata', new_log_textfile)
    ififuncs.hashlib_append(
        logs_dir, new_manifest_textfile,
        os.path.dirname(os.path.dirname(logs_dir))
    )
    if args.supplement:
        os.makedirs(supplemental_dir)
        supplement_cmd = ['-i', args.supplement, '-user', user, '-new_folder', supplemental_dir, os.path.dirname(sip_path), '-copy']
        package_update.main(supplement_cmd)
    ififuncs.sort_manifest(new_manifest_textfile)
    if not args.quiet:
        log_report(log_names)
    finish = datetime.datetime.now()
    print '\n', user, 'ran this script at %s and it finished at %s' % (start, finish)
    if args.d:
        content_title = create_content_title_text(sip_path)
        ififuncs.manifest_replace(
            new_manifest_textfile,
            os.path.join('objects', os.path.basename(args.i[0])).replace("\\", "/"),
            os.path.join('objects', content_title).replace("\\", "/")
        )
    return new_log_textfile, new_manifest_textfile


if __name__ == '__main__':
    main(sys.argv[1:])
