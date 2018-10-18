#!/usr/bin/env python
'''
Copy pastes drectories while comparing checksum manifests of src and dst.
'''

import sys
import subprocess
import os
import filecmp
import tempfile
import time
import argparse
import hashlib
import shutil
import ififuncs
from ififuncs import make_desktop_logs_dir, make_desktop_manifest_dir, generate_log


def hashlib_md5(filename):
    '''
    Create an md5 checksum. This should use the ififuncs function instead.
    '''
    read_size = 0
    last_percent_done = 0
    md5_object = hashlib.md5()
    total_size = os.path.getsize(filename)
    with open(str(filename), 'rb') as file_object:
        while True:
            buf = file_object.read(2**20)
            if not buf:
                break
            read_size += len(buf)
            md5_object.update(buf)
            percent_done = 100 * read_size / total_size
            if percent_done > last_percent_done:
                sys.stdout.write('[%d%%]\r' % percent_done)
                sys.stdout.flush()
                last_percent_done = percent_done
    md5_output = md5_object.hexdigest()
    return md5_output + '  ' + os.path.abspath(filename) +  '\n'


def test_write_capabilities(directory, log_name_source):
    '''
    Checks if drives have write access.
    Also checks if source is a file or directory (no file support right now)
    '''
    if os.path.isdir(directory):
        temp = tempfile.mkstemp(dir=directory, suffix='.tmp')
        os.close(temp[0]) # Needed for windows.
        os.remove(temp[1])
    elif os.path.isfile(directory):
        print('\nFile transfer is not currently supported, only directories.\n')
        generate_log(
            log_name_source,
            'Error: Attempted file transfer. Source and Destination must be a directory'
        )
        generate_log(log_name_source, 'move.py exit')
        sys.exit()
    else:
        print(' %s is either not a directory or it does not exist' % directory)
        generate_log(
            log_name_source,
            ' %s is either not a directory or it does not exist' % directory
        )
        generate_log(log_name_source, 'move.py exit')
        sys.exit()


def remove_bad_files(root_dir, log_name_source):
    '''
    Stolen and adapted from Ben Fino-Radin. Removes annoying files.
    '''
    rm_these = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
    for root, _, files in os.walk(root_dir):
        for name in files:
            path = os.path.join(root, name)
            for i in rm_these:
                if name == i:
                    print('***********************' + 'removing: ' + path)
                    if not log_name_source == None:
                        generate_log(
                            log_name_source,
                            'EVENT = Unwanted file removal - %s was removed' % path
                        )
                    try:
                        os.remove(path)
                    except OSError:
                        print('can\'t delete as source is read-only')


def make_manifest(
        manifest_dir,
        manifest_textfile, path_to_remove
    ):
    '''
    Generates a checksum text manifest.
    '''
    checksum_list = []
    manifest_generator = ''
    source_counter = 0
    print('Counting the amount of files to be processed.')
    for root, directories, filenames in os.walk(manifest_dir):
        directories[:] = [
            d for d in directories if d[0] != '.'
        ]
        directories[:] = [
            d for d in directories if d != 'System Volume Information'
        ]
        directories[:] = [
                d for d in directories if d != '$RECYCLE.BIN'
        ]
        directories[:] = [
                d for d in directories if d != 'Seagate'
        ]
        filenames = [
            f for f in filenames if os.path.basename(root) != 'System Volume Information'
        ]
        filenames = [
            f for f in filenames if f[0] != '.'
        ]
        for files in filenames:
            source_counter += 1
    counter2 = 1
    if os.path.isdir(manifest_dir):
        os.chdir(manifest_dir)
        for root, directories, filenames in os.walk(manifest_dir):
            directories[:] = [
                d for d in directories if d[0] != '.'
            ]
            directories[:] = [
                d for d in directories if d != 'System Volume Information'
            ]
            directories[:] = [
                d for d in directories if d != '$RECYCLE.BIN'
            ]
            directories[:] = [
                d for d in directories if d != 'Seagate'
            ]
            filenames = [
                f for f in filenames if os.path.basename(root) != 'System Volume Information'
            ]
            filenames = [
                f for f in filenames if f[0] != '.'
            ]
            for files in filenames:
                checksum_list.append([root, files])
    elif os.path.isfile(manifest_dir):
        checksum_list = [[os.path.dirname(manifest_dir), os.path.basename(manifest_dir)]]
    if len(checksum_list) == 1:
        source_counter = 1
    for files in checksum_list:
        print('Generating MD5 for %s - %d of %d' % (
            os.path.join(files[0], files[1]), counter2, source_counter)
            )
        md5 = hashlib_md5(os.path.join(files[0], files[1]))
        root2 = files[0].replace(path_to_remove, '')
        try:
            if root2[0] == '/':
                root2 = root2[1:]
            if root2[0] == '\\':
                root2 = root2[1:]
        except: IndexError
        manifest_generator += md5[:32] + '  ' + os.path.join(
            root2, files[1]
            ).replace("\\", "/") + '\n'
        counter2 += 1
    manifest_list = manifest_generator.splitlines()
    files_in_manifest = len(manifest_list)
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list, key=lambda x: (x[34:]))
    with open(manifest_textfile, "wb") as text:
        for i in manifest_list:
            text.write(i + '\n')
    return files_in_manifest


def copy_dir(
        source, destination_final_path,
        log_name_source, rootpos, destination, dirname, args
    ):
    '''
    Depending on which operating system is running the script, system tools
    are launched that copy paste source files to destination.
    '''
    if sys.platform == "win32":
        if os.path.isfile(source):
            generate_log(
                log_name_source,
                'EVENT = File Transfer, status=started, agentName=Windows, module=shutil.copy2'
            )
            print('copying file with python/shutil')
            shutil.copy2(source, destination_final_path)
        else:
            subprocess.call([
                'robocopy', source,
                destination_final_path,
                '/E', '/XA:SH',
                '/XD', '.*',
                '/XD', '*System Volume Information*',
                '/XD', 'Seagate',
                '/XD', '$Recycle.bin', '/a-:SH', '/a+:R'
            ])
            generate_log(
                log_name_source,
                'EVENT = File Transfer, status=started, agentName=Windows O.S, agentName=Robocopy'
            )
    elif sys.platform == "darwin":
        if args.l:
            cmd = [
                'gcp', '--preserve=mode,timestamps',
                '-nRv', source, destination_final_path
            ]
            generate_log(
                log_name_source, 'EVENT = File Transfer, status=started, agentName=OSX - agentName=gcp'
            )
            subprocess.call(cmd)
        # https://github.com/amiaopensource/ltopers/blob/master/writelto#L51
        else:
            if rootpos == 'y':
                if not os.path.isdir(destination + '/' + dirname):
                    os.makedirs(destination + '/' + dirname)
                cmd = [
                    'rsync', '-rtv',
                    '--exclude=.*', '--exclude=.*/',
                    '--stats', '--progress',
                    source, destination + '/' + dirname
                ]
            else:
                cmd = [
                    'rsync', '-rtv',
                    '--exclude=.*', '--exclude=.*/',
                    '--stats', '--progress', source, destination
                ]
            generate_log(
                log_name_source, 'EVENT = File Transfer, status=started, agentName=OSX, agentName=rsync'
            )
            print(cmd)
            subprocess.call(cmd)
    elif sys.platform == "linux2":
        # https://github.com/amiaopensource/ltopers/blob/master/writelto#L51
        cmd = [
            'cp', '--preserve=mode,timestamps',
            '-nRv', source, destination_final_path
        ]
        generate_log(
            log_name_source, 'EVENT = File Transfer, status=started, agentName=Linux, agentName=cp'
        )
        subprocess.call(cmd)
    generate_log(
                log_name_source,
                'EVENT = File Transfer, status=completed'
            )

def diff_report(file1, file2, log_name_source):
    '''
    Analyzes checksum manifests in order to find mismatches.
    '''
    print('Comparing manifests to verify file transfer')
    with open(file1, 'r') as file1_manifest:
        sourcelist = file1_manifest.readlines()
    with open(file2, 'r') as file2_manifest:
        destlist = file2_manifest.readlines()
    for i in sourcelist:
        if i not in destlist:
            print('%s was expected, but a different value was found in destination manifest' % i.rstrip())
            generate_log(
                log_name_source,
                'ERROR = %s was expected, but a different value was found in destination manifest' % i.rstrip())


def check_extra_files(file1, file2, log_name_source):
    '''
    Are there any extra files in the destination directory?
    '''
    with open(file1, 'r') as file1_manifest:
        sourcelist = file1_manifest.readlines()
    with open(file2, 'r') as file2_manifest:
        destlist = file2_manifest.readlines()
    destlist_files = []
    sourcelist_files = []
    for dest_files in destlist:
        destlist_files.append(dest_files[32:])
    for source_files in sourcelist:
        sourcelist_files.append(source_files[32:])
    for i in destlist_files:
        if i not in sourcelist_files:
            print('%s is in your destination manifest but is not in the source manifest' % i.rstrip())
            generate_log(
                log_name_source,
                'ERROR = %s is in your destination manifest but is not in the source manifest' % i.rstrip())


def check_overwrite(file2check):
    '''
    Asks user if they want to overwrite pre-existing manifests.
    '''
    if os.path.isfile(file2check):
        print('A manifest already exists at your destination. Overwrite? Y/N?')
        overwrite_destination_manifest = ''
        while overwrite_destination_manifest not in ('Y', 'y', 'N', 'n'):
            overwrite_destination_manifest = raw_input()
            if overwrite_destination_manifest not in ('Y', 'y', 'N', 'n'):
                print('Incorrect input. Please enter Y or N')
        return overwrite_destination_manifest


def manifest_file_count(manifest2check):
    '''
    Checks an ixisting manifest for file count and file list
    '''
    if os.path.isfile(manifest2check):
        print('A manifest already exists - Checking if manifest is up to date')
        with open(manifest2check, "r") as fo:
            manifest_files = []
            manifest_lines = [line.split(',') for line in fo.readlines()]
            for line in manifest_lines:
                manifest_files.append(line[0][34:].rstrip())
            count_in_manifest = len(manifest_lines)
            manifest_info = [count_in_manifest, manifest_files]
    return manifest_info


def check_overwrite_dir(dir2check):
    '''
    Asks user if they want to overwrite a pre-existing destination directory.
    '''
    if os.path.isdir(dir2check):
        if len(os.listdir(dir2check)) > 1:
            print('A directory already exists at your destination. Overwrite? Y/N?')
            overwrite_destination_dir = ''
            while overwrite_destination_dir not in ('Y', 'y', 'N', 'n'):
                overwrite_destination_dir = raw_input()
                if overwrite_destination_dir not in ('Y', 'y', 'N', 'n'):
                    print('Incorrect input. Please enter Y or N')
            return overwrite_destination_dir
        else:
            print('A directory exists in your destination but it is empty so we shall proceed')

def check_for_sip(args):
    '''
    This checks if the input folder contains the actual payload, eg:
    the UUID folder(containing logs/metadata/objects) and the manifest sidecar.
    '''
    remove_bad_files(args, None)
    for filenames in os.listdir(args):
        # make sure that it's an IFI SIP.
        if 'manifest.md5' in filenames:
            if len(os.listdir(args)) <= 3: # to allow for  the sha512 manifest
                dircheck = filenames.replace('_manifest.md5', '')
                if os.path.isdir(os.path.join(args, dircheck)):
                    return os.path.join(args, dircheck)


def setup(args_):
    '''
    Sets a bunch of filename variables and parses command line.
    some examples:
    if manifest_sidecar = /home/kieranjol/fakeeeeee/fakeeeeee_manifest.md5
    then manifes_root = /home/kieranjol/fakeeeeee_manifest.md5
    '''
    parser = argparse.ArgumentParser(
        description='Copy directory with checksum comparison'
                    'and manifest generation.Written by Kieran O\'Leary.')
    parser.add_argument(
        'source', help='Input directory'
    )
    parser.add_argument(
        'destination',
        help='Destination directory'
    )
    parser.add_argument(
        '-l', '-lto',
        action='store_true',
        help='use gcp instead of rsync on osx for SPEED on LTO'
    )
    parser.add_argument(
        '-move',
        action='store_true',
        help='Move files instead of copying - much faster!'
    )
    parser.add_argument(
        '-justcopy',
        action='store_true',
        help='Do not generate destination manifest and verify integrity :('
    )
    parser.add_argument(
        '-y',
        action='store_true',
        help='Answers YES to the question: Not enough free space, would you like to continue?'
    )
    rootpos = ''
    dircheck = None
    args = parser.parse_args(args_)
    if os.path.isdir(args.source):
        dircheck = check_for_sip(args.source)
    if dircheck != None:
        if os.path.isdir(dircheck):
            source = check_for_sip(args.source)
            destination = os.path.join(args.destination, os.path.basename(args.source))
            os.makedirs(destination)
    else:
        source = os.path.abspath(args.source)
        destination = args.destination
    normpath = os.path.normpath(source)
    #is there any benefit to this over os.path.basename
    dirname = os.path.split(os.path.basename(source))[1]
    if dirname == '':
        rootpos = 'y'
        '''
        dirname = raw_input(
            'What do you want your destination folder to be called?\n'
        )
        '''
    relative_path = normpath.split(os.sep)[-1]
    # or hardcode
    destination_final_path = os.path.join(destination, dirname)
    if rootpos == 'y':
        manifest_destination = os.path.dirname(destination) + '/%s_manifest.md5' % os.path.basename(destination)
    else:
        manifest_destination = destination + '/%s_manifest.md5' % dirname
    if os.path.isfile(manifest_destination):
        print('Destination manifest already exists')
    if rootpos == 'y':
        manifest_filename = '%s_manifest.md5' % os.path.basename(destination)
    else:
        manifest_filename = '%s_manifest.md5' % dirname
    desktop_manifest_dir = make_desktop_manifest_dir()
    # manifest = desktop manifest, looks like this can get rewritten later.
    manifest = os.path.join(
        desktop_manifest_dir, manifest_filename
    )
    manifest_sidecar = os.path.join(
        os.path.dirname(source), relative_path + '_manifest.md5'
    )
    manifest_root = source + '/%s_manifest.md5' % os.path.basename(source)
    log_name_filename = dirname + time.strftime("_%Y_%m_%dT%H_%M_%S")
    desktop_logs_dir = make_desktop_logs_dir()
    log_name_source = "%s/%s.log" % (desktop_logs_dir, log_name_filename)
    generate_log(log_name_source, 'copyit.py started.')
    ififuncs.generate_log(
        log_name_source,
        'eventDetail=copyit.py %s' % ififuncs.get_script_version('copyit.py'))
    generate_log(log_name_source, 'Source: %s' % source)
    generate_log(log_name_source, 'Destination: %s'  % destination)
    print('Checking total size of input folder')
    total_input_size = ififuncs.get_folder_size(os.path.abspath(args.source))
    print('Checking if enough space in destination folder')
    free_space = ififuncs.get_free_space(args.destination)
    if total_input_size > free_space:
        print('You do not have enough free space!')
        if args.y:
            go_forth_blindly = 'Y'
        else:
            go_forth_blindly = ififuncs.ask_yes_no('Would you like to continue anyway? Press Y or N')
        if go_forth_blindly == 'Y':
            generate_log(log_name_source, 'You do not have enough free space!, but the user has decided to continue anyhow')
        else:
            generate_log(log_name_source, 'You do not have enough free space! - Exiting')
            sys.exit()
    return args, rootpos, manifest_sidecar, log_name_source, destination_final_path, manifest_root, manifest_destination, manifest, destination, dirname, desktop_manifest_dir


def count_stuff(source):
    '''
    Counts total files to be processed.
    '''
    source_count = 0
    file_list = []
    for root, directories, filenames in os.walk(source):
        filenames = [f for f in filenames if f[0] != '.']
        directories[:] = [d for d in directories if d[0] != '.']
        for files in filenames:
            source_count += 1
            relative_path = os.path.join(root, files).replace(os.path.dirname(source), '')[1:]
            file_list.append(relative_path)
    if os.path.isfile(source):
        if len(file_list) == 0:
            source_count = 1
    return source_count, file_list


def overwrite_check(
        destination, log_name_source,
        destination_final_path, manifest_destination
    ):
    '''
    Possibly redundant - this launches other overwrite functions.
    '''
    try:
        test_write_capabilities(destination, log_name_source)
    except OSError:
        print('You cannot write to your destination!')
        generate_log(
            log_name_source,
            'EVENT = I/O Test - Failure - No write access to destination directory.'
        )
        sys.exit()
    overwrite_destination_manifest = check_overwrite(manifest_destination)
    overwrite_destination_dir = check_overwrite_dir(destination_final_path)
    return overwrite_destination_manifest, overwrite_destination_dir


def manifest_existence(
        manifest_root, manifest_sidecar,
        manifest, source_count, file_list, log_name_source
    ):
    '''
    Checks for the three different kinds of source manifests:
    Sidecar, desktop and root of drive
    '''
    count_in_manifest = 0
    manifest_files = []
    proceed = 'n'
    if os.path.isfile(manifest_root):
        proceed = 'y'
        manifest_info = manifest_file_count(manifest_root)
        count_in_manifest = manifest_info[0]
        manifest_files = manifest_info[1]
    elif os.path.isfile(manifest_sidecar):
        manifest_info = manifest_file_count(manifest_sidecar)
        proceed = 'y'
        count_in_manifest = manifest_info[0]
        manifest_files = manifest_info[1]
    elif os.path.isfile(manifest):
        manifest_info = manifest_file_count(manifest)
        count_in_manifest = manifest_info[0]
        manifest_files = manifest_info[1]
        proceed = 'y'
    if proceed == 'y':
        if source_count != count_in_manifest:
            print('checking which files are different')
            for i in file_list:
                if i not in manifest_files:
                    print(i, 'is present in your source directory but not in the source manifest')
            for i in manifest_files:
                if i not in file_list:
                    print(i, 'is present in manifest but is missing in your source files')
            print('This manifest may be outdated as the number of files in your directory does not match the number of files in the manifest')
            print('There are', source_count, 'files in your source directory', count_in_manifest, 'in the manifest')
            generate_log(log_name_source, 'EVENT = Existing source manifest check - Failure - The number of files in the source directory is not equal to the number of files in the source manifest ')
            sys.exit()
    return proceed, count_in_manifest, manifest_files


def make_destination_manifest(
        overwrite_destination_manifest, log_name_source,
        rootpos, destination_final_path,
        manifest_destination, destination
    ):
    '''
    Um, write destination manifest
    '''
    if overwrite_destination_manifest not in ('N', 'n'):
        if overwrite_destination_manifest == None:
            generate_log(
                log_name_source, 'EVENT = Generating destination manifest: status=started, eventType=message digest calculation, module=hashlib'
            )
        else:
            generate_log(
                log_name_source,
                'EVENT = Destination Manifest Overwrite - Destination manifest already exists - Overwriting.'
            )
        print('Generating destination manifest')
        if rootpos == 'y':
            files_in_manifest = make_manifest(
                destination_final_path,
                manifest_destination, os.path.dirname(destination)
            )
            generate_log(
                log_name_source,
                'EVENT = Generating destination manifest: status=completed'
            )
        else:
            files_in_manifest = make_manifest(
                destination_final_path,
                manifest_destination, destination
            )
            generate_log(
                log_name_source,
                'EVENT = Generating destination manifest: status=completed')
    else:
        generate_log(
            log_name_source,
            'EVENT = File Transfer Overwrite - Destination directory already exists - Not Overwriting.'
        )
    remove_bad_files(destination_final_path, log_name_source)
    return files_in_manifest


def verify_copy(manifest, manifest_destination, log_name_source, overwrite_destination_manifest, files_in_manifest, destination_count, source_count):
    if filecmp.cmp(manifest, manifest_destination, shallow=False):
        print("Your files have reached their destination and the checksums match")
        generate_log(
            log_name_source,
            'EVENT = File Transfer Judgement - Success, eventOutcome=pass'
        )
    else:
        print("***********YOUR CHECKSUMS DO NOT MATCH*************")
        if overwrite_destination_manifest not in ('N', 'n'):
            generate_log(
                log_name_source,
                'EVENT = File Transfer Outcome - Failure, eventOutcome=fail'
            )
            print(' There are: \n %s files in your destination manifest \n' % files_in_manifest)
            print(' %s files in your destination \n %s files at source' % (
                destination_count, source_count)
            )
            diff_report(manifest, manifest_destination, log_name_source)
            check_extra_files(manifest, manifest_destination, log_name_source)
            generate_log(log_name_source, 'EVENT = File Transfer Failure Explanation -  %s files in your destination,  %s files at source' % (destination_count, source_count))
        else:
            print(' %s files in your destination \n %s files at source' % (
                destination_count, source_count)
            )
def control_flow(manifest_sidecar, log_name_source, manifest, rootpos, args, source):
    if os.path.isfile(manifest_sidecar):
        print('Manifest Sidecar exists - Source manifest Generation will be skipped.')
        generate_log(
            log_name_source,
            'EVENT = Manifest sidecar exists - source manifest generation will be skipped'
        )
        manifest = manifest_sidecar
    elif not os.path.isfile(manifest):
        try:
            print('Generating source manifest')
            generate_log(log_name_source, 'EVENT = Generating source manifest: status=started, eventType=message digest calculation, module=hashlib')
            if rootpos == 'y':
                make_manifest(
                    os.path.abspath(args.source), manifest, os.path.abspath(args.source)
                )
            else:
                make_manifest(
                    source, manifest,
                    os.path.dirname(source)
                )
            generate_log(log_name_source, 'EVENT = Generating source manifest: status=completed')
        except OSError:
            print('You do not have access to this directory. Perhaps it is read only, perhaps some files or folders have illegal characters, or the wrong file system\n')
            sys.exit()
    return manifest_sidecar, manifest, rootpos
def main(args_):
    '''
    Launches the functions that will safely copy and paste your files.
    '''
    manifest_temp = '--' # add two characters so that I can slice for manifest_temp[1] later.
    dircheck = None
    args, rootpos, manifest_sidecar, log_name_source, destination_final_path, manifest_root, manifest_destination, manifest, destination, dirname, desktop_manifest_dir = setup(args_)
    if os.path.isdir(args.source):
        dircheck = check_for_sip(args.source)
    if dircheck != None:
        if os.path.isdir(dircheck):
            source = check_for_sip(args.source)
    else:
        source = os.path.abspath(args.source)
        destination = args.destination
    overwrite_destination_manifest, overwrite_destination_dir = overwrite_check(
        destination, log_name_source,
        destination_final_path, manifest_destination
    )
    remove_bad_files(
        source, log_name_source
    )
    source_count, file_list = count_stuff(
        source
    )
    manifest_existence(
        manifest_root, manifest_sidecar,
        manifest, source_count,
        file_list, log_name_source
    )
    manifest_sidecar, manifest, rootpos = control_flow(
        manifest_sidecar, log_name_source, manifest, rootpos, args, source
    )
    if overwrite_destination_dir not in ('N', 'n'):
        if overwrite_destination_dir != None:
            generate_log(
                log_name_source,
                'EVENT = File Transfer Overwrite - Destination directory already exists - Overwriting.'
            )
        if not args.move:
            copy_dir(
                source, destination_final_path,
                log_name_source, rootpos, destination, dirname, args
            )
        else:
            shutil.move(source, destination_final_path)
    else:
        generate_log(
            log_name_source,
            'EVENT = File Transfer Overwrite - Destination directory already exists - Not Overwriting.'
        )
    if args.justcopy:
        generate_log(
            log_name_source,
            'EVENT = Exiting without destination manifest or verification due to the use of -justcopy'
        )
        print 'Exiting without destination manifest or verification due to the use of -justcopy'
        sys.exit()
    else:
        files_in_manifest = make_destination_manifest(
            overwrite_destination_manifest, log_name_source,
            rootpos, destination_final_path,
            manifest_destination,
            destination
        )
        destination_count = 0
        # dear god do this better, this is dreadful code!
        for _, _, filenames in os.walk(destination_final_path):
            for _ in filenames:
                destination_count += 1 #works in windows at least
        if rootpos == 'y':
            manifest_temp = tempfile.mkstemp(
                dir=desktop_manifest_dir, suffix='.md5'
            )
            os.close(manifest_temp[0]) # Needed for windows.
            with open(manifest, 'r') as fo:
                dest_manifest_list = fo.readlines()
                with open(manifest_temp[1], 'wb') as temp_object:
                    for i in dest_manifest_list:
                        temp_object.write(i[:33] + ' ' + os.path.basename(os.path.dirname(destination_final_path)) + '/' +  i[34:])
                legacy_manifest = manifest
                manifest = manifest_temp[1]
        verify_copy(
            manifest, manifest_destination, log_name_source, overwrite_destination_manifest, files_in_manifest, destination_count, source_count
        )
        manifest_rename = manifest[:-4] + time.strftime("_%Y_%m_%dT%H_%M_%S") + '.md5'
        if os.path.normpath(os.path.dirname(manifest)) == os.path.normpath(desktop_manifest_dir):
            os.rename(manifest, manifest_rename)
            shutil.move(manifest_rename, os.path.join(desktop_manifest_dir, 'old_manifests'))
            if rootpos == 'y':
                legacy_manifest_rename = legacy_manifest[:-4] + time.strftime("_%Y_%m_%dT%H_%M_%S") + '.md5'
                os.rename(legacy_manifest, legacy_manifest_rename)
                shutil.move(legacy_manifest_rename, os.path.join(desktop_manifest_dir, 'old_manifests'))
        # hack to also copy the sha512 manifest :(
        # Stop the temp manifest from copying
        if not os.path.basename(manifest_temp[1]) == os.path.basename(manifest):
            sha512_manifest = manifest.replace('_manifest.md5', '_manifest-sha512.txt')
            if os.path.isfile(sha512_manifest):
                shutil.copy2(sha512_manifest, os.path.dirname(destination_final_path))
                print '%s has been copied to %s' % (sha512_manifest, os.path.dirname(destination_final_path))
        return log_name_source
if __name__ == '__main__':
    main(sys.argv[1:])
