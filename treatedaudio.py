#!/usr/bin/env python
import subprocess
import sys
import os
import hashlib
import shutil
from glob import glob

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

'''
TODO - check for typos in filename + conformance check for things like 'is protools.txt in /session info?'
TODO - check for spaces?
1. create metadata folder
2. Put in mediainfo + mediatrace
3. framemd5s of treated_audio
4. Todo - premis/revtmd
4. md5 manifest for everything

4. 
'''

input = sys.argv[1]

parent_dir = os.path.dirname(input)
md5_file = os.path.dirname(os.path.dirname(parent_dir)) +  'deliverable_audio_only.md5'
metadata_dir = parent_dir + '/xml_files'
md5_dir = parent_dir + '/md5'
logs_dir = os.path.dirname(os.path.dirname(parent_dir)) + '/logs'
treated_wav_log_dir = logs_dir + '/audio/treated_wav'
deliverable_wav_dir = parent_dir + '/deliverable_wav'
framemd5 = md5_dir + '/' + os.path.basename(input) +'.framemd5'
normpath = os.path.normpath(parent_dir)
relative_path = normpath.split(os.sep)[-1]
manifest =  '%s_manifest.md5' % (relative_path)
logfile = logs_dir + '/audio/' + os.path.basename(input) + '_framemd5.log'
filenoext = os.path.splitext(input)[0]
os.makedirs(metadata_dir)
os.makedirs(md5_dir)
os.makedirs(deliverable_wav_dir)


inputxml =  "%s/%s_mediainfo.xml" % (metadata_dir,os.path.basename(input) )
print inputxml
tracexml =  "%s/%s_mediatrace.xml" % (metadata_dir,os.path.basename(input) )
def set_environment(logfile):
    env_dict = os.environ.copy()
    # https://github.com/imdn/scripts/blob/0dd89a002d38d1ff6c938d6f70764e6dd8815fdd/ffmpy.py#L272
    env_dict['FFREPORT'] = 'file={}:level=48'.format(logfile)
    return env_dict
    
    
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
            
def make_mediainfo(xmlfilename, xmlvariable, inputfilename):
    with open(xmlfilename, "w+") as fo:
        xmlvariable = subprocess.check_output(['mediainfo',
                        '-f',
                        '--language=raw', # Use verbose output.
                        '--output=XML',
                        inputfilename])       #input filename
        fo.write(xmlvariable)
def make_mediatrace(tracefilename, xmlvariable, inputfilename):
    with open(tracefilename, "w+") as fo:
        xmlvariable = subprocess.check_output(['mediainfo',
                        '-f',
                        '--Details=1', # Use verbose output.
                        '--output=XML',
                        inputfilename])       #input filename
        fo.write(xmlvariable)
make_mediainfo(inputxml,'mediaxmlinput',input)
make_mediatrace(tracexml,'mediatracexmlinput',input)

env_dict = set_environment(logfile)
fmd5cmd = ['ffmpeg','-i',input,'-report','-f','framemd5', framemd5]
subprocess.call(fmd5cmd, env=env_dict)   

                  
remove_bad_files(parent_dir)  

os.chdir(parent_dir)  
 
subprocess.call([ 'gcp','--preserve=mode,timestamps', '-nRv',input, treated_wav_log_dir])
shutil.move(input,deliverable_wav_dir + '/' + os.path.basename(input))           

make_manifest(os.path.dirname(os.path.dirname(parent_dir)),manifest)   