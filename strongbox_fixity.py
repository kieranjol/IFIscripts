#!/usr/bin/env python
'''
Analyses the CSV file reports from Strongbox.
Accepts an identifier input, at least the package ID but
the UUID would also be useful.
The script then finds the relevant entries, harvests the checksums and
stores them as a regular manifest.
It would make sense to also accept an existing sha512 manifest as an argparse
so that the script can tell if they are identical.
'''
import os
import sys
import argparse
import ififuncs

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Analyses the CSV file reports from Strongbox.'
        'Prints the output to the terminal'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'input', help='Input directory'
    )
    parser.add_argument(
        '-id',
        help='Enter the identifier that you would like to search for. UUID/Accession/OE.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def find_checksums(csv_file, identifier):
    '''
    Finds the relevant entries in the CSV and prints to terminal
    '''
    csv_dict = ififuncs.extract_metadata(csv_file)
    manifest_lines = []
    for items in csv_dict:
        for x in items:
            if type(x) is dict:
                if identifier in x['path']:
                    manifest_line = x['hash_code'] + '  ' + x['path']
                    manifest_lines.append(manifest_line)
    manifest_list = sorted(manifest_lines, key=lambda x: (x[130:]))
    for i in manifest_list:
        print i

def main(args_):
    args = parse_args(args_)
    source = args.input
    identifier = args.id
    find_checksums(source, identifier)
    

if __name__ == '__main__':
    main(sys.argv[1:])

