#!/usr/bin/env python

'''''
to do  - install ffmpegnpmetadata on brian pc
'''
import subprocess
import sys
import os
from glob import glob
from ififuncs import diff_textfiles
from ififuncs import make_manifest
source_directory = sys.argv[1]

def make_framemd5(directory, container):
    os.chdir(directory)
    images = glob('*.%s' % container)
    global dirname
    #dirname = ''  intentionally commented out as this is hardcoded for now
    
    print images
    numberless_filename = images[0].split("_")[0:-1]
    
    ffmpeg_friendly_name = ''
    counter = 0
    while  counter <len(numberless_filename) :
        ffmpeg_friendly_name += numberless_filename[counter] + '_'
        counter += 1
    output_dirname = dirname + '/' + ffmpeg_friendly_name + '_dpx_transcodes'
    try:
        os.makedirs(output_dirname + '/scans')
        os.makedirs(output_dirname + '/framemd5')
    except: OSError
    
    output = output_dirname + '/framemd5/%s%s.framemd5' % (ffmpeg_friendly_name,container)
    print output 
    ffmpeg_friendly_name += "%06d." + '%s' % container
    framemd5 = ['ffmpeg','-f','image2', '-i', ffmpeg_friendly_name,'-f','framemd5',output]
    print framemd5
    subprocess.call(framemd5)   
    info = [output_dirname, output]
    return info
        
info = make_framemd5(source_directory, 'tiff')
output_dirname = info[0]  


source_textfile = info[1]
  

images = glob('*.tiff')
for tiff in images:
    cmd = ['ffmpegnometadata','-f','image2','-framerate','24', '-i', tiff ,output_dirname +  '/scans' '/' + tiff[:-4] + 'dpx']
    print cmd
    subprocess.call(cmd)
manifest_textfile = output_dirname + '/manifest.md5'    
other = make_framemd5(output_dirname + '/scans', 'dpx')
other_textfile = other[1]
print source_textfile
print other_textfile
diff_textfiles(source_textfile, other_textfile)
make_manifest(dirname, os.path.basename(output_dirname), manifest_textfile)
