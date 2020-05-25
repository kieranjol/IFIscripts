#!/usr/bin/env python3
'''
Creates some test video files via ffmpeg.
Usage: testfiles.py -o path/to/dir
Run testfiles.py -h for help.
Written by Kieran O'Leary.
'''
import subprocess
import os
import argparse
import sys
import ififuncs

def parse_args(args_):
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
    parser.add_argument(
        '-onlyvideo',
        help='Only creates video, no image sequences', action='store_true'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def main(args_):
    '''
    Creates three v210/mov tesfiles in a test_files subdirectory
    '''
    ififuncs.check_existence(['ffmpeg'])
    args = parse_args(args_)
    output_dir = os.path.join(os.path.abspath(args.o), 'test_files')
    ten_bit_dpx_dir = os.path.join(output_dir, 'ten_bit_dpx')
    sixteen_bit_dpx_dir = os.path.join(output_dir, 'sixteen_bit_dpx')
    multi_reel_dir = os.path.join(output_dir, 'multi_reel')
    reel1 = os.path.join(multi_reel_dir, 'whatever_reel1')
    reel2 = os.path.join(multi_reel_dir, 'whatever_reel2')
    reel3 = os.path.join(multi_reel_dir, 'whatever_reel3')
    bars_cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc', '-n',
        '-f', 'lavfi', '-i', 'sine', '-c:v', 'v210', '-ac', '2', '-c:a', 'pcm_s24le',
        '-t', '20', os.path.join(output_dir, 'bars_v210_pcm24le_stereo_20sec.mov')
        ]
    mandel_cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'mandelbrot', '-n',
        '-c:v', 'v210', '-t', '5', os.path.join(output_dir, 'mandel_silent.mov')
        ]

    life_cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc',
        '-pix_fmt', 'gbrp10le', '-t', '20', os.path.join(ten_bit_dpx_dir, 'ten_bit_%06d.dpx'),
        '-f', 'lavfi', '-i', 'sine', '-ac', '2', '-c:a', 'pcm_s24le', '-t', '20', os.path.join(ten_bit_dpx_dir, 'ten_bit.wav')
        ]
    reel1_cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc',
        '-pix_fmt', 'gbrp10le', '-t', '20', os.path.join(reel1, 'ten_bit_reel1_%06d.dpx'),
        '-f', 'lavfi', '-i', 'sine', '-ac', '2', '-c:a', 'pcm_s24le', '-t', '20', os.path.join(reel1, 'ten_bit_reel1.wav')
        ]
    reel2_cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc2',
        '-pix_fmt', 'gbrp10le', '-t', '20', os.path.join(reel2, 'ten_bit_reel2_%06d.dpx'),
        '-f', 'lavfi', '-i', 'sine', '-ac', '2', '-c:a', 'pcm_s24le', '-t', '20', os.path.join(reel2, 'ten_bit_reel2.wav')
        ]
    reel3_cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'mandelbrot',
        '-pix_fmt', 'gbrp10le', '-t', '20', os.path.join(reel3, 'ten_bit_reel3_%06d.dpx'),
        '-f', 'lavfi', '-i', 'sine', '-ac', '2', '-c:a', 'pcm_s24le', '-t', '20', os.path.join(reel3, 'ten_bit_reel3.wav')
        ]
    dpx16_cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc2',
        '-pix_fmt', 'rgb48le', '-t', '20', os.path.join(sixteen_bit_dpx_dir, 'sixteen_bit_%06d.dpx')
        ]
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    subprocess.call(bars_cmd)
    subprocess.call(mandel_cmd)
    if not args.onlyvideo:
        if not os.path.isdir(ten_bit_dpx_dir):
            os.makedirs(ten_bit_dpx_dir)
        if not os.path.isdir(sixteen_bit_dpx_dir):
            os.makedirs(sixteen_bit_dpx_dir)
        if not os.path.isdir(reel1):
            os.makedirs(reel1)
        if not os.path.isdir(reel2):
            os.makedirs(reel2)
        if not os.path.isdir(reel3):
            os.makedirs(reel3)
        subprocess.call(dpx16_cmd)
        subprocess.call(reel1_cmd)
        subprocess.call(reel2_cmd)
        subprocess.call(reel3_cmd)
        subprocess.call(life_cmd)

if __name__ == '__main__':
    main(sys.argv[1:])
