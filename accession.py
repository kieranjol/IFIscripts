#! /usr/bin/env python
'''
Runs (Spectrum) accessioning procedures on packages
that have been through the Object Entry process
Written by Kieran O'Leary
MIT License
'''

import sys
import argparse
import ififuncs


def main():
    '''
    Launches the various functions that will accession a package
    '''
    accession_number = ififuncs.get_accession_number()
    
if __name__ == '__main__':
    main()