#!/usr/bin/env python
'''
Audits logfiles to determine relationships, like is a package a derivative of
another, or does a package have no parent.
This script can aid in automating large accessioning procedures that involve
the accessioning of derivatives along with masters, eg a Camera Card and
a concatenated derivative, or a master file and a mezzanine.
Eventually this should provide an ordered list that will determine the
best order in which these packages should be accessioned by accession.py
Example output:
oe0001 not a child of another package
oe0008 has a parent: oe0001
oe0005 not a child of another package
'''
import sys
import os
import ififuncs

def get_listings(source):
    '''
    returns a list containing the absolute path of a folder containing Object
    Entry packages.
    '''
    source = sys.argv[1]
    listing = os.listdir(source)
    directories = []
    for directory in listing:
        if directory[:2] == 'oe':
            full_path = os.path.join(source, directory)
            if os.path.isdir(full_path):
                directories.append(full_path)
    return directories

def main():
    '''
    Analyzes a directory containing Object Entry packages and prints their
    relationships or lack thereof.
    Eventually this should provide an ordered list that will determine the
    best order in which these packages should be accessioned by accession.py
    '''
    directories = get_listings(sys.argv[1])
    oe_uuid_dict = ififuncs.group_ids(sys.argv[1])
    final_list = []
    for directory in directories:
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith('_sip_log.log'):
                    uuid_search = ififuncs.find_parent(
                        os.path.join(root, filename), oe_uuid_dict
                    )
                    print uuid_search

if __name__ == '__main__':
    main()
