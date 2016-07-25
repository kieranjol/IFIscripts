#!/usr/bin/env python

# Written by Kieran O'Leary, with a major review and overhaul/cleanup by Zach Kelling aka @Zeekay
# Makes a single ffv1.mkv

import subprocess
import sys
import filecmp
from glob import glob
import os
import shutil
import csv
import time
import itertools
import getpass

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

def generate_log(log, what2log):
    if not os.path.isfile(log):
        with open(log,"wb") as fo:
            fo.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + getpass.getuser() + ' ' + what2log + ' \n')
    else:
        with open(log,"ab") as fo:
            fo.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + getpass.getuser() + ' ' + what2log + ' \n')
# Write metadata for original video file - with open will auto close the file.
def make_mediainfo(xmlfilename, xmlvariable, inputfilename):
    with open(xmlfilename, "w+") as fo:
        xmlvariable = subprocess.check_output(['mediainfo',
                        '-f',
                        '--language=raw', # Use verbose output.
                        '--output=XML',
                        inputfilename])       #input filename
        fo.write(xmlvariable)

def make_manifest(relative_manifest_path, manifest_textfile):
    os.chdir(relative_manifest_path)
    manifest_generator = subprocess.check_output(['md5deep', '-ler', '.'])
    manifest_list = manifest_generator.splitlines()
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list,  key=lambda x:(x[34:])) 
    with open(manifest_textfile,"wb") as fo:
        for i in manifest_list:
            fo.write(i + '\n')


if len(sys.argv) < 2:
    print 'IFI FFV1.MKV SCRIPT'
    print 'USAGE: PYTHON makeffv1.py FILENAME'
    print 'OR'
    print 'USAGE: PYTHON makeffv1.py DirectoryNAME'
    print 'If input is a directory, all files will be processed'
    print 'If input is a file, only that file will be processed'
    sys.exit()
    
    
else:
    # Input, either file or firectory, that we want to process.
    input = sys.argv[1]
    print input

    # Store the directory containing the input file/directory.
    wd = os.path.dirname(input)

    # Change current working directory to the value stored as "wd"
    os.chdir(wd)

    # Store the actual file/directory name without the full path.
    file_without_path = os.path.basename(input)
    print file_without_path
    csv_report_filename = os.path.basename(input) + 'framehash_benchmark' + time.strftime("_%Y_%m_%dT%H_%M_%S") + '.csv'

    # Check if input is a file.
    # AFAIK, os.path.isfile only works if full path isn't present.
    if os.path.isfile(file_without_path):      
        print os.path.isfile(file_without_path)
        print "single file found"
        video_files = []                       # Create empty list 
        video_files.append(file_without_path)  # Add filename to list
        print video_files

    # Check if input is a directory. 
    elif os.path.isdir(file_without_path):  
        os.chdir(file_without_path)
        video_files =  glob('*.mov') + glob('*.mp4') + glob('*.mxf') + glob('*.mkv') + glob('*.avi') + glob('*.y4m')

    # Prints some stuff if input isn't a file or directory.
    else: 
        print "Your input isn't a file or a directory."
        print "What was it? I'm curious."  
    create_csv(csv_report_filename, ('FILENAME', 'Lossless?'))
    for filename in video_files: #loop all files in directory


        filenoext = os.path.splitext(filename)[0]
        # Change directory to directory with video files


        print filenoext
        # Generate new directory names in AIP
        metadata_dir   = "%s/metadata" % filenoext
        log_dir = "%s/logs" % filenoext
        data_dir   = "%s/data" % filenoext
        provenance_dir   = "%s/provenance" % filenoext

        # Actually create the directories.
        os.makedirs(metadata_dir)
        os.makedirs(data_dir)
        os.makedirs(provenance_dir)
        os.makedirs(log_dir)

        #Generate filenames for new files in AIP.
        inputxml  = "%s/%s.xml" % (metadata_dir,os.path.basename(filename) )
        output    = "%s/%s.mkv" % (data_dir, os.path.basename(filename))

        # Generate filename of ffv1.mkv without the path.
        outputfilename = os.path.basename(output)

        outputxml = "%s/%s.xml" % (metadata_dir, outputfilename)
        fmd5      = "%s/%s.framemd5" % (provenance_dir, os.path.basename(filename))
        fmd5ffv1  = output + ".framemd5"
        log       = "%s/%s_log.log" %  (log_dir,filename)
        generate_log(log, 'Input = %s' % filename)
        generate_log(log, 'Output = %s' % output) 
        generate_log(log, 'makeffv1.py transcode to FFV1 and framemd5 generation of source started.') 
        # Transcode video file writing frame md5 and output appropriately
        subprocess.call(['ffmpeg',
                        '-i', filename,
                        '-c:v', 'ffv1',        # Use FFv1 codec
                        '-g','1',              # Use intra-frame only aka ALL-I aka GOP=1
                        '-level','3',          # Use Version 3 of FFv1
                        '-c:a','copy',         # Copy and paste audio bitsream with no transcoding
                        '-map','0',
                        '-dn',
                        '-report',
                        '-slicecrc', '1',
                        '-slices', '16',
                        output,	
                        '-f','framemd5','-an'  # Create decoded md5 checksums for every frame of the input. -an ignores audio
                        , fmd5  ])
        generate_log(log, 'makeffv1.py transcode to FFV1 and framemd5 generation completed.')        
        generate_log(log, 'makeffv1.py Framemd5 generation of output file started.')
        subprocess.call(['ffmpeg',    # Create decoded md5 checksums for every frame of the ffv1 output
                        '-i',output,
                        '-report',
                        '-f','framemd5','-an',
                        fmd5ffv1 ])
        generate_log(log, 'makeffv1.py Framemd5 generation of output file completed')                
        log_files =  glob('*.log')                
        for i in log_files:
            if 'ffmpeg' in i:
                shutil.move(i, '%s/%s' % (log_dir,i))
                generate_log(log, 'makeffv1.py %s moved to log directory' % i)
        # Verify that the video really is lossless by comparing the fixity of the two framemd5 files. 
        
        # Adapted from Andrew Dalke - http://stackoverflow.com/a/8304087/2188572
        def read_non_comment_lines(infile):
            for lineno, line in enumerate(infile):
                #if line[:1] != "#":
                    yield lineno, line
        checksum_mismatches = []
        with open(fmd5) as f1:
            with open(fmd5ffv1) as f2:
                for (lineno1, line1), (lineno2, line2) in itertools.izip(
                               read_non_comment_lines(f1), read_non_comment_lines(f2)):
                    if line1 != line2:
                        if 'sar' in line1:
                            checksum_mismatches = ['sar']
                        else:
                            checksum_mismatches.append(1)
        if len(checksum_mismatches) == 0:
            print 'LOSSLESS'
            append_csv(csv_report_filename, (output,'LOSSLESS'))
            generate_log(log, 'makeffv1.py Transcode was lossless') 
        elif len(checksum_mismatches) == 1:
            if checksum_mismatches[0] == 'sar':
                print 'Image content is lossless, Pixel Aspect Ratio has been altered'
                append_csv(csv_report_filename, (output,'LOSSLESS - different PAR'))
                generate_log(log, 'makeffv1.py Image content is lossless, but Pixel Aspect Ratio has been altered')
        elif len(checksum_mismatches) > 1:
            print 'NOT LOSSLESS'     
            append_csv(csv_report_filename, (output,'NOT LOSSLESS'))
            generate_log(log, 'makeffv1.py Not Lossless.')

        if filecmp.cmp(fmd5, fmd5ffv1, shallow=False): 
            print "YOUR FILES ARE LOSSLESS YOU SHOULD BE SO HAPPY!!!"

        else:
        	print "YOUR CHECKSUMS DO NOT MATCH, BACK TO THE DRAWING BOARD!!!"
        	#sys.exit()                 # Script will exit the loop if transcode is not lossless.

        make_mediainfo(inputxml,'mediaxmlinput',filename)
        make_mediainfo(outputxml,'mediaxmloutput',output)
        normpath = os.path.normpath(filename)
        source_parent_dir = os.path.dirname(filename)
        relative_path = normpath.split(os.sep)[-1]
        manifest =  '%s_manifest.md5' % (relative_path)
        generate_log(log, 'makeffv1.py MD5 manifest started')
        make_manifest(filenoext,manifest)
        os.chdir('..')
        generate_log(log, 'makeffv1.py MD5 manifest completed')
        
