#!/usr/bin/env python3
'''
Just a helper script that collates PBCore CSV files from packages
'''
import argparse
import batchaccession

def parse_args():
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Collates PBCore CSV files from archival packages and stores in the Desktop logs folder'
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
    collated_pbcore = batchaccession.gather_metadata(source)
    print('Merged PBCore CSV is stored in %s' % collated_pbcore)
if __name__ == '__main__':
    main()


