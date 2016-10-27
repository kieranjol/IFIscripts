#!/usr/bin/env python

import subprocess
import sys
import os
from glob import glob
import datetime
import time
import csv

            
def get_filenames(directory, log_filename_alteration):
    os.chdir(directory)
    tiff_check = glob('*.tiff')
    dpx_check = glob('*.dpx')
    if len(dpx_check) > 0:
        images = dpx_check     
    elif len(tiff_check) > 0:
        images = tiff_check
    else:  
        return 'none'    
    images.sort()
   
    if '864000' in images[0]:
        start_number = '864000'
    elif len(images[0].split("_")[-1].split(".")) > 2:
        start_number = images[0].split("_")[-1].split(".")[1]
        
    else:
        
        start_number = images[0].split("_")[-1].split(".")[0]
    container = images[0].split(".")[-1]
    if len(images[0].split("_")[-1].split(".")) > 2:
        numberless_filename = images[0].split(".")
        
    else:
        numberless_filename = images[0].split("_")[0:-1]
    
    ffmpeg_friendly_name = ''
    counter = 0
    if len(images[0].split("_")[-1].split(".")) > 2:
        numberless_filename = images[0].split(".")[0:-1]
        for i in numberless_filename[:-1]:
            ffmpeg_friendly_name += i + '.'
        print ffmpeg_friendly_name

    else:
        while  counter <len(numberless_filename) :
            ffmpeg_friendly_name += numberless_filename[counter] + '_'
            counter += 1

    image_seq_without_container = ffmpeg_friendly_name
    if len(images[0].split("_")[-1].split(".")) > 2:
        image_seq_without_container = ffmpeg_friendly_name[:-1] + ffmpeg_friendly_name[-1].replace('_', '.')
    start_number_length = len(start_number)
    number_regex = "%0" + str(start_number_length) + 'd.'
    ffmpeg_friendly_name += number_regex + '%s' % container
    info = [image_seq_without_container, start_number, container]
    return info


source_directory = sys.argv[1]
if not os.path.isdir(source_directory):
    print 'Input is not a directory. Please rerun the script, providing the parent directory of the image sequence as input\nfor example:\nplayerseq.py /volumes/fakefolder/parentdir'
    sys.exit()

source_parent_dir    = os.path.dirname(source_directory)
split_path           = os.path.split(os.path.basename(source_directory))[1]
info = get_filenames(source_directory, 'dpx_framemd5')

image_seq_without_container = info[0]
start_number                = info[1]
container                   = info[2]
start_number_length = len(start_number)
number_regex = "%0" + str(start_number_length) + 'd.'
mezzanine_dir            = '/Volumes/Media1/individual_exports'
audio_file = raw_input('Drag and drop the actual WAV file and press ENTER\n').rstrip()
dpx_filename                = image_seq_without_container + number_regex + container
seq2prores= ['ffmpeg','-f','image2','-framerate','24', '-start_number', start_number, '-i', source_directory + '/' + dpx_filename ,'-i', audio_file,'-c:v','prores','-profile:v', '3','-c:a','copy', mezzanine_dir + '/' + image_seq_without_container  + '_mezzanine.mov']
print seq2prores
subprocess.call(seq2prores)