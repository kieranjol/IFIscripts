#!/usr/bin/env python3
'''
Creates framemd5 sidecars on all mov/mkv files in all subfolders beneath your input.
If the input is a file, then framemd5.py will just generate a sidecar for this one file.
'''
import subprocess
import os
import argparse
import ififuncs

def parse_args():
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Creates framemd5 sidecars on all mov/mkv files in all subfolders beneath your input.'
        ' If the input is a file, then framemd5.py will just generate a sidecar for this one file.'
    )
    parser.add_argument(
        '-i',
        help='full path of input file or directory', required=True
    )
    parsed_args = parser.parse_args()
    return parsed_args

def main():
    '''
    Simple recursive process that makes framemd5 sidecar reports.
    '''
    ififuncs.check_existence(['ffmpeg'])
    args = parse_args()
    source = args.i
    fmd5 = source + '_source.framemd5'
    if os.path.isfile(source):
        cmd = [
            'ffmpeg',
            '-i',
            source,
            '-f',
            'framemd5',
            '-an',
            fmd5
            ]
        subprocess.call(cmd)
    else:
        for root, _, filenames in os.walk(source):
            for filename in filenames:
                if filename.endswith(('.mov', '.mkv', '.dv')):
                    if filename[0] != '.':
                        full_path = os.path.join(root, filename)
                        cmd = [
                            'ffmpeg',
                            '-i',
                            full_path,
                            '-f',
                            'framemd5',
                            '-an',
                            full_path + '_source.framemd5'
                            ]
                        subprocess.call(cmd)


if __name__ == '__main__':
    main()

