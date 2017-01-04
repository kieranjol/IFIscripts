import subprocess
import sys
import base64
import time
import smtplib
import mimetypes
import getpass
import os
import filecmp
import hashlib
import datetime
from glob import glob
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import csv

def diff_textfiles(source_textfile, other_textfile):
    if filecmp.cmp(source_textfile, other_textfile, shallow=False):
        print "YOUR FILES ARE LOSSLESS YOU SHOULD BE SO HAPPY!!!"
        return 'lossless'

    else:
    	print "CHECKSUM MISMATCH - Further information on the next line!!!"
        return 'lossy'
    	#sys.exit()                 # Script will exit the loop if transcode is not lossless.


def make_mediainfo(xmlfilename, xmlvariable, inputfilename):
  with open(xmlfilename, "w+") as fo:
  	xmlvariable = subprocess.check_output(['mediainfo',
  						'-f',
  						'--language=raw','--File_TestContinuousFileNames=0', # Use verbose output.
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
    var_type = subprocess.check_output(['mediainfo',
                                        '--Language=raw',
                                        '--Full',
                                        type,
                                        filename ]).replace('\n', '')
    return var_type
# example - duration =  get_mediainfo('duration', '--inform=General;%Duration_String4%', sys.argv[1] )

def send_gmail(email_to, attachment, subject, email_body, email_address, password):
    emailfrom = ""
    emailto = email_to
    #emailto = ", ".join(emailto)
    fileToSend = attachment
    username = email_address
    password = password


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
    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)


    server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server_ssl.ehlo() # optional, called by login()
    server_ssl.login(username, password)
    # ssl server doesn't support or need tls, so don't call server_ssl.starttls()
    server_ssl.sendmail(emailfrom, emailto, msg.as_string())
    print msg.as_string()
    #server_ssl.quit()
    server_ssl.close()
    print 'successfully sent the mail'

def frames_to_seconds(audio_entry_point):
    audio_frame_count  = float(audio_entry_point)
    audio_frame_count  = float(audio_frame_count) / 24.000 # Change to EditRate variable.
    audio_frame_count  = round(audio_frame_count, 3)
    return audio_frame_count


def set_environment(logfile):
    env_dict = os.environ.copy()
    # https://github.com/imdn/scripts/blob/0dd89a002d38d1ff6c938d6f70764e6dd8815fdd/ffmpy.py#L272
    env_dict['FFREPORT'] = 'file={}:level=48'.format(logfile)
    return env_dict


def generate_log(log, what2log):
    if not os.path.isfile(log):
        with open(log,"wb") as fo:
            fo.write(time.strftime("%Y-%m-%dT%H:%M:%S ")
            + getpass.getuser()
            + ' ' + what2log + ' \n')
    else:
        with open(log,"ab") as fo:
            fo.write(time.strftime("%Y-%m-%dT%H:%M:%S ")
            + getpass.getuser()
            + ' ' + what2log + ' \n')


def hashlib_md5(filename):
   read_size = 0
   last_percent_done = 0
   m = hashlib.md5()
   total_size = os.path.getsize(filename)
   with open(str(filename), 'rb') as f:
       while True:
           buf = f.read(2**20)
           if not buf:
               break
           read_size += len(buf)
           m.update(buf)
           percent_done = 100 * read_size / total_size
           if percent_done > last_percent_done:
               sys.stdout.write('[%d%%]\r' % percent_done)
               sys.stdout.flush()


               last_percent_done = percent_done
   md5_output = m.hexdigest()
   return md5_output

def hashlib_manifest(manifest_dir, manifest_textfile, path_to_remove):
    file_count = 0
    for root, directories, filenames in os.walk(manifest_dir):
            filenames = [f for f in filenames if not f[0] == '.']
            directories[:] = [d for d in directories if not d[0] == '.']
            for files in filenames:
                    print "Calculating number of files to process in current directory -  %s files        \r"% file_count,
                    file_count +=1
    manifest_generator = ''
    md5_counter = 1
    for root, directories, filenames in os.walk(manifest_dir):
        filenames = [f for f in filenames if not f[0] == '.']
        directories[:] = [d for d in directories if not d[0] == '.']
        for files in filenames:
            print 'Generating MD5 for %s - file %d of %d' % (os.path.join(root,files), md5_counter, file_count)
            md5 = hashlib_md5(os.path.join(root, files))
            md5_counter +=1
            root2 = os.path.abspath(root).replace(path_to_remove, '')
            try:
                if root2[0] == '/':
                    root2 = root2[1:]
                if root2[0] == '\\':
                    root2 = root2[1:]
            except: IndexError
            manifest_generator +=    md5[:32] + '  ' + os.path.join(root2,files).replace("\\", "/") + '\n'
    manifest_list = manifest_generator.splitlines()
    files_in_manifest = len(manifest_list)
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list,  key=lambda x:(x[34:]))
    with open(manifest_textfile,"wb") as fo:
        for i in manifest_list:
            fo.write(i + '\n')


def make_manifest(manifest_dir, relative_manifest_path, manifest_textfile):
    os.chdir(manifest_dir)
    if not os.path.isfile(manifest_textfile):

        manifest_generator = subprocess.check_output(['md5deep', '-ler', relative_manifest_path])
        manifest_list = manifest_generator.splitlines()
        files_in_manifest = len(manifest_list)
        # http://stackoverflow.com/a/31306961/2188572
        manifest_list = sorted(manifest_list,  key=lambda x:(x[34:]))
        with open(manifest_textfile,"wb") as fo:
            for i in manifest_list:
                fo.write(i + '\n')
        return files_in_manifest
    else:
        print 'Manifest already exists'
        sys.exit()
def make_mediatrace(tracefilename, xmlvariable, inputfilename):
    with open(tracefilename, "w+") as fo:
        xmlvariable = subprocess.check_output(['mediainfo',
                        '-f',
                        '--Details=1','--File_TestContinuousFileNames=0', # Use verbose output.
                        '--output=XML',
                        inputfilename])       #input filename
        fo.write(xmlvariable)



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

def create_csv(csv_file, *args):
    f = open(csv_file, 'wb')
    try:
        writer = csv.writer(f)
        writer.writerow(*args)
    finally:
        f.close()


def append_csv(csv_file, *args):
    f = open(csv_file, 'ab')
    try:
        writer = csv.writer(f)
        writer.writerow(*args)
    finally:
        f.close()


def make_desktop_manifest_dir():
    desktop_manifest_dir = os.path.expanduser("~/Desktop/moveit_manifests")
    if not os.path.isdir(desktop_manifest_dir):
        #I should probably ask permission here, or ask for alternative location
        os.makedirs(desktop_manifest_dir)
    return desktop_manifest_dir


def make_desktop_logs_dir():
    desktop_logs_dir = os.path.expanduser("~/Desktop/ifiscripts_logs")
    if not os.path.isdir(desktop_logs_dir):
        #I should probably ask permission here, or ask for alternative location
        os.makedirs(desktop_logs_dir)
    return desktop_logs_dir

def get_image_sequence_files(directory):
    # This function accepts a directory as input, and checks returns a list of files in an image sequence.
    os.chdir(directory)
    tiff_check = glob('*.tiff')
    dpx_check = glob('*.dpx')
    tif_check = glob('*.tif')
    if len(dpx_check) > 0:
        images = dpx_check
        images.sort()
    elif len(tiff_check) > 0:
        images = tiff_check
        images.sort()
    elif len(tif_check) > 0:
        images = tif_check
        images.sort()
    else:
        return 'none'
    return images

def get_ffmpeg_friendly_name(images):
    if '864000' in images[0]:
        start_number = '864000'
    elif len(images[0].split("_")[-1].split(".")) > 2:
        start_number = images[0].split("_")[-1].split(".")[1]
    else:
        start_number = images[0].split("_")[-1].split(".")[0]
    container               = images[0].split(".")[-1]
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
    return ffmpeg_friendly_name, container, start_number
    
def get_date_modified(filename):
    """Gets the date modified date of a filename in ISO8601 style.

    Date created values seem to be difficult to grab in a cross-platform way.


        Args:
            filename: Path of filename to check.

        Returns:
            date_modified: string, for example '2016-12-19T21:30:43'

        """
    epoch_time = os.path.getmtime(filename)
    date_modified =  datetime.datetime.fromtimestamp(epoch_time).strftime("%Y-%m-%dT%H:%M:%S")
    return date_modified