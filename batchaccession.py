#!/usr/bin/env python
'''
Batch process packages by running accession.py and makepbcore.py
The outcome will be:
* Packages are accessioned
* Filmographic records can be ingested to DB TEXTWORKS
* Technical records can be ingested to DB TEXTWORKS
* Skeleton accession record can be also be made available.
'''
import argparse
import sys
import csv
import os
import time
import ififuncs
import accession
import copyit
import order


def gather_metadata(source):
    '''
    Loops through all subfolders that contain pbcore_csv and then harvests the
    metadata and store in a single file for the purposes of batch import into
    the DB TEXTWORKS technical database.
    '''
    metadata = []
    for root, _, filenames in sorted(os.walk(source)):
        for filename in filenames:
            if filename.endswith('.csv'):
                with open(os.path.join(root,filename), 'r') as csv_file:
                    csv_rows = csv_file.readlines()
                if metadata:
                    metadata.append([csv_rows[1].replace('\"', '')])
                else:
                    metadata.append([csv_rows[0]])
                    metadata.append([csv_rows[1].replace('\"', '')])
    collated_pbcore = os.path.join(
        ififuncs.make_desktop_logs_dir(),
        time.strftime("%Y-%m-%dT%H_%M_%S_pbcore.csv")
    )
    with open(collated_pbcore, 'w') as fo:
        for i in metadata:
            fo.write(i[0])
    return collated_pbcore


def initial_check(args, accession_digits, oe_list, reference_number):
    '''
    Tells the user which packages will be accessioned and what their accession
    numbers will be.
    '''
    to_accession = {}
    wont_accession = []
    # accession = 'af' + str(accession_digits)
    ref = reference_number
    reference_digits = int(ref[2:])
    for root, _, _ in sorted(os.walk(args.input)):
        if os.path.basename(root)[:2] == 'oe' and len(os.path.basename(root)[2:]) == 4:
            if copyit.check_for_sip(root) is None:
                wont_accession.append(root)
            else:
                # this is just batchaccessioning if no csv is supplied
                if not oe_list:
                    to_accession[root] = 'aaa' + str(accession_digits).zfill(4)
                    accession_digits += 1
                else:
                    if os.path.basename(root) in oe_list:
                        to_accession[
                            os.path.join(os.path.dirname(root),
                                         order.main(root))
                        ] = [
                            'aaa' + str(accession_digits).zfill(4),
                            ref[:2] + str(reference_digits).zfill(4)
                        ]
                        accession_digits += 1
                        to_accession[root] = ['aaa' + str(accession_digits).zfill(4), ref[:2] + str(reference_digits)]
                        reference_digits += 1
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
    parser.add_argument(
        '-csv',
        help='Enter the path to the Filmographic CSV'
    )
    parser.add_argument(
        '-reference',
        help='Enter the starting Filmographic reference number for the representation.'
    )
    parser.add_argument(
        '-dryrun', action='store_true',
        help='The script will reveal which identifiers will be assigned but will not actually perform any actions.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def get_filmographic_number(number):
    '''
    This check is not sustainable, will have to be made more flexible!
    '''
    if len(number) == 7:
        if number[:3] != 'af1':
            number = ififuncs.get_reference_number()
        return number
    else:
        number = ififuncs.get_reference_number()
        return number


def get_number(args):
    '''
    Figure out the first accession number and how to increment per package.
    '''
    if args.start_number:
        if args.start_number[:3] != 'aaa':
            print 'First three characters must be \'aaa\' and last four characters must be four digits'
            accession_number = ififuncs.get_accession_number()
        elif len(args.start_number[3:]) not in range(4, 6):
            accession_number = ififuncs.get_accession_number()
            print 'First three characters must be \'aaa\' and last four characters must be four digits'
        elif not args.start_number[3:].isdigit():
            accession_number = ififuncs.get_accession_number()
            print 'First three characters must be \'aaa\' and last four characters must be four digits'
        else:
            accession_number = args.start_number
    else:
        accession_number = ififuncs.get_accession_number()
    accession_digits = accession_number[3:].zfill(4)
    return accession_number[:3] + accession_digits


def main(args_):
    '''
    Batch process packages by running accession.py and makepbcore.py
    '''
    args = parse_args(args_)
    oe_list = []
    if args.csv:
        for line_item in ififuncs.extract_metadata(args.csv)[0]:
            oe_number = line_item['Object Entry'].lower()
            # this transforms OE-#### to oe####
            transformed_oe = oe_number[:2] + oe_number[3:]
            oe_list.append(transformed_oe)
    if args.reference:
        reference_number = get_filmographic_number(args.reference)
    else:
        reference_number = ififuncs.get_reference_number()
    user = ififuncs.get_user()
    accession_number = get_number(args)
    accession_digits = int(accession_number[3:])
    to_accession = initial_check(args, accession_digits, oe_list, reference_number)
    register = accession.make_register()
    if args.csv:
        desktop_logs_dir = ififuncs.make_desktop_logs_dir()
        new_csv = os.path.join(desktop_logs_dir, os.path.basename(args.csv))
        filmographic_dict, headers = ififuncs.extract_metadata(args.csv)
        for oe_package in to_accession:
            for filmographic_record in filmographic_dict:
                if os.path.basename(oe_package).upper()[:2] + '-' + os.path.basename(oe_package)[2:] == filmographic_record['Object Entry']:
                    filmographic_record['Reference Number'] = to_accession[oe_package][1]
        with open(new_csv, 'w') as csvfile:
            fieldnames = headers
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in filmographic_dict:
                writer.writerow(i)
    if args.dryrun:
        sys.exit()
    proceed = ififuncs.ask_yes_no(
        'Do you want to proceed?'
    )
    if proceed == 'Y':
        for package in sorted(to_accession.keys()):
            accession.main([
                package, '-user', user,
                '-p', '-f',
                '-number', to_accession[package][0],
                '-reference', to_accession[package][1],
                '-register', register
            ])
    collated_pbcore = gather_metadata(args.input)
    print '\nA helper accessions register has been generated in order to help with registration - located here: %s' % register
    print '\nA modified filmographic CSV has been generated with added reference numbers - located here: %s' % new_csv
    print '\nA collated CSV consisting of each PBCore report has been generated for batch database import - located here: %s' % collated_pbcore
if __name__ == '__main__':
    main(sys.argv[1:])
