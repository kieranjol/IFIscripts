#!/usr/bin/env python

import subprocess
import sys
import os
import shutil
from glob import glob
from ififuncs import diff_textfiles
from ififuncs import make_manifest
from ififuncs import generate_log
import datetime
import time
import csv
import uuid
from ififuncs import create_csv
from ififuncs import append_csv
from ififuncs import send_gmail
from premis import make_premis
from premis import write_premis
from premis import make_agent
from premis import make_event


'''''
Events:
md5 manifest created of source
framemd5 of source
tiff2dpx
framemd5 output
manifest of output
'''

def set_environment(logfile):
    env_dict = os.environ.copy()
    # https://github.com/imdn/scripts/blob/0dd89a002d38d1ff6c938d6f70764e6dd8815fdd/ffmpy.py#L272
    env_dict['FFREPORT'] = 'file={}:level=48'.format(logfile)
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
def file_check(dir2check):
    os.chdir(dir2check)
    tiff_check = glob('*.tiff')
    dpx_check = glob('*.dpx')
    if len(dpx_check) > 0:
        print 'DPX sequence, not TIFF. Not processing'
        return 'DPX'
    elif len(tiff_check) > 0:
        return 'TIFF'
    else:
        print 'no images found'
        return 'none'    
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
permission = ''
all_files = sys.argv[1:]
if not permission == 'y' or permission == 'Y':
    print '\n\n**** All TIFF sequences within these directories will be converted to DPX.\n'
    for i in all_files:
        print i
    permission =  raw_input('\n**** These are the directories that wil be turned into DPX. \n**** If this looks ok, please press Y, otherwise, type N\n' )
    while permission not in ('Y','y','N','n'):
        permission =  raw_input('\n**** These are the directories that wil be turned into DPX. \n**** If this looks ok, please press Y, otherwise, type N\n')
    if permission == 'n' or permission == 'N':
        print 'Exiting at your command- Cheerio for now'
        sys.exit()
    elif permission =='y' or permission == 'Y':
        print 'Ok so!' 
user = ''
if not user == '1' or user == '2':
    user =  raw_input('\n\n**** Who did the actual scanning?\nPress 1 or 2\n\n1. Brian Cash\n2. Gavin Martin\n' )
    while user not in ('1','2'):
        user =  raw_input('\n\n**** Who did the actual scanning?\nPress 1 or 2\n\n1. Brian Cash\n2. Gavin Martin\n')
if user == '1':
    user = 'Brian Cash'
    print 'Hi Brian, I promise not to leave any water bottles in the telecine room from now on '
    time.sleep(1)
elif user == '2':
    user = 'Gavin Martin'
    print 'Hi Gavin, Have you renewed your subscription to American Cinematographer?'
    time.sleep(1)
print user

create_csv(csv_report_filename, ('Sequence Name', 'Lossless?', 'Start time', 'Finish Time'))
for source_directory in all_files:
    for root,dirnames,filenames in os.walk(source_directory):
            source_directory = root
            if not file_check(source_directory) == 'TIFF':
                append_csv(csv_report_filename, (source_directory,'EMPTY DIRECTORY - SKIPPED', 'n/a', 'n/a'))
                continue

            root_dir = os.path.dirname(os.path.dirname(root))
            general_log = root_dir + '/logs/image/%s_image_log.log' % os.path.basename(root_dir)
            generate_log(general_log, 'Input = %s' % root)
            remove_bad_files(source_directory)
            source_parent_dir           = os.path.dirname(source_directory)
            normpath                    = os.path.normpath(source_directory)
            relative_path               = normpath.split(os.sep)[-1]
            split_path                  = os.path.split(os.path.basename(source_directory))[1]
            start                       = datetime.datetime.now()
            source_manifest             = root_dir + '/%s_manifest.md5' % relative_path
            generate_log(general_log, 'Generating source manifest via md5deep and storing as  %s' % source_manifest)
            make_manifest(root_dir, root_dir, source_manifest)
            info                        = make_framemd5(source_directory, 'tiff', 'tiff_framemd5')
            output_dirname              = info[0]
            source_textfile             = info[1]
            fmd5copy                    = root_dir + '/metadata/image'
            shutil.copy(source_textfile,fmd5copy )
            image_seq_without_container = info[2]
            tiff_filename               = image_seq_without_container + "%06d.tiff"
            dpx_filename                = image_seq_without_container + "%06d.dpx"
            logfile                     = output_dirname + '/image/logs/%sdpx_transcode.log' % image_seq_without_container
            env_dict                    = set_environment(logfile)
            generate_log(general_log, 'Starting TIFF to DPX transcode')
            tiff2dpx                    = ['ffmpegnometadata','-report','-f','image2','-framerate','24', '-i', tiff_filename ,output_dirname +  '/image/dpx_files' '/' + dpx_filename]
            print tiff2dpx

            subprocess.call(tiff2dpx,env=env_dict)
            generate_log(general_log, 'TIFF to DPX transcode complete')
            parent_basename =  os.path.basename(output_dirname)
            manifest_textfile = os.path.dirname(output_dirname) + '/' +  parent_basename + '_manifest.md5'
            generate_log(general_log, 'Generating destination manifest via md5deep and storing as  %s' % manifest_textfile)
            other = make_framemd5(output_dirname + '/image/dpx_files', 'dpx', 'dpx_framemd5')
            other_textfile = other[1]
            judgement = diff_textfiles(source_textfile, other_textfile)
            generate_log(general_log, 'Outcome of transcode was:  %s' % judgement)
            make_manifest(output_parent_directory, os.path.basename(output_dirname), manifest_textfile)
            finish = datetime.datetime.now()
            split_list = os.path.basename(os.path.dirname(source_parent_dir)).split('_')
            items = {"workflow":"scanning","oe":split_list[0], "filmographic":split_list[1], "sourceAccession":split_list[2], "interventions":['placeholder'], "prepList":['placeholder'], "user":user}
            xml_info    = make_premis(source_directory, items)
            doc         = xml_info[0]
            premisxml   = xml_info[1]
            premis = doc.getroot()
            capture_uuid                                = str(uuid.uuid4())
            capture_received_uuid                       = str(uuid.uuid4())
            premis_checksum_uuid                        = str(uuid.uuid4())
            framemd5_uuid                               = str(uuid.uuid4())
            scannerAgent                                = make_agent(premis,capture_uuid, '1f4c1369-e9d1-425b-a810-6db1150955ba')
            scannerPCAgent                              = make_agent(premis,capture_uuid, 'ca731b64-638f-4dc3-9d27-0fc14387e38c')
            scannerLinuxAgent                           = make_agent(premis,capture_uuid, 'b22baa5c-8160-427d-9e2f-b62a7263439d')
            hashlibAgent                                = make_agent(premis,capture_uuid, '9430725d-7523-4071-9063-e8a6ac4f84c4')
            operatorAgent                               = make_agent(premis,capture_uuid,items['user'])
            transcoderMachine                           = make_agent(premis,capture_received_uuid, '946e5d40-a07f-47d1-9637-def5cb7854ba')
            transcoderMachineOS                         = make_agent(premis,capture_received_uuid, '192f61b1-8130-4236-a827-a194a20557fe')
            macMiniTelecineMachineAgent                 = make_agent(premis,premis_checksum_uuid, '230d72da-07e7-4a79-96ca-998b9f7a3e41')
            macMiniTelecineOSAgent                      = make_agent(premis,premis_checksum_uuid, 'a3bc371f-11fa-4319-a656-1e53c2527552')
            ffmpegAgent                                 = make_agent(premis,framemd5_uuid , 'ee83e19e-cdb1-4d83-91fb-7faf7eff738e')

            make_event(premis, 'creation', 'Film scanned to 12-bit RAW Bayer format and transcoded internally by ca731b64-638f-4dc3-9d27-0fc14387e38c to 16-bit RGB linear TIFF', [scannerAgent, operatorAgent, scannerPCAgent, scannerLinuxAgent], capture_uuid,xml_info[2])
            make_event(premis, 'creation', 'TIFF image sequence is received via ethernet from ca731b64-638f-4dc3-9d27-0fc14387e38c and written to Disk', [transcoderMachine,transcoderMachineOS, operatorAgent], capture_received_uuid,xml_info[2])
            make_event(premis, 'message digest calculation', '', [hashlibAgent, operatorAgent,macMiniTelecineMachineAgent, macMiniTelecineOSAgent], premis_checksum_uuid,xml_info[2])
            make_event(premis, 'message digest calculation', 'Frame level checksums', [ffmpegAgent, operatorAgent,macMiniTelecineMachineAgent, macMiniTelecineOSAgent], framemd5_uuid,xml_info[2] )
            write_premis(doc, premisxml)
            print premisxml
            append_csv(csv_report_filename, (parent_basename,judgement, start, finish))
    #send_gmail(emails, csv_report_filename, 'makedpx completed', 'Hi,\n Please the attached log for details of the makedpx job, \nSincerely yours,\nIFIROBOT', config[2].rstrip(), config[3].rstrip())