#!/usr/bin/env python
import subprocess
import sys
import os
import hashlib
import shutil
from glob import glob
from premis import make_premis
from premis import write_premis
from premis import make_agent
from premis import make_event
import uuid

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
           
input = sys.argv[1]
desktop_dir = os.path.expanduser("~/Desktop/%s") % os.path.basename(input)
parent_dir = os.path.dirname(input)
root_dir = os.path.dirname(os.path.dirname(parent_dir))
metadata_dir = root_dir + '/metadata/audio'
logs_dir = root_dir + '/logs/audio'

aeo_raw_extract_wav_dir = root_dir + '/objects/audio'
framemd5 = metadata_dir + '/' + os.path.basename(input) +'.framemd5'
logfile = logs_dir + '/' + os.path.basename(input) + '_framemd5.log'
normpath = os.path.normpath(root_dir)
relative_path = normpath.split(os.sep)[-1]
manifest =  '%s_manifest.md5' % (relative_path)

filenoext = os.path.splitext(input)[0]

inputxml =  inputxml  = "%s/%s_mediainfo.xml" % (metadata_dir,os.path.basename(input) )
print inputxml

        
make_mediainfo(inputxml,'mediaxmlinput',input)


env_dict = set_environment(logfile)
ffmpegcmd = ['ffmpeg',    # Create decoded md5 checksums for every frame of the ffv1 output
                        '-i',input,
                        '-report',
                        '-f','framemd5',
                        framemd5 ]
subprocess.call(ffmpegcmd,env=env_dict)   
shutil.copy(input, desktop_dir)                       
remove_bad_files(parent_dir)  
os.chdir(parent_dir)  
log_files =  glob('*.txt')                
for i in log_files:
   
        shutil.move(i, '%s/%s' % (logs_dir,i))             

make_manifest(parent_dir,manifest)
split_list = root_dir.split('_')
items = {"workflow":"raw audio","oe":split_list[0], "filmographic":split_list[1], "sourceAccession":split_list[2], "interventions":['placeholder'], "prepList":['placeholder'], "user":'Brian Cash'}
xml_info    = make_premis(aeo_raw_extract_wav_dir, items)
doc         = xml_info[0]
premisxml   = xml_info[1]
premis = doc.getroot()
capture_uuid                                = str(uuid.uuid4())
capture_received_uuid                       = str(uuid.uuid4())
premis_checksum_uuid                        = str(uuid.uuid4())
framemd5_uuid                               = str(uuid.uuid4())
aeolightAgent                               = make_agent(premis,capture_uuid, 'agentaa00005')
hashlibAgent                                = make_agent(premis,capture_uuid, 'agentaa00008')
operatorAgent                               = make_agent(premis,capture_uuid,items['user'])
macMiniTelecineMachineAgent                 = make_agent(premis,premis_checksum_uuid, 'agentaa00022')
macMiniTelecineOSAgent                      = make_agent(premis,premis_checksum_uuid, 'agentaa00011')
ffmpegAgent                                 = make_agent(premis,framemd5_uuid , 'agentaa00006')

make_event(premis, 'creation', 'PCM WAV file extracted from overscanned image area of source TIFF files', [aeolightAgent, operatorAgent, macMiniTelecineMachineAgent, macMiniTelecineOSAgent], capture_uuid,xml_info[2])
make_event(premis, 'message digest calculation', '', [hashlibAgent, operatorAgent,macMiniTelecineMachineAgent, macMiniTelecineOSAgent], premis_checksum_uuid,xml_info[2])
make_event(premis, 'message digest calculation', 'Frame level checksums', [ffmpegAgent, operatorAgent,macMiniTelecineMachineAgent, macMiniTelecineOSAgent], framemd5_uuid,xml_info[2] )
write_premis(doc, premisxml)
print premisxml