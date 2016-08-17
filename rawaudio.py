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

input = sys.argv[1]
desktop_dir = os.path.expanduser("~/Desktop/%s") % os.path.basename(input)
parent_dir = os.path.dirname(input)
md5_file = input + '.md5'
metadata_dir = parent_dir + '/xml_files'
md5_dir = parent_dir + '/md5'
logs_dir = parent_dir + '/log'
aeo_raw_extract_wav_dir = parent_dir + '/aeo_raw_extract_wav'
framemd5 = md5_dir + '/' + os.path.basename(input) +'.framemd5'
normpath = os.path.normpath(parent_dir)
relative_path = normpath.split(os.sep)[-1]
manifest =  '%s_manifest.md5' % (relative_path)
filenoext = os.path.splitext(input)[0]
os.makedirs(metadata_dir)
os.makedirs(md5_dir)
os.makedirs(aeo_raw_extract_wav_dir)
os.makedirs(logs_dir)

inputxml =  inputxml  = "%s/%s_mediainfo.xml" % (metadata_dir,os.path.basename(input) )
print inputxml
def make_mediainfo(xmlfilename, xmlvariable, inputfilename):
    with open(xmlfilename, "w+") as fo:
        xmlvariable = subprocess.check_output(['mediainfo',
                        '-f',
                        '--language=raw', # Use verbose output.
                        '--output=XML',
                        inputfilename])       #input filename
        fo.write(xmlvariable)
        
make_mediainfo(inputxml,'mediaxmlinput',input)



subprocess.call(['ffmpeg',    # Create decoded md5 checksums for every frame of the ffv1 output
                        '-i',input,
                        '-report',
                        '-f','framemd5',
                        framemd5 ])   
shutil.copy(input, desktop_dir)   

def remove_bad_files(root_dir):
    rm_these = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
    for root, dirs, files in os.walk(root_dir):
        for name in files:
            path = os.path.join(root, name)
            for i in rm_these:
                if name == i:
                    print '***********************' + 'removing: ' + path
                    os.remove(path)
                    
remove_bad_files(parent_dir)  
shutil.move(input,aeo_raw_extract_wav_dir + '/' + os.path.basename(input)) 
os.chdir(parent_dir)  
log_files =  glob('*.txt')                
for i in log_files:
   
        shutil.move(i, '%s/%s' % (logs_dir,i))             
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
make_manifest(parent_dir,manifest)   