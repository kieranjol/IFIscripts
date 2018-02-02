#! /usr/bin/env python
'''
Runs (Spectrum) accessioning procedures on packages
that have been through the Object Entry process
Written by Kieran O'Leary
MIT License
'''

import sys
import os
import argparse
import ififuncs


def main():
    '''
    Launches the various functions that will accession a package
    '''
    input = [sys.argv[1]]
    oe_number =  os.path.basename(os.path.dirname(ififuncs.check_for_sip(input)))
    accession_number = ififuncs.get_accession_number()
    ififuncs.ask_yes_no('Do you want to rename %s with %s' % ( oe_number, accession_number))
    
if __name__ == '__main__':
    main()