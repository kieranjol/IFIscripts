import subprocess
import sys
import base64
import time
import smtplib
import mimetypes
import getpass
import os
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

def make_mediainfo(xmlfilename, xmlvariable, inputfilename):
  with open(xmlfilename, "w+") as fo:
  	xmlvariable = subprocess.check_output(['mediainfo',
  						'-f',
  						'--language=raw', # Use verbose output.
  						'--output=XML',
  						inputfilename])       #input filename
  	fo.write(xmlvariable)


def make_qctools(input):
   
    qctools_args = ['ffprobe', '-f', 'lavfi', '-i',] 
    qctools_args += ["movie=%s:s=v+a[in0][in1],[in0]signalstats=stat=tout+vrep+brng,cropdetect=reset=1:round=1,split[a][b];[a]field=top[a1];[b]field=bottom[b1],[a1][b1]psnr[out0];[in1]ebur128=metadata=1,astats=metadata=1:reset=1:length=0.4[out1]" % input] 
    qctools_args += ['-show_frames', '-show_versions', '-of', 'xml=x=1:q=1', '-noprivate']
    print qctools_args
    qctoolsreport = subprocess.check_output(qctools_args)
    return qctoolsreport
   
def write_qctools_gz(qctoolsxml, sourcefile):
    with open(qctoolsxml, "w+") as fo:
        fo.write(make_qctools(sourcefile))
    subprocess.call(['gzip', qctoolsxml]) 
    
def get_audio_stream_count():
    audio_stream_count = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'flat', sys.argv[1]]).splitlines()
    return len(audio_stream_count)
def get_mediainfo(var_type, type, filename):
    var_type = subprocess.check_output(['MediaInfo', '--Language=raw', '--Full', type , filename ]).replace('\n', '')
    return var_type
# example - duration =  get_mediainfo('duration', '--inform=General;%Duration_String4%', sys.argv[1] )

def send_gmail(email_to, attachment, subject, email_body):
    emailfrom = ""
    emailto = email_to
    #emailto = ", ".join(emailto)
    fileToSend = attachment
    username = ""
    password = ""

    msg = MIMEMultipart()
    msg["From"]    = emailfrom
    msg["To"]      = ", ".join(emailto)
    msg["Subject"] = subject
    msg.preamble   = "testtesttest"
    body = MIMEText(email_body)
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
        
def frames_to_seconds(audio_entry_point):
    audio_frame_count  = float(audio_entry_point) 
    audio_frame_count  = float(audio_frame_count) / 24.000 # Change to EditRate variable.
    audio_frame_count  = round(audio_frame_count, 3)
    return audio_frame_count
def generate_log(log, what2log):
    if not os.path.isfile(log):
        with open(log,"wb") as fo:
            fo.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + getpass.getuser() + ' ' + what2log + ' \n')
    else:
        with open(log,"ab") as fo:
            fo.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + getpass.getuser() + ' ' + what2log + ' \n')

def make_manifest(manifest_dir, relative_manifest_path, manifest_textfile):
    os.chdir(manifest_dir)
    
    manifest_generator = subprocess.check_output(['md5deep', '-ler', relative_manifest_path])
    manifest_list = manifest_generator.splitlines()
    files_in_manifest = len(manifest_list)
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list,  key=lambda x:(x[34:])) 
    with open(manifest_textfile,"wb") as fo:
        for i in manifest_list:
            fo.write(i + '\n')
    return files_in_manifest
    
def check_overwrite(file2check):
    if os.path.isfile(file2check):
        print 'A manifest already exists at your destination. Overwrite? Y/N?'
        overwrite_destination_manifest = ''
        while overwrite_destination_manifest not in ('Y','y','N','n'):
            overwrite_destination_manifest = raw_input()
            if overwrite_destination_manifest not in ('Y','y','N','n'):
                print 'Incorrect input. Please enter Y or N'
        return overwrite_destination_manifest
def manifest_file_count(manifest2check):
    if os.path.isfile(manifest2check):
        print 'A manifest already exists'
        with open(manifest2check, "r") as fo:
            manifest_lines = [line.split(',') for line in fo.readlines()]
            count_in_manifest =  len(manifest_lines)
    return count_in_manifest