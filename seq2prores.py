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
from premis import make_premis
from premis import write_premis
from premis import make_agent
from premis import make_event
from premis import setup_xml
from premis import create_unit
from premis import create_representation

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
def premis_description(root_dir, aeo_raw_extract_wav_dir, user):
    source_directory = root_dir 
    
    representation_uuid = str(uuid.uuid4())
    premisxml, premis_namespace, doc, premis = setup_xml(source_directory)
    split_list = os.path.basename(os.path.dirname(os.path.dirname(root_dir))).split('_')
    audio_items = {"workflow":"treated audio","oe":split_list[0], "filmographic":split_list[1], "sourceAccession":split_list[2], "interventions":['placeholder'], "prepList":['placeholder'], "user":'Brian Cash'}
    image_items = {"workflow":"grade","oe":split_list[0], "filmographic":split_list[1], "sourceAccession":split_list[2], "interventions":['placeholder'], "prepList":['placeholder'], "user":user}
    linking_representation_uuids = []
    xml_info    = make_premis(aeo_raw_extract_wav_dir, audio_items, premis, premis_namespace, premisxml, representation_uuid, 'nosequence')

    linking_representation_uuids.append(xml_info[2])
    xml_info    = make_premis(source_directory, image_items, premis, premis_namespace,premisxml, representation_uuid, 'sequence')

    linking_representation_uuids.append(xml_info[2])
    linking_representation_uuids.append(image_items['sourceAccession'])
    create_representation(premisxml, premis_namespace, doc, premis, audio_items,linking_representation_uuids, representation_uuid, 'sequence' )
    doc         = xml_info[0]
    premisxml   = xml_info[1]
    premis = doc.getroot()
    audio_framemd5_uuid                         = str(uuid.uuid4())
    premis_checksum_uuid                        = str(uuid.uuid4())
    framemd5_uuid                               = str(uuid.uuid4())
    package_manifest_uuid                       = str(uuid.uuid4())
   
    ffmpegAgent_events                          = [framemd5_uuid, audio_framemd5_uuid]
    ffmpegAgent                                 = make_agent(premis,ffmpegAgent_events , 'ee83e19e-cdb1-4d83-91fb-7faf7eff738e')
    write_premis(doc, premisxml)
    return representation_uuid

def main():
    desktop_logdir = os.path.expanduser("~/Desktop/") + 'seq_csv_reports'
    if not os.path.isdir(desktop_logdir):
        os.makedirs(desktop_logdir)
    csv_report_filename = desktop_logdir + '/dpx_transcode_report' + time.strftime("_%Y_%m_%dT%H_%M_%S") + '.csv'

    source_directory = sys.argv[1]
    create_csv(csv_report_filename, ('Sequence Name', 'Start time', 'Finish Time'))
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
            master_audio =  master_parent_dir + '/objects/audio/' + os.listdir(master_parent_dir + '/objects/audio')[0]
            mezzanine_file =  mezzanine_object_dir + '/' + os.path.basename(mezzanine_parent_dir) + '_mezzanine.mov'
            image_seq_without_container = info[0]
            start_number                = info[1]
            container                   = info[2]
            start_number_length = len(start_number)
            number_regex = "%0" + str(start_number_length) + 'd.'
            audio_dir            = source_parent_dir + '/audio'
            logs_dir            =  mezzanine_parent_dir + '/logs'
            user = 'kieran'
            source_representation_uuid = premis_description(master_object_dir, master_parent_dir + '/objects/audio', user)

            os.chdir(audio_dir)
            audio_file_list = glob('*.wav')
            audio_file = os.path.join(audio_dir,audio_file_list[0])
            dpx_filename                = image_seq_without_container + number_regex + container
            logfile = logs_dir + '/%s_prores.log' % os.path.basename(mezzanine_parent_dir)
            env_dict = os.environ.copy()
            # https://github.com/imdn/scripts/blob/0dd89a002d38d1ff6c938d6f70764e6dd8815fdd/ffmpy.py#L272
            logfile = "\'" + logfile + "\'"
            env_dict['FFREPORT'] = 'file={}:level=48'.format(logfile)
            seq2prores= ['ffmpeg','-f','image2','-framerate','24', '-start_number', start_number, '-i', root + '/' + dpx_filename ,'-i', audio_file,'-c:v','prores','-profile:v', '3','-c:a','pcm_s24le', '-ar', '48000', mezzanine_object_dir + '/' + os.path.basename(mezzanine_parent_dir) + '_mezzanine.mov','-f', 'framemd5', '-an', master_metadata_dir + '/image/' + os.path.basename(master_parent_dir) + '.framemd5']
            print seq2prores
            subprocess.call(seq2prores,env=env_dict)
            representation_uuid = str(uuid.uuid4())
            split_list = os.path.basename(mezzanine_parent_dir).split('_')
            user = 'kieran'
            premisxml, premis_namespace, doc, premis = setup_xml(mezzanine_file)
            items = {"workflow":"seq2prores","oe":'n/a', "filmographic":split_list[0], "sourceAccession":split_list[1], "interventions":['placeholder'], "prepList":['placeholder'], "user":user}
            premis = doc.getroot()
            xml_info    = make_premis(mezzanine_file, items, premis, premis_namespace,premisxml, representation_uuid, '????')
            sequence = xml_info[3]

            linking_representation_uuids = []
            linking_representation_uuids.append(xml_info[2])
            linking_representation_uuids.append(xml_info[2])
            linking_representation_uuids.append(source_representation_uuid)
            create_representation(premisxml, premis_namespace, doc, premis, items,linking_representation_uuids, representation_uuid,sequence )
            doc         = xml_info[0]
            premisxml   = xml_info[1]
            framemd5_uuid                               = str(uuid.uuid4())
            final_sip_manifest_uuid                              = str(uuid.uuid4())
            prores_event_uuid = str(uuid.uuid4())
            #ffmpegAgent                                 = make_agent(premis,[framemd5_uuid ], 'ee83e19e-cdb1-4d83-91fb-7faf7eff738e')
            make_event(premis, 'creation', 'Image Sequence and WAV re-encoded to Apple Pro Res 422 HQ with 44khz 24-bit PCM audio', [['UUID','ee83e19e-cdb1-4d83-91fb-7faf7eff738e' ]],prores_event_uuid,representation_uuid, 'outcome')
            write_premis(doc, premisxml)
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
            make_event(premis, 'message digest calculation', 'Checksum manifest for whole package created', [['UUID','9430725d-7523-4071-9063-e8a6ac4f84c4' ]],final_sip_manifest_uuid,representation_uuid, 'source')
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
