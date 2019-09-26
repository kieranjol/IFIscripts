#!/usr/bin/env python3
'''
Just a helper script that collates CSV files within a folder
'''
import argparse
import os
import ififuncs
import time

def gather_metadata(source):
    '''
    Loops through all subfolders that contain pbcore_csv and then harvests the
    metadata and store in a single file for the purposes of batch import into
    the DB TEXTWORKS technical database.
    '''
    metadata = []
    for root, _, filenames in sorted(os.walk(source)):
        for filename in filenames:
            if filename.endswith('csv'):
                with open(os.path.join(root,filename), 'r') as csv_file:
                    csv_rows = csv_file.readlines()
                if len(csv_rows) > 1:
                    if metadata:
                        metadata.append([csv_rows[1]])
                    else:
                        metadata.append([csv_rows[0]])
                        metadata.append([csv_rows[1]])
                else:
                    print('%s has been skipped due to no actual data in the CSV' % filename)
    collated_pbcore = os.path.join(
        ififuncs.make_desktop_logs_dir(),
        time.strftime("%Y-%m-%dT%H_%M_%S_collated.csv")
    )
    with open(collated_pbcore, 'w') as fo:
        for i in metadata:
            fo.write(i[0])
    return collated_pbcore
def parse_args():
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Collates CSV files from archival packages and stores in the Desktop logs folder'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'input', help='Input directory'
    )
    parsed_args = parser.parse_args()
    return parsed_args

def main():
    args = parse_args()
    source = args.input
    collated_pbcore = gather_metadata(source)
    print('Merged CSV is stored in %s' % collated_pbcore)
if __name__ == '__main__':
    main()