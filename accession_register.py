#!/usr/bin/env python
'''
Generates a helper accessions register based on the metadata in other
spreadsheets.
'''
import sys
import argparse
import csv
import time
import os
import ififuncs

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Generates a helper accessions register.'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        '-register', help='Path to helper accessions register'
    )
    parser.add_argument(
        '-technical',
        help='Path to technical/PBCore CSV.'
    )
    parser.add_argument(
        '-filmographic',
        help='Path to Filmographic CSV. Must contain reference numbers.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def find_checksums(csv_file, identifier):
    '''
    Finds the relevant entries in the CSV and prints to terminal
    '''
    csv_dict = ififuncs.extract_metadata(csv_file)
    manifest_lines = []
    for items in csv_dict:
        for x in items:
            if type(x) is dict:
                if identifier in x['path']:
                    identifier_string = "/%s/" % identifier
                    manifest_line = x['hash_code'] + '  ' + x['path'].replace(identifier_string, '')
                    manifest_lines.append(manifest_line)
    strongbox_list = sorted(manifest_lines, key=lambda x: (x[130:]))
    return strongbox_list

def main(args_):
    '''
    Launches functions that will generate a helper accessions register
    '''
    args = parse_args(args_)
    register_dict = ififuncs.extract_metadata(args.register)[0]
    technical_dict = ififuncs.extract_metadata(args.technical)[0]
    filmographic_dict = ififuncs.extract_metadata(args.filmographic)[0]
    for accession in register_dict:
        number = accession['accession number']
        for technical_record in technical_dict:
            if technical_record['Accession Number'] == number:
                accession['acquisition method'] = technical_record['Type Of Deposit']
                accession['acquired from'] = technical_record['Donor']
                accession['date acquired'] = technical_record['Date Of Donation']
                for filmographic_record in filmographic_dict:
                    if filmographic_record['Reference Number'] == technical_record['Reference Number']:
                        if filmographic_record['Title'] == '':
                            title = filmographic_record['TitleSeries'] + '; ' + filmographic_record['EpisodeNo']
                        else:
                            title = filmographic_record['Title']
                        simple = '%s (%s) | %s' % (title, filmographic_record['Year'], technical_record['dig_object_descrip'])
                        if accession['acquisition method'] == 'Reproduction':
                            simple += ' | Reproduction of %s' % technical_record['TTape Origin']
                        accession['simple name; basic description; identification; historical information'] = simple
    desktop_logs_dir = ififuncs.make_desktop_logs_dir()
    new_csv_filename = time.strftime("%Y-%m-%dT%H_%M_%S_") + 'helper_register.csv'
    new_csv = os.path.join(desktop_logs_dir, new_csv_filename)
    with open(new_csv, 'w') as csvfile:
            fieldnames = ififuncs.extract_metadata(args.register)[1]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in register_dict:
                writer.writerow(i)
    print('\nYour helper CSV file is located here: %s\n' % new_csv)



if __name__ == '__main__':
    main(sys.argv[1:])
