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
        'Prints the output to the terminal if the -manifest option is not used'
        'if the -manifest option is used, just the differences, if any, will appear on screen'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'input', help='Input directory'
    )
    parser.add_argument(
        '-id',
        help='Enter the identifier that you would like to search for. UUID/Accession/OE.'
    )
    parser.add_argument(
        '-manifest',
        help='Enter the sha512 manifest that you would like to compare against.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def diff_manifests(args, strongbox_list):
    '''
    Compare the list of strongbox hashes to the original AIP manifest.
    '''
    print '\nStrongbox_fixity - IFIscripts'
    print '\nDiffing the manifests..'
    with open(args.manifest, 'r') as original_manifest:
        aip_manifest = original_manifest.read().splitlines()
    # A list of items in strongbox, that are different in aip sha512 manifest
    strongbox_check = [item for item in strongbox_list if item not in aip_manifest]
    # A list of items in the AIP manifest, that are different in the strongbox manifest
    aip_check =  [item for item in aip_manifest if item not in strongbox_list]
    if len(strongbox_check) == 0:
        print 'All files in the strongbox manifest are present in your AIP manifest and the hashes validate'
    else:
        for i in strongbox_check:
            print '%s is different from the strongbox_csv to the AIP manifest' % i
    if len(aip_check) == 0:
        print 'All files in the AIP manifest are present in your strongbox manifest and the hashes validate'
    else:
        for i in strongbox_check:
            print '%s is different from the AIP manifest to the Strongbox manifest' % i
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
                    identifier_string = "/%s/" % identifier
                    manifest_line = x['hash_code'] + '  ' + x['path'].replace(identifier_string, '')
                    manifest_lines.append(manifest_line)
    strongbox_list = sorted(manifest_lines, key=lambda x: (x[130:]))
    return strongbox_list

def main(args_):
    args = parse_args(args_)
    source = args.input
    identifier = args.id
    strongbox_list = find_checksums(source, identifier)
    if args.manifest:
        diff_manifests(args, strongbox_list)
    else:
        for i in strongbox_list:
            print i
    

if __name__ == '__main__':
    main(sys.argv[1:])

