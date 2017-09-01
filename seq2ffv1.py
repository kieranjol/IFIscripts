#!/usr/bin/env python

'''
Usage: seq2ffv1.py source_parent_directory output_directory
The script will look through all subdirectories beneath the
source_parent_directory for a DPX or image sequence.
The script will then:
Create folder structure for each image sequence in
your designated output_directory.
Create framemd5 values of the source sequence
Transcode to a single FFV1 in Matroska file
Create framemd5 values for the FFV1 in Matroska file
Verify losslessness
(There will most likely be a warning about pixel aspect ratio
- https://www.ietf.org/mail-archive/web/cellar/current/msg00739.html)
Generate CSV log that will be saved to your desktop
'''
import subprocess
import os
import argparse
import itertools
import tempfile
import shutil
import ififuncs
import sipcreator

def run_loop(args):
    '''
    Launches a recursive loop to process all images sequences in your
    subdirectories.
    '''
    for source_directory, _, _ in os.walk(args.source_directory):
        output_dirname = args.destination
        images = ififuncs.get_image_sequence_files(source_directory)
        (ffmpeg_friendly_name,
         start_number, root_filename) = ififuncs.parse_image_sequence(images)
        source_abspath = os.path.join(source_directory, ffmpeg_friendly_name)
        make_ffv1(
            start_number,
            source_abspath,
            output_dirname,
            root_filename,
        )


def verify_losslessness(source_textfile, ffv1_md5):
    '''
    Compares two framemd5 documents in order to determine losslessness.
    '''
    ififuncs.diff_textfiles(source_textfile, ffv1_md5)
    checksum_mismatches = []
    with open(source_textfile) as source_md5_object:
        with open(ffv1_md5) as ffv1_md5_object:
            for (line1), (line2) in itertools.izip(
                ififuncs.read_lines(
                    source_md5_object
                ), ififuncs.read_lines(ffv1_md5_object)
            ):
                if line1 != line2:
                    if 'sar' in line1:
                        checksum_mismatches = ['sar']
                    else:
                        checksum_mismatches.append(1)

def make_ffv1(
        start_number,
        source_abspath,
        output_dirname,
        root_filename,
    ):
    '''
    This launches the image sequence to FFV1/Matroska process
    as well as framemd5 losslessness verification.
    '''
    object_entry = ififuncs.get_object_entry()
    files_to_move = []
    pix_fmt = ififuncs.img_seq_pixfmt(
        start_number,
        source_abspath
    )
    temp_dir = tempfile.gettempdir()
    logfile = os.path.join(
        temp_dir,
        '%s_ffv1_transcode.log' % root_filename
    )
    files_to_move.append(logfile)
    logfile = "\'" + logfile + "\'"
    env_dict = ififuncs.set_environment(logfile)
    ffv1_path = os.path.join(output_dirname, root_filename + '.mkv')
    source_textfile = os.path.join(
        temp_dir, root_filename + 'source.framemd5'
    )
    files_to_move.append(source_textfile)
    ffv12dpx = [
        'ffmpeg', '-report',
        '-f', 'image2',
        '-framerate', '24',
        '-start_number', start_number,
        '-i', source_abspath,
        '-strict', '-2',
        '-c:v', 'ffv1',
        '-level', '3',
        '-g', '1',
        '-slicecrc', '1',
        '-slices', '16',
        '-pix_fmt', pix_fmt,
        ffv1_path,
        '-f', 'framemd5', source_textfile
    ]
    print ffv12dpx
    subprocess.call(ffv12dpx, env=env_dict)
    ffv1_md5 = os.path.join(
        temp_dir,
        root_filename + 'ffv1.framemd5'
    )
    files_to_move.append(ffv1_md5)
    ffv1_fmd5_cmd = [
        'ffmpeg',
        '-i', ffv1_path,
        '-pix_fmt', pix_fmt,
        '-f', 'framemd5',
        ffv1_md5
    ]
    ffv1_fmd5_logfile = os.path.join(
        temp_dir, '%s_ffv1_framemd5.log' % root_filename
    )
    files_to_move.append(ffv1_fmd5_logfile)
    ffv1_fmd5_logfile = "\'" + ffv1_fmd5_logfile + "\'"
    ffv1_fmd5_env_dict = ififuncs.set_environment(ffv1_fmd5_logfile)
    subprocess.call(ffv1_fmd5_cmd, env=ffv1_fmd5_env_dict)
    verify_losslessness(source_textfile, ffv1_md5)
    uuid = ififuncs.create_uuid()
    sip_dir = os.path.join(
        os.path.dirname(ffv1_path), os.path.join(object_entry, uuid)
    )
    sipcreator_log, sipcreator_manifest = sipcreator.main([
        '-i',
        ffv1_path,
        '-u',
        uuid,
        '-quiet',
        '-user',
        'Kieran',
        '-oe',
        object_entry,
        '-o', os.path.dirname(ffv1_path)])
    logs_dir = os.path.join(sip_dir, 'logs')
    metadata_dir = os.path.join(sip_dir, 'metadata')
    for files in files_to_move:
        if files.endswith('.log'):
            shutil.move(files, logs_dir)
            ififuncs.manifest_update(
                sipcreator_manifest,
                os.path.join(logs_dir, os.path.basename(files))
            )
        elif files.endswith('.framemd5'):
            shutil.move(files, metadata_dir)
            ififuncs.manifest_update(
                sipcreator_manifest,
                os.path.join(metadata_dir, os.path.basename(files))
            )
    return source_textfile, ffv1_md5

def setup():
    '''
    Sets up a lot of the variables and filepaths.
    '''
    parser = argparse.ArgumentParser(description='Transcode all DPX or TIFF'
                                    ' image sequence in the subfolders of your'
                                    ' source directory to FFV1 Version 3'
                                    ' in a Matroska Container.'
                                    ' Written by Kieran O\'Leary.')
    parser.add_argument('source_directory', help='Input directory')
    parser.add_argument('destination', help='Destination directory')
    args = parser.parse_args()
    return args

def main():
    '''
    Overly long main function that does most of the heavy lifting.
    This needs to be broken up into smaller functions.
    '''
    args = setup()
    run_loop(args)


if __name__ == '__main__':
    main()
