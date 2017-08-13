#!/usr/bin/env python

'''
Usage: seq2ffv1.py source_parent_directory output_directory
The script will look through all subdirectories beneath the source_parent_directory for a DPX or image sequence.
The script will then:
Create folder structure for each image sequence in your designated output_directory
Create framemd5 values of the source sequence
Transcode to a single FFV1 in Matroska file
Create framemd5 values for the FFV1 in Matroska file
Verify losslessness (There will most likely be a warning about pixel aspect ratio - https://www.ietf.org/mail-archive/web/cellar/current/msg00739.html)
Create md5 manifest of everything in your output directory
Generate CSV log that will be saved to your desktop
'''
import subprocess
import os
import argparse
import datetime
import time
import itertools
from ififuncs import diff_textfiles
from ififuncs import make_manifest
from ififuncs import get_mediainfo
from ififuncs import create_csv
from ififuncs import append_csv
from ififuncs import get_image_sequence_files
from ififuncs import get_ffmpeg_friendly_name



def read_non_comment_lines(infile):
    '''
    This looks like I just copy pasted from stack overflow.
    There is a commented line here that actually negates the usefulness of this
    function, in that it doesn't discard commented lines. To be investgated.
    '''
    for lineno, line in enumerate(infile):
        #if line[:1] != "#":
        yield lineno, line


def set_environment(logfile):
    '''
    Sets environment variable for ffmpeg logfile. Should be moved to ififuncs.
    '''
    env_dict = os.environ.copy()
    # https://github.com/imdn/scripts/blob/0dd89a002d38d1ff6c938d6f70764e6dd8815fdd/ffmpy.py#L272
    env_dict['FFREPORT'] = 'file={}:level=48'.format(logfile)
    return env_dict


def make_framemd5(directory, log_filename_alteration, args):
    '''
    Apparently this makes framemd5s. But it clearly does a lot more.
    '''
    images = get_image_sequence_files(directory)
    if images == 'none':
        return 'none'
    sequence_length = len(images)
    ffmpeg_friendly_name, container, start_number = get_ffmpeg_friendly_name(images)
    output_parent_directory = args.destination
    if start_number == '864000':
        output_dirname = os.path.join(
            output_parent_directory,
            os.path.basename(directory) + time.strftime("%Y_%m_%dT%H_%M_%S")
        )
        basename = os.path.basename(directory)
    else:
        output_dirname = os.path.join(
            output_parent_directory,
            ffmpeg_friendly_name + time.strftime("%Y_%m_%dT%H_%M_%S")
        )
        basename = ffmpeg_friendly_name
    logs_dir = output_dirname + '/logs'
    objects_dir = output_dirname + '/objects'
    metadata_dir = output_dirname + '/metadata'
    try:
        os.makedirs(output_dirname)
        os.makedirs(logs_dir)
        os.makedirs(objects_dir)
        os.makedirs(metadata_dir)
    except: OSError
    output = output_dirname + '/metadata/%ssource.framemd5' % (basename)
    logfile = output_dirname + '/logs/%s%s.log' % (basename, log_filename_alteration)
    logfile = "\'" + logfile + "\'"
    env_dict = set_environment(logfile)
    image_seq_without_container = ffmpeg_friendly_name
    start_number_length = len(start_number)
    number_regex = "%0" + str(start_number_length) + 'd.'
    if len(images[0].split("_")[-1].split(".")) > 2:
        image_seq_without_container = ffmpeg_friendly_name[:-1] + ffmpeg_friendly_name[-1].replace('_', '.')
        ffmpeg_friendly_name = image_seq_without_container
    ffmpeg_friendly_name += number_regex + '%s' % container
    framemd5 = [
        'ffmpeg', '-start_number',
        start_number, '-report',
        '-f', 'image2',
        '-framerate', '24',
        '-i', ffmpeg_friendly_name,
        '-f', 'framemd5', output
    ]
    print framemd5
    subprocess.call(framemd5, env=env_dict)
    info = [
        output_dirname,
        output,
        image_seq_without_container,
        start_number,
        container,
        ffmpeg_friendly_name,
        number_regex,
        sequence_length
    ]
    return info

def remove_bad_files(root_dir):
    '''
    removes unwanted files. unless something is altered, just use the ififuncs
    function instead.
    '''
    rm_these = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
    for root, _, files in os.walk(root_dir):
        for name in files:
            path = os.path.join(root, name)
            for i in rm_these:
                if name == i:
                    print '***********************' + 'removing: ' + path
                    os.remove(path)
def main():
    '''
    Overly long main function that does most of the heavy lifting.
    This needs to be broken up into smaller functions.
    '''
    csv_report_filename = os.path.join(
        os.path.expanduser("~/Desktop/"),
        'dpx_transcode_report' + time.strftime("_%Y_%m_%dT%H_%M_%S") + '.csv'
    )
    parser = argparse.ArgumentParser(description='Transcode all DPX or TIFF image sequence in the subfolders of your source directory to FFV1 Version 3 in a Matroska Container. A CSV report is generated on your desktop.'
                                     ' Written by Kieran O\'Leary.')
    parser.add_argument('source_directory', help='Input directory')
    parser.add_argument('destination', help='Destination directory')
    args = parser.parse_args()
    source_directory = args.source_directory
    create_csv(csv_report_filename, (
        'Sequence Name', 'Lossless?',
        'Start time', 'Finish Time',
        'Transcode Start Time', 'Transcode Finish Time',
        'Transcode Time', 'Frame Count',
        'Encode FPS', 'Sequence Size',
        'FFV1 Size', 'Pixel Format',
        'Sequence Type', 'Width',
        'Height', 'Compression Ratio'
        ))
    for root, _, filenames in os.walk(source_directory):
        source_directory = root # + '/tiff_scans'
        total_size = 0
        start = datetime.datetime.now()
        info = make_framemd5(source_directory, 'dpx_framemd5', args)
        if info == 'none':
            continue
        for files in filenames:
            total_size += os.path.getsize(os.path.join(root, files))
        output_dirname = info[0]
        source_textfile = info[1]
        image_seq_without_container = info[2]
        start_number = info[3]
        container = info[4]
        dpx_filename = info[5]
        sequence_length = info[7]
        output_filename = image_seq_without_container[:-1]
        logfile = output_dirname + '/logs/%s_ffv1_transcode.log' % output_filename
        logfile = "\'" + logfile + "\'"
        env_dict = set_environment(logfile)
        ffprobe_cmd = [
            'ffprobe',
            '-start_number', start_number,
            '-i', os.path.abspath(dpx_filename),
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries',
            'stream=pix_fmt',
            '-of', 'default=noprint_wrappers=1:nokey=1'
        ]
        pix_fmt = subprocess.check_output(ffprobe_cmd).rstrip()
        ffv12dpx = [
            'ffmpeg', '-report',
            '-f', 'image2',
            '-framerate', '24',
            '-start_number', start_number,
            '-i', os.path.abspath(dpx_filename),
            '-strict', '-2',
            '-c:v', 'ffv1',
            '-level', '3',
            '-g', '1',
            '-slicecrc', '1',
            '-slices', '16',
            '-pix_fmt', pix_fmt,
            output_dirname +  '/objects/' + output_filename + '.mkv'
        ]
        print ffv12dpx
        transcode_start = datetime.datetime.now()
        transcode_start_machine = time.time()
        subprocess.call(ffv12dpx, env=env_dict)
        transcode_finish = datetime.datetime.now()
        transcode_finish_machine = time.time()
        transcode_time = transcode_finish_machine - transcode_start_machine
        parent_basename = os.path.basename(output_dirname)
        manifest_textfile = os.path.join(
            os.path.dirname(output_dirname), parent_basename + '_manifest.md5'
        )
        ffv1_path = output_dirname +  '/objects/'  + output_filename + '.mkv'
        width = get_mediainfo('duration', '--inform=Video;%Width%', ffv1_path)
        height = get_mediainfo('duration', '--inform=Video;%Height%', ffv1_path)
        ffv1_md5 = output_dirname +  '/metadata/' + image_seq_without_container + 'ffv1.framemd5'
        ffv1_fmd5_cmd = [
            'ffmpeg',
            '-i', ffv1_path,
            '-pix_fmt', pix_fmt,
            '-f', 'framemd5',
            ffv1_md5
        ]
        ffv1_fmd5_logfile = os.path.join(
            output_dirname, '/logs/%s_ffv1_framemd5.log' % output_filename
        )
        ffv1_fmd5_logfile = "\'" + ffv1_fmd5_logfile + "\'"
        ffv1_fmd5_env_dict = set_environment(ffv1_fmd5_logfile)
        subprocess.call(ffv1_fmd5_cmd, env=ffv1_fmd5_env_dict)
        finish = datetime.datetime.now()
        ffv1_size = os.path.getsize(ffv1_path)
        comp_ratio = float(total_size) / float(os.path.getsize(ffv1_path))
        judgement = diff_textfiles(source_textfile, ffv1_md5)
        fps = float(sequence_length) / float(transcode_time)
        checksum_mismatches = []
        with open(source_textfile) as f1:
            with open(ffv1_md5) as f2:
                for (lineno1, line1), (lineno2, line2) in itertools.izip(
                        read_non_comment_lines(f1), read_non_comment_lines(f2)
                ):
                    if line1 != line2:
                        if 'sar' in line1:
                            checksum_mismatches = ['sar']
                        else:
                            checksum_mismatches.append(1)
        if len(checksum_mismatches) == 0:
            print 'LOSSLESS'
            append_csv(
                csv_report_filename, (
                    parent_basename, judgement,
                    start, finish,
                    transcode_start, transcode_finish,
                    transcode_time, sequence_length,
                    fps, total_size,
                    ffv1_size, pix_fmt,
                    container, width,
                    height, comp_ratio
                )
            )

        elif len(checksum_mismatches) == 1:
            if checksum_mismatches[0] == 'sar':
                print 'Image content is lossless, Pixel Aspect Ratio has been altered - This is mostly likely because your source had no pixel aspect ratio information, and Matroska is specifying 1:1. https://www.ietf.org/mail-archive/web/cellar/current/msg00739.html '
                append_csv(csv_report_filename, (
                    parent_basename, 'LOSSLESS - different PAR',
                    start, finish, transcode_start,
                    transcode_finish, transcode_time,
                    sequence_length, fps,
                    total_size, ffv1_size,
                    pix_fmt, container,
                    width, height,
                    comp_ratio
                )
                          )
        elif len(checksum_mismatches) > 1:
            print 'NOT LOSSLESS'
            append_csv(csv_report_filename, (
                parent_basename, judgement,
                start, finish, transcode_start,
                transcode_finish, transcode_time,
                sequence_length, fps,
                total_size, ffv1_size,
                pix_fmt, container,
                width, height,
                comp_ratio
            ))
        make_manifest(args.destination, os.path.basename(output_dirname), manifest_textfile)

if __name__ == '__main__':
    main()
