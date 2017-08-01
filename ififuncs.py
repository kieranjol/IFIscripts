#!/usr/bin/env python
'''
A collection of functions that other scripts can use.

'''
import subprocess
import sys
import time
import smtplib
import mimetypes
import getpass
import os
import filecmp
import hashlib
import datetime
import uuid
import tempfile
import csv
from glob import glob
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from lxml import etree

def diff_textfiles(source_textfile, other_textfile):
    '''
    Compares two textfiles. Returns strings that indicate losslessness.
    '''
    if filecmp.cmp(source_textfile, other_textfile, shallow=False):
        print "YOUR FILES ARE LOSSLESS YOU SHOULD BE SO HAPPY!!!"
        return 'lossless'

    else:
        print "CHECKSUM MISMATCH - Further information on the next line!!!"
        return 'lossy'


def make_mediainfo(xmlfilename, xmlvariable, inputfilename):
    '''
    Writes a verbose mediainfo XML output.
    '''
    mediainfo_cmd = [
        'mediainfo',
        '-f',
        '--language=raw',
        '--File_TestContinuousFileNames=0',
        '--output=XML',
        inputfilename
    ]
    with open(xmlfilename, "w+") as fo:
        xmlvariable = subprocess.check_output(mediainfo_cmd)
        fo.write(xmlvariable)


def make_mediaconch(full_path, mediaconch_xmlfile):
    '''
    Creates a mediaconch implementation check XML report.
    '''
    mediaconch_cmd = [
        'mediaconch',
        '-fx',
        full_path
    ]
    print 'Mediaconch is analyzing %s' % full_path
    mediaconch_output = subprocess.check_output(mediaconch_cmd)
    with open(mediaconch_xmlfile, 'wb') as xmlfile:
        xmlfile.write(mediaconch_output)


def make_qctools(input):
    '''
    Runs an ffprobe process that stores QCTools XML info as a variable.
    A file is not actually created here.
    '''
    qctools_args = ['ffprobe', '-f', 'lavfi', '-i',]
    qctools_args += ["movie=%s:s=v+a[in0][in1],[in0]signalstats=stat=tout+vrep+brng,cropdetect=reset=1:round=1,split[a][b];[a]field=top[a1];[b]field=bottom[b1],[a1][b1]psnr[out0];[in1]ebur128=metadata=1,astats=metadata=1:reset=1:length=0.4[out1]" % input]
    qctools_args += ['-show_frames', '-show_versions', '-of', 'xml=x=1:q=1', '-noprivate']
    print qctools_args
    qctoolsreport = subprocess.check_output(qctools_args)
    return qctoolsreport


def write_qctools_gz(qctoolsxml, sourcefile):
    '''
    This accepts a variable containing XML that is written to a file.
    '''
    with open(qctoolsxml, "w+") as fo:
        fo.write(make_qctools(sourcefile))
    subprocess.call(['gzip', qctoolsxml])


def get_audio_stream_count():
    '''
    Returns the number of audio streams in the form of an INT.
    '''
    ffprobe_cmd = [
        'ffprobe', '-v',
        'error', '-select_streams', 'a',
        '-show_entries', 'stream=index', '-of', 'flat',
        sys.argv[1]
    ]
    audio_stream_count = subprocess.check_output(ffprobe_cmd).splitlines()
    return len(audio_stream_count)


def get_mediainfo(var_type, type, filename):
    '''
    Uses mediainfo to extract a single item of metadata
    example:
    duration =  get_mediainfo(
        'duration', '--inform=General;%Duration_String4%', sys.argv[1]
    )
    '''
    mediainfo_cmd = [
        'mediainfo',
        '--Language=raw',
        '--Full',
        type,
        filename
    ]
    var_type = subprocess.check_output(mediainfo_cmd).replace('\n', '')
    return var_type


def get_milliseconds(filename):
    '''
    Returns a float with the duration of a file in milliseconds.
    '''
    milliseconds = get_mediainfo(
        'miliseconds',
        '--inform=General;%Duration%',
        filename
    )
    return float(milliseconds)

def convert_millis(milli):
    '''
    Accepts milliseconds and returns this value as HH:MM:SS.NNN
    '''
    a = datetime.timedelta(milliseconds=milli)
    b = str(a)
    # no millseconds are present if there is no remainder. We need milliseconds!
    if len(b) == 7:
        b += '.000000'
    timestamp = datetime.datetime.strptime(b, "%H:%M:%S.%f").time()
    c = str(timestamp)
    if len(c) == 8:
        c += '.000000'
    return str(c)[:-3]


def send_gmail(email_to, attachment, subject, email_body, email_address, password):
    '''
    Rarely used but working emailer.
    '''
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
    audio_frame_count = float(audio_entry_point)
    audio_frame_count = float(audio_frame_count) / 24.000 # Change to EditRate variable.
    audio_frame_count = round(audio_frame_count, 3)
    return audio_frame_count


def set_environment(logfile):
    env_dict = os.environ.copy()
    # https://github.com/imdn/scripts/blob/0dd89a002d38d1ff6c938d6f70764e6dd8815fdd/ffmpy.py#L272
    env_dict['FFREPORT'] = 'file={}:level=48'.format(logfile)
    return env_dict


def generate_log(log, what2log):
    if not os.path.isfile(log):
        with open(log, "wb") as fo:
            fo.write(time.strftime("%Y-%m-%dT%H:%M:%S ")
                     + getpass.getuser()
                     + ' ' + what2log + ' \n')
    else:
        with open(log, "ab") as fo:
            fo.write(time.strftime("%Y-%m-%dT%H:%M:%S ")
                     + getpass.getuser()
                     + ' ' + what2log + ' \n')


def hashlib_md5(filename):
    '''
    uses hashlib to return an MD5 checksum of an input filename
    '''
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
    '''
    Creates an MD5 manifest with relative filepaths.
    '''
    file_count = 0
    for root, directories, filenames in os.walk(manifest_dir):
        filenames = [f for f in filenames if not f[0] == '.']
        directories[:] = [d for d in directories if not d[0] == '.']
        for files in filenames:
            print "Calculating number of files to process in current directory -  %s files        \r"% file_count,
            file_count += 1
    manifest_generator = ''
    md5_counter = 1
    for root, directories, filenames in os.walk(manifest_dir):
        filenames = [f for f in filenames if f[0] != '.']
        directories[:] = [d for d in directories if d[0] != '.']
        for files in filenames:
            print 'Generating MD5 for %s - file %d of %d' % (os.path.join(root, files), md5_counter, file_count)
            md5 = hashlib_md5(os.path.join(root, files))
            md5_counter += 1
            root2 = os.path.abspath(root).replace(path_to_remove, '')
            try:
                if root2[0] == '/':
                    root2 = root2[1:]
                if root2[0] == '\\':
                    root2 = root2[1:]
            except: IndexError
            manifest_generator += md5[:32] + '  ' + os.path.join(root2, files).replace("\\", "/") + '\n'
    manifest_list = manifest_generator.splitlines()
    files_in_manifest = len(manifest_list)
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list, key=lambda x: (x[34:]))
    with open(manifest_textfile, "wb") as fo:
        for i in manifest_list:
            fo.write(i + '\n')


def hashlib_append(manifest_dir, manifest_textfile, path_to_remove):
    '''
    Lazy rehash of hashlib_manifest, except this just adds files to an existing manifest.
    '''
    file_count = 0
    for root, directories, filenames in os.walk(manifest_dir):
        filenames = [f for f in filenames if not f[0] == '.']
        directories[:] = [d for d in directories if not d[0] == '.']
        for files in filenames:
            print "Calculating number of files to process in current directory -  %s files        \r"% file_count,
            file_count += 1
    manifest_generator = ''
    md5_counter = 1
    for root, directories, filenames in os.walk(manifest_dir):
        filenames = [f for f in filenames if not f[0] == '.']
        directories[:] = [d for d in directories if not d[0] == '.']
        for files in filenames:
            print 'Generating MD5 for %s - file %d of %d' % (os.path.join(root, files), md5_counter, file_count)
            md5 = hashlib_md5(os.path.join(root, files))
            md5_counter += 1
            root2 = os.path.abspath(root).replace(path_to_remove, '')
            try:
                if root2[0] == '/':
                    root2 = root2[1:]
                if root2[0] == '\\':
                    root2 = root2[1:]
            except: IndexError
            manifest_generator += md5[:32] + '  ' + os.path.join(root2, files).replace("\\", "/") + '\n'
    manifest_list = manifest_generator.splitlines()
    files_in_manifest = len(manifest_list)
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list, key=lambda x: (x[34:]))
    with open(manifest_textfile, "ab") as fo:
        for i in manifest_list:
            fo.write(i + '\n')


def make_manifest(manifest_dir, relative_manifest_path, manifest_textfile):
    os.chdir(manifest_dir)
    if not os.path.isfile(manifest_textfile):

        manifest_generator = subprocess.check_output(['md5deep', '-ler', relative_manifest_path])
        manifest_list = manifest_generator.splitlines()
        files_in_manifest = len(manifest_list)
        # http://stackoverflow.com/a/31306961/2188572
        manifest_list = sorted(manifest_list, key=lambda x: (x[34:]))
        with open(manifest_textfile, "wb") as fo:
            for i in manifest_list:
                fo.write(i + '\n')
        return files_in_manifest
    else:
        print 'Manifest already exists'
        sys.exit()
def make_mediatrace(tracefilename, xmlvariable, inputfilename):
    with open(tracefilename, "w+") as fo:
        mediatrace_cmd = [
            'mediainfo',
            '-f',
            '--Details=1', '--File_TestContinuousFileNames=0', # Use verbose output.
            '--output=XML',
            inputfilename
        ]
        xmlvariable = subprocess.check_output(mediatrace_cmd)       #input filename
        fo.write(xmlvariable)



def check_overwrite(file2check):
    if os.path.isfile(file2check):
        print 'A manifest already exists at your destination. Overwrite? Y/N?'
        overwrite_destination_manifest = ''
        while overwrite_destination_manifest not in ('Y', 'y', 'N', 'n'):
            overwrite_destination_manifest = raw_input()
            if overwrite_destination_manifest not in ('Y', 'y', 'N', 'n'):
                print 'Incorrect input. Please enter Y or N'
        return overwrite_destination_manifest
def manifest_file_count(manifest2check):
    '''
    Checks how many entries are in a manifest
    '''
    if os.path.isfile(manifest2check):
        print 'A manifest already exists'
        with open(manifest2check, "r") as fo:
            manifest_lines = [line.split(',') for line in fo.readlines()]
            count_in_manifest = len(manifest_lines)
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
    else:
        if not os.path.isdir(os.path.join(desktop_manifest_dir, 'old_manifests')):
            os.makedirs(os.path.join(desktop_manifest_dir, 'old_manifests'))
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
    '''
    Parses image sequence filenames so that they are easily passed to ffmpeg.
    '''
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
        while  counter < len(numberless_filename):
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
    date_modified = datetime.datetime.fromtimestamp(epoch_time).strftime("%Y-%m-%dT%H:%M:%S")
    return date_modified


def create_uuid():
    '''
    Returns a randonly generated UUID as a string
    '''
    new_uuid = str(uuid.uuid4())
    return new_uuid

def make_folder_structure(path):
    '''
    Makes logs, objects, metadata directories in the supplied path
    '''
    metadata_dir = "%s/metadata" % path
    log_dir = "%s/logs" % path
    #old_manifests_dir = "%s/logs/old_manifests" % path
    data_dir = "%s/objects" % path
    # Actually create the directories.
    os.makedirs(metadata_dir)
    os.makedirs(data_dir)
    os.makedirs(log_dir)
    #os.makedirs(old_manifests_dir)


def get_user():
    '''
    Asks user who they are. Returns a string with their name
    '''
    user = ''
    if user not in ('1', '2', '3', '4', '5', '6'):
        user = raw_input(
            '\n\n**** Who are you?\nPress 1,2,3,4,5,6\n\n1. Brian Cash\n2. Gavin Martin\n3. Kieran O\'Leary\n4. Raelene Casey\n5. Aoife Fitzmaurice\n6. Felix Meehan\n'
        )
        while user not in ('1', '2', '3', '4', '5', '6'):
            user = raw_input(
                '\n\n**** Who are you?\nPress 1,2,3,4,5,6\n1. Brian Cash\n2. Gavin Martin\n3. Kieran O\'Leary\n4. Raelene Casey\n5. Aoife Fitzmaurice\n6. Felix Meehan\n'
            )
    if user == '1':
        user = 'Brian Cash'
        time.sleep(1)
    elif user == '2':
        user = 'Gavin Martin'
        time.sleep(1)
    elif user == '3':
        user = 'Kieran O\'Leary'
        time.sleep(1)
    elif user == '4':
        user = 'Raelene Casey'
        time.sleep(1)
    elif user == '5':
        user = 'Aoife Fitzmaurice'
        time.sleep(1)
    elif user == '6':
        user = 'Felix Meehan'
        print 'Cork baiiiiiiii'
        time.sleep(1)
    return user


def sort_manifest(manifest_textfile):
    '''
    Sorts an md5 manifest in alphabetical order.
    Some scripts like moveit.py will require a manifest to be ordered like this.
    '''
    with open(manifest_textfile, "r") as fo:
        manifest_lines = fo.readlines()
        with open(manifest_textfile,"wb") as ba:
            manifest_list = sorted(manifest_lines, key=lambda x: (x[34:]))
            for i in manifest_list:
                ba.write(i)

def concat_textfile(video_files, concat_file):
    '''
    Create concat textfile for all files in video_files
    a condition is needed elsewhere to ensure concat_file is empty
    '''
    for video in video_files:
        with open(concat_file, 'ab') as textfile:
            textfile.write('file \'%s\'\n' % video)


def sanitise_filenames(video_files):
    '''
    this just replaces quotes with underscores.
    only used right now to make concat scripts work.
    The change should only happen if user says YES
    previous and current filename should be logged.
    Also there should be a better way of returning the list.
    '''
    overwrite = ''
    renamed_files = []
    for video in video_files:
        if '\'' in video:
            print 'A quote is in your filename %s , replace with underscore?' % video
            while overwrite not in ('Y', 'y', 'N', 'n'):
                overwrite = raw_input()
                if overwrite not in ('Y', 'y', 'N', 'n'):
                    print 'Incorrect input. Please enter Y or N'
                if overwrite in ('Y', 'y'):
                    rename = video.replace('\'', '_')
                    os.rename(video, rename)
                    renamed_files.append(rename)
        else:
            renamed_files.append(video)
    return renamed_files


def get_temp_concat(root_name):
    '''
    generates a temp file as a textfile for ffmpeg concatenation.
    '''
    temp_dir = tempfile.gettempdir()
    video_concat_filename = os.path.basename(
        root_name) + '_video_concat' + time.strftime("_%Y_%m_%dT%H_%M_%S")
    # Slashes are significant for ffmpeg concat files.
    if sys.platform == "win32":
        video_concat_textfile = temp_dir + "\%s.txt" % video_concat_filename
    else:
        video_concat_textfile = temp_dir + "/%s.txt" % video_concat_filename
    return video_concat_textfile

def get_script_version(scriptname):
    '''
    uses git to get SHA:DATETIME for a script
    '''
    home = os.path.expanduser("~/")
    os.chdir(home)
    if os.path.isdir('ifigit/ifiscripts'):
        os.chdir('ifigit/ifiscripts')
        print("Changing directory to %s to extract script version`") %os.getcwd()
        script_version = subprocess.check_output([
            'git', 'log', '-n', '1', '--pretty=format:%H:%aI', scriptname
        ])
    return script_version


def validate_uuid4(uuid_string):

    """
    Validate that a UUID string is in
    fact a valid uuid4.

    Written by ShawnMilo
    https://gist.github.com/ShawnMilo/7777304#file-validate_uuid4-py
    """

    try:
        uuid.UUID(uuid_string, version=4)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        return False

def get_source_uuid():
    '''
    Asks user for uuid. A valid uuid must be provided.
    '''
    source_uuid = False
    while source_uuid is False:
        uuid_ = raw_input(
            '\n\n**** Please enter the UUID of the source representation\n\n'
        )
        source_uuid = validate_uuid4(uuid_)
    return uuid_

def get_object_entry():
    '''
    Asks user for an Object Entry number. A valid Object Entry (OE####) must be provided.
    '''
    object_entry = False
    while object_entry is False:
        object_entry = raw_input(
            '\n\n**** Please enter the object entry number of the representation\n\n'
        )
        if object_entry[:2] != 'oe':
            print 'First two characters must be \'oe\' and last four characters must be four digits'
            object_entry = False
        elif len(object_entry[2:]) != 4:
            object_entry = False
            print 'First two characters must be \'oe\' and last four characters must be four digits'
        elif not object_entry[2:].isdigit():
            object_entry = False
            print 'First two characters must be \'oe\' and last four characters must be four digits'
        else:
            return object_entry


def get_contenttitletext(cpl):
    '''
    Returns the <ContentTitleText> element text from a DCP CPL.xml
    '''
    cpl_parse = etree.parse(cpl)
    cpl_namespace = cpl_parse.xpath('namespace-uri(.)')
    contenttitletext = cpl_parse.findtext('//ns:ContentTitleText', namespaces={'ns': cpl_namespace})
    return contenttitletext


def find_cpl(source):
    '''
    Recursively searchs through all files in order to find a DCI DCP CPL XML.
    '''
    for root, _, filenames in os.walk(source):
        for filename in filenames:
            if filename.endswith('.xml'):
                if filename[0] != '.':
                    cpl_parse = etree.parse(os.path.join(root, filename))
                    cpl_namespace = cpl_parse.xpath('namespace-uri(.)')
                    if 'CPL' in cpl_namespace:
                        return os.path.join(root, filename)

def ask_yes_no(question):
    '''
    Returns Y or N. The question variable is just a string.
    '''
    answer = ''
    print '\n', question, '\n', 'enter Y or N'
    while answer not in ('Y', 'y', 'N', 'n'):
        answer = raw_input()
        if answer not in ('Y', 'y', 'N', 'n'):
            print 'Incorrect input. Please enter Y or N'
        if answer in ('Y', 'y'):
            return 'Y'
        elif answer in ('N,' 'n'):
            return 'N'

def manifest_replace(manifest, to_be_replaced, replaced_with):
    '''
    Replace strings in a checksum manifest (or any textfile)
    Ideally, this should never replace the checksum, just a path alteration.
    Although this could be useful for changing the logs checksum value.
    '''
    with open(manifest, 'r') as fo:
        original_lines = fo.readlines()
    with open(manifest, 'wb') as ba:
        for lines in original_lines:
            new_lines = lines.replace(to_be_replaced, replaced_with)
            ba.write(new_lines)

def manifest_update(manifest, path):
    '''
    Adds a new entry to your manifest and sort.
    '''
    manifest_generator = ''
    with open(manifest, 'r') as fo:
        original_lines = fo.readlines()
        md5 = hashlib_md5(path)
        path_to_remove = os.path.dirname(os.path.dirname(os.path.dirname(path)))
        root2 = os.path.abspath(path).replace(path_to_remove, '')
        try:
            if root2[0] == '/':
                root2 = root2[1:]
            if root2[0] == '\\':
                root2 = root2[1:]
        except: IndexError
        manifest_generator += md5[:32] + '  ' + root2.replace("\\", "/") + '\n'
        for i in original_lines:
            manifest_generator += i
    manifest_list = manifest_generator.splitlines()
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list, key=lambda x: (x[34:]))
    with open(manifest,"wb") as fo:
        for i in manifest_list:
            fo.write(i + '\n')

def check_for_uuid(args):
    '''
    Tries to check if a filepath contains a UUID.
    Returns false if an invalid UUID is found
    Returns the UUID if a UUID is found.
    '''
    source_uuid = False
    while source_uuid is False:
        if validate_uuid4(os.path.basename(args.i[0])) != False:
            return os.path.basename(args.i[0])
        else:
            returned_dir = check_for_sip(args.i)
            if returned_dir is None:
                return False
            uuid_check = os.path.basename(returned_dir)
            if validate_uuid4(uuid_check) != False:
                return uuid_check
            else:
                return source_uuid


def check_for_sip(args):
    '''
    This checks if the input folder contains the actual payload, eg:
    the UUID folder(containing logs/metadata/objects) and the manifest sidecar.
    Just realised that args.i can be a list, but for our main concat workflow, a single dir will be passed.
    Hence the args[0]
    Also choose a better variable name than args as args=/a/path here.
    '''
    for filenames in os.listdir(args[0]):
        if 'manifest.md5' in filenames:
            dircheck = filenames.replace('_manifest.md5', '')
            if os.path.isdir(os.path.join(args[0], dircheck)):
                print 'ifi sip found'
                return os.path.join(args[0], dircheck)

def checksum_replace(manifest, logname):
    '''
    Update a value in a checksum manifest.
    Variables just refer to lognames right now, which is the only thing that needs to change at the moment.
    '''
    updated_manifest = []
    new_checksum = hashlib_md5(logname)
    with open(manifest, 'r') as manifesto:
        manifest_lines = manifesto.readlines()
        for lines in manifest_lines:
            if os.path.basename(logname) in lines:
                lines = lines[31:].replace(lines[31:], new_checksum + lines[32:])
            updated_manifest.append(lines)
    with open(manifest, 'wb') as fo:
        for lines in updated_manifest:
            fo.write(lines)
