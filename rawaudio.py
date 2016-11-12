#!/usr/bin/env python
import subprocess
import argparse
import sys
import os
import hashlib
import shutil
import uuid
import time
import uuid
from glob import glob
from premis import make_premis
from premis import write_premis
from premis import make_agent
from premis import make_event
from premis import setup_xml
from premis import create_representation


'''
1. Accepts the wav as input
2. in /audio subfolder, the only files should be the audio.wav and the log.txt
3. workhorse copy sent to desktop
4. mediainfo in /xml_files
5. framemd5 in /md5
6. manifest in audio directory
7. log gets moved to /log
8. audio gets moved to aeo_raw_extract_wav
9. To DO - Premis/revtmd.

usage = python rawaudio.py audio.wav

'''
def set_environment(logfile):
    env_dict = os.environ.copy()
    # https://github.com/imdn/scripts/blob/0dd89a002d38d1ff6c938d6f70764e6dd8815fdd/ffmpy.py#L272
    env_dict['FFREPORT'] = 'file={}:level=48'.format(logfile)
    return env_dict

def make_mediainfo(xmlfilename, xmlvariable, inputfilename):
    with open(xmlfilename, "w+") as fo:
        xmlvariable = subprocess.check_output(['mediainfo',
                        '-f',
                        '--language=raw', # Use verbose output.
                        '--output=XML',
                        inputfilename])       #input filename
        fo.write(xmlvariable)

def remove_bad_files(root_dir):
    rm_these = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
    for root, dirs, files in os.walk(root_dir):
        for name in files:
            path = os.path.join(root, name)
            for i in rm_these:
                if name == i:
                    print '***********************' + 'removing: ' + path
                    os.remove(path)

def make_manifest(relative_manifest_path, manifest_textfile):
    print relative_manifest_path
    os.chdir(relative_manifest_path)
    manifest_generator = subprocess.check_output(['md5deep', '-ler', '.'])
    manifest_list = manifest_generator.splitlines()
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list,  key=lambda x:(x[34:])) 
    with open(manifest_textfile,"wb") as fo:
        for i in manifest_list:
            fo.write(i + '\n')


def get_user():
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
    return user


def make_parser():
    parser = argparse.ArgumentParser(description='Workflow specific metadata generator.'
                                'Accepts a WAV file as input.'
                                ' Designed for a specific IFI Irish Film Archive workflow. '
                                'Written by Kieran O\'Leary.')
    parser.add_argument('input', help='file path of parent directory')
    parser.add_argument('-v', action='store_true', help='verbose mode - Display full ffmpeg information')
    return parser

total_process = 6
parser = make_parser()
args = parser.parse_args()
input = args.input
if not input.endswith('.wav'):
   print 'This script accepts a WAV file contained in a very specific folder path as input.\nExiting'
   sys.exit()
user = get_user()
desktop_dir = os.path.expanduser("~/Desktop/%s") % os.path.basename(input)
parent_dir = os.path.dirname(input)
root_dir = os.path.dirname(os.path.dirname(parent_dir))
os.chdir(root_dir)
metadata_dir = root_dir + '/metadata/audio'
logs_dir = 'logs/audio'

aeo_raw_extract_wav_dir = root_dir + '/objects/audio'
framemd5 = metadata_dir + '/' + os.path.basename(input) +'.framemd5'
logfile = logs_dir + '/%s_framemd5.log' % os.path.basename(input)
process_counter = 1
print 'Process %d of %d - Logfile of framemd5 ffmpeg process located in %s/%s' % (process_counter,total_process, root_dir, logfile)
process_counter += 1
normpath = os.path.normpath(root_dir)
relative_path = normpath.split(os.sep)[-1]
manifest =  root_dir + '/audio_manifest.md5' 

filenoext = os.path.splitext(input)[0]
inputxml =  inputxml  = "%s/%s_mediainfo.xml" % (metadata_dir,os.path.basename(input))
make_mediainfo(inputxml,'mediaxmlinput',input)
env_dict = set_environment(logfile)
ffmpegcmd = ['ffmpeg',    # Create decoded md5 checksums for every frame of the ffv1 output
                        '-i',input,
                        '-report',]
if not args.v:
    ffmpegcmd += ['-v', '0']
ffmpegcmd +=    ['-f','framemd5',
                        framemd5 ]
print 'Process %d of %d - Generating framemd5 values for source WAV' % (process_counter,total_process)
process_counter += 1
subprocess.call(ffmpegcmd,env=env_dict)
print 'Process %d of %d - Creating a workhorse copy of source WAV on Desktop' % (process_counter,total_process)
process_counter += 1
shutil.copy(input, desktop_dir)
print 'Process %d of %d - Checking if any unwanted files should be removed, eg .DS_Stores or desktop.ini/thumbs.db' % (process_counter,total_process)
process_counter += 1
remove_bad_files(root_dir)
os.chdir(parent_dir)  
log_files =  glob('*.txt')                
for i in log_files:
   
        shutil.move(i, '%s/%s' % (logs_dir,i))             

print 'Process %d of %d - Generating manifest' % (process_counter,total_process)
process_counter += 1
make_manifest(root_dir,manifest)


'''
BEGIN PREMIS
'''
source_directory = root_dir + '/objects/image'
print 'Process %d of %d - Generating PREMIS XML file' % (process_counter,total_process)
process_counter += 1
representation_uuid = str(uuid.uuid4())
premisxml, premis_namespace, doc, premis = setup_xml(source_directory)
split_list = os.path.basename(root_dir).split('_')
audio_items = {"workflow":"raw audio","oe":split_list[0], "filmographic":split_list[1], "sourceAccession":split_list[2], "interventions":['placeholder'], "prepList":['placeholder'], "user":'Brian Cash'}
image_items = {"workflow":"scanning","oe":split_list[0], "filmographic":split_list[1], "sourceAccession":split_list[2], "interventions":['placeholder'], "prepList":['placeholder'], "user":user}
linking_representation_uuids = []
xml_info    = make_premis(aeo_raw_extract_wav_dir, audio_items, premis, premis_namespace, premisxml, representation_uuid, 'nosequence')
xml_info    = make_premis(source_directory, image_items, premis, premis_namespace,premisxml, representation_uuid, 'sequence')
linking_representation_uuids.append(xml_info[2])
linking_representation_uuids.append(xml_info[2])
linking_representation_uuids.append(image_items['sourceAccession'])
create_representation(premisxml, premis_namespace, doc, premis, audio_items,linking_representation_uuids, representation_uuid )
doc         = xml_info[0]
premisxml   = xml_info[1]
premis = doc.getroot()
extract_uuid                                = str(uuid.uuid4())
capture_received_uuid                       = str(uuid.uuid4())
audio_premis_checksum_uuid                  = str(uuid.uuid4())
audio_framemd5_uuid                         = str(uuid.uuid4())
capture_uuid                                = str(uuid.uuid4())
capture_received_uuid                       = str(uuid.uuid4())
premis_checksum_uuid                        = str(uuid.uuid4())
framemd5_uuid                               = str(uuid.uuid4())
aeolightAgent                               = make_agent(premis,capture_uuid, '50602139-104a-46ef-a53c-04fcb538723a')
hashlibAgent                                = make_agent(premis,capture_uuid, '9430725d-7523-4071-9063-e8a6ac4f84c4')
operatorAgent                               = make_agent(premis,capture_uuid,audio_items['user'])
macMiniTelecineMachineAgent                 = make_agent(premis,premis_checksum_uuid, '230d72da-07e7-4a79-96ca-998b9f7a3e41')
macMiniTelecineOSAgent                      = make_agent(premis,premis_checksum_uuid, '9486b779-907c-4cc4-802c-22e07dc1242f')
ffmpegAgent                                 = make_agent(premis,framemd5_uuid , 'ee83e19e-cdb1-4d83-91fb-7faf7eff738e')
scannerAgent                                = make_agent(premis,capture_uuid, '1f4c1369-e9d1-425b-a810-6db1150955ba')
scannerPCAgent                              = make_agent(premis,capture_uuid, 'ca731b64-638f-4dc3-9d27-0fc14387e38c')
scannerLinuxAgent                           = make_agent(premis,capture_uuid, 'b22baa5c-8160-427d-9e2f-b62a7263439d')
hashlibAgent                                = make_agent(premis,capture_uuid, '9430725d-7523-4071-9063-e8a6ac4f84c4')
operatorAgent                               = make_agent(premis,capture_uuid,image_items['user'])
transcoderMachine                           = make_agent(premis,capture_received_uuid, '946e5d40-a07f-47d1-9637-def5cb7854ba')
transcoderMachineOS                         = make_agent(premis,capture_received_uuid, '192f61b1-8130-4236-a827-a194a20557fe')
make_event(premis, 'creation', 'PCM WAV file extracted from overscanned image area of source TIFF files', [aeolightAgent, operatorAgent, macMiniTelecineMachineAgent, macMiniTelecineOSAgent], extract_uuid,xml_info[2])
make_event(premis, 'message digest calculation', '', [hashlibAgent, operatorAgent,macMiniTelecineMachineAgent, macMiniTelecineOSAgent], audio_premis_checksum_uuid,xml_info[2])
make_event(premis, 'message digest calculation', 'Frame level checksums of audio', [ffmpegAgent, operatorAgent,macMiniTelecineMachineAgent, macMiniTelecineOSAgent], audio_framemd5_uuid,xml_info[2] )
make_event(premis, 'creation', 'Film scanned to 12-bit RAW Bayer format and transcoded internally by ca731b64-638f-4dc3-9d27-0fc14387e38c to 16-bit RGB linear TIFF', [scannerAgent, operatorAgent, scannerPCAgent, scannerLinuxAgent], capture_uuid,xml_info[2])
make_event(premis, 'creation', 'TIFF image sequence is received via ethernet from ca731b64-638f-4dc3-9d27-0fc14387e38c and written to Disk', [transcoderMachine,transcoderMachineOS, operatorAgent], capture_received_uuid,xml_info[2])
make_event(premis, 'message digest calculation', '', [hashlibAgent, operatorAgent,macMiniTelecineMachineAgent, macMiniTelecineOSAgent], premis_checksum_uuid,xml_info[2])
make_event(premis, 'message digest calculation', 'Frame level checksums of image', [ffmpegAgent, operatorAgent,macMiniTelecineMachineAgent, macMiniTelecineOSAgent], framemd5_uuid,xml_info[2] )
write_premis(doc, premisxml)

