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
import time
import ififuncs
import manifest
import makedfxml
import validate
import makepbcore


def make_register():
    '''
    This sends a placeholder accessions register to the desktop logs directory.
    This should get rid of some of the more painful, repetitive identifier matching.
    '''
    desktop_logs_dir = ififuncs.make_desktop_logs_dir()
    register = os.path.join(
        desktop_logs_dir,
        'register_' + time.strftime("%Y-%m-%dT%H_%M_%S.csv")
    )
    ififuncs.create_csv(register, (
        'entry number',
        'accession number',
        'date acquired',
        'acquired from',
        'acquisition method',
        'simple name; basic description; identification; historical information',
        'notes'
    ))
    return register


def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Accessions objects into the Irish Film Institute collection'
        'Completes the transformation of a SIP into an AIP.'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'input', help='Input directory'
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.')
    parser.add_argument(
        '-number',
        help='Enter the Accession number for the representation.The parent Object Entry number will be replaced with this name.'
    )
    parser.add_argument(
        '-force',
        help='Renames OE with accession number without confirmation.', action='store_true'
    )
    parser.add_argument(
        '-pbcore',
        help='launches makepbcore and updates AIP', action='store_true'
    )
    parser.add_argument(
        '-reference',
        help='Enter the Filmographic reference number for the representation. This is only relevant when used with -pbcore' 
    )
    parser.add_argument(
        '-register',
        help='Path of accessions register CSV file. Mostly to be used by batchaccession.py'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def make_dfxml(args,new_uuid_path,uuid):
    '''
    Adds Digital Forensics XML to metadata folder and updates manifests.
    '''
    metadata = os.path.join(new_uuid_path, 'metadata')
    dfxml = os.path.join(metadata, uuid + '_dfxml.xml')
    makedfxml.main([new_uuid_path, '-o', dfxml])
    return dfxml


def main(args_):
    '''
    Launches the various functions that will accession a package
    '''
    args = parse_args(args_)
    source = args.input
    uuid_directory = ififuncs.check_for_sip([source])
    if uuid_directory is not None:
        oe_path = os.path.dirname(uuid_directory)
        oe_number = os.path.basename(oe_path)
        if args.user:
            user = args.user
        else:
            user = ififuncs.get_user()
        if args.number:
            if args.number[:3] != 'aaa':
                print 'First three characters must be \'aaa\' and last four characters must be four digits'
                accession_number = ififuncs.get_accession_number()
            elif len(args.number[3:]) != 4:
                accession_number = ififuncs.get_accession_number()
                print 'First three characters must be \'aaa\' and last four characters must be four digits'
            elif not args.number[3:].isdigit():
                accession_number = ififuncs.get_accession_number()
                print 'First three characters must be \'aaa\' and last four characters must be four digits'
            else:
                accession_number = args.number
        else:
            accession_number = ififuncs.get_accession_number()
        if args.pbcore:
            if args.reference:
                Reference_Number = args.reference
            else:
                Reference_Number = ififuncs.get_reference_number()
        accession_path = os.path.join(
            os.path.dirname(oe_path), accession_number
        )
        uuid = os.path.basename(uuid_directory)
        new_uuid_path = os.path.join(accession_path, uuid)
        logs_dir = os.path.join(new_uuid_path, 'logs')
        sipcreator_log = os.path.join(logs_dir, uuid) + '_sip_log.log'
        if args.force:
            proceed = 'Y'
        else:
            proceed = ififuncs.ask_yes_no(
                'Do you want to rename %s with %s' % (oe_number, accession_number)
            )
        if proceed == 'Y':
            os.rename(oe_path, accession_path)
        if args.register:
            register = args.register
        else:
            register = make_register()
        ififuncs.append_csv(register, (oe_number.upper()[:2] + '-' + oe_number[2:6], accession_number, '','','','', ''))
        ififuncs.generate_log(
            sipcreator_log,
            'EVENT = accession.py started'
        )
        ififuncs.generate_log(
            sipcreator_log,
            'eventDetail=accession.py %s' % ififuncs.get_script_version('accession.py')
        )
        ififuncs.generate_log(
            sipcreator_log,
            'Command line arguments: %s' % args
        )
        ififuncs.generate_log(
            sipcreator_log,
            'EVENT = agentName=%s' % user
        )
        ififuncs.generate_log(
            sipcreator_log,
            'EVENT = eventType=Identifier assignment,'
            ' eventIdentifierType=accession number, value=%s'
            % accession_number
        )
        ififuncs.generate_log(
            sipcreator_log,
            'EVENT = eventType=accession,'
            ' eventIdentifierType=accession number, value=%s'
            % accession_number
        )
        sip_manifest = os.path.join(
            accession_path, uuid
            ) + '_manifest.md5'
        sha512_log = manifest.main([new_uuid_path, '-sha512', '-s'])
        sha512_manifest = os.path.join(
            os.path.dirname(new_uuid_path), uuid + '_manifest-sha512.txt'
        )
        ififuncs.merge_logs_append(sha512_log, sipcreator_log, sip_manifest)
        os.remove(sha512_log)
        print('Generating Digital Forensics XML')
        dfxml = make_dfxml(args, new_uuid_path, uuid)
        ififuncs.generate_log(
            sipcreator_log,
            'EVENT = Metadata extraction - eventDetail=File system metadata extraction using Digital Forensics XML, eventOutcome=%s, agentName=makedfxml' % (dfxml)
        )
        ififuncs.generate_log(
            sipcreator_log,
            'EVENT = accession.py finished'
        )
        ififuncs.checksum_replace(sip_manifest, sipcreator_log, 'md5')
        ififuncs.checksum_replace(sha512_manifest, sipcreator_log, 'sha512')
        ififuncs.manifest_update(sip_manifest, dfxml)
        ififuncs.sha512_update(sha512_manifest, dfxml)
        if args.pbcore:
            makepbcore.main([accession_path, '-p', '-user', user, '-reference', Reference_Number])
    else:
        print 'not a valid package. The input should include a package that has been through Object Entry'

if __name__ == '__main__':
    main(sys.argv[1:])
