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
        elif len(args.start_number[2:]) != 4:
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
        print checksums
        for line in checksums:
            if old_oe in line:
                if 'source' in line:
                    # if source (v210) logs or metadata exist, leave filename
                    # alone, just change the path.
                    line = line[:40].replace(old_oe, uuid) + line[40:]
                else:
                    line = line.replace(old_oe, uuid)
                updated_lines.append(line)
    return updated_lines

def rename_files(new_uuid_path, old_oe, uuid):
    '''
    Renames files from OE numbers to UUID where appropriate.
    '''
    for root, _, filenames in os.walk(new_uuid_path):
        for filename in filenames:
            if old_oe in filename:
                if 'source' not in filename:
                    new_filename = os.path.join(root, filename).replace(old_oe, uuid)
                    os.rename(os.path.join(root, filename), new_filename)

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
    for root, _, filenames in os.walk(args.input):
        if os.path.basename(root)[:2] == 'oe':
            if len(os.path.basename(root)[2:]) == 4:
                old_oe_path = root
                old_oe = os.path.basename(root)
                manifest = os.path.join(
                    os.path.dirname(root),
                    old_oe + '_manifest.md5'
                    )
                uuid = ififuncs.create_uuid()
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
                rename_files(new_uuid_path, old_oe, uuid)


if __name__ == '__main__':
    main(sys.argv[1:])

