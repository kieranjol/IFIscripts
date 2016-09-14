#!/usr/bin/env python

import subprocess
import sys
import os
from glob import glob
from ififuncs import diff_textfiles
import datetime
import time
import csv
from ififuncs import create_csv
from ififuncs import append_csv
from ififuncs import send_gmail

def make_manifest(relative_manifest_path, manifest_textfile):
    os.chdir(relative_manifest_path)
    manifest_generator = subprocess.check_output(['md5deep', '-ler', '.'])
    manifest_list = manifest_generator.splitlines()
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list,  key=lambda x:(x[34:])) 
    with open(manifest_textfile,"wb") as fo:
        for i in manifest_list:
            fo.write(i + '\n')
            
            
def set_environment(logfile):
    env_dict = os.environ.copy()
    # https://github.com/imdn/scripts/blob/0dd89a002d38d1ff6c938d6f70764e6dd8815fdd/ffmpy.py#L272
    env_dict['FFREPORT'] = 'file={}:level=48'.format(logfile)
    return env_dict
    
    
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
        numberless_filename = images[0].split(".")[0].split("_")   
    else:
        numberless_filename = images[0].split("_")[0:-1]
    ffmpeg_friendly_name = ''
    counter = 0
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

source_directory = sys.argv[1]
create_csv(csv_report_filename, ('Sequence Name', 'Lossless?', 'Start time', 'Finish Time', 'Sequence Size', 'FFV1 Size', 'Compression Ratio'))
for root,dirnames,filenames in os.walk(source_directory):
        #if "tiff_scans"  in dirnames:
        source_directory = root# + '/tiff_scans'
        total_size = 0
        remove_bad_files(source_directory)
        source_parent_dir    = os.path.dirname(source_directory)
        normpath             = os.path.normpath(source_directory) 
        relative_path        = normpath.split(os.sep)[-1]
        split_path           = os.path.split(os.path.basename(source_directory))[1]
        start = datetime.datetime.now()
        source_manifest = source_parent_dir + '/' + os.path.basename(os.path.dirname(root)) + time.strftime("%Y%m%dT%H_%M_%S") +  '_manifest.md5'
        info = get_filenames(source_directory, 'dpx_framemd5')
        if info == 'none':
            continue
        for files in filenames:
            total_size += os.path.getsize(os.path.join(root,files))
        
        image_seq_without_container = info[0]
        start_number                = info[1]
        container                   = info[2]
        start_number_length = len(start_number)
        number_regex = "%0" + str(start_number_length) + 'd.'
        audio_dir            = source_parent_dir + '/audio'
        logs_dir            = source_parent_dir + '/logs'
        mezzanine_dir            = source_parent_dir + '/mezzanine'
        if not os.path.isdir(mezzanine_dir):
            os.makedirs(mezzanine_dir)
        if not os.path.isdir(logs_dir):
            os.makedirs(logs_dir)
        os.chdir(audio_dir)
        audio_file_list = glob('*.wav')
        audio_file = os.path.join(audio_dir,audio_file_list[0])
        dpx_filename                = image_seq_without_container + number_regex + container
        logfile = logs_dir + '/%s_prores.log' % os.path.basename(os.path.dirname(root))
        env_dict = set_environment(logfile)
        seq2prores= ['ffmpeg','-report','-f','image2','-framerate','24', '-start_number', start_number, '-i', root + '/' + dpx_filename ,'-i', audio_file,'-c:v','prores','-profile:v', '3','-c:a','copy', mezzanine_dir + '/' + os.path.basename(os.path.dirname(root)) + '.mov']
        print seq2prores
        subprocess.call(seq2prores,env=env_dict)
        make_manifest(source_parent_dir, source_manifest)
        finish = datetime.datetime.now()
        #append_csv(csv_report_filename, (parent_basename,judgement, start, finish,total_size, ffv1_size, comp_ratio))
        
#send_gmail(emails, csv_report_filename, 'makedpx completed', 'Hi,\n Please the attached log for details of the makedpx job, \nSincerely yours,\nIFIROBOT', config[2].rstrip(), config[3].rstrip())
