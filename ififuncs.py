import subprocess
import sys

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
