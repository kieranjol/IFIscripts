#!/usr/bin/env python
import sys
import os
import subprocess
import makeffv1

def main():
    video_files, csv_report_filename = makeffv1.get_input()
    makeffv1.make_ffv1(video_files, csv_report_filename)
    if os.path.isdir(sys.argv[1]):
       output = sys.argv[1]
    elif os.path.isfile(sys.argv[1]):
       output = os.path.dirname(sys.argv[1])
    for video in video_files:
        subprocess.check_call([sys.executable,os.path.expanduser("~/ifigit/ifiscripts/bitc.py"),
        '-clean','-yadif',
        '-crf','20',
        os.path.join(output,video),
        '-o', output])


if __name__ == '__main__':
    main()
