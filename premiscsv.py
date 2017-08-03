#!/usr/bin/env python
'''
Extracts preservation events from an IFI plain text log file and converts
to a CSV using the PREMIS data dictionary
'''
import os
import sys
# from lxml import etree
import ififuncs
def find_events(logfile):
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
                ififuncs.append_csv('events.csv', event_row)

def make_events_csv():
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
    ififuncs.create_csv('events.csv', premis_events)

def main():
    '''
    Launches all the other functions when run from the command line.
    '''
    make_events_csv()
    logfile = sys.argv[1]
    find_events(logfile)

if __name__ == '__main__':
    main()
