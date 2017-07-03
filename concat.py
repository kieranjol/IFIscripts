#!/usr/bin/env python
'''
Concatenates video files using ffmpeg stream copy
'''
import sys
import subprocess
import os
import argparse
import ififuncs


def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Concatenate video files using ffmpeg stream copy'
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
        '-r', '-recursive',
        help='recursively process all files in subdirectories. This could be potentially a disaster - so use with caution or with XDCAM', action='store_true'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def ffmpeg_concat(concat_file, args, uuid):
    '''
    Launch the actual ffmpeg concatenation command
    '''
    cmd = [
        'ffmpeg', '-f', 'concat', '-safe', '0',
        '-i', concat_file,
        '-c', 'copy', '-map', '0:a?', '-map', '0:v',
        os.path.join(args.o, '%s.mkv' % uuid)
    ]
    print cmd
    subprocess.call(
        cmd
    )


def recursive_file_list(video_files):
    '''
    Recursively search through directories for AV files and add to list.
    '''
    # check if all inputs are actually directories
    recursive_list = []
    for directory in video_files:
        if not os.path.isdir(directory):
            print 'You have selected the recursive option, but not all of your inputs are directories.'
            sys.exit()
        else:
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    if filename.endswith(('.MP4', '.mp4', '.mov', '.mkv', '.mxf')):
                        recursive_list.append(os.path.join(root, filename))
    print recursive_list
    return recursive_list



def main(args_):
    '''
    Launches the functions that prepare and execute the concatenation.
    '''
    uuid = ififuncs.create_uuid()
    args = parse_args(args_)
    video_files = args.i
    concat_file = ififuncs.get_temp_concat('concat_stuff')
    if args.r:
        video_files = recursive_file_list(video_files)
    video_files = ififuncs.sanitise_filenames(video_files)
    ififuncs.concat_textfile(video_files, concat_file)
    ffmpeg_concat(concat_file, args, uuid)

if __name__ == '__main__':
    main(sys.argv[1:])
