#!/usr/bin/env python
import subprocess
import sys
import os
from glob import glob


def get_audio_stream_count(filename):
	audio_stream_count = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index','-of', 'flat', filename]).splitlines()
	return len(audio_stream_count)


def make_qctools(input):
    qctools_args = ['ffprobe', '-f', 'lavfi', '-i',]
    audio_tracks = get_audio_stream_count(input)
    if audio_tracks > 0:
        qctools_args += ["movie=%s:s=v+a[in0][in1],[in0]signalstats=stat=tout+vrep+brng,cropdetect=reset=1:round=1,split[a][b];[a]field=top[a1];[b]field=bottom[b1],[a1][b1]psnr[out0];[in1]ebur128=metadata=1,astats=metadata=1:reset=1:length=0.4[out1]" % input]
    elif audio_tracks == 0:
        qctools_args += ["movie=%s,signalstats=stat=tout+vrep+brng,cropdetect=reset=1,split[a][b];[a]field=top[a1];[b]field=bottom[b1],[a1][b1]psnr" % input]
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
print os.path.abspath(wd), 111

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
    for i in video_files:
        qctoolsxml_file = i + '.qctools.xml'
        write_qctools_gz(qctoolsxml_file, i)

# Check if input is a directory.
elif os.path.isdir(file_without_path):
    for root, dirs, filenames in os.walk(sys.argv[1]):
        for filename in filenames:
            os.chdir(root)
            if filename.endswith(('.mkv', '.mov')):
                qctoolsxml_file = filename + '.qctools.xml'
                write_qctools_gz(qctoolsxml_file, filename)


# Prints some stuff if input isn't a file or directory.
else:
    print "Your input isn't a file or a directory."
    print "What was it? I'm curious."



