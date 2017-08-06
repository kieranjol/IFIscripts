#!/usr/bin/env python
'''
Extracts preservation events from an IFI plain text log file and converts
to a CSV using the PREMIS data dictionary
'''
import os
import sys
import csv
import shutil
import argparse
# from lxml import etree
import ififuncs


def find_events(logfile, objects_csv, output):
    '''
    A very hacky attempt to extract the relevant preservation events from our
    log files.
    '''
    sip_test = os.path.basename(logfile).replace('_sip_log.log', '')
    if ififuncs.validate_uuid4(sip_test) != False:
        linking_object_identifier_value = sip_test
    with open(logfile, 'r') as logfile_object:
        log_lines = logfile_object.readlines()
    for event_test in log_lines:
        if 'eventDetail=copyit.py' in event_test:
            logsplit = event_test.split(',')
            for line_fragment in logsplit:
                manifest_event = line_fragment.replace(
                    'eventDetail', ''
                ).replace('\n', '').split('=')[1]
    object_info = ififuncs.extract_metadata('objects.csv')
    object_locations = {}
    for i in object_info:
        object_locations[i['contentLocationValue']] = i['objectIdentifier'].split(', ')[1].replace(']', '')
    for log_entry in log_lines:
        valid_entries = [
            'eventType',
            'eventDetail=sipcreator.py',
            'eventDetail=Mediatrace',
            'eventDetail=Technical',
            'eventDetail=copyit.py'
        ]
        for entry in valid_entries:
            if entry in log_entry:
                break_loop = ''
                event_outcome = ''
                event_detail = ''
                event_outcome_detail_note = ''
                event_type = ''
                event_row = []
                datetime = log_entry[:19]
                logsplit = log_entry.split(',')
                for line_fragment in logsplit:
                    if 'eventType' in line_fragment:
                        if 'EVENT =' in line_fragment:
                            line_fragment = line_fragment.split('EVENT =')[1]
                        event_type = line_fragment.replace(
                            ' eventType=', ''
                        ).replace('assignement', 'assignment')
                    if ' value' in line_fragment:
                        # this assumes that the value is the outcome of an identifier assigment.
                        event_outcome = line_fragment[7:].replace('\n', '')
                    # we are less concerned with events starting.
                    if 'status=started' in line_fragment:
                        break_loop = 'continue'
                    if 'Generating destination manifest:' in line_fragment:
                        break_loop = ''
                        event_detail = manifest_event
                    # ugh, this might run multiple times.
                    if 'eventDetail=sipcreator.py' in log_entry:
                        event_type = 'Information Package Creation'
                        event_detail = line_fragment.replace(
                            'eventDetail', ''
                        ).replace('\n', '').split('=')[1]
                        event_outcome_detail_note = 'Submission Information Package'
                    if ('eventDetail=Mediatrace' in log_entry) or ('eventDetail=Technical' in log_entry):
                        event_type = 'metadata extraction'
                        event_detail = log_entry.split(
                            'eventDetail=', 1
                        )[1].split(',')[0]
                        event_outcome = log_entry.split(
                            'eventOutcome=', 1
                        )[1].replace(', agentName=mediainfo', '').replace('\n', '')
                        if 'eventDetail=Mediatrace' in log_entry:
                            event_outcome = event_outcome.replace('mediainfo.xml', 'mediatrace.xml')
                        for x in object_locations:
                            '''
                            This is trying to get the UUID of the source object
                            that relates to the mediainfo xmls. This is
                            achieved via a dictionary.
                            '''
                            if 'objects' in x:
                                a = os.path.basename(event_outcome).replace('_mediainfo.xml', '').replace('_mediatrace.xml', '')[:-1]
                                b = os.path.basename(x)
                                if a == b:
                                    linking_object_identifier_value = object_locations[x].replace('\'','')
                if (break_loop == 'continue') or (event_type == ''):
                    continue
                print event_type
                event_row = [
                    'UUID', ififuncs.create_uuid(),
                    event_type, datetime, event_detail,
                    '',
                    event_outcome, '',
                    event_outcome_detail_note, '',
                    '', '',
                    '', 'UUID',
                    linking_object_identifier_value, ''
                ]
                ififuncs.append_csv(output, event_row)

def update_objects(output, objects_csv):
    '''
    Update the object description with the linkingEventIdentifiers
    '''
    link_dict = {}
    event_dicts = ififuncs.extract_metadata(output)
    for i in event_dicts:
        a =  i['eventIdentifierValue']
        try:
            link_dict[i['linkingObjectIdentifierValue']]  += a + '|'
        except KeyError:
            link_dict[i['linkingObjectIdentifierValue']]  = a + '|'
    print link_dict
    object_dicts = ififuncs.extract_metadata(objects_csv)
    for x in object_dicts:
        for link in link_dict:

            if link ==  x['objectIdentifier'].split(', ')[1].replace(']', '').replace('\'',''):
                x['linkingEventIdentifierValue'] = link_dict[link]
    premis_object_units = [
        'objectIdentifier',
        'objectCategory',
        'messageDigestAlgorithm', 'messageDigest', 'messageDigestOriginator',
        'size',	'formatName', 'formatVersion',
        'formatRegistryName', 'formatRegistryKey', 'formatRegistryRole',
        'objectCharacteristicsExtension', 'originalName',
        'contentLocationType', 'contentLocationValue',
        'relatedObjectIdentifierType', 'relatedObjectIdentifierValue',
        'relatedObjectSequence',
        'relatedEventIdentifierType', 'relatedEventIdentifierValue',
        'relatedEventSequence',
        'linkingEventIdentifierType', 'linkingEventIdentifierValue',
        'relationship_structural_includes',
        'relationship_structural_isincludedin',
        'relationship_structural_represents',
        'relationship_structural_hasroot',
        'relationship_derivation_hassource'
    ]
    with open('mycsvfile.csv', 'wb') as f:
        counter = 0
        for i in object_dicts:
            w = csv.DictWriter(f, fieldnames=premis_object_units)
            if counter == 0:
                w.writeheader()
            counter += 1
            w.writerow(i)
    shutil.move('mycsvfile.csv', objects_csv)

def make_events_csv(output):
    '''
    Generates a CSV with PREMIS-esque headings. Currently it's just called
    'bla.csv' but it will probably be called:
    UUID_premisevents.csv
    and sit in the metadata directory.
    '''
    premis_events = [
        'eventIdentifierType', 'eventIdentifierValue',
        'eventType', 'eventDateTime', 'eventDetail',
        'eventDetailExtension',
        'eventOutcome',	'eventOutcomeDetail',
        'eventOutcomeDetailNote', 'eventOutcomeDetailExtension',
        'linkingAgentIdentifierType', 'linkingAgentIdentifierValue',
        'linkingAgentIdentifierRole', 'linkingObjectIdentifierType',
        'linkingObjectIdentifierValue', 'linkingObjectRole'
    ]
    ififuncs.create_csv(output, premis_events)

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Describes events using PREMIS data dictionary via CSV'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        '-i',
        help='full path of a log textfile', required=True
    )
    parser.add_argument(
        '-o',
        help='full path of output csv', required=True
    )
    parser.add_argument(
        '-object_csv',
        help='full path of object description csv', required=True
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args
def main(args_):
    '''
    Launches all the other functions when run from the command line.
    '''
    args = parse_args(args_)
    logfile = args.i
    output = args.o
    objects_csv = args.object_csv
    make_events_csv(output)
    find_events(logfile, objects_csv, output)
    update_objects(output, objects_csv)

if __name__ == '__main__':
    main(sys.argv[1:])
