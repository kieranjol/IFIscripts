#!/usr/bin/env python
'''
Runs Digital Forensic XML.
'''
import os
import sys
import argparse
import walk_to_dfxml
from lxml import etree


def parse_args(args_):
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
    parser.add_argument(
        '-o',
        help='full path to an output XML file'
    )
    parser.add_argument(
        '-n',
        action="store_true", help="Do not calculate any hashes"
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def main(args_):
    '''
    Launches the functions that will print your digital forensics XML.
    Hashes are turned off by default.
    '''
    args = parse_args(args_)
    if args.o:
        if not args.o.endswith("xml"):
            print('output file must be XML')
    source = args.input
    os.chdir(source)
    if args.n:
        hash_arg = ["-n"]
    else:
        hash_arg = []
    output = walk_to_dfxml.main(hash_arg)
    parser = etree.XMLParser(remove_blank_text=True)
    dfxml_out = etree.fromstring((output), parser=parser)
    if args.o:
        with open(args.o, 'w') as xml_doc:
            xml_doc.write(etree.tostring(dfxml_out, pretty_print=True).decode('ascii'))
    else:
        print(etree.tostring(dfxml_out, pretty_print=True).decode('ascii'))


if __name__ == '__main__':
    main(sys.argv[1:])
