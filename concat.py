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
    parsed_args = parser.parse_args(args_)
    return parsed_args


def ffmpeg_concat(concat_file, args):
    '''
    Launch the actual ffmpeg concatenation command
    '''
    cmd = [
        'ffmpeg', '-f', 'concat', '-safe', '0',
        '-i', concat_file,
        '-c', 'copy',
        os.path.join(args.o, 'output.mkv')
    ]
    print cmd
    subprocess.call(
        cmd
    )


def main(args_):
    '''
    Launches the functions that prepare and execute the concatenation.
    '''
    args = parse_args(args_)
    video_files = args.i
    concat_file = ififuncs.get_temp_concat('concat_stuff')
    video_files = ififuncs.sanitise_filenames(video_files)
    ififuncs.concat_textfile(video_files, concat_file)
    ffmpeg_concat(concat_file, args)

if __name__ == '__main__':
    main(sys.argv[1:])
