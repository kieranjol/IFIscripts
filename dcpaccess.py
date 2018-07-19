#!/usr/bin/env python

import sys
try:
    from lxml import etree
except ImportError:
    print ('*** ERROR - LXML IS MISSING ***\nThis external module is required for xml parsing.\nInstall with  `pip install lxml`.\nYou may need to restart your terminal or your computer, but it should work immediately.\nYou may need to run `sudo pip install lxml` on some osx/linux machines.\n If having issues installing lxml on windows, download the relevant .whl file from here http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml and run `pip install /path/to/lxml_filename.whl')
    sys.exit()
import pdb
from glob import glob
import csv
import os
from os import listdir
from os.path import isfile, join
import subprocess
import base64
import time
import re
import smtplib
import argparse
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import tempfile
from decimal import *
from sys import platform as _platform
getcontext().prec = 4

# Use argparse for command line options.
parser = argparse.ArgumentParser(description='Unencrypted DCP to H264 transcoder.'
                                 ' Written by Kieran O\'Leary.')
parser.add_argument('input')
'''
parser.add_argument(
                    '-bag', 
                    action='store_true',help='bag the dcp_dir if it passes the hash check')
'''
parser.add_argument(
                    '-m', 
                    action='store_true',help='send email report')
parser.add_argument(
                    '-s', 
                    action='store_true',help='Burn in subtitles. This will take a long time. It makes more sense to make a clean copy first, then make subtitled surrogates from that new copy. Jpeg2000 decoding is slow, ProRes or h264 is significantly faster.')
parser.add_argument(
                    '-p', 
                    action='store_true',help='Use Apple ProRes 4:2:2 HQ instead of H264')
parser.add_argument(
                    '-hd',
                    action='store_true',help='Scale to 1920:1080 while preserving the aspect ratio')
args = parser.parse_args()
'''
if args.bag:
    bagging = 'enabled'
else:
    bagging = 'disabled'
'''

if args.m:
    email = 'enabled'
else:
    email = 'disabled'
if args.s:
    print( '***********************************************')
    print ('You have chosen to burn in subtitles. This will take a long time. A better approach may be to make a clean transcode to a high quality format such as PRORES and make further clean or subtitled surrogates from that new copy. ')
    print ('***********************************************')
    time.sleep(1)
lut_path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), '26_XYZ-22_Rec709.cube')
# Set a bunch of variables for filenaming.    
dcp_dir               = args.input
# This temp directory should work on all operating systems. 
temp_dir              = tempfile.gettempdir()
video_concat_filename = os.path.basename(dcp_dir) + '_video_concat' + time.strftime("_%Y_%m_%dT%H_%M_%S")
audio_concat_filename = os.path.basename(dcp_dir) + '_audio_concat' + time.strftime("_%Y_%m_%dT%H_%M_%S")
# Slashes are significant for ffmpeg concat files.
if _platform == "win32":
    video_concat_textfile = os.path.expanduser("~\Desktop\%s.txt") % video_concat_filename
    audio_concat_textfile = os.path.expanduser("~\Desktop\%s.txt") % audio_concat_filename
else:
    video_concat_textfile = temp_dir + "/%s.txt" % video_concat_filename
    audio_concat_textfile = temp_dir + "/%s.txt" % audio_concat_filename
    

def find_assetmap():   
    if 'ASSETMAP' in dcp_files:
        assetmap = 'ASSETMAP'
    elif 'ASSETMAP.xml' in dcp_files:
        assetmap = 'ASSETMAP.xml'
    return assetmap
        
        
# Begin recursive search through sub-directories for DCPs.  
def choose_cpl(): 
    global cpl_list
    # Some DCPs have multiple CPLs!       
    cpl_number = 1
    print ('Multiple CPL files found')
    for i in cpl_list:
        print (cpl_number,  i)
        cpl_number += 1   
    print( 'Please select which CPL you would like to process')
    chosen_cpl = raw_input()
    cpl_parse = etree.parse(cpl_list[int(chosen_cpl) - 1]) # The -1 is due to python zero-indexing.
    if args.s:
        cpl_namespace      = cpl_parse.xpath('namespace-uri(.)') 
        subtitle_language  =  cpl_parse.findall('//ns:MainSubtitle/ns:Language',namespaces={'ns': cpl_namespace})
        print( 'This CPL contains ', subtitle_language[0].text, ' subtitles. Proceed?')         
    return cpl_parse 
    
    
def find_cpl():
    # Generate an empty list as there may be multiple CPLs.    
    # Get a list of all XML files in the main DCP directory.
    xmlfiles = glob('*.xml')
    # Loop through xmlfiles in order to find any CPLL files.
    for i in xmlfiles:
        try:  
            xmlname = etree.parse(i)
        except SyntaxError:
            print( 'not a valid CPL!')
            continue
        except KeyError:
            print( 'Missing CPL!')
            continue
        xml_namespace = xmlname.xpath('namespace-uri(.)')
        # Create list of CPLs.
        if 'CPL' in xml_namespace:
            cpl_list.append(i) 
        if len(cpl_list) == 0:  
            continue
        elif len(cpl_list) == 1:
            cpl_parse = etree.parse(cpl_list[0])
    if len(cpl_list) > 1:
        cpl_parse = choose_cpl() 
        # As there can be multiple subtitles, This options gives some info/choice.
        subs_confirmation  = raw_input('Y/N')       
        while subs_confirmation not in ['Y','y']:
            cpl_parse = choose_cpl()
            subs_confirmation  = raw_input('Y/N')    
            return cpl_parse
        return cpl_parse    
    else:
        return cpl_parse  

        
def delay_check(media_type,cpl_parse, cpl_namespace ):
    # Check if there is an intended audio delay.
    count   = cpl_parse.xpath('count(//ns:%s/ns:EntryPoint)' % media_type,namespaces={'ns': cpl_namespace} )
    xmluuid_list               = cpl_parse.xpath('//ns:%s/ns:Id' % media_type,namespaces={'ns': cpl_namespace})
    EntryPoint_list            = cpl_parse.xpath('//ns:%s/ns:EntryPoint' % media_type,namespaces={'ns': cpl_namespace})
    dur_list                   = cpl_parse.xpath('//ns:%s/ns:Duration' % media_type,namespaces={'ns': cpl_namespace})
    dur_intrinsic_list         = cpl_parse.xpath('//ns:%s/ns:IntrinsicDuration' % media_type,namespaces={'ns': cpl_namespace})
    counter = 0
    delays  = 0
    audio_delay = {}
    while counter < count:
        audio_delay_values = []
        xmluuid = xmluuid_list[counter]
        EntryPoint = EntryPoint_list[counter]
        entrypoint_audio      = float(EntryPoint.text)
        if EntryPoint.text != '0':
            delays += 1
            # EntryPoint is in frames. The following converts to seconds.
            entrypoint_audio  = float(EntryPoint.text) 
            entrypoint_audio  = float(entrypoint_audio) / float(fps) # Change to EditRate variable.
            entrypoint_audio  = round(entrypoint_audio, 3)
        audio_delay_values.append(entrypoint_audio) 
        dur                   = dur_list[counter]
        dur_intrinsic         = dur_intrinsic_list[counter]
        tail_test             = int(dur_intrinsic.text) - int(dur.text)
        if tail_test > 0:
            delays +=1
        tail_delay = int(dur.text)
        tail_delay = float(tail_delay) / float(fps)
        tail_delay = round(tail_delay, 3)
        audio_delay_values.append(tail_delay)
        audio_delay_values.append(file_paths[xmluuid.text][0])
        # audio_delay stores [entrypoint, tail_delay, file_path]
        audio_delay[xmluuid.text] = audio_delay_values
        counter += 1
    test_list = []
    test_list.append(audio_delay)
    test_list.append(delays)
    return test_list
            
            
def burn_subs():
    counter = 0
    subs_counter = 0
    count = len(subs)
    sub_delay = 1
    if not len(subs) == len(pic_mxfs):
        print('The amount of picture files does not equal the amount of subtitles. This feature is not supported yet. Sorry!')
        sub_delay = 0
        # This assumes that if there are less subtitles than video files, it's because there's an extra AV reel at the head.A more robust option will be added later. Right now this fixes the one use case I've seen.
    if delays != 0:
        for i in audio_delay:
            # Wrapping PCM in matroska as WAV has 4 gig limit.
            subprocess.call(['ffmpeg','-ss',str(audio_delay[i][0]),
            '-i',audio_delay[i][2],'-t',str(audio_delay[i][1]),
            '-c:a','copy', temp_dir + '/'+ audio_delay[i][2] + '.mkv'])    
    while counter < count:
        srt_file = temp_dir + '/' + os.path.basename(subs[subs_counter]) +'.srt'
        output_filename = os.path.basename(dcp_dir) + '_subs_reel' + str(counter + 1) + time.strftime("_%Y_%m_%dT%H_%M_%S")
        output_subs_mkv = os.path.expanduser("~/Desktop/%s.mkv") % output_filename
        try:  
            xmlo = etree.parse(subs[subs_counter])
        except SyntaxError:
            if 'mxf' in srt_file:
                print('Subtitle file is most likely an SMPTE MXF which is not currently supported.')
            else:
                print ('not a valid CPL!')
            counter +=1
            continue
        except KeyError:
            print ('Missing CPL!')
            counter +=1
            continue
        sub_count = int(xmlo.xpath('count(//Subtitle)'))
        current_sub_counter = 0
        with open(srt_file, "w") as myfile:
               print ('Transforming ', sub_count, 'subtitles')
        while current_sub_counter < sub_count:
            counter2 = current_sub_counter +1
            in_point = xmlo.xpath('//Subtitle')[current_sub_counter].attrib['TimeIn']
            out      = xmlo.xpath('//Subtitle')[current_sub_counter].attrib['TimeOut']
            in_point = in_point[:8] + '.' + in_point[9:]
            out      = out[:8] + '.' + out[9:]
            with open(srt_file, "a") as myfile:
                myfile.write(str(current_sub_counter + 1) + '\n')
                myfile.write(in_point + ' --> ' + out + '\n')
                bla =  [bla.text for bla in xmlo.iterfind('.//Subtitle[%s]//Text' % int(counter2) ) ]
                for i in bla:
                        myfile.write(i.encode("utf-8") + '\n')
                myfile.write('\n')
                print( 'Transforming ' + str(current_sub_counter) + ' of' + str(count) + ' subtitles\r') ,
            current_sub_counter +=1 
        current_sub_counter= 0
        os.chdir(os.path.dirname(lut_path))
        if delays == 0:
            print( 'There were no audio delays.')
            command = ['ffmpeg','-c:v ','libopenjpeg','-i',pic_mxfs[counter],'-i',aud_mxfs[counter],
            '-c:a','copy', '-c:v', 'libx264', '-vf', 'lut3d=26_XYZ-22_Rec709.cube']
        else:
            command = ['ffmpeg','-c:v ','libopenjpeg','-i',pic_mxfs[counter],'-i',temp_dir + '/' + aud_mxfs[counter] + '.mkv',
            '-c:a','copy', '-c:v', 'libx264','-vf', 'lut3d=26_XYZ-22_Rec709.cube']
        pix_fmt = ['-pix_fmt','yuv420p']   
        subs_command =  ['-vf', 'format=yuv420p,subtitles=%s' % srt_file]
        if sub_delay > 0:
            command += subs_command
            sub_delay += 1
            subs_counter +=1
        elif sub_delay == 0:
            command += pix_fmt
            subs_counter = 0
            sub_delay += 1
        command += [output_subs_mkv ]
        print (command)
        subprocess.call(command)
        counter += 1 
    sys.exit()
    
    
def concat():
            # Create concat file. There is definitely a better way of doing this. Patch welcome ;)
            if _platform == "win32":
                dir_append    = dir + '\\'
                concat_string = 'file \'' 
                concat_append = '\''
            else:
                dir_append    = dir + '/'
                concat_string = 'file \'' 
                concat_append = '\''
            if num_video_delays == 0:
                picture_files_fix1 = [dir_append + x for x in pic_mxfs]
            else:
                picture_files_fix1 = [temp_dir + '/' + x + '.mkv' for x in pic_mxfs]
            # http://stackoverflow.com/a/2050721/2188572
            picture_files_fix2 = [concat_string + x for x in picture_files_fix1]
            finalpic           = [x + concat_append for x in picture_files_fix2]
            if num_audio_delays == 0:
                audio_files_fix1 = [dir_append + x  for x in aud_mxfs]
            else:
                audio_files_fix1 = [temp_dir + '/' + x + '.mkv' for x in aud_mxfs]
            audio_files_fix2     = [concat_string + x for x in audio_files_fix1]
            finalaudio           = [x + concat_append for x in audio_files_fix2]
            concat_list = []
            concat_list.append(finalaudio)
            concat_list.append(finalpic)   
            return concat_list 
            
            
def send_gmail():
    emailfrom = ""
    emailto = ['', '']
    #emailto = ", ".join(emailto)
    fileToSend = ''
    username = ""
    password = ""

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = ", ".join(emailto)
    msg["Subject"] = "Hash check complete"
    msg.preamble = "testtesttest"
    body = MIMEText("example email body")
    msg.attach(body)

    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    if maintype == "text":
        fp = open(fileToSend)
        # Note: we should handle calculating the charset
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "image":
        fp = open(fileToSend, "rb")
        attachment = MIMEImage(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "audio":
        fp = open(fileToSend, "rb")
        attachment = MIMEAudio(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(fileToSend, "rb")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)


    server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server_ssl.ehlo() # optional, called by login()
    server_ssl.login(username, password)  
    # ssl server doesn't support or need tls, so don't call server_ssl.starttls() 
    server_ssl.sendmail(emailfrom, emailto, msg.as_string())
    print(msg.as_string())
    #server_ssl.quit()
    server_ssl.close()
    print ('successfully sent the mail')  
    
# Write the list of filenames containing picture to a textfile. 
# http://www.pythonforbeginners.com/files/reading-and-writing-files-in-python
def write_textfile(textfile, list_type):
    file = open(textfile, "w")
    for item in list_type:
      file.write("%s\n" % item)
    file.close()  # ffmpeg can't access the textfile until it's closed.   
          
for root,dirnames,filenames in os.walk(dcp_dir):
    if ("ASSETMAP.xml"  in filenames) or ("ASSETMAP"  in filenames) :
        dir = root
        output_filename       = os.path.basename(dir) + '_muxed' + time.strftime("_%Y_%m_%dT%H_%M_%S")
        output                = os.path.expanduser("~/Desktop/%s.mkv") % output_filename
        if args.p:
           codec = ['prores','-profile:v','3', '-c:a', 'copy']
           output      = os.path.expanduser("~/Desktop/%s.mov") % output_filename
        else:   
           codec = ['libx264','-pix_fmt','yuv420p', '-crf', '19' ,'-preset','veryfast', '-c:a', 'aac']
        # Change directory to directory with video files.
        # Changing directory makes globbing easier (from my experience anyhow).
        os.chdir(dir)

        # Scan the main DCP directory for an assetmap. 
        dcp_files = [f for f in listdir(dir) if isfile(join(dir, f))]
        assetmap  = find_assetmap()

        # Parse the assetmap in order to find the namespace.  
        try:  
            assetmap_xml = etree.parse(assetmap)
        except SyntaxError:

            print('Not a valid ASSETMAP!')
            continue
           
        assetmap_namespace = assetmap_xml.xpath('namespace-uri(.)')     

        cpl_list = []

        cpl_parse = find_cpl() 
    
        cpl_namespace = cpl_parse.xpath('namespace-uri(.)') 
        subtitle_language    =  cpl_parse.findall('//ns:MainSubtitle/ns:Language',namespaces={'ns': cpl_namespace})  
        xmluuid              =  cpl_parse.findall('//ns:MainPicture/ns:Id',namespaces={'ns': cpl_namespace})
        xmluuid_audio        =  cpl_parse.findall('//ns:MainSound/ns:Id',namespaces={'ns': cpl_namespace})
        xmluuid_subs         =  cpl_parse.findall('//ns:MainSubtitle/ns:Id',namespaces={'ns': cpl_namespace})
        duration_image       =  cpl_parse.findall('//ns:MainPicture/ns:Duration',namespaces={'ns': cpl_namespace})
        duration_audio       =  cpl_parse.findall('//ns:MainSound/ns:Duration',namespaces={'ns': cpl_namespace})
        intrinsic_image      =  cpl_parse.findall('//ns:MainPicture/ns:IntrinsicDuration',namespaces={'ns': cpl_namespace})
        intrinsic_audio      =  cpl_parse.findall('//ns:MainSound/ns:IntrinsicDuration',namespaces={'ns': cpl_namespace})
        entry_image          =  cpl_parse.findall('//ns:MainPicture/ns:EntryPoint',namespaces={'ns': cpl_namespace})
        entry_audio          =  cpl_parse.findall('//ns:MainSound/ns:EntryPoint',namespaces={'ns': cpl_namespace})
        
        video_fps            =  cpl_parse.xpath('//ns:MainPicture/ns:EditRate',namespaces={'ns': cpl_namespace})
        for i in video_fps:
            fps = i.text[:-1]
        # http://stackoverflow.com/questions/37038148/extract-value-from-element-when-second-namespace-is-used-in-lxml/37038309
        # Some DCPS use a specific namespace for closed captions.
        if len(xmluuid_subs) == 0:
            xmluuid_subs = cpl_parse.xpath('//proto2007:MainClosedCaption/proto2004:Id', namespaces={
                'proto2004': 'http://www.digicine.com/PROTO-ASDCP-CPL-20040511#',
                'proto2007': 'http://www.digicine.com/PROTO-ASDCP-CC-CPL-20070926#',
            })
        
        audio_delay = {}
        file_paths  = {} 
        # Begin analysis of assetmap xml.

        assetmap_paths =  assetmap_xml.findall('//ns:Path',namespaces={'ns': assetmap_namespace})
        assetmap_uuids =  assetmap_xml.findall('//ns:Asset/ns:Id',namespaces={'ns': assetmap_namespace})
            
        counter = 0 
        while counter <= len(assetmap_paths) -1 :

            if 'file:///' in assetmap_paths[counter].text:
                remove_this = 'file:///'
                assetmap_paths[counter].text =  assetmap_paths[counter].text.replace(remove_this,"")
            elif 'file://' in assetmap_paths[counter].text:
                remove_this = 'file://'
                assetmap_paths[counter].text =  assetmap_paths[counter].text.replace(remove_this,"")            

            elif 'file:/' in assetmap_paths[counter].text:
                remove_this = 'file:/'
                assetmap_paths[counter].text =  assetmap_paths[counter].text.replace(remove_this,"")           

            file_paths[assetmap_uuids[counter].text] = [assetmap_paths[counter].text] # {assetmapuuid:assetmapfilename}
            counter += 1
            
        pic_mxfs = [] 
          
        for pic_uuid_object in xmluuid:
            for pic_uuid in file_paths[pic_uuid_object.text]:            
                pic_mxfs.append(pic_uuid)
                 
        aud_mxfs = []   
        for aud_uuid_object in xmluuid_audio:
            for aud_uuid in file_paths[aud_uuid_object.text]:            
                aud_mxfs.append(aud_uuid)


        subs = []   
        for sub_uuid_object in xmluuid_subs:
            for sub_uuid in file_paths[sub_uuid_object.text]:            
                subs.append(sub_uuid)
    
        audio_delay_info = delay_check('MainSound',cpl_parse, cpl_namespace)
        video_delay_info = delay_check('MainPicture',cpl_parse, cpl_namespace)

        audio_delay      = audio_delay_info[0]
        num_audio_delays  = audio_delay_info[1]
        video_delay      = video_delay_info[0]
        num_video_delays  = video_delay_info[1]

        if args.s:
            burn_subs()
        concat_list = concat()
        finalaudio  = concat_list[0]
        finalpic    = concat_list[1]
        if num_audio_delays == 0:
            print( 'There were no audio delays.')
        else:
            for i in audio_delay:
                print( 'rewrapping')
                # Wrapping PCM in matroska as WAV has 4 gig limit.
                rewrap = ['ffmpeg','-ss',str(audio_delay[i][0]),'-c:v ','libopenjpeg',
                '-i',audio_delay[i][2],'-t',str(audio_delay[i][1]),
                '-c:a','copy', temp_dir + '/'+ audio_delay[i][2] + '.mkv']
                print rewrap
                subprocess.call(rewrap)
        if num_video_delays == 0:
            print( 'There were no video delays.')
        else:
            for i in video_delay:
                print( 'rewrapping')
                # Wrapping PCM in matroska as WAV has 4 gig limit.
                rewrap = ['ffmpeg','-ss',str(video_delay[i][0]),'-c:v ','libopenjpeg',
                '-i',video_delay[i][2],'-t',str(video_delay[i][1]),
                '-c:v','copy', temp_dir + '/'+ video_delay[i][2] + '.mkv']
                print(rewrap)
                subprocess.call(rewrap)        
        write_textfile(video_concat_textfile, finalpic)
        write_textfile(audio_concat_textfile, finalaudio)
        os.chdir(os.path.dirname(lut_path))
        command = ['ffmpeg','-f','concat','-safe', '0','-c:v ','libopenjpeg',
                   '-i',video_concat_textfile,'-f','concat','-safe', '0',
                   '-i',audio_concat_textfile, '-vf', 'lut3d=./26_XYZ-22_Rec709.cube','-c:v']

        command += codec
        if args.hd:
            command += ['-vf', "scale=1920:-1,setsar=1/1,pad=1920:1080:0:(oh-ih)/2,lut3d=26_XYZ-22_Rec709.cube"]
        command += [output]
        print (command)
        subprocess.call(command)        
        # Removes PKLs from list of files to hash, as these files are not in manifest.

if email == 'enabled': 
    send_gmail()

