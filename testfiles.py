#!/usr/bin/env python
'''
Creates some test video files via ffmpeg.
Usage: testfiles.py -o path/to/dir
Run testfiles.py -h for help.
Written by Kieran O'Leary.
'''
import subprocess
import os
import argparse

def parse_args():
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Creates some test video files via ffmpeg'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        '-o', '-output',
        help='full path of output directory', required=True
    )
    parsed_args = parser.parse_args()
    return parsed_args


def main():
    '''
    Creates three v210/mov tesfiles in a test_files subdirectory
    '''
    args = parse_args()
    output_dir = os.path.join(args.o, 'test_files')
    bars_cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc',
        '-c:v', 'v210', '-t', '20', os.path.join(output_dir, 'bars.mov')
        ]
    mandel_cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'mandelbrot',
        '-c:v', 'v210', '-t', '20', os.path.join(output_dir, 'mandel.mov')
        ]
    life_cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'life',
        '-c:v', 'v210', '-t', '20', os.path.join(output_dir, 'life.mov')
        ]
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    subprocess.call(bars_cmd)
    subprocess.call(mandel_cmd)
    subprocess.call(life_cmd)


if __name__ == '__main__':
    main()


