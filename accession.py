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
    source = [sys.argv[1]]
    uuid_directory = ififuncs.check_for_sip(source)
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
        uuid = os.path.basename(uuid_directory)
        new_uuid_path = os.path.join(accession_path, uuid)
        logs_dir = os.path.join(new_uuid_path, 'logs')
        sipcreator_log = os.path.join(logs_dir, uuid) + '_sip_log.log'
        sip_manifest = os.path.join(
            accession_path, uuid
            ) + '_manifest.md5'
        sha512_log = manifest.main([new_uuid_path, '-sha512', '-s'])
        ififuncs.merge_logs_append(sha512_log, sipcreator_log, sip_manifest)
        os.remove(sha512_log)
    else:
        print 'not a valid package. The input should include a package that has been through Object Entry'
if __name__ == '__main__':
    main()
