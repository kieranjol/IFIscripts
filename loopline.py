#!/usr/bin/env python
import sys
import os
import subprocess
import makeffv1

def main():
    video_files, csv_report_filename = makeffv1.get_input()
    makeffv1.make_ffv1(video_files, csv_report_filename)
    for video in video_files:
        subprocess.call(['bitc.py',
        '-clean','-yadif',
        '-crf','20',
        video,
        '-o', os.path.dirname(sys.argv[1])])
    
if __name__ == '__main__':
    main()
