#!/usr/bin/env python
import sys
import os
import subprocess
import makeffv1
import dvsip
from ififuncs import get_mediainfo

def main():
    video_files, csv_report_filename = makeffv1.get_input()
    dv_files = dvsip.get_input()
    all_files = video_files + dv_files
    if os.path.isdir(sys.argv[1]):
       output = sys.argv[1]
    elif os.path.isfile(sys.argv[1]):
       output = os.path.dirname(sys.argv[1])
    proxies_dir = os.path.join(output, 'proxies')
    if not os.path.isdir(proxies_dir):
        os.makedirs(proxies_dir)
    for video in all_files:
        subprocess.check_call(
            [sys.executable, os.path.expanduser("~/ifigit/ifiscripts/bitc.py"),
            '-clean','-yadif',
            '-crf','20',
            os.path.join(output,video),
            '-o', proxies_dir]
            )
    makeffv1.make_ffv1(video_files, csv_report_filename)
    dvsip.make_sip(dv_files)
    print 'Proxies sent to %s' % proxies_dir


if __name__ == '__main__':
    main()
