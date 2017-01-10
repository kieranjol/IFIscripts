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
from ififuncs import hashlib_manifest
from ififuncs import get_date_modified
from premis import make_premis
from premis import write_premis
from premis import make_agent
from premis import make_event
from premis import setup_xml
from premis import create_representation
from premis import create_intellectual_entity


'''
1. Accepts directory as input
2. Looks for the wav file
3. in /audio subfolder, the only files should be the audio.wav and the log.txt
4. workhorse wav copy sent to desktop
5. premis xml created
6. audio framemd5 gets moved to /metadata/audio
7. audio mediainfo gets moved to /metadata/audio
8. log gets moved to /logs/audio
9. manifest for whole SIP in directory


usage = python rawbatch.py directory

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


def get_user():
    user = ''
    if not user == '1' or user == '2':
        user =  raw_input('\n\n**** Who did the actual scanning?\nPress 1 or 2\n\n1. Brian Cash\n2. Gavin Martin\n' )
        while user not in ('1','2'):
            user =  raw_input('\n\n**** Who did the actual scanning?\nPress 1 or 2\n\n1. Brian Cash\n2. Gavin Martin\n')
    if user == '1':
        user = 'Brian Cash'
        print 'Hi Brian, I believe that we can move on from that water bottle message as I have changed my terrible ways'
        time.sleep(1)
    elif user == '2':
        user = 'Gavin Martin'
        print 'Hi Gavin, Have you renewed your subscription to American Cinematographer?'
        time.sleep(1)
    return user

def get_aeolight_workstation():
    aeolight_station = ''
    if not aeolight_station == '1' or aeolight_station == '2':
        aeolight_station =  raw_input('\n\n**** Where was AEO-Light run?\nPress 1 or 2\n\n1. telecine room mac\n2. CA machine\n' )
        while aeolight_station not in ('1','2'):
            aeolight_station =  raw_input('\n\n**** Where was AEO-Light run?\nPress 1 or 2\n\n1. telecine room mac\n2. CA machine\n')
    if aeolight_station == '1':
        aeolight_station = 'telecine'
    elif aeolight_station == '2':
        aeolight_station = 'ca_machine'
    return aeolight_station


def make_parser():
    parser = argparse.ArgumentParser(description='Workflow specific metadata generator.'
                                'Accepts a WAV file as input.'
                                ' Designed for a specific IFI Irish Film Archive workflow. '
                                'Written by Kieran O\'Leary.')
    parser.add_argument('input', help='file path of parent directory')
    parser.add_argument('-v', action='store_true', help='verbose mode - Display full ffmpeg information')
    return parser


def process_audio(input, args):
    total_process = 6
    desktop_dir = os.path.expanduser("~/Desktop/%s") % os.path.basename(input)
    parent_dir = os.path.dirname(input)
    root_dir = os.path.dirname(os.path.dirname(parent_dir))
    os.chdir(root_dir)
    metadata_dir = root_dir + '/metadata/audio'
    aeo_light_premislog = input + '.xml'
    if os.path.isfile(aeo_light_premislog):
        shutil.move(aeo_light_premislog, metadata_dir)
    logs_dir = 'logs/audio'
    aeo_raw_extract_wav_dir = root_dir + '/objects/audio'
    framemd5 = metadata_dir + '/' + os.path.basename(input) +'.framemd5'
    if os.path.isfile(framemd5):
        return 'x', 'x', 'x', 'x'
    logfile = logs_dir + '/%s_framemd5.log' % os.path.basename(input)
    process_counter = 1
    print 'Process %d of %d - Logfile of framemd5 ffmpeg process located in %s/%s' % (process_counter,total_process, root_dir, logfile)
    process_counter += 1
    normpath = os.path.normpath(root_dir)
    relative_path = normpath.split(os.sep)[-1]
    manifest =  root_dir + '/raw_sip_manifest.md5'
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
    print 'Process %d of %d - Generating manifest' % (process_counter,total_process)
    process_counter += 1
    hashlib_manifest(root_dir, manifest, root_dir)
    return root_dir, process_counter, total_process, aeo_raw_extract_wav_dir


def premis_description(root_dir, process_counter, total_process, aeo_raw_extract_wav_dir, user, aeolight_workstation, audio_date_modified, intellectual_entity_uuid):
    source_directory = root_dir + '/objects/image'
    image_dir_list = os.listdir(source_directory)
    for image_files in image_dir_list:
        if not image_files[0] == '.':
            if image_files.endswith('.tiff'):
                first_image =  source_directory + '/' + image_files
                image_date_modified = get_date_modified(first_image)
                continue
    print 'Process %d of %d - Generating PREMIS XML file' % (process_counter,total_process)
    process_counter += 1
    representation_uuid = str(uuid.uuid4())
    premisxml, premis_namespace, doc, premis = setup_xml(source_directory)
    split_list = os.path.basename(root_dir).split('_')
    if 'ifard2016' in split_list[2]:
        split_list[2] = split_list[2].replace('ifard2016', 'IFA-(RD)2016-')
    elif 'ifard2017' in split_list[2]:
        split_list[2] = split_list[2].replace('ifard2017', 'IFA-(RD)2017-')
    audio_items = {"workflow":"raw audio","oe":split_list[0], "filmographic":split_list[1], "sourceAccession":split_list[2], "interventions":['placeholder'], "prepList":['placeholder'], "user":'Brian Cash'}
    image_items = {"workflow":"scanning","oe":split_list[0], "filmographic":split_list[1], "sourceAccession":split_list[2], "interventions":['placeholder'], "prepList":['placeholder'], "user":user}
    linking_representation_uuids = []
    xml_info    = make_premis(aeo_raw_extract_wav_dir, audio_items, premis, premis_namespace, premisxml, representation_uuid, 'nosequence')

    linking_representation_uuids.append(xml_info[2])
    xml_info    = make_premis(source_directory, image_items, premis, premis_namespace,premisxml, representation_uuid, 'sequence')
    image_uuids = xml_info[4]
    linking_representation_uuids.append(image_uuids)

    linking_representation_uuids.append(image_items['sourceAccession'])
    audio_file_uuid = linking_representation_uuids[0]
    create_intellectual_entity(premisxml, premis_namespace, doc, premis, audio_items, intellectual_entity_uuid)
    create_representation(premisxml, premis_namespace, doc, premis, audio_items,linking_representation_uuids, representation_uuid, 'sequence', intellectual_entity_uuid)
    doc         = xml_info[0]
    premisxml   = xml_info[1]
    premis = doc.getroot()
    extract_uuid                                = str(uuid.uuid4())
    capture_received_uuid                       = str(uuid.uuid4())
    audio_premis_checksum_uuid                  = str(uuid.uuid4())
    audio_framemd5_uuid                         = str(uuid.uuid4())
    scanning_uuid                               = str(uuid.uuid4())
    premis_checksum_uuid                        = str(uuid.uuid4())
    package_manifest_uuid                       = str(uuid.uuid4())
    aeolight_events = [extract_uuid]
    aeolightAgent                               = make_agent(premis,aeolight_events, 'bc3de900-3903-4764-ab91-2ce89977d0d2')
    hashlib_events                              = [audio_premis_checksum_uuid, premis_checksum_uuid, package_manifest_uuid]
    hashlibAgent                                = make_agent(premis,hashlib_events, '9430725d-7523-4071-9063-e8a6ac4f84c4')
    brian_events                                = [extract_uuid]
    if user == 'Brian Cash':
        brian_events += audio_premis_checksum_uuid,audio_framemd5_uuid,premis_checksum_uuid,package_manifest_uuid
        brian_events = [capture_received_uuid, scanning_uuid]
    elif user == 'Gavin Martin':
        brian_events += audio_premis_checksum_uuid,audio_framemd5_uuid,premis_checksum_uuid,package_manifest_uuid
        gavin_events = [capture_received_uuid, scanning_uuid]
        gavinAgent                                  = make_agent(premis,gavin_events, '9cab0b9c-4787-4482-8927-a045178c8e39')


    if user == 'Gavin Martin':
        script_user_Agent  = gavinAgent

    brianAgent                                  = make_agent(premis,brian_events, '0b96a20d-49f5-46e9-950d-4e11242a487e')
    if user == 'Brian Cash':
        script_user_Agent = brianAgent

    if aeolight_workstation == 'telecine':
        macMiniTelecineMachineAgent_events          = [extract_uuid, audio_premis_checksum_uuid, premis_checksum_uuid, audio_framemd5_uuid,package_manifest_uuid ]
        macMiniTelecineMachineAgent                 = make_agent(premis,macMiniTelecineMachineAgent_events, '230d72da-07e7-4a79-96ca-998b9f7a3e41')
        macMiniTelecineMachineOSAgent_events        = [extract_uuid, audio_premis_checksum_uuid, premis_checksum_uuid, audio_framemd5_uuid, package_manifest_uuid ]
        macMiniTelecineOSAgent                      = make_agent(premis,macMiniTelecineMachineOSAgent_events, '9486b779-907c-4cc4-802c-22e07dc1242f')
        transcoderMachine                           = make_agent(premis,[capture_received_uuid], '946e5d40-a07f-47d1-9637-def5cb7854ba')
        transcoderMachineOS                         = make_agent(premis,[capture_received_uuid], '192f61b1-8130-4236-a827-a194a20557fe')
        aeolight_computer = macMiniTelecineMachineAgent
        aeolight_OS = macMiniTelecineOSAgent
    elif aeolight_workstation == 'ca_machine':
        macMiniTelecineMachineAgent_events          = [audio_premis_checksum_uuid, premis_checksum_uuid, audio_framemd5_uuid,package_manifest_uuid ]
        macMiniTelecineMachineAgent                 = make_agent(premis,macMiniTelecineMachineAgent_events, '230d72da-07e7-4a79-96ca-998b9f7a3e41')
        macMiniTelecineMachineOSAgent_events        = [audio_premis_checksum_uuid, premis_checksum_uuid, audio_framemd5_uuid, package_manifest_uuid ]
        macMiniTelecineOSAgent                      = make_agent(premis,macMiniTelecineMachineOSAgent_events, '9486b779-907c-4cc4-802c-22e07dc1242f')
        transcoderMachine                           = make_agent(premis,[capture_received_uuid, extract_uuid], '946e5d40-a07f-47d1-9637-def5cb7854ba')
        transcoderMachineOS                         = make_agent(premis,[capture_received_uuid, extract_uuid], '192f61b1-8130-4236-a827-a194a20557fe')
        aeolight_computer = transcoderMachine
        aeolight_OS = transcoderMachineOS
    ffmpegAgent_events                          = [audio_framemd5_uuid]
    ffmpegAgent                                 = make_agent(premis,ffmpegAgent_events , 'ee83e19e-cdb1-4d83-91fb-7faf7eff738e')
    scannerAgent                                = make_agent(premis,[scanning_uuid], '1f4c1369-e9d1-425b-a810-6db1150955ba')
    scannerPCAgent                              = make_agent(premis,[scanning_uuid], 'ca731b64-638f-4dc3-9d27-0fc14387e38c')
    scannerLinuxAgent                           = make_agent(premis,[scanning_uuid], 'b22baa5c-8160-427d-9e2f-b62a7263439d')

    make_event(premis, 'creation', 'Film scanned to 12-bit RAW Bayer format and transcoded internally by ca731b64-638f-4dc3-9d27-0fc14387e38c to 16-bit RGB linear TIFF', [scannerAgent, script_user_Agent, scannerPCAgent, scannerLinuxAgent], scanning_uuid,xml_info[4], 'outcome', image_date_modified)
    make_event(premis, 'creation', 'TIFF image sequence is received via ethernet from ca731b64-638f-4dc3-9d27-0fc14387e38c and written to Disk', [transcoderMachine,transcoderMachineOS, script_user_Agent], capture_received_uuid,image_uuids,'outcome', image_date_modified)
    make_event(premis, 'creation', 'PCM WAV file extracted from overscanned image area of source TIFF files', [aeolightAgent, brianAgent, aeolight_computer, aeolight_OS ], extract_uuid,[audio_file_uuid], 'outcome',audio_date_modified)
    make_event(premis, 'message digest calculation', 'Whole file checksum of audio created for PREMIS XML', [hashlibAgent, brianAgent,macMiniTelecineMachineAgent, macMiniTelecineOSAgent], audio_premis_checksum_uuid,[audio_file_uuid], 'source', 'now')
    make_event(premis, 'message digest calculation', 'Frame level checksums of audio', [ffmpegAgent, brianAgent,macMiniTelecineMachineAgent, macMiniTelecineOSAgent], audio_framemd5_uuid,[audio_file_uuid], 'source', 'now' )

    make_event(premis, 'message digest calculation', 'Whole file checksums of image created for PREMIS XML', [hashlibAgent, brianAgent,macMiniTelecineMachineAgent, macMiniTelecineOSAgent], premis_checksum_uuid,[representation_uuid], 'source', 'now')
    make_event(premis, 'message digest calculation', 'Checksum manifest for whole package created', [hashlibAgent, brianAgent,macMiniTelecineMachineAgent, macMiniTelecineOSAgent], package_manifest_uuid,[representation_uuid], 'source', 'now' )
    write_premis(doc, premisxml)

def main():
    parser = make_parser()
    args = parser.parse_args()
    input = args.input
    user = get_user()
    aeolight_workstation = get_aeolight_workstation()
    for root, dirnames, filenames in os.walk(input):
        for files in filenames:
            if files.endswith('.wav'):
                root_dir, process_counter, total_process, aeo_raw_extract_wav_dir = process_audio(os.path.join(root,files), args)
                audio_date_modified = get_date_modified(os.path.join(root,files))
                if total_process == 'x':
                    continue
                else:
                    intellectual_entity_uuid = str(uuid.uuid4())
                    premis_description(root_dir,process_counter, total_process, aeo_raw_extract_wav_dir, user, aeolight_workstation, audio_date_modified, intellectual_entity_uuid)
            else:
                continue

if __name__ == '__main__':
    main()
