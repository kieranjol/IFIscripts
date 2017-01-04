#!/usr/bin/env python

import subprocess
import sys
import os
from glob import glob
from ififuncs import diff_textfiles
import datetime
import time
import csv
import uuid
import lxml.etree as ET
from ififuncs import create_csv
from ififuncs import append_csv
from ififuncs import send_gmail
from ififuncs import hashlib_manifest
from ififuncs import make_mediainfo
from ififuncs import make_mediatrace
from ififuncs import get_date_modified
from premis import make_premis
from premis import write_premis
from premis import make_agent
from premis import make_event
from premis import setup_xml
from premis import create_unit
from premis import create_representation
from premis import create_intellectual_entity

def get_user():
    user = ''
    if user not in ('1','2', '3', '4', '5'):
        user =  raw_input('\n\n**** Who are you?\nPress 1,2,3,4,5\n\n1. Brian Cash\n2. Gavin Martin\n3. Kieran O\'Leary\n4. Raelene Casey\n5. Aoife Fitzmaurice\n' )
        while user not in ('1','2', '3', '4', '5'):
            user =  raw_input('\n\n**** Who are you?\nPress 1,2,3,4,5\n1. Brian Cash\n2. Gavin Martin\n3. Kieran O\'Leary\n4. Raelene Casey\n5. Aoife Fitzmaurice\n')
    if user == '1':
        user = 'Brian Cash'
        print 'Hi Brian, i still need to give you back twin peaks '
        time.sleep(1)
    elif user == '2':
        user = 'Gavin Martin'
        print 'Hi Gavin, Have you renewed your subscription to American Cinematographer?'
        time.sleep(1)
    elif user == '3':
        user = 'Kieran O\'Leary'
        print 'Hi Kieran, NO MESSAGE FOR YOU'
        time.sleep(1)
    elif user == '4':
        user = 'Raelene Casey'
        print 'Hi Raelene - Injoke of the week: Williamsburg/Australia/Blondy/Colin Farrell'
        time.sleep(1)
    elif user == '5':
        user = 'Aoife Fitzmaurice'
        print 'Hi Aoife, Paul Galvin < Roy Keane'
        time.sleep(1)
    return user

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
    image_date_modified = get_date_modified(images[0])
    mediainfo_xml = '%s/%s_mediainfo.xml' % (os.path.dirname(os.path.dirname(directory)) + '/metadata/image', images[0])
    mediatrace_xml = '%s/%s_mediatrace.xml' % (os.path.dirname(os.path.dirname(directory)) + '/metadata/image', images[0])

    if not os.path.isfile(mediainfo_xml):
        print 'Creating mediainfo XML for %s' % images[0]
        make_mediainfo(mediainfo_xml, 'mediaxmloutput', images[0])
    if not os.path.isfile(mediatrace_xml):
        print 'Creating mediatrace XML for %s' % images[0]
        make_mediatrace(mediatrace_xml, 'mediatracexmlinput', images[0])
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
    info = [image_seq_without_container, start_number, container, image_date_modified]
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


def premis_description(root_dir, aeo_raw_extract_wav_dir, user, image_date_modified, audio_date_modified, intellectual_entity_uuid):
    source_directory = root_dir

    representation_uuid = str(uuid.uuid4())
    premisxml, premis_namespace, doc, premis = setup_xml(source_directory)
    split_list = os.path.basename(os.path.dirname(os.path.dirname(root_dir))).split('_')
    if 'ifard2016' in split_list[2]:
        split_list[2] = split_list[2].replace('ifard2016', 'IFA-(RD)2016-')
    elif 'ifard2017' in split_list[2]:
        split_list[2] = split_list[2].replace('ifard2017', 'IFA-(RD)2017-')

    audio_items = {"workflow":"treated audio","oe":split_list[0], "filmographic":split_list[1], "sourceAccession":split_list[2], "interventions":['placeholder'], "prepList":['placeholder'], "user":'Brian Cash'}
    image_items = {"workflow":"grade","oe":split_list[0], "filmographic":split_list[1], "sourceAccession":split_list[2], "interventions":['placeholder'], "prepList":['placeholder'], "user":'Gavin Martin'}
    linking_representation_uuids = []
    xml_info    = make_premis(aeo_raw_extract_wav_dir, audio_items, premis, premis_namespace, premisxml, representation_uuid, 'nosequence')

    linking_representation_uuids.append(xml_info[2])
    xml_info    = make_premis(source_directory, image_items, premis, premis_namespace,premisxml, representation_uuid, 'sequence')
    print xml_info
    linking_representation_uuids.append(xml_info[4])
    linking_representation_uuids.append(image_items['sourceAccession'])
    create_intellectual_entity(premisxml, premis_namespace, doc, premis, audio_items, intellectual_entity_uuid)
    create_representation(premisxml, premis_namespace, doc, premis, audio_items,linking_representation_uuids, representation_uuid, 'sequence', intellectual_entity_uuid )
    doc         = xml_info[0]
    premisxml   = xml_info[1]
    premis = doc.getroot()
    '''
    events:
    audio - audio cleaning in rx5
    export from protools

    image:
    crop in avid
    grade in baselight
    export from avid

    framemd5 audio
    framemd5 image
    whole md5

    '''
    audio_rx5_uuid                              = str(uuid.uuid4())
    audio_protools_uuid                         = str(uuid.uuid4())
    image_avid_crop_uuid                        = str(uuid.uuid4())
    image_baselight_grade_uuid                  = str(uuid.uuid4())
    package_manifest_uuid                       = str(uuid.uuid4())
    image_framemd5_uuid                         = str(uuid.uuid4())

    ffmpegAgent_events                          = [image_framemd5_uuid ]
    hashlib_events                              = [package_manifest_uuid]
    avid_events                                 = [image_avid_crop_uuid,image_baselight_grade_uuid]
    protools_events                             = [audio_protools_uuid]
    baselight_events                            = [image_baselight_grade_uuid]
    rx5_events                                  = [audio_rx5_uuid]
    macMiniTelecineMachineAgent_events          = [audio_rx5_uuid, package_manifest_uuid, image_framemd5_uuid, audio_protools_uuid]
    macMiniTelecineMachineOSAgent_events        = [audio_rx5_uuid, package_manifest_uuid, image_framemd5_uuid, audio_protools_uuid]
    macProTelecineMachineOSAgent_events         = [image_avid_crop_uuid, image_baselight_grade_uuid]
    macProTelecineMachineAgent_events           = [image_avid_crop_uuid, image_baselight_grade_uuid]
    gavin_events                                = [image_avid_crop_uuid, image_baselight_grade_uuid]
    brian_events                                = [audio_rx5_uuid,  audio_protools_uuid]


    if user == 'Gavin Martin':
        gavin_events += package_manifest_uuid, image_framemd5_uuid
    elif user == 'Brian Cash':
        brian_events += package_manifest_uuid, image_framemd5_uuid
    else:
        script_user_events                      = [package_manifest_uuid, image_framemd5_uuid,]

        script_user_Agent                       = make_agent(premis,script_user_events, user )
    gavinAgent                                  = make_agent(premis,gavin_events, '9cab0b9c-4787-4482-8927-a045178c8e39')
    if user == 'Gavin Martin':
        script_user_Agent  = gavinAgent

    brianAgent                                  = make_agent(premis,brian_events, '0b96a20d-49f5-46e9-950d-4e11242a487e')
    if user == 'Brian Cash':
        script_user_Agent = brianAgent
    macMiniTelecineMachineAgent                 = make_agent(premis,macMiniTelecineMachineAgent_events, '230d72da-07e7-4a79-96ca-998b9f7a3e41')
    macProTelecineMachineAgent                  = make_agent(premis,macMiniTelecineMachineAgent_events, '838a1a1b-7ddd-4846-ae8e-3b5ecb4aae55')
    macMiniTelecineOSAgent                      = make_agent(premis,macMiniTelecineMachineOSAgent_events, '68f56ede-a1cf-48aa-b1d8-dc9850d5bfcc')
    macProTelecineOSAgent                       = make_agent(premis,macProTelecineMachineOSAgent_events, '52adf876-bf30-431c-b0c6-80cc4fd9406c')
    ffmpegAgent                                 = make_agent(premis,ffmpegAgent_events , 'ee83e19e-cdb1-4d83-91fb-7faf7eff738e')
    hashlibAgent                                = make_agent(premis,hashlib_events, '9430725d-7523-4071-9063-e8a6ac4f84c4')
    avidAgent                                   = make_agent(premis,avid_events, '11e157a3-1aa7-4195-b816-009a3d47148c')
    protoolsAgent                               = make_agent(premis,protools_events, '55003bbd-49a4-4c7b-8da2-0d5b9bf10168')
    baselightAgent                              = make_agent(premis,baselight_events, '8c02d962-5ac5-4e51-a30c-002553134320')
    rx5Agent                                    = make_agent(premis,rx5_events, 'e5872957-8ee8-4c20-bd8e-d76e1de01b34')


    make_event(premis, 'creation', 'Audio cleanup', [macMiniTelecineMachineAgent ,macMiniTelecineOSAgent, rx5Agent  , brianAgent ],audio_rx5_uuid,[linking_representation_uuids[0]], 'outcome', audio_date_modified)
    make_event(premis, 'creation', 'Audio trimming and export', [macMiniTelecineMachineAgent ,macMiniTelecineOSAgent, protoolsAgent, brianAgent ],audio_protools_uuid ,[linking_representation_uuids[0]], 'outcome', audio_date_modified)
    make_event(premis, 'creation', 'Import to Avid and remove overscan', [macProTelecineMachineAgent ,macProTelecineOSAgent, avidAgent, gavinAgent ],image_avid_crop_uuid,xml_info[4], 'outcome', image_date_modified)
    make_event(premis, 'creation', 'Colour Correction', [macProTelecineMachineAgent ,macProTelecineOSAgent, baselightAgent , gavinAgent ],image_baselight_grade_uuid ,xml_info[4], 'outcome', image_date_modified)
    make_event(premis, 'message digest calculation', 'Frame level checksums of image', [macMiniTelecineMachineAgent ,macMiniTelecineOSAgent, ffmpegAgent, script_user_Agent ],image_framemd5_uuid,xml_info[4], 'source', 'now' )
    make_event(premis, 'message digest calculation', 'Checksum manifest for whole package created', [hashlibAgent,macMiniTelecineMachineAgent, macMiniTelecineOSAgent,script_user_Agent], package_manifest_uuid,[representation_uuid], 'source', 'now' )

    write_premis(doc, premisxml)
    return representation_uuid

def main():
    desktop_logdir = os.path.expanduser("~/Desktop/") + 'seq_csv_reports'
    if not os.path.isdir(desktop_logdir):
        os.makedirs(desktop_logdir)
    all_files = sys.argv[1:]
    permission = ''
    if not permission == 'y' or permission == 'Y':
        print '\n\n**** All image sequences within these directories will be converted the input for this script.\n'
        for i in all_files:
            print i
        permission =  raw_input('\n**** All image sequences within these directories will be converted the input for this script \n**** If this looks ok, please press Y, otherwise, type N\n' )
        while permission not in ('Y','y','N','n'):
            permission =  raw_input('\n**** All image sequences within these directories will be converted the input for this script \n**** If this looks ok, please press Y, otherwise, type N\n')
        if permission == 'n' or permission == 'N':
            print 'Exiting at your command- Cheerio for now'
            sys.exit()
        elif permission =='y' or permission == 'Y':
            print 'Ok so!'
    csv_report_filename = desktop_logdir + '/seq2prores_report' + time.strftime("_%Y_%m_%dT%H_%M_%S") + '.csv'
    user = get_user()
    create_csv(csv_report_filename, ('Sequence Name', 'Start time', 'Finish Time'))
    for source_directory in all_files:
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

                info = get_filenames(source_directory, 'dpx_framemd5')
                if info == 'none':
                    continue
                for files in filenames:
                    total_size += os.path.getsize(os.path.join(root,files))
                master_parent_dir     = os.path.dirname(source_parent_dir)
                master_object_dir     = master_parent_dir + '/objects/image'
                master_metadata_dir = master_parent_dir + '/' + 'metadata'
                middle =  os.listdir(os.path.dirname(os.path.dirname(master_parent_dir)) + '/mezzanine')[0]
                mezzanine_object_dir            =  os.path.dirname(os.path.dirname(master_parent_dir)) + '/mezzanine/%s/objects' % middle
                mezzanine_parent_dir   = os.path.dirname(os.path.dirname(master_parent_dir)) + '/mezzanine/%s' % middle
                mezzanine_metadata_dir = mezzanine_parent_dir + '/metadata'
                source_manifest =  master_parent_dir + '/' + os.path.basename( master_parent_dir) +  '_manifest.md5'
                mezzanine_manifest =   mezzanine_parent_dir + '/' + os.path.basename( mezzanine_parent_dir) +  '_manifest.md5'
                audio_dir_list = os.listdir(master_parent_dir + '/objects/audio')
                for audio_files in audio_dir_list:
                    if not audio_files[0] == '.':
                        if audio_files.endswith('.wav'):
                            master_audio =  master_parent_dir + '/objects/audio/' + audio_files
                            audio_date_modified = get_date_modified(master_audio)
                mezzanine_file =  mezzanine_object_dir + '/' + os.path.basename(mezzanine_parent_dir) + '_mezzanine.mov'
                if os.path.isfile(mezzanine_file):
                    print 'Mezzanine file already exists so this script has most likely already been run.. skipping.'
                    continue
                image_seq_without_container = info[0]
                start_number                = info[1]
                container                   = info[2]
                image_date_modified         = info[3]
                start_number_length = len(start_number)
                number_regex = "%0" + str(start_number_length) + 'd.'
                audio_dir            = source_parent_dir + '/audio'
                logs_dir            =  mezzanine_parent_dir + '/logs'
                intellectual_entity_uuid = str(uuid.uuid4())
                source_representation_uuid = premis_description(master_object_dir, master_parent_dir + '/objects/audio', user, image_date_modified, audio_date_modified, intellectual_entity_uuid)

                os.chdir(audio_dir)
                audio_file_list = glob('*.wav')
                audio_file = os.path.join(audio_dir,audio_file_list[0])
                dpx_filename                = image_seq_without_container + number_regex + container
                logfile = logs_dir + '/%s_prores.log' % os.path.basename(mezzanine_parent_dir)
                env_dict = os.environ.copy()
                # https://github.com/imdn/scripts/blob/0dd89a002d38d1ff6c938d6f70764e6dd8815fdd/ffmpy.py#L272
                logfile = "\'" + logfile + "\'"
                env_dict['FFREPORT'] = 'file={}:level=48'.format(logfile)
                seq2prores= ['ffmpeg','-y','-f','image2','-framerate','24', '-start_number', start_number, '-i', root + '/' + dpx_filename ,'-i', audio_file,'-c:v','prores','-profile:v', '3','-c:a','pcm_s24le', '-ar', '48000', mezzanine_object_dir + '/' + os.path.basename(mezzanine_parent_dir) + '_mezzanine.mov','-f', 'framemd5', '-an', master_metadata_dir + '/image/' + os.path.basename(master_parent_dir) + '.framemd5', '-c:a', 'pcm_s24le', '-f', 'framemd5', '-vn', master_metadata_dir + '/audio/' + os.path.basename(master_parent_dir) + '.framemd5']
                print seq2prores
                subprocess.call(seq2prores,env=env_dict)
                representation_uuid = str(uuid.uuid4())
                split_list = os.path.basename(mezzanine_parent_dir).split('_')
                premisxml, premis_namespace, doc, premis = setup_xml(mezzanine_file)
                items = {"workflow":"seq2prores","oe":'n/a', "filmographic":split_list[0], "sourceAccession":split_list[1], "interventions":['placeholder'], "prepList":['placeholder'], "user":user}
                premis = doc.getroot()
                xml_info    = make_premis(mezzanine_file, items, premis, premis_namespace,premisxml, representation_uuid, '????')
                sequence = xml_info[3]

                linking_representation_uuids = []
                linking_representation_uuids.append(xml_info[2])
                linking_representation_uuids.append(xml_info[2]) # the duplicate does nothing btw, they are a placeholder from a hardcoded function
                linking_representation_uuids.append(source_representation_uuid)
                create_intellectual_entity(premisxml, premis_namespace, doc, premis, items, intellectual_entity_uuid)
                create_representation(premisxml, premis_namespace, doc, premis, items,linking_representation_uuids, representation_uuid,sequence, intellectual_entity_uuid)
                doc         = xml_info[0]
                premisxml   = xml_info[1]
                final_sip_manifest_uuid                     = str(uuid.uuid4())
                prores_event_uuid                           = str(uuid.uuid4())

                macMiniTelecineMachineAgent_events          = [prores_event_uuid,final_sip_manifest_uuid  ]
                macMiniTelecineMachineAgent                 = make_agent(premis,macMiniTelecineMachineAgent_events, '230d72da-07e7-4a79-96ca-998b9f7a3e41')
                macMiniTelecineMachineOSAgent_events        = [prores_event_uuid,final_sip_manifest_uuid ]
                macMiniTelecineOSAgent                      = make_agent(premis,macMiniTelecineMachineOSAgent_events, '9486b779-907c-4cc4-802c-22e07dc1242f')

                hashlib_events                              = [final_sip_manifest_uuid ]
                hashlibAgent                                = make_agent(premis,hashlib_events, '9430725d-7523-4071-9063-e8a6ac4f84c4')
                ffmpegAgent_events                          = [prores_event_uuid ]
                ffmpegAgent                                 = make_agent(premis,ffmpegAgent_events , 'ee83e19e-cdb1-4d83-91fb-7faf7eff738e')
                operatorEvents                              = [final_sip_manifest_uuid,prores_event_uuid]
                operatorAgent                               = make_agent(premis,operatorEvents ,user)
                #ffmpegAgent                                 = make_agent(premis,[framemd5_uuid ], 'ee83e19e-cdb1-4d83-91fb-7faf7eff738e')
                make_event(premis, 'creation', 'Image Sequence and WAV re-encoded to Apple Pro Res 422 HQ with 48khz 24-bit PCM audio', [macMiniTelecineMachineAgent ,macMiniTelecineOSAgent, ffmpegAgent, operatorAgent ],prores_event_uuid,[representation_uuid], 'outcome', 'now')

                print premisxml
                mezzanine_mediainfoxml =  "%s/%s_mediainfo.xml" % (mezzanine_metadata_dir,os.path.basename(mezzanine_parent_dir) )
                tracexml =  "%s/%s_mediatrace.xml" % (mezzanine_metadata_dir,os.path.basename(mezzanine_parent_dir) )
                audio_mediainfoxml = "%s/%s_mediainfo.xml" % (master_metadata_dir + '/audio',os.path.basename(master_audio) )
                audio_mediatracexml = "%s/%s_mediatrace.xml" % (master_metadata_dir + '/audio',os.path.basename(master_audio) )
                if not os.path.isfile(audio_mediainfoxml):
                    make_mediainfo(audio_mediainfoxml,'audiomediaxmlinput',master_audio)
                if not os.path.isfile(audio_mediatracexml):
                    make_mediainfo(audio_mediatracexml,'audiomediatraceinput',master_audio)
                if not os.path.isfile(mezzanine_mediainfoxml):
                    make_mediainfo(mezzanine_mediainfoxml,'mediaxmlinput',mezzanine_object_dir + '/' + os.path.basename(mezzanine_parent_dir) + '_mezzanine.mov')
                if not os.path.isfile(tracexml):
                    make_mediatrace(tracexml,'mediatracexmlinput',mezzanine_object_dir + '/' + os.path.basename(mezzanine_parent_dir) + '_mezzanine.mov')
                hashlib_manifest(master_parent_dir, source_manifest, master_parent_dir)
                hashlib_manifest(mezzanine_parent_dir, mezzanine_manifest, mezzanine_parent_dir)
                make_event(premis, 'message digest calculation', 'Checksum manifest for whole package created', [macMiniTelecineMachineAgent ,macMiniTelecineOSAgent, operatorAgent],final_sip_manifest_uuid,[representation_uuid], 'source', 'now')
                write_premis(doc, premisxml)
                finish = datetime.datetime.now()
                append_csv(csv_report_filename, (os.path.basename( master_parent_dir), start, finish))
                '''
                to create premis you must:
                1. have a parent folder with oe_filmo_source in folder name
                2. generate premis object with setup_xml()
                3. generate a representation uuid4.
                4. populate a user variable
                5. use make_premis, passing a file or a folder with sequence
                6. create a representation and link to file
                '''
        #send_gmail(emails, csv_report_filename, 'makedpx completed', 'Hi,\n Please the attached log for details of the makedpx job, \nSincerely yours,\nIFIROBOT', config[2].rstrip(), config[3].rstrip())
if __name__ == '__main__':
    main()
