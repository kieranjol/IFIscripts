#! /usr/bin/env python
'''
Runs (Spectrum) accessioning procedures on packages
that have been through the Object Entry process
Written by Kieran O'Leary
MIT License
'''

import sys
import os
import ififuncs
import manifest


def main():
    '''
    Launches the various functions that will accession a package
    '''
    input = [sys.argv[1]]
    uuid_directory = ififuncs.check_for_sip(input)
    if uuid_directory is not None:
        oe_path = os.path.dirname(uuid_directory)
        oe_number = os.path.basename(oe_path)
        accession_number = ififuncs.get_accession_number()
        accession_path = os.path.join(
            os.path.dirname(oe_path), accession_number
        )
        proceed = ififuncs.ask_yes_no(
            'Do you want to rename %s with %s' % (oe_number, accession_number)
        )
        if proceed == 'Y':
            os.rename(oe_path, accession_path)
        print oe_path, accession_path
        new_uuid_path = os.path.join(accession_path, os.path.basename(uuid_directory))
        manifest.main([new_uuid_path, '-sha512', '-s'])
    else:
        print 'not a valid package. The input should include a package that has been through Object Entry'
if __name__ == '__main__':
    main()
