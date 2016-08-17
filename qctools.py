#!/usr/bin/env python
import subprocess
import sys


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
    
qctoolsxml_file = sys.argv[1] + '.qctools.xml'
write_qctools_gz(qctoolsxml_file, sys.argv[1])
