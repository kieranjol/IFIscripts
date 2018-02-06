#!/usr/bin/env python
'''
Runs Digital Forensic XML.
'''
import os
import argparse
import subprocess
from lxml import etree


def parse_args():
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Prints Digital Forensics XML to your terminal'
        'Proof of concept - hashes are turned off for now. no logging etc..'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'input',
        help='full path of input directory.'
    )
    parsed_args = parser.parse_args()
    return parsed_args


def main():
    '''
    Launches the functions that will print your digital forensics XML.
    Hashes are turned off by default.
    '''
    args = parse_args()
    source = args.input
    os.chdir(source)
    output = subprocess.check_output(['walk_to_dfxml.py', '-n'])
    parser = etree.XMLParser(remove_blank_text=True)
    premis = etree.fromstring((output), parser=parser)
    print(etree.tostring(premis, pretty_print=True))


if __name__ == '__main__':
    main()
