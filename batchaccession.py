#!/usr/bin/env python
'''
Batch process packages by running accession.py and makepbcore.py
'''
import argparse
import sys
import os
import ififuncs
import accession
import copyit

def initial_check(args, accession_digits):
    '''
    Tells the user which packages will be accessioned and what their accession
    numbers will be.
    '''
    to_accession = {}
    wont_accession = []
    for root, _, _ in os.walk(args.input):
        if os.path.basename(root)[:2] == 'oe':
            if len(os.path.basename(root)[2:]) == 4:
                if copyit.check_for_sip(root) is None:
                    wont_accession.append(root)
                    #print '%s looks like it is not a fully formed SIP. Perhaps loopline_repackage.py should proccess it?' % root
                else:
                    to_accession[root] = 'aaa' + str(accession_digits)
                    accession_digits += 1
    for fails in wont_accession:
        print '%s looks like it is not a fully formed SIP. Perhaps loopline_repackage.py should proccess it?' % fails
    for success in sorted(to_accession.keys()):
        print '%s will be accessioned as %s' %  (success, to_accession[success])
    return to_accession

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
    to_accession = initial_check(args, accession_digits)
    proceed = ififuncs.ask_yes_no(
        'Do you want to proceed?'
    )
    if proceed == 'Y':
        for package in sorted(to_accession.keys()):
            accession.main([
                package, '-user', user,
                '-p', '-f', '-number',
                to_accession[package]
            ])

if __name__ == '__main__':
    main(sys.argv[1:])

