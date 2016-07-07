import sys
import subprocess

input_dir = sys.argv[1]

subprocess.call(['ffmpeg', '-f', 'lavfi', '-i', 'testsrc', '-c:v', 'prores', '-t', '20', input_dir + 'bars.mov'])
subprocess.call(['ffmpeg', '-f', 'lavfi', '-i', 'mandelbrot', '-c:v', 'prores', '-t', '20', input_dir + 'mandel.mov'])
subprocess.call(['ffmpeg', '-f', 'lavfi', '-i', 'life', '-c:v', 'prores', '-t', '20', input_dir + 'life.mov'])
