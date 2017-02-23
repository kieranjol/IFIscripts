#!/usr/bin/env python
import sys
import os
import subprocess


def make_palette(input):
    cmd = ['ffmpeg',
           '-i', input,
           '-filter_complex',
           'fps=24,scale=500:-1:flags=lanczos,palettegen',
           'palette.png']
    subprocess.call(cmd)

def make_gif(input):
    cmd = ['ffmpeg',
           '-i', input,
           '-i', 'palette.png',
           '-filter_complex',
           '[0:v]fps=24,scale=500:-1:flags=lanczos[v],[v][1:v]paletteuse',
           input + '.gif']
    subprocess.call(cmd)

def main():
    input = sys.argv[1]
    make_palette(input)
    make_gif(input)
    os.remove('palette.png')


if __name__ == '__main__':
    main()
