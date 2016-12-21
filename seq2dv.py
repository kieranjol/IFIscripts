#!/usr/bin/env python

import subprocess
import sys
import os
from glob import glob


def get_input(root):
    source_directory = root
    os.chdir(source_directory)
    images = (glob('*.tif')
            + glob('*.tiff')
            + glob('*.dpx'))
    return images, source_directory


def get_filenames(images, source_directory):
    numberless_filename = images[0].split("_")[0:-1]
    ffmpeg_friendly_name = ''
    counter = 0
    while  counter <len(numberless_filename) :
        ffmpeg_friendly_name += numberless_filename[counter] + '_'
        counter += 1
    dirname = os.path.dirname(source_directory)
    output = dirname + '/%s_consolidate.mov' % os.path.split(source_directory)[-1]
    return ffmpeg_friendly_name, output
 

def make_dv(ffmpeg_friendly_name, output):
    ffmpeg_friendly_name += '%06d.tiff'
    cmd = ['ffmpeg','-f','image2',
           '-framerate','24',
           '-i', ffmpeg_friendly_name,
           '-c:v','dvvideo',
           '-vf','scale=720x576',
           output]
    print cmd
    subprocess.call(cmd)
def main():
    all_files = sys.argv[1:]
    for folders in all_files:
        for root, dirs, files in os.walk(folders):
            if len(files) > 10:
                if files[5].endswith(('.tif', '.tiff', '.dpx' )):
                    print '***********************************************************************************************************************************************************'
                    images,source_directory = get_input(root)
                    ffmpeg_friendly_name,output = get_filenames(images, source_directory)
                    make_dv(ffmpeg_friendly_name, output)

if __name__ == '__main__':
    main()