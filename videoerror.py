#!/usr/bin/env python3
'''
Catches errors in m2t video files via ffmpeg.
'''
import subprocess
import os
import json
import argparse
import time
import ififuncs
import bitc

def parse_args():
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Catches errors in m2t files via ffmpeg.'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'input', help='Input directory'
    )
    parsed_args = parser.parse_args()
    return parsed_args

def main():
    '''
    Launches the commands that generate the CSV error report
    '''
    args = parse_args()
    source = args.input
    csv_filename = os.path.join(
        ififuncs.make_desktop_logs_dir(),
        time.strftime("%Y-%m-%dT%H_%M_%S_videoerrors.csv")
    )
    print('Report stored as %s' % csv_filename)
    if not os.path.isfile(csv_filename):
        ififuncs.create_csv(csv_filename, ['filename', 'start_time', 'timestamp', 'error', 'notes'])
    for root, _, filenames in os.walk(source):
        for filename in filenames:
            if filename.endswith('.m2t'):
                with open(csv_filename, 'r') as fo:
                    if not filename in fo.read():
                        try:
                            start_time = bitc.getffprobe('start_time', 'stream=start_time', os.path.join(root, filename)).rsplit()[0]
                            json_output = subprocess.check_output(['ffprobe', '-sexagesimal', os.path.join(root, filename), '-show_error', '-show_log', '16', '-show_frames', '-of', 'json'])
                            errors = False
                            ffprobe_dict = json.loads(json_output)
                            for values in ffprobe_dict:
                                for more in ffprobe_dict[values]:
                                    if 'logs' in more:
                                        errors = True
                                        print(more['pkt_pts_time'], more['logs'])
                                        ififuncs.append_csv(csv_filename, [filename, start_time, more['pkt_pts_time'], more['logs'], ''])
                            if errors == False:
                                ififuncs.append_csv(csv_filename, [filename, start_time, 'no errors', 'no errors', ''])
                        except subprocess.CalledProcessError:
                            ififuncs.append_csv(csv_filename, [filename, start_time, 'script error - process file manually', '', ''])
    print('Report stored as %s' % csv_filename)

if __name__ == '__main__':
    main()
