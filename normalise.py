#!/usr/bin/env python
'''
Performs normalisation to FFV1/Matroska.
This performs a basic normalisation and does not enforce any folder structure.
This supercedes makeffv1 within our workflows. This is mostly because makeffv1 imposes a specific, outdated
folder structure, and it's best to let SIPCREATOR handle the folder structure and let normalise.py handle
the actual normalisation.
'''
import sys
import os
import subprocess
import ififuncs

def extract_provenance(filename):
    '''
    This will extract mediainfo and mediatrace XML
    '''
    parent_folder = os.path.dirname(filename)
    inputxml = "%s/%s_mediainfo.xml" % (parent_folder, os.path.basename(filename))
    inputtracexml = "%s/%s_mediatrace.xml" % (parent_folder, os.path.basename(filename))
    print(' - Generating mediainfo xml of input file and saving it in %s' % inputxml)
    ififuncs.make_mediainfo(inputxml, 'mediaxmlinput', filename)
    print ' - Generating mediatrace xml of input file and saving it in %s' % inputtracexml
    ififuncs.make_mediatrace(inputtracexml, 'mediatracexmlinput', filename)
    return parent_folder

def normalise_process(filename):
    '''
    Begins the actual normalisation process using FFmpeg
    '''
    output_uuid = ififuncs.create_uuid()
    print(' - The following UUID has been generated: %s' % output_uuid)
    parent_folder = os.path.dirname(filename)
    output = "%s/%s.mkv" % (
        parent_folder, output_uuid
        )
    print(' - The normalise file will have this filename: %s' % output)
    fmd5 = "%s/%s_source.framemd5" % (
        parent_folder, os.path.basename(filename)
        )
    print(' - Framemd5s for each frame of your input file will be stored in: %s' % fmd5)

    ffv1_logfile = os.path.join(parent_folder, '%s_normalise.log' % output_uuid)
    print(' - The FFmpeg logfile for the transcode will be stored in: %s' % ffv1_logfile)
    print(' - FFmpeg will begin normalisation now.')
    ffv1_env_dict = ififuncs.set_environment(ffv1_logfile)
    ffv1_command = [
        'ffmpeg',
        '-i', filename,
        '-c:v', 'ffv1',         # Use FFv1 codec
        '-g', '1',              # Use intra-frame only aka ALL-I aka GOP=1
        '-level', '3',          # Use Version 3 of FFv1
        '-c:a', 'copy',         # Copy and paste audio bitsream with no transcoding
        '-map', '0',
        '-dn',
        '-report',
        '-slicecrc', '1',
        '-slices', '16',
    ]
    if ififuncs.check_for_fcp(filename) is True:
        print(' - A 720/576 file with no Pixel Aspect Ratio and scan type metadata has been detected.')
        ffv1_command += [
            '-vf',
            'setfield=tff, setdar=4/3'
            ]
        print(' - -vf setfield=tff, setdar=4/3 will be added to the FFmpeg command.')
    ffv1_command += [
        output,
        '-f', 'framemd5', '-an',  # Create decoded md5 checksums for every frame of the input. -an ignores audio
        fmd5
        ]
    print(ffv1_command)
    subprocess.call(ffv1_command, env=ffv1_env_dict)
    return output, output_uuid, fmd5

def verify_losslessness(parent_folder, output, output_uuid, fmd5):
    '''
    Verify the losslessness of the process using framemd5.
    An additional metadata check should also occur.
    '''
    fmd5_logfile = os.path.join(parent_folder, '%s_framemd5.log' % output_uuid)
    fmd5ffv1 = "%s/%s.framemd5" % (parent_folder, output_uuid)
    print(' - Framemd5s for each frame of your output file will be stored in: %s' % fmd5ffv1)
    fmd5_env_dict = ififuncs.set_environment(fmd5_logfile)
    print(' - FFmpeg will attempt to verify the losslessness of the normalisation by using Framemd5s.')
    fmd5_command = [
        'ffmpeg',    # Create decoded md5 checksums for every frame
        '-i', output,
        '-report',
        '-f', 'framemd5', '-an',
        fmd5ffv1
        ]
    print fmd5_command
    subprocess.call(fmd5_command, env=fmd5_env_dict)
    checksum_mismatches = ififuncs.diff_framemd5s(fmd5, fmd5ffv1)
    if len(checksum_mismatches) > 0:
        print 'not lossless'
    else:
        print 'lossless'

def main():
    print('\n - Normalise.py started')
    source = sys.argv[1]
    file_list = ififuncs.get_video_files(source)
    for filename in file_list:
        print('\n - Processing: %s' % filename)
        parent_folder = extract_provenance(filename)
        output, output_uuid, fmd5 = normalise_process(filename)
        verify_losslessness(parent_folder, output, output_uuid, fmd5)

if __name__ == '__main__':
    main()