#!/usr/bin/env python3
'''
Generates Mediaconch xml reports
Accepts a file extension pattern and a policy input
Reports of fails are generated to the screen
Sidecars in XML format generated
'''
import argparse
import os
import subprocess
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
def parse_args():
    '''
    Accept command line arguments
    '''
    parser = argparse.ArgumentParser(description='Generates Mediaconch xml reports'
    'Accepts a file extension pattern and a policy input'
    'Reports of fails are generated to the screen'
    'Sidecars in XML format generated'
    )
    parser.add_argument('input', help='path to parent directory')
    parser.add_argument('-object_extension_pattern', help='the filename extension that you would like to scan for')
    parser.add_argument('-policy', help='the full path to the mediaconch XML policy')
    parsed_args = parser.parse_args()
    return parsed_args

def main():
    '''
    Launches the main functions
    '''
    args = parse_args()
    source_folder = args.input
    for root, _, filenames in os.walk(source_folder):
        for filename in filenames:
            if filename[0] != '.':
                if filename.endswith(args.object_extension_pattern):
                    full_path = os.path.join(root, filename)
                    sidecar = full_path + '_MediaConchReport.xml'
                    mediaconch_cmd = ['mediaconch', full_path, '-p', args.policy, '-fx']
                    # Running mediaconch twice is very lazy but it saves on XML parsing.
                    mediaconch_overview_cmd = ['mediaconch', full_path, '-p', args.policy]
                    mediaconch_output = subprocess.check_output(mediaconch_cmd)
                    mediaconch_overview = subprocess.check_output(mediaconch_overview_cmd)
                    if 'fail!' in str(mediaconch_overview):
                        logging.info('%s does not validate against the policy - look at the sidecar XML for more info' % filename)
                    elif 'pass!' in str(mediaconch_overview):
                        logging.info('%s: No failure detected' % filename)
                    if not os.path.isfile(sidecar):
                        with open(sidecar, 'wb') as sidecar_object:
                            sidecar_object.write(mediaconch_output)
                            logging.info('Generating sidecar - %s' % sidecar)
                    else:
                        logging.info('%s already exists - skipping' % sidecar)
                    if filename.endswith('.mkv'):
                        mkv_implementation_overview_cmd = ['mediaconch', full_path]
                        mkv_implementation_overview = subprocess.check_output(mkv_implementation_overview_cmd)
                        if 'fail!' in str(mkv_implementation_overview):
                            logging.info('%s does not validate against the implementation - look at the sidecar XML for more info' % filename)
                        elif 'pass!' in str(mkv_implementation_overview):
                            logging.info('%s: Valid implementation' % filename)
                        mkv_sidecar_output = subprocess.check_output(['mediaconch', '-fx', full_path])
                        if not os.path.isfile(full_path + '_implementation_report'):
                            with open(full_path + '_ImplementationReport.xml', 'wb') as fo:
                                fo.write(mkv_sidecar_output)
                                logging.info('Generating implementation report sidecar: %s'% full_path + 'ImplementationReport.xml')

if __name__ == '__main__':
    main()
