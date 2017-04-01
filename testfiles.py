#!/usr/bin/env python
import sys
import subprocess
import os


def main():
    '''
    Creates three v210/mov tesfiles in a test_files subdirectory
    '''
    output_dir = os.path.join(sys.argv[1], 'test_files')
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


