#!/usr/bin/env python
import subprocess
import sys
import os
import shutil
import argparse
import datetime
import time
import csv
import uuid
from glob import glob
from ififuncs import create_csv
from ififuncs import append_csv
from ififuncs import send_gmail
from ififuncs import hashlib_manifest
from ififuncs import diff_textfiles
from ififuncs import make_manifest
from ififuncs import generate_log


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
    batch_dir = os.path.basename(os.path.dirname(os.path.dirname(root_dir)))
    output_parent_directory = os.path.join(args.o, batch_dir)
    if not os.path.isdir(output_parent_directory):
        os.makedirs(output_parent_directory)

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
    info = [output_dirname, output, image_seq_without_container, output_parent_directory]
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

def premis_log(source_parent_dir, source_directory):
    split_list = os.path.basename(os.path.dirname(source_parent_dir)).split('_')
    premisxml, premis_namespace, doc, premis = setup_xml(source_directory)
    items = {"workflow":"scanning","oe":split_list[0], "filmographic":split_list[1], "sourceAccession":split_list[2], "interventions":['placeholder'], "prepList":['placeholder'], "user":user}
    premis = doc.getroot()
    framemd5_uuid                               = str(uuid.uuid4())
    final_sip_manifest_uuid                              = str(uuid.uuid4())
    a = doc.xpath('//ns:agentIdentifierValue',namespaces={'ns': premis_namespace})
    for i in a:
        if i.text == '9430725d-7523-4071-9063-e8a6ac4f84c4':
            linkingEventIdentifier      = create_unit(-1,i.getparent().getparent(),'linkingEventIdentifier')
            linkingEventIdentifierType = create_unit(1,linkingEventIdentifier, 'linkingEventIdentifierType')
            linkingEventIdentifierValue = create_unit(1,linkingEventIdentifier, 'linkingEventIdentifierValue')
            linkingEventIdentifierValue.text = final_sip_manifest_uuid
            linkingEventIdentifierType.text = 'UUID'
        elif i.text == 'ee83e19e-cdb1-4d83-91fb-7faf7eff738e':
            linkingEventIdentifier      = create_unit(-1,i.getparent().getparent(),'linkingEventIdentifier')
            linkingEventIdentifierType = create_unit(1,linkingEventIdentifier, 'linkingEventIdentifierType')
            linkingEventIdentifierValue = create_unit(1,linkingEventIdentifier, 'linkingEventIdentifierValue')
            linkingEventIdentifierValue.text = framemd5_uuid
            linkingEventIdentifierType.text = 'UUID'
    representation_uuid  = doc.findall('//ns:objectIdentifierValue',namespaces={'ns': premis_namespace})[0].text
    #ffmpegAgent                                 = make_agent(premis,[framemd5_uuid ], 'ee83e19e-cdb1-4d83-91fb-7faf7eff738e')
    make_event(premis, 'message digest calculation', 'Checksum manifest for whole package created', [['UUID','9430725d-7523-4071-9063-e8a6ac4f84c4' ]],final_sip_manifest_uuid,[representation_uuid], 'source', 'now')
    make_event(premis, 'message digest calculation', 'Frame level checksums of images', [['UUID','ee83e19e-cdb1-4d83-91fb-7faf7eff738e' ]], framemd5_uuid, [representation_uuid], 'source', 'now' )
    write_premis(doc, premisxml)

parser = argparse.ArgumentParser(description='DPX2TIFF specific workflow for IFI'
                                ' Written by Kieran O\'Leary.')
parser.add_argument(
                    'input', nargs='+',
                    help='full path of input directory'
                    )
parser.add_argument(
                    '-o',
                    help='full path of output directory', required=True)
args = parser.parse_args()
print args

csv_report_filename = os.path.expanduser("~/Desktop/") + 'dpx_transcode_report' + time.strftime("_%Y_%m_%dT%H_%M_%S") + '.csv'

#permission for correct directories sought from user
permission = ''
all_files = args.input
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
        
#user identity sought for accurate premis documentation
user = ''
if not user == '1' or user == '2'or user == '3':
    user =  raw_input('\n\n**** Who are you?\nPress 1 or 2 or 3\n\n1. Brian Cash\n2. Gavin Martin\n3. Raelene Casey\n' )
    while user not in ('1','2','3'):
        user =  raw_input('\n\n**** Who are you?\nPress 1 or 2 or 3\n\n1. Brian Cash\n2. Gavin Martin\n3. Raelene Casey\n')
if user == '1':
    user = 'Brian Cash'
    print 'Hi Brian, Congratulations on becoming a father!!!'
elif user == '2':
    user = 'Gavin Martin'
    print 'Hi Gavin, Have you renewed your subscription to American Cinematographer?'
elif user == '3':
    user = 'Raelene Casey'
    print 'Hi Raelene, Brian must be out of the office'
    time.sleep(1)

create_csv(csv_report_filename, ('Sequence Name', 'Lossless?', 'Start time', 'Finish Time'))
space_counter = 0
for source_directory in all_files:
    for root,dirnames,filenames in os.walk(source_directory):
        for folders in dirnames:
            if ' ' in folders:
                print 'Space found in %s - DELETE IT PLEASE' % os.path.join(root,folders)
                space_counter += 1
    if space_counter > 0:
        sys.exit()

    for root,dirnames,filenames in os.walk(source_directory):
            source_directory = root
            if not file_check(source_directory) == 'TIFF':
                append_csv(csv_report_filename, (source_directory,'EMPTY DIRECTORY - SKIPPED', 'n/a', 'n/a'))
                continue

            root_dir = os.path.dirname(os.path.dirname(root))
            general_log = root_dir + '/logs/image/%s__second_pass_image_log.log' % os.path.basename(root_dir)
            generate_log(general_log, 'Input = %s' % root)
            source_parent_dir           = os.path.dirname(source_directory)
            normpath                    = os.path.normpath(source_directory)
            relative_path               = normpath.split(os.sep)[-1]
            split_path                  = os.path.split(os.path.basename(source_directory))[1]
            start                       = datetime.datetime.now()
            source_manifest             = root_dir + '/%s_manifest.md5' % relative_path
            info                        = make_framemd5(source_directory, 'tiff', 'tiff_framemd5')
            output_dirname              = info[0]
            source_textfile             = info[1]
            fmd5copy                    = root_dir + '/metadata/image'
            shutil.copy(source_textfile,fmd5copy )
            image_seq_without_container = info[2]
            output_parent_directory     = info[3]
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
            source_metadata_dir = root_dir + '/metadata/image'
            shutil.copy(source_textfile, source_metadata_dir + '/%s' % os.path.basename(source_textfile))
            finish = datetime.datetime.now()
            append_csv(csv_report_filename, (parent_basename,judgement, start, finish))
