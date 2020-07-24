#!/usr/bin/env python
'''
Launches qcli on all mov/mkv files in all subfolders beneath your input.
qcli makes xml.gz QCTools reports.
'''
import sys
import subprocess
import os
import ififuncs


def main():
    '''
    Simple recursive process that makes QCTools sidecar reports.
    '''
    ififuncs.check_existence(['qcli'])
    source = sys.argv[1]
    if os.path.isfile(source):
        cmd = [
            'qcli',
            '-i',
            source]
        subprocess.call(cmd)
    else:
        for root, _, filenames in os.walk(source):
            for filename in filenames:
                if filename.endswith(('.mov', '.mkv','.dv', '.m2t')):
                    if filename[0] != '.':
                        cmd = [
                            'qcli',
                            '-i',
                            os.path.join(root, filename)
                        ]
                        subprocess.call(cmd)


if __name__ == '__main__':
    main()

