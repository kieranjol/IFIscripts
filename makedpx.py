#!/usr/bin/env python

import subprocess
import sys
import os
from glob import glob
from ififuncs import diff_textfiles
from ififuncs import make_manifest
import datetime
import time
import csv
from ififuncs import create_csv
from ififuncs import append_csv
from ififuncs import send_gmail


def set_environment(logfile):
    env_dict = os.environ.copy()
    # https://github.com/imdn/scripts/blob/0dd89a002d38d1ff6c938d6f70764e6dd8815fdd/ffmpy.py#L272
    env_dict['FFREPORT'] = 'file={}:level=32'.format(logfile)
    return env_dict
    
def make_framemd5(directory, container, log_filename_alteration):
    os.chdir(directory)
    
    images = glob('*.%s' % container)
    global output_parent_directory
    output_parent_directory = config[1].rstrip()
    numberless_filename = images[0].split("_")[0:-1]
    ffmpeg_friendly_name = ''
    counter = 0
    while  counter <len(numberless_filename) :
        ffmpeg_friendly_name += numberless_filename[counter] + '_'
        counter += 1
    output_dirname = output_parent_directory + '/' + ffmpeg_friendly_name + 'dpx_transcodes'
    try:
        os.makedirs(output_dirname + '/image')
        os.makedirs(output_dirname + '/image/logs')
        os.makedirs(output_dirname + '/image/md5')
        os.makedirs(output_dirname + '/image/dpx_files')
        os.makedirs(output_dirname + '/image/xml_files')
     
    except: OSError

    output = output_dirname + '/image/md5/%s%s.framemd5' % (ffmpeg_friendly_name,container)
    logfile = output_dirname + '/image/logs/%s%s.log' % (ffmpeg_friendly_name, log_filename_alteration)
    env_dict = set_environment(logfile)
    image_seq_without_container = ffmpeg_friendly_name
    ffmpeg_friendly_name += "%06d." + '%s' % container
    framemd5 = ['ffmpeg','-report','-f','image2', '-i', ffmpeg_friendly_name,'-f','framemd5',output]
    print framemd5
    subprocess.call(framemd5, env=env_dict)   
    info = [output_dirname, output, image_seq_without_container]
    return info
    
def remove_bad_files(root_dir):
    rm_these = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
    for root, dirs, files in os.walk(root_dir):
        for name in files:
            path = os.path.join(root, name)
            for i in rm_these:
                if name == i:
                    print '***********************' + 'removing: ' + path   
                    os.remove(path)
csv_report_filename = os.path.expanduser("~/Desktop/") + 'dpx_transcode_report' + time.strftime("_%Y_%m_%dT%H_%M_%S") + '.csv'
dpxconfig = os.path.expanduser("~/Desktop/") + 'make_dpx_config.txt'
with open(dpxconfig, 'r') as fo:
    config = fo.readlines()
emails = config[0].split(',')

source_directory = sys.argv[1]

create_csv(csv_report_filename, ('Sequence Name', 'Lossless?', 'Start time', 'Finish Time'))
for root,dirnames,filenames in os.walk(source_directory):
    if "tiff_scans"  in dirnames:
        source_directory = root + '/tiff_scans'
        remove_bad_files(source_directory)
        source_parent_dir    = os.path.dirname(source_directory)
        normpath             = os.path.normpath(source_directory) 
        relative_path        = normpath.split(os.sep)[-1]
        split_path           = os.path.split(os.path.basename(source_directory))[1]
        start = datetime.datetime.now()
        source_manifest = source_parent_dir + '/%s_manifest.md5' % relative_path
        make_manifest(os.path.dirname(source_directory), os.path.basename(source_directory), source_manifest)
        
        info = make_framemd5(source_directory, 'tiff', 'tiff_framemd5')
        output_dirname = info[0]  
        source_textfile = info[1]
        image_seq_without_container = info[2]
        images = glob('*.tiff')
        tiff_filename = image_seq_without_container + "%06d.tiff" 
        dpx_filename = image_seq_without_container + "%06d.dpx" 
        tiff2dpx = ['ffmpegnometadata','-f','image2','-framerate','24', '-i', tiff_filename ,output_dirname +  '/image/dpx_files' '/' + dpx_filename]
        print tiff2dpx
        subprocess.call(tiff2dpx)
        parent_basename =  os.path.basename(output_dirname)
        manifest_textfile = os.path.dirname(output_dirname) + '/' +  parent_basename + '_manifest.md5'
        other = make_framemd5(output_dirname + '/image/dpx_files', 'dpx', 'dpx_framemd5')
        other_textfile = other[1]
        judgement = diff_textfiles(source_textfile, other_textfile)
        make_manifest(output_parent_directory, os.path.basename(output_dirname), manifest_textfile)
        finish = datetime.datetime.now()
        append_csv(csv_report_filename, (parent_basename,judgement, start, finish))
#send_gmail(emails, csv_report_filename, 'makedpx completed', 'Hi,\n Please the attached log for details of the makedpx job, \nSincerely yours,\nIFIROBOT', config[2].rstrip(), config[3].rstrip())