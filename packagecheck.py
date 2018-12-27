#!/usr/bin/env python
'''
Checks packages for correct structure.
Also returns a dictionary containing important varibles such as
folder paths and identifiers.
'''
import os
import argparse
import sys
import ififuncs


def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Check packages for correct structure.'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'input',
        help='full path of package'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def analyse_package(sip_path):
    '''
    Return a dictionary full of folder and file path variables
    '''
    package_info = {}
    package_info['sip_path'] = sip_path
    uuid = os.path.basename(sip_path)
    if ififuncs.validate_uuid4(uuid) is not False:
        package_info['uuid'] = uuid
        package_info['oe_path'] = os.path.dirname(sip_path)
        package_info['parent_identifier'] = os.path.basename(package_info['oe_path']) # can be OE or aaa
        package_info['manifest'] = os.path.join(package_info['oe_path'], uuid + '_manifest.md5')
        package_info['logs_dir'] = os.path.join(sip_path, 'logs')
        package_info['metadata_dir'] = os.path.join(sip_path, 'metadata')
        package_info['objects_dir'] = os.path.join(sip_path, 'objects')
        package_info['sip_log'] = os.path.join(package_info['logs_dir'], uuid + '_sip_log.log')
        package_info['objects'] = os.listdir(package_info['objects_dir'])
    else:
        return False
    return package_info

def test_package(package_info):
    '''
    Test if key files or folders exist.
    '''
    error_list = []
    question_list = []
    folder_list = [
        package_info['oe_path'],
        package_info['logs_dir'],
        package_info['objects_dir'],
        package_info['metadata_dir'],
        package_info['sip_path']
    ]
    file_list = [
        package_info['manifest'],
        package_info['sip_log']
    ]
    for folder in folder_list:
        if not os.path.isdir(folder):
            error_list.append(folder)
    for filename in file_list:
        if not os.path.isfile(filename):
            error_list.append(filename)
    metadata_files = os.listdir(package_info['metadata_dir'])
    for metadata_file in metadata_files:
        full_path = os.path.join(package_info['metadata_dir'], metadata_file)
        if os.path.getsize(full_path) == 0:
            question_list.append(full_path)
    for object_files in package_info['objects']:
        mediainfo = os.path.join(package_info['metadata_dir'], object_files + '_mediainfo.xml')
        if not os.path.isfile(mediainfo):
             question_list.append(mediainfo)
        mediatrace= os.path.join(package_info['metadata_dir'], object_files + '_mediatrace.xml')
        if not os.path.isfile(mediatrace):
             question_list.append(mediatrace)
    if not error_list:
        print('Key files and folders all exist')
    else:
        for error in error_list:
            print((('%s does not exist') % error))
    if not question_list:
        print('No further errors detected')
    else:
        for error in question_list:
            print((('%s requires investigation') % error))
    return error_list, question_list


def main(args_):
    '''
    Launch all the functions for determining folder and file paths.
    '''
    args = parse_args(args_)
    source = args.input
    sip_path = ififuncs.check_for_sip([source])
    if sip_path is not None:
        package_info = analyse_package(sip_path)
    if package_info is False:
        print('Valid UUID not found in folder path')
    else:
        print(package_info)
    error_list, question_list = test_package(package_info)
    return package_info, error_list, question_list

if __name__ == '__main__':
    main(sys.argv[1:])
