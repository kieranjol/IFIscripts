#!/usr/bin/env python
'''
Launches qcli on all mov/mkv files in all subfolders beneath your input.
qcli makes xml.gz QCTools reports.
'''
import sys
import subprocess
import os


def main():
    '''
    Simple recursive process that makes QCTools sidecar reports.
    '''
    for root, _, filenames in os.walk(sys.argv[1]):
        for filename in filenames:
            if filename.endswith(('.mov', '.mkv')):
                if filename[0] != '.':
                    cmd = [
                        'qcli',
                        '-i',
                        os.path.join(root, filename)
                    ]
                    subprocess.call(cmd)


if __name__ == '__main__':
    main()

