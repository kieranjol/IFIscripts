#!/usr/bin/env python
'''
Batch process packages by running accession.py and makepbcore.py
The outcome will be:
* Packages are accessioned
* Filmographic records can be ingested to DB TEXTWORKS
* Technical records can be ingested to DB TEXTWORKS
* Skeleton accession record can be also be made available.

NOTE - this is almost done, you just need to find when to_accession[package] == 3, then
add an arg to the accession commmand that will declare the package as a reproduction.
'''
import argparse
import sys
import csv
import os
import re
import time
import ififuncs
import accession
import copyit
import order

'''
the following two functions for natural sorting are stolen from
https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
'''
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]


def gather_metadata(source):
    '''
    Loops through all subfolders that contain pbcore_csv and then harvests the
    metadata and store in a single file for the purposes of batch import into
    the DB TEXTWORKS technical database.
    '''
    metadata = []
    for root, _, filenames in sorted(os.walk(source)):
        for filename in filenames:
            if filename.endswith('pbcore.csv'):
                with open(os.path.join(root,filename), 'r') as csv_file:
                    csv_rows = csv_file.readlines()
                if metadata:
                    metadata.append([csv_rows[1]])
                else:
                    metadata.append([csv_rows[0]])
                    metadata.append([csv_rows[1]])
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
    # so just reverse this - loop through the csv first.
    # this will break the non CSV usage of batchaccession for now.
    for thingies in oe_list:
        for root, _, _ in sorted(os.walk(args.input)):
            if os.path.basename(root)[:2] == 'oe' and len(os.path.basename(root)[2:]) >= 4:
                if copyit.check_for_sip(root) is None:
                    wont_accession.append(root)
                else:
                    # this is just batchaccessioning if no csv is supplied
                    # this is pretty pointless at the moment seeing as this is loopline through oe_list :(
                    if not oe_list:
                        to_accession[root] = 'aaa' + str(accession_digits).zfill(4)
                        accession_digits += 1
                    else:
                        # gets parent info
                        if os.path.basename(root) == thingies:
                            to_accession[
                                os.path.join(os.path.dirname(root),
                                             order.main(root))
                            ] = [
                                'aaa' + str(accession_digits).zfill(4),
                                ref[:2] + str(reference_digits).zfill(4)
                            ]
                            if root in to_accession:
                                # If a single file is found, this prevents the file being
                                # processed twice, with a skip in the number run
                                reference_digits += 1
                                accession_digits += 1
                                continue
                            accession_digits += 1
                            # gets reproduction info
                            to_accession[root] = ['aaa' + str(accession_digits).zfill(4), ref[:2] + str(reference_digits), 'reproduction']
                            reference_digits += 1
                            accession_digits += 1
    for fails in wont_accession:
        print '%s looks like it is not a fully formed SIP. Perhaps loopline_repackage.py should proccess it?' % fails
    for success in sorted(to_accession.keys()):
        print '%s will be accessioned as %s' %  (success, to_accession[success])
    return to_accession

def get_filmographic_titles(to_accession, filmographic_dict):
    '''
    Retrieves filmographic titles of packages to be accessioned for QC purposes
    '''
    for ids in to_accession:
        oe_number = os.path.basename(ids)
        oe = oe_number[:2].upper() + '-' + oe_number[2:]
        for record in filmographic_dict:
            if record['Object Entry'] == oe:
                print record['Title']
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
        '-filmographic',
        help='Enter the path to the Filmographic CSV'
    )
    parser.add_argument(
        '-oe_csv',
        help='Enter the path to the Object Entry CSV'
    )
    parser.add_argument(
        '-reference',
        help='Enter the starting Filmographic reference number for the representation. This is not required when using the -oe_csv option'
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
        return number.upper()
    else:
        number = ififuncs.get_reference_number()
        return number.upper()


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
def process_oe_csv(oe_csv_extraction, source_path):
    '''
    generate a dictionary with the relevant data per object, namely:
    title, reference number, OE number and parent.
    '''
    oe_dicts = []
    for record in oe_csv_extraction[0]:
        try:
            dictionary = {}
            dictionary['Object Entry'] = record['OE No.']
            dictionary['normalised_oe_number']  = dictionary['Object Entry'][:2].lower() + dictionary['Object Entry'][3:]
            dictionary['source_path'] = os.path.join(source_path, dictionary['normalised_oe_number'])
            dictionary['parent'] = record['Additional Information'].split('Reproduction of ')[1].split('|')[0].rstrip()
            dictionary['reference number'] = record['Additional Information'].split('Representation of ')[1].split('|')[0].rstrip()
            oe_dicts.append(dictionary)
        except IndexError:
            continue
    return oe_dicts

def main(args_):
    '''
    Batch process packages by running accession.py and makepbcore.py
    '''
    args = parse_args(args_)
    oe_list = []
    if args.oe_csv:
        if not args.filmographic:
            print(' - batchaccession.py - ERROR\n - No -filmographic argument supplied. This is mandatory when using the -oe_csv option. \n - Exiting..')
            sys.exit()
        oe_csv_extraction = ififuncs.extract_metadata(args.oe_csv)
        initial_oe_list = oe_csv_extraction[0]
        oe_dicts = process_oe_csv(oe_csv_extraction, args.input)
        # temp hack while we're performing both workflows
        helper_csv = args.oe_csv
    elif args.filmographic:
        initial_oe_list = ififuncs.extract_metadata(args.filmographic)[0]
        # temp hack while we're performing both workflows
        helper_csv = args.filmographic
    if args.oe_csv or args.filmographic:
        for line_item in ififuncs.extract_metadata(helper_csv)[0]:
            try:
                oe_number = line_item['Object Entry'].lower()
            except KeyError:
                oe_number = line_item['OE No.'].lower()
            # this transforms OE-#### to oe####
            transformed_oe = oe_number[:2] + oe_number[3:]
            oe_list.append(transformed_oe)
    if not args.oe_csv:
        # No need to ask for the reference number if the OE csv option is supplied.
        # The assumption here is that the OE csv contains the reference numbers though.
        if args.reference:
            reference_number = get_filmographic_number(args.reference)
        else:
            reference_number = ififuncs.get_reference_number()
    donor = ififuncs.ask_question('Who is the source of acquisition, as appears on the donor agreement? This will not affect Reproductions.')
    depositor_reference = ififuncs.ask_question('What is the donor/depositor number? This will not affect Reproductions.')
    acquisition_type = ififuncs.get_acquisition_type('')
    user = ififuncs.get_user()
    accession_number = get_number(args)
    accession_digits = int(accession_number[3:])
    if not args.oe_csv:
        to_accession = initial_check(args, accession_digits, oe_list, reference_number)
    else:
        to_accession = {}
        for oe_record in oe_dicts:
            if os.path.isdir(oe_record['source_path']):
                to_accession[oe_record['source_path']] = ['aaa' + str(accession_digits).zfill(4), oe_record['reference number'], oe_record['parent']]
                accession_digits += 1
    for success in sorted(to_accession.keys()):
        print('%s will be accessioned as %s' %  (success, to_accession[success]))
    register = accession.make_register()
    if args.filmographic:
        desktop_logs_dir = ififuncs.make_desktop_logs_dir()
        if args.dryrun:
            new_csv_filename = time.strftime("%Y-%m-%dT%H_%M_%S_DRYRUN_SHEET_PLEASE_DO_NOT_INGEST_JUST_IGNORE_COMPLETELY") + os.path.basename(args.filmographic)
        else:
            new_csv_filename = time.strftime("%Y-%m-%dT%H_%M_%S_") + os.path.basename(args.filmographic)
        new_csv = os.path.join(desktop_logs_dir, new_csv_filename)
        if not args.oe_csv:
            filmographic_dict, headers = ififuncs.extract_metadata(args.filmographic)
            for oe_package in to_accession:
                for filmographic_record in filmographic_dict:
                    if os.path.basename(oe_package).upper()[:2] + '-' + os.path.basename(oe_package)[2:] == filmographic_record['Object Entry']:
                        filmographic_record['Reference Number'] = to_accession[oe_package][1]
            get_filmographic_titles(to_accession, filmographic_dict)
            with open(new_csv, 'w') as csvfile:
                fieldnames = headers
                # Removes Object Entry from headings as it's not needed in database.
                del fieldnames[1]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for i in filmographic_dict:
                    i.pop('Object Entry', None)
                    # Only include records that have reference numbers
                    if not i['Reference Number'] == '':
                        writer.writerow(i)
    if args.dryrun:
        sys.exit()
    proceed = ififuncs.ask_yes_no(
        'Do you want to proceed?'
    )
    if args.oe_csv:
        new_csv = args.filmographic
    if proceed == 'Y':
        for package in sorted(to_accession.keys(), key=natural_keys):
            accession_cmd = [
                package, '-user', user,
                '-pbcore', '-f',
                '-number', to_accession[package][0],
                '-reference', to_accession[package][1],
                '-register', register,
                '-csv', new_csv
            ]
            if len(to_accession[package]) == 3:
                accession_cmd.extend(['-acquisition_type', '13'])
                if args.oe_csv:
                    accession_cmd.extend(['-parent', to_accession[package][2]])
                else:
                    accession_cmd.extend(['-parent', order.main(package)])
            else:
                accession_cmd.extend(['-donor', donor])
                accession_cmd.extend(['-depositor_reference', depositor_reference])
                accession_cmd.extend(['-acquisition_type', acquisition_type[2]])
            print accession_cmd
            accession.main(accession_cmd)
    collated_pbcore = gather_metadata(args.input)
    sorted_filepath = ififuncs.sort_csv(register, 'accession number')
    print '\nA helper accessions register has been generated in order to help with registration - located here: %s' % sorted_filepath
    print '\nA modified filmographic CSV has been generated with added reference numbers - located here: %s' % new_csv
    print '\nA collated CSV consisting of each PBCore report has been generated for batch database import - located here: %s' % collated_pbcore
if __name__ == '__main__':
    main(sys.argv[1:])
