#!/usr/bin/env python
'''
Retrospectively updates older FFV1/DV packages in order to meet our current
packaging requirements. This should allow accession.py and makepbcore.py to run as
expected. This script should work on files created by:
makeffv1.py
dvsip.py
loopline.py
'''
import argparse
import sys
import shutil
import os
import time
import ififuncs

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Retrospectively updates older FFV1/DV packages in order to'
        'meet our current packaging requirements. This should allow'
        ' accession.py and makepbcore.py to run as expected.'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'input', help='Input directory'
    )
    parser.add_argument(
        '-start_number',
        help='Enter the Object Entry number for the first package. The script will increment by one for each subsequent package.'
    )
    parser.add_argument(
        '-technical',
        help='Path to technical/PBCore CSV.'
    )
    parser.add_argument(
        '-filmographic',
        help='Path to Filmographic CSV. Must contain reference numbers.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def get_numbers(args):
    '''
    Figure out the first OE number and how to increment per package.
    '''
    if args.start_number:
        if args.start_number[:2] != 'oe':
            print 'First two characters must be \'oe\' and last four characters must be four digits'
            object_entry = ififuncs.get_object_entry()
        elif len(args.start_number[2:]) not in range(4, 6):
            print 'First two characters must be \'oe\' and last four characters must be four digits'
            object_entry = ififuncs.get_object_entry()
        elif not args.start_number[2:].isdigit():
            object_entry = ififuncs.get_object_entry()
            print 'First two characters must be \'oe\' and last four characters must be four digits'
        else:
            object_entry = args.start_number
    else:
        object_entry = ififuncs.get_object_entry()
    object_entry_digits = int(object_entry[2:])
    new_object_entry = 'oe' + str(object_entry_digits)
    return new_object_entry

def update_manifest(manifest, old_oe, uuid):
    '''
    Updates the existing checksum manifest by replacing OE numbers with
    UUIDs where appropriate. Anything logfiles or metadata relating to the
    original v210.mov will be left alone.
    '''
    updated_lines = []
    with open(manifest, 'r') as file_object:
        checksums = file_object.readlines()
        for line in checksums:
            if old_oe in line:
                if 'source' in line:
                    # if source (v210) logs or metadata exist, leave filename
                    # alone, just change the path.
                    line = line[:40].replace(old_oe, uuid) + line[40:]
                elif '.mov_log.log' in line:
                    line = line.replace(old_oe, uuid).replace('.mov_log', '_sip_log')
                else:
                    line = line.replace(old_oe, uuid)
                updated_lines.append(line)
    return updated_lines

def rename_files(new_uuid_path, old_oe, uuid, manifest, logname):
    '''
    Renames files from OE numbers to UUID where appropriate.
    '''
    for root, _, filenames in os.walk(new_uuid_path):
        for filename in filenames:
            if old_oe in filename:
                if 'source' not in filename:
                    if '.mov_log.log' in filename:
                        new_filename = os.path.join(root, filename).replace('.mov_log', '_sip_log').replace(old_oe, uuid)
                        os.rename(os.path.join(root, filename), new_filename)
                        logname = new_filename
                        ififuncs.generate_log(
                            logname,
                            'EVENT = eventType=Filename change,'
                            ' eventOutcomeDetailNote=%s changed to %s'
                            % (os.path.join(root, filename), new_filename)
                        )
                    else:
                        new_filename = os.path.join(root, filename).replace(old_oe, uuid)
                        os.rename(os.path.join(root, filename), new_filename)
                        ififuncs.generate_log(
                            logname,
                            'EVENT = eventType=Filename change,'
                            ' eventOutcomeDetailNote=%s changed to %s'
                            % (os.path.join(root, filename), new_filename)
                        )
    return logname


def move_files(root, new_object_entry, old_oe_path, old_uuid_path, uuid):
    '''
    Moves files into their new folder paths.
    '''
    new_oe_path = os.path.join(
        os.path.dirname(root),
        new_object_entry
    )
    os.makedirs(new_oe_path)
    os.rename(old_oe_path, old_uuid_path)
    new_uuid_path = os.path.join(new_oe_path, uuid)
    shutil.move(old_uuid_path, new_oe_path)
    return new_oe_path, new_uuid_path

def make_register():
    '''
    This sends a placeholder accessions register to the desktop logs directory.
    This should get rid of some of the more painful, repetitive identifier matching.
    '''
    desktop_logs_dir = ififuncs.make_desktop_logs_dir()
    register = os.path.join(
        desktop_logs_dir,
        'oe_register_' + time.strftime("%Y-%m-%dT%H_%M_%S.csv")
    )
    ififuncs.create_csv(register, (
        'OE No.',
        'Date Received',
        'Quantity',
        'Format',
        'Description',
        'Contact Name',
        'Type of Acquisition',
        'Accession Number',
        'Additional Information',
        'Habitat',
        'Vinegar No.'
    ))
    return register

def get_date_modified(directory):
    '''
    Returns the date modified of a file in DD/MM/YYYY, which is
    the format used for the Object Entry register. yes, we should be using
    ISO8601 but we'll fix this later.
    '''
    file_list = ififuncs.recursive_file_list(directory)
    # This will blindly use the first video file it encounters.
    # This is fine for this project as all the objects folders contain single files.
    extension = os.path.splitext(file_list[0])[1]
    return time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(file_list[0]))), extension


def main(args_):
    '''
    Retrospectively updates older FFV1/DV packages in order to meet our current
    packaging requirements. This should allow accession.py and makepbcore.py to run as
    expected. This script should work on files created by:
    makeffv1.py
    dvsip.py
    loopline.py
    '''
    args = parse_args(args_)
    user = ififuncs.get_user()
    new_object_entry = get_numbers(args)
    filmographic_csv = args.filmographic
    technical_csv = args.technical
    filmographic_oe_list = []
    filmo_csv_extraction = ififuncs.extract_metadata(filmographic_csv)
    tech_csv_extraction = ififuncs.extract_metadata(technical_csv)
    register = make_register()
    for line_item in filmo_csv_extraction[0]:
        dictionary = {}
        oe_number = line_item['Object Entry'].lower()
        dictionary['title'] = line_item['Title']
        if dictionary['title'] == '':
            dictionary['title'] = '%s - %s' % (line_item['TitleSeries'], line_item['EpisodeNo'])
        dictionary['uppercase_dashed_oe'] = oe_number.upper()
        for tech_record in tech_csv_extraction[0]:
            if tech_record['Reference Number'] == dictionary['uppercase_dashed_oe']:
                dictionary['source_accession_number'] = tech_record['Accession Number']
                dictionary['filmographic_reference_number'] = tech_record['new_ref']
                # this transforms OE-#### to oe####
                dictionary['old_oe'] = oe_number[:2] + oe_number[3:]
                filmographic_oe_list.append(dictionary)
    for oe_package in filmographic_oe_list:
        for root, _, filenames in os.walk(args.input):
            if os.path.basename(root) == oe_package['old_oe']:
                old_oe_path = root
                old_oe = os.path.basename(root)
                log_dir = os.path.join(root, 'logs')
                for files in os.listdir(log_dir):
                    if '.mov_log.log' in files:
                        log = os.path.join(log_dir, files)
                manifest = os.path.join(
                    os.path.dirname(root),
                    old_oe + '_manifest.md5'
                    )
                uuid = ififuncs.create_uuid()
                uuid_event = (
                    'EVENT = eventType=Identifier assignement,'
                    ' eventIdentifierType=UUID, value=%s, module=uuid.uuid4'
                ) % uuid
                ififuncs.generate_log(
                    log,
                    'EVENT = loopline_repackage.py started'
                )
                ififuncs.generate_log(
                    log,
                    'eventDetail=loopline_repackage.py %s' % ififuncs.get_script_version('loopline_repackage.py')
                )
                ififuncs.generate_log(
                    log,
                    'Command line arguments: %s' % args
                )
                ififuncs.generate_log(
                    log,
                    'EVENT = agentName=%s' % user
                )
                ififuncs.generate_log(
                    log,
                    uuid_event
                )
                ififuncs.generate_log(
                    log,
                    'EVENT = eventType=Identifier assignement,'
                    ' eventIdentifierType=object entry, value=%s'
                    % new_object_entry
                )
                ififuncs.generate_log(
                    log,
                    'EVENT = eventType=Identifier assignement,'
                    ' eventIdentifierType=Filmographic reference number , value=%s'
                    % oe_package['filmographic_reference_number']
                )
                oe_package['new_object_entry'] = new_object_entry
                print('Transforming %s into %s' % (oe_package['old_oe'], oe_package['new_object_entry']))
                ififuncs.generate_log(
                        log,
                        'Relationship, derivation, has source=%s' % oe_package['source_accession_number']
                    )
                old_uuid_path = os.path.join(os.path.dirname(root), uuid)
                new_oe_path, new_uuid_path = move_files(
                    root, new_object_entry, old_oe_path, old_uuid_path, uuid
                )
                updated_lines = update_manifest(manifest, old_oe, uuid)
                new_manifest = os.path.join(new_oe_path, uuid) + '_manifest.md5'
                shutil.move(manifest, new_manifest)
                with open(new_manifest, 'w') as fo:
                    for lines in updated_lines:
                        fo.write(lines)
                new_logs_path = os.path.join(new_uuid_path, 'logs')
                for files in os.listdir(new_logs_path):
                    if '.mov_log.log' in files:
                        log = os.path.join(new_logs_path, files)
                logname = rename_files(new_uuid_path, old_oe, uuid, new_manifest, log)
                date_modified, extension = get_date_modified(new_uuid_path)
                # This normally would be bad practise, but this project only has two formats. MOV/DV and FFv1/MKV
                if extension == '.mkv':
                    av_format = 'FFV1/PCM/Matroska'
                elif extension == '.mov':
                    av_format = 'DV/PCM/QuickTime'
                provenance_string = 'Reproduction of %s' % oe_package['source_accession_number']
                ififuncs.append_csv(register, (oe_package['new_object_entry'].upper()[:2] + '-' + oe_package['new_object_entry'][2:],date_modified, '1',av_format,oe_package['title'],'contact_name','Reproduction','', provenance_string, '', ''))
                ififuncs.generate_log(
                    logname,
                    'EVENT = loopline_repackage.py finished'
                )
                ififuncs.checksum_replace(new_manifest, logname, 'md5')
                oe_digits = int(os.path.basename(new_oe_path)[2:]) + 1
                new_object_entry = 'oe' + str(oe_digits)
if __name__ == '__main__':
    main(sys.argv[1:])

