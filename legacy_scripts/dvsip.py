#!/usr/bin/env python

import subprocess
import sys
import os
from glob import glob
import shutil
try:
    from ififuncs import set_environment
    from ififuncs import hashlib_manifest
    from ififuncs import make_mediatrace
    from ififuncs import make_mediainfo
    from ififuncs import generate_log
    from ififuncs import get_mediainfo
except ImportError:
    print('*** ERROR - IFIFUNCS IS MISSING - *** \n'
    'dvsip requires that ififuncs.py is located in the same directory'
    ' as some functions are located in that script -'
    'https://github.com/kieranjol/IFIscripts/blob/master/ififuncs.py')
    sys.exit()

def get_input():
    if len(sys.argv) < 2:
        print ('IFI DV SIP CREATION SCRIPT')
        print ('USAGE: PYTHON dvsip.py FILENAME')
        print ('OR')
        print ('USAGE: PYTHON dvsip.py DirectoryNAME')
        print ('If input is a directory, all files will be processed')
        print ('If input is a file, only that file will be processed')
        sys.exit()
    else:
        # Input, either file or firectory, that we want to process.
        input = sys.argv[1]
        # Store the directory containing the input file/directory.
        wd = os.path.dirname(input)
        # Change current working directory to the value stored as "wd"
        os.chdir(os.path.abspath(wd))
        # Store the actual file/directory name without the full path.
        file_without_path = os.path.basename(input)
        # Check if input is a file.
        # AFAIK, os.path.isfile only works if full path isn't present.
        if os.path.isfile(file_without_path):
            print('single file found')
            video_files = []                       # Create empty list
            video_files.append(file_without_path)  # Add filename to list
        # Check if input is a directory.
        elif os.path.isdir(file_without_path):
            os.chdir(file_without_path)
            video_files = (
                glob('*.mov')
                + glob('*.dv')
                )
        else:
            print("Your input isn't a file or a directory.")
            print("What was it? I'm curious.")
        dv_test = []    
        for test_files in video_files:
            codec =  get_mediainfo(
                'codec', '--inform=Video;%Codec%',
                 test_files
                 ).rstrip()
            if codec.rstrip() != 'DV':
                dv_test.append(test_files)
                print('Non-DV file found, skipping')
        for i in dv_test:
            if i in video_files:
                video_files.remove(i)
        return video_files


def make_sip(video_files):
    for filename in video_files: #loop all files in directory
        filenoext = os.path.splitext(filename)[0]
        # Generate new directory names
        metadata_dir = '%s/metadata' % filenoext
        log_dir = '%s/logs' % filenoext
        data_dir = '%s/objects' % filenoext
        # Actually create the directories.
        os.makedirs(metadata_dir)
        os.makedirs(data_dir)
        os.makedirs(log_dir)
        #Generate filenames for new files.
        inputxml = '%s/%s_mediainfo.xml' % (
            metadata_dir, os.path.basename(filename)
            )
        inputtracexml = '%s/%s_mediatrace.xml' % (
            metadata_dir, os.path.basename(filename)
            )
        fmd5 = '%s/%s.framemd5' % (
            metadata_dir, os.path.basename(filename)
            )
        log = '%s/%s_log.log' %  (log_dir, filename)
        generate_log(log, 'Input = %s' % filename)
        fmd5_logfile = log_dir + '/%s_framemd5.log' % filename
        fmd5_env_dict = set_environment(fmd5_logfile)
        fmd5_command = [
            'ffmpeg',    # Create decoded md5 checksums for every frame
            '-i', filename,
            '-report',
            '-f', 'framemd5', '-an',
            fmd5
            ]
        print(fmd5_command)
        subprocess.call(fmd5_command, env=fmd5_env_dict)
        generate_log(
            log,
            'makeffv1.py Framemd5 generation of output file completed'
            )
        if os.path.basename(sys.argv[0]) == 'makeffv1.py':
            shutil.copy(sys.argv[0], log_dir)
        print('Generating mediainfo xml of input file and saving it in %s') % inputxml
        make_mediainfo(inputxml, 'mediaxmlinput', filename)
        print('Generating mediatrace xml of input file and saving it in %s') % inputtracexml
        make_mediatrace(inputtracexml, 'mediatracexmlinput', filename)
        source_parent_dir = os.path.dirname(os.path.abspath(filename))
        manifest = '%s/%s_manifest.md5' % (source_parent_dir, filenoext)
        if os.path.isfile(filename):
            shutil.move(filename, data_dir)
            generate_log(log, 'dvsip.py DV file moved to %s' % data_dir)
        generate_log(log, 'dvsip.py MD5 manifest started')
        hashlib_manifest(filenoext, manifest, source_parent_dir)
def main():
    video_files = get_input()
    make_sip(video_files)
if __name__ == '__main__':
    main()
