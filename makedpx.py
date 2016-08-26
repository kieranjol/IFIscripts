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
import datetime


print datetime.datetime.now()
def remove_bad_files(root_dir):
    rm_these = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
    for root, dirs, files in os.walk(root_dir):
        for name in files:
            path = os.path.join(root, name)
            for i in rm_these:
                if name == i:
                    print '***********************' + 'removing: ' + path   
                    os.remove(path)

source_directory = sys.argv[1]

for root,dirnames,filenames in os.walk(source_directory):
    if "tiff_scans"  in dirnames:
        print root
        source_directory = root + '/tiff_scans'
        
       
        
        remove_bad_files(source_directory)
        source_parent_dir    = os.path.dirname(source_directory)
        normpath             = os.path.normpath(source_directory) 
        dirname              = os.path.split(os.path.basename(source_directory))[1]
        relative_path        = normpath.split(os.sep)[-1]


        source_manifest = source_parent_dir + '/%s_manifest.md5' % relative_path

        make_manifest(os.path.dirname(source_directory), os.path.basename(source_directory), source_manifest)
        def make_framemd5(directory, container):
            os.chdir(directory)
            images = glob('*.%s' % container)
            global dirname
            #dirname = ''
            print images
            numberless_filename = images[0].split("_")[0:-1]
            ffmpeg_friendly_name = ''
            counter = 0
            while  counter <len(numberless_filename) :
                ffmpeg_friendly_name += numberless_filename[counter] + '_'
                counter += 1
            output_dirname = dirname + '/' + ffmpeg_friendly_name + 'dpx_transcodes'
            try:
                os.makedirs(output_dirname + '/image')
                os.makedirs(output_dirname + '/image/logs')
                os.makedirs(output_dirname + '/image/md5')
                os.makedirs(output_dirname + '/image/dpx_files')
                os.makedirs(output_dirname + '/image/xml_files')
             
            except: OSError
    
            output = output_dirname + '/image/md5/%s%s.framemd5' % (ffmpeg_friendly_name,container)
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
            cmd = ['ffmpegnometadata','-f','image2','-framerate','24', '-i', tiff ,output_dirname +  '/image/dpx_files' '/' + tiff[:-4] + 'dpx']
            print cmd
            subprocess.call(cmd)
        parent_basename =  os.path.basename(output_dirname)
        manifest_textfile = os.path.dirname(output_dirname) + '/' +  parent_basename + '_manifest.md5'
        other = make_framemd5(output_dirname + '/image/dpx_files', 'dpx')
        other_textfile = other[1]
        print source_textfile
        print other_textfile
        diff_textfiles(source_textfile, other_textfile)
        make_manifest(dirname, os.path.basename(output_dirname), manifest_textfile)
        print time
        print datetime.datetime.now()
