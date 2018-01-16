#!/usr/bin/env python
'''
Creates PREMIS CSV and XML descriptions by launching other IFIscripts,
such as logs2premis.py, premisobjects.py, premiscsv2xml.py'
'''
import os
import argparse
import premisobjects
import premiscsv2xml
import logs2premis


def parse_args():
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Creates PREMIS CSV and XML descriptions by launching'
        'other IFIscripts, such as logs2premis.py, premisobjects.py,'
        'premiscsv2xml.py'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'input',
        help='full path to your input directory'
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.'
    )
    parser.add_argument(
        '-object_csv', required=True,
        help='full path and filename of the output objects CSV.'
    )
    parser.add_argument(
        '-event_csv', required=True,
        help='full path and filename of the output events CSV'
    )
    parsed_args = parser.parse_args()
    return parsed_args


def launch_scripts(source, args):
    '''
    Launches premisobjects, logs2premis and premiscsv2xml in input directory
    '''
    for root, _, _ in os.walk(source):
        if os.path.basename(root) == 'objects':
            objects_csv = args.object_csv
            events_csv = args.event_csv
            uuid_dir = os.path.dirname(root)
            logs_dir = os.path.join(
                uuid_dir, 'logs'
            )
            logname = os.path.join(
                logs_dir, os.path.basename(uuid_dir + '_sip_log.log')
            )
            manifest = os.path.join(
                os.path.dirname(uuid_dir), os.path.basename(uuid_dir + '_manifest.md5')
            )
            premisobjects.main(
                ['-i', root, '-m', manifest, '-o', objects_csv]
            )
            logs2premis.main(
                ['-i', logname, '-object_csv', objects_csv, '-o', events_csv]
            )
            premiscsv2xml.main(
                ['-i', objects_csv, '-ev', events_csv]
            )


def main():
    '''
    Launch the other functions when called from the command line
    '''
    args = parse_args()
    source = args.input
    launch_scripts(source, args)

if __name__ == '__main__':
    main()
