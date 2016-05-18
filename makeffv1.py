#!/usr/bin/env python

# Written by Kieran O'Leary, with a major review and overhaul/cleanup by Zach Kelling aka @Zeekay
# Makes a single ffv1.mkv

import subprocess
import sys
import filecmp
from glob import glob
import os
import shutil


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
        video_files =  glob('*.mov') + glob('*.mp4') + glob('*.mxf') + glob('*.mkv') + glob('*.avi')

    # Prints some stuff if input isn't a file or directory.
    else: 
        print "Your input isn't a file or a directory."
        print "What was it? I'm curious."  

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
        
        
        subprocess.call(['ffmpeg',     # Create decoded md5 checksums for every frame of the ffv1 output
                        '-i',output,
                        '-report',
                        '-f','framemd5','-an',
                        fmd5ffv1 ])
        log_files =  glob('*.log')                
        for i in log_files:
            shutil.move(i, '%s/%s' % (log_dir,i))
        # Verify that the video really is lossless by comparing the fixity of the two framemd5 files. 
        if filecmp.cmp(fmd5, fmd5ffv1, shallow=False): 
        	print "YOUR FILES ARE LOSSLESS YOU SHOULD BE SO HAPPY!!!"
        else:
        	print "YOUR CHECKSUMS DO NOT MATCH, BACK TO THE DRAWING BOARD!!!"
        	sys.exit()                 # Script will exit the loop if transcode is not lossless.


        # Write metadata for original video file - with open will auto close the file.
        def make_mediainfo(xmlfilename, xmlvariable, inputfilename):
          with open(xmlfilename, "w+") as fo:
          	xmlvariable = subprocess.check_output(['mediainfo',
          						'-f',
          						'--language=raw', # Use verbose output.
          						'--output=XML',
          						inputfilename])       #input filename
          	fo.write(xmlvariable)
    
        make_mediainfo(inputxml,'mediaxmlinput',filename)
        make_mediainfo(outputxml,'mediaxmloutput',output)
	

