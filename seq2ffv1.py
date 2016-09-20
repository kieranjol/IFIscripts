#!/usr/bin/env python

import subprocess
import sys
import os
from glob import glob
from ififuncs import diff_textfiles
from ififuncs import make_manifest
from ififuncs import get_mediainfo
import datetime
import time
import csv
from ififuncs import create_csv
from ififuncs import append_csv
from ififuncs import send_gmail
import itertools

def read_non_comment_lines(infile):
    for lineno, line in enumerate(infile):
        #if line[:1] != "#":
            yield lineno, line
def set_environment(logfile):
    env_dict = os.environ.copy()
    # https://github.com/imdn/scripts/blob/0dd89a002d38d1ff6c938d6f70764e6dd8815fdd/ffmpy.py#L272
    env_dict['FFREPORT'] = 'file={}:level=48'.format(logfile)
    return env_dict


def make_framemd5(directory, log_filename_alteration):
    os.chdir(directory)
    
    tiff_check = glob('*.tiff')
    dpx_check = glob('*.dpx')
    if len(dpx_check) > 0:
        images = dpx_check
        
    elif len(tiff_check) > 0:
        images = tiff_check
    else:
        print 'no images found'
        return 'none'
        
    images.sort()
    sequence_length = len(images)
    global output_parent_directory
    if '864000' in images[0]:
        start_number = '864000'
    elif len(images[0].split("_")[-1].split(".")) > 2:
        start_number = images[0].split("_")[-1].split(".")[1]
        
    else:
        
        start_number = images[0].split("_")[-1].split(".")[0]
    container = images[0].split(".")[-1]
    output_parent_directory = config[1].rstrip()
    if len(images[0].split("_")[-1].split(".")) > 2:
        numberless_filename = images[0].split(".")[0].split("_")
    else:
        numberless_filename = images[0].split("_")[0:-1]
    
    ffmpeg_friendly_name = ''
    counter = 0
    while  counter <len(numberless_filename) :
        ffmpeg_friendly_name += numberless_filename[counter] + '_'
        counter += 1
    
    if start_number == '864000':
        output_dirname = output_parent_directory + '/' + os.path.basename(directory) + time.strftime("%Y_%m_%dT%H_%M_%S")
        basename = os.path.basename(directory)
    else:        
        output_dirname = output_parent_directory + '/' + ffmpeg_friendly_name + time.strftime("%Y_%m_%dT%H_%M_%S")
        basename = ffmpeg_friendly_name
    try:
        os.makedirs(output_dirname)
        os.makedirs(output_dirname + '/logs')
        os.makedirs(output_dirname + '/md5')
        os.makedirs(output_dirname + '/video')
        os.makedirs(output_dirname + '/xml_files')
     
    except: OSError

    output = output_dirname + '/md5/%ssource.framemd5' % (basename)
    logfile = output_dirname + '/logs/%s%s.log' % (basename, log_filename_alteration)
    env_dict = set_environment(logfile)
    image_seq_without_container = ffmpeg_friendly_name
    start_number_length = len(start_number)
    number_regex = "%0" + str(start_number_length) + 'd.'
    if len(images[0].split("_")[-1].split(".")) > 2:
        image_seq_without_container = ffmpeg_friendly_name[:-1] + ffmpeg_friendly_name[-1].replace('_', '.')
        ffmpeg_friendly_name = image_seq_without_container
        
    ffmpeg_friendly_name += number_regex + '%s' % container
    
    
    framemd5 = ['ffmpeg','-start_number', start_number, '-report','-f','image2','-framerate','24', '-i', ffmpeg_friendly_name,'-f','framemd5',output]
    print framemd5
    subprocess.call(framemd5, env=env_dict)   
    info = [output_dirname, output, image_seq_without_container, start_number, container, ffmpeg_friendly_name, number_regex, sequence_length]
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

create_csv(csv_report_filename, ('Sequence Name', 'Lossless?', 'Start time', 'Finish Time', 'Transcode Start Time', 'Transcode Finish Time','Transcode Time', 'Frame Count', 'Encode FPS','Sequence Size', 'FFV1 Size','Pixel Format', 'Sequence Type','Width','Height','Compression Ratio'))
for root,dirnames,filenames in os.walk(source_directory):
        #if "tiff_scans"  in dirnames:
        source_directory = root # + '/tiff_scans'
        total_size = 0
        #remove_bad_files(source_directory)
        source_parent_dir    = os.path.dirname(source_directory)
        normpath             = os.path.normpath(source_directory) 
        relative_path        = normpath.split(os.sep)[-1]
        split_path           = os.path.split(os.path.basename(source_directory))[1]
        start = datetime.datetime.now()
        source_manifest = source_parent_dir + '/%s_manifest.md5' % relative_path
        #make_manifest(os.path.dirname(source_directory), os.path.basename(source_directory), source_manifest)
        info = make_framemd5(source_directory, 'dpx_framemd5')
        if info == 'none':
            continue
        for files in filenames:
            total_size += os.path.getsize(os.path.join(root,files))
        output_dirname              = info[0]  
        source_textfile             = info[1]
        image_seq_without_container = info[2]
        start_number                = info[3]
        container                   = info[4]
        dpx_filename                = info[5] 
        sequence_length             = info[7]
        output_filename             = image_seq_without_container[:-1] 
        print output_filename


        logfile = output_dirname + '/logs/%s_ffv1_transcode.log' % output_filename
        env_dict = set_environment(logfile)
        pix_fmt = subprocess.check_output(['ffprobe',
                                                '-start_number', start_number,
                                                '-i', os.path.abspath(dpx_filename),
                                                '-v', 'error',
                                                '-select_streams', 'v:0',
                                                '-show_entries',
                                                'stream=pix_fmt',
                                                '-of', 'default=noprint_wrappers=1:nokey=1',
                                                ]).rstrip()
        
        ffv12dpx = ['ffmpeg','-report','-f','image2','-framerate','24', '-start_number', start_number, '-i', os.path.abspath(dpx_filename) ,'-strict', '-2','-c:v','ffv1','-level', '3', '-pix_fmt', pix_fmt ,output_dirname +  '/video/' + output_filename + '.mkv']
        print ffv12dpx
        transcode_start = datetime.datetime.now()
        transcode_start_machine_readable = time.time()
        subprocess.call(ffv12dpx,env=env_dict)
        transcode_finish = datetime.datetime.now()
        transcode_finish_machine_readable = time.time()
        transcode_time = transcode_finish_machine_readable - transcode_start_machine_readable
        parent_basename   =  os.path.basename(output_dirname)
        manifest_textfile = os.path.dirname(output_dirname) + '/' +  parent_basename + '_manifest.md5'
        ffv1_path         = output_dirname +  '/video/'  + output_filename + '.mkv'
        width =  get_mediainfo('duration', '--inform=Video;%Width%', ffv1_path)
        height =  get_mediainfo('duration', '--inform=Video;%Height%', ffv1_path )
        ffv1_md5          = output_dirname +  '/md5/' + image_seq_without_container + 'ffv1.framemd5'
        ffv1_fmd5_cmd = ['ffmpeg','-i', ffv1_path, '-pix_fmt', pix_fmt,'-f', 'framemd5', ffv1_md5]
        ffv1_fmd5_logfile = output_dirname + '/logs/%s_ffv1_framemd5.log' % output_filename
        ffv1_fmd5_env_dict = set_environment(ffv1_fmd5_logfile)
        subprocess.call(ffv1_fmd5_cmd,env=ffv1_fmd5_env_dict)
        finish = datetime.datetime.now()
        ffv1_size = os.path.getsize(ffv1_path)
        comp_ratio =  float(total_size) / float(os.path.getsize(ffv1_path))
        judgement = diff_textfiles(source_textfile, ffv1_md5)
        fps = float(sequence_length) / float(transcode_time)
        #other_textfile = other[1]
        checksum_mismatches = []
        with open(source_textfile) as f1:
            with open(ffv1_md5) as f2:
                for (lineno1, line1), (lineno2, line2) in itertools.izip(
                               read_non_comment_lines(f1), read_non_comment_lines(f2)):
                    if line1 != line2:
                        if 'sar' in line1:
                            checksum_mismatches = ['sar']
                        else:
                            checksum_mismatches.append(1)
        if len(checksum_mismatches) == 0:
            print 'LOSSLESS'
            append_csv(csv_report_filename, (parent_basename,judgement, start, finish,transcode_start, transcode_finish,transcode_time, sequence_length, fps, total_size, ffv1_size, pix_fmt, container, width, height,comp_ratio))

        elif len(checksum_mismatches) == 1:
            if checksum_mismatches[0] == 'sar':
                print 'Image content is lossless, Pixel Aspect Ratio has been altered'
                append_csv(csv_report_filename, (parent_basename,'LOSSLESS - different PAR',start, finish,transcode_start, transcode_finish,transcode_time,sequence_length, fps,total_size, ffv1_size, pix_fmt, container,width, height,comp_ratio))
        elif len(checksum_mismatches) > 1:
            print 'NOT LOSSLESS'     
            print csv_report_filename
            append_csv(csv_report_filename, (parent_basename,judgement, start, finish,transcode_start, transcode_finish,transcode_time,sequence_length, fps,total_size, ffv1_size, pix_fmt,container, width, height,comp_ratio))
        #make_manifest(output_parent_directory, os.path.basename(output_dirname), manifest_textfile)
        
        
#send_gmail(emails, csv_report_filename, 'makedpx completed', 'Hi,\n Please the attached log for details of the makedpx job, \nSincerely yours,\nIFIROBOT', config[2].rstrip(), config[3].rstrip())
