#!/usr/bin/env python
'''
Batch process packages by running accession.py and makepbcore.py
'''
import argparse
import sys
import os
import ififuncs
import accession

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Batch process packages by running accession.py and makepbcore.py'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'input', help='Input directory'
    )
    parser.add_argument(
        '-start_number',
        help='Enter the Accession number for the first package. The script will increment by one for each subsequent package.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args
def get_number(args):
    '''
    Figure out the first accession number and how to increment per package.
    '''
    if args.start_number:
        if args.start_number[:3] != 'aaa':
            print 'First three characters must be \'aaa\' and last four characters must be four digits'
            accession_number = ififuncs.get_accession_number()
        elif len(args.start_number[3:]) != 4:
            accession_number = ififuncs.get_accession_number()
            print 'First three characters must be \'aaa\' and last four characters must be four digits'
        elif not args.start_number[3:].isdigit():
            accession_number = ififuncs.get_accession_number()
            print 'First three characters must be \'aaa\' and last four characters must be four digits'
        else:
            accession_number = args.start_number
    else:
        accession_number = ififuncs.get_accession_number()
    return accession_number
def main(args_):
    '''
    Batch process packages by running accession.py and makepbcore.py
    '''
    args = parse_args(args_)
    user = ififuncs.get_user()
    accession_number = get_number(args)
    accession_digits = int(accession_number[3:])
    new_accession_number = 'aaa' + str(accession_digits)
    for root, _, _ in os.walk(args.input):
        if os.path.basename(root)[:2] == 'oe':
            if len(os.path.basename(root)[2:]) == 4:
                accession.main([root, '-user', user, '-p', '-f', '-number', new_accession_number])
                accession_digits = int(new_accession_number[3:]) + 1
                new_accession_number = 'aaa' + str(accession_digits)

if __name__ == '__main__':
    main(sys.argv[1:])

