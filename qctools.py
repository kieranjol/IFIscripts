#!/usr/bin/env python
import subprocess
import sys
import os
from glob import glob

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

input = sys.argv[1]
print input

# Store the directory containing the input file/directory.
wd = os.path.dirname(input)

# Change current working directory to the value stored as "wd"
os.chdir(os.path.abspath(wd))

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
    video_files =  glob('*.mov') + glob('*.mp4') + glob('*.mxf') + glob('*.mkv') + glob('*.avi') + glob('*.y4m')

# Prints some stuff if input isn't a file or directory.
else: 
    print "Your input isn't a file or a directory."
    print "What was it? I'm curious."  
for filename in video_files: #loop all files in directory
   
    qctoolsxml_file = filename + '.qctools.xml'
    write_qctools_gz(qctoolsxml_file, filename)
