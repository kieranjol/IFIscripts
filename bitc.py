#!/usr/bin/env python

import subprocess
import sys
import os
from glob import glob
import pdb
from sys import platform as _platform

if len(sys.argv) < 2:
    print 'IFI H264.MOV BITC/WATERMARK ACCESS COPY SCRIPT'
    print 'USAGE: PYTHON bitc.py FILENAME'
    print 'OR'
    print 'USAGE: PYTHON bitc.py DirectoryNAME'
    print 'If input is a directory, all files will be processed' 
    print 'If input is a file, only that file will be processed'    
    sys.exit()

else:

    # Input, either file or firectory, that we want to transcode losslessly and generate metadata for
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
        video_files =  glob('*.mov') + glob('*.mp4') + glob('*.mxf') + glob('*.mkv')

    # Prints some stuff if input isn't a file or directory.
    else: 
        print "Your input isn't a file or a directory."
        print "What was it? I'm curious."  

    for filename in video_files: #loop all files in directory
        print filename
        output = filename + "_vimeo.mov"
        def getffprobe(variable, streamvalue, which_file):
            variable = subprocess.check_output(['ffprobe',
                                                        '-v', 'error',
                                                        '-select_streams', 'v:0',
                                                        '-show_entries', 
                                                        streamvalue,
                                                        '-of', 'default=noprint_wrappers=1:nokey=1',
                                                        which_file])
            return variable
        video_height = float(getffprobe('video_height','stream=height', filename))
        video_width  = float(getffprobe('video_width','stream=width', filename))

        print video_height
        print video_width

        # Calculate appropriate font size
        font_size = video_height / 12
        watermark_size = video_height / 14
        #pdb.set_trace()

        if _platform == "darwin":
            print "OS X"
            font_path= "fontfile=/Library/Fonts/AppleGothic.ttf"
        elif _platform == "linux2":
            print "linux"
            font_path= "fontfile=/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
        elif _platform == "win32":
            font_path = "'fontfile=C\:\\\Windows\\\Fonts\\\\'arial.ttf'"

        # Get starting timecode in a raw state that requires processing further on in the script.
        timecode_test_raw = getffprobe('timecode_test_raw','format_tags=timecode:stream_tags=timecode', filename)
        get_framerate = getffprobe('get_frame_rate','stream=avg_frame_rate', filename)

        # This tests if there is actually a timecode present in the file.								
        if not timecode_test_raw:
            # The timecode needs to be phrased in a way unique to each operating system.
            # Note the backslashes.
            # This section makes up a timecode if none is present in the file.
            if _platform == "darwin" or _platform == "linux2":
                print "OS X"
                timecode_test = '01\\\:00\\\:00\\\:00'
            elif _platform == "win32":
                print "Windows"
                timecode_test = '01\:00\:00\:00'
                
        else:
            # If timecode is present, this will escape the colons
            # so that it is compatible with each operating system.
            if _platform == "darwin" or _platform == "linux2":
                print "OS X"
                timecode_test = timecode_test_raw.replace(':', '\\\:').replace('\n', '')
            elif _platform == "win32":
                timecode_test = timecode_test_raw.replace(':', '\\:').replace('\n', '').replace('\r', '')
                print "Windows"

            #pdb.set_trace()
        # This removes the new line character from the framemrate.
        fixed_framerate = get_framerate.rstrip()

        #all these prints are just for testing. Will be removed later.
        print fixed_framerate	
        drawtext_options = ("drawtext=%s:fontcolor=white:fontsize=%s:timecode=%s:\
        rate=%s:x=(w-text_w)/2:y=h/1.2:boxcolor=0x000000AA:box=1,\
        drawtext=%s:fontcolor=white:text='INSERT WATERMARK TEXT HERE':\
        x=(w-text_w)/2:y=(h-text_h)/2:fontsize=%s:alpha=0.4" % 
        (font_path,font_size, timecode_test, fixed_framerate, font_path,watermark_size))
        print drawtext_options
        print timecode_test
        print get_framerate

        subprocess.call(['ffmpeg',
                        '-i', filename,
                        '-c:v', 'libx264',
                        '-crf', '22',
                        '-pix_fmt', 'yuv420p',
                        '-vf',drawtext_options, output])
