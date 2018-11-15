#! /usr/bin/env python
'''
Retrospectively updates packages with DFXML and sha512 manifests.
Written by Kieran O'Leary
MIT License
'''
import argparse
import os
import sys
import ififuncs
import accession
import manifest

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
    parsed_args = parser.parse_args(args_)
    return parsed_args


def main(args_):
    '''
    Launch all the functions for creating an IFI SIP.
    '''
    args = parse_args(args_)
    source = args.input
    user = ififuncs.get_user()
    for root, _, _ in os.walk(source):
        if ififuncs.check_for_uuid_generic(root) is not False:
            print(" - Processing %s" % root)
            uuid_path = root
            uuid = ififuncs.check_for_uuid_generic(root)
            logs_dir = os.path.join(uuid_path, 'logs')
            logs_dir = os.path.join(uuid_path, 'logs')
            metadata_dir = os.path.join(uuid_path, 'metadata')
            dfxml = os.path.join(metadata_dir, uuid + '_dfxml.xml')
            new_log_textfile = os.path.join(logs_dir, uuid) + '_sip_log.log'
            sha512_manifest = os.path.join(
                os.path.dirname(uuid_path), uuid + '_manifest-sha512.txt'
            )
            if not os.path.isfile(dfxml) and not os.path.isfile(sha512_manifest):
                new_manifest_textfile = os.path.join(os.path.dirname(uuid_path), uuid) + '_manifest.md5'
                ififuncs.generate_log(
                    new_log_textfile,
                    'EVENT = shadfxml.py started'
                )
                ififuncs.generate_log(
                    new_log_textfile,
                    'eventDetail=shadfxml.py %s' % ififuncs.get_script_version('shadfxml.py')
                )
                ififuncs.generate_log(
                    new_log_textfile,
                    'Command line arguments: %s' % args
                )
                ififuncs.generate_log(
                    new_log_textfile,
                    'EVENT = agentName=%s' % user
                )
                if not os.path.isfile(dfxml):
                    print('Generating Digital Forensics XML')
                    dfxml = accession.make_dfxml(args, uuid_path, uuid)
                    ififuncs.generate_log(
                        new_log_textfile,
                        'EVENT = Metadata extraction - eventDetail=File system metadata extraction using Digital Forensics XML, eventOutcome=%s, agentName=makedfxml' % (dfxml)
                    )
                    ififuncs.manifest_update(new_manifest_textfile, dfxml)
                if not os.path.isfile(sha512_manifest):
                    sha512_log = manifest.main([uuid_path, '-sha512', '-s'])
                    ififuncs.merge_logs_append(sha512_log, new_log_textfile, new_manifest_textfile)
                    ififuncs.checksum_replace(sha512_manifest, new_log_textfile, 'sha512')
                    os.remove(sha512_log)
                ififuncs.sort_manifest(new_manifest_textfile)
            else:
                print("Exiting as this package already has DFXML and SHA512")

if __name__ == '__main__':
    main(sys.argv[1:])
