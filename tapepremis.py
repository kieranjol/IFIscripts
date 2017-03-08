#!/usr/bin/env python
import subprocess
import argparse
import sys
import os
import hashlib
import shutil
import uuid
import time
import uuid
from glob import glob
import lxml.etree as ET
from ififuncs import hashlib_manifest
from ififuncs import get_date_modified
from premis import make_premis
from premis import write_premis
from premis import make_agent
from premis import make_event
from premis import setup_xml
from premis import create_representation
from premis import create_intellectual_entity


def capture_description(premis, xml_info,capture_station):
    '''
    Events:
    1. capture - glean from v210 mediainfo xml
    2. ffv1 - ffmpeg logs but get time from sip log also user input
    3. lossless verification - ffmpeg logs and time/judgement from sip log
    4. whole file manifest - sip log
    that's it?
    '''
    capture_uuid                                = str(uuid.uuid4())
    transcode_uuid                              = str(uuid.uuid4())
    framemd5_uuid                               = str(uuid.uuid4())
    manifest_uuid                               = str(uuid.uuid4())
    ffmpegAgent                                 = make_agent(premis,[transcode_uuid] , 'ee83e19e-cdb1-4d83-91fb-7faf7eff738e')
    j30sdiAgent                                 = make_agent(premis,[capture_uuid] , 'e2ca7ad2-8edf-4e4e-a3c7-36e970c796c9')
    bm4kAgent                                   = make_agent(premis,[capture_uuid] , 'f47b98a2-b879-4786-9f6b-11fc3234a91e')
    edit_suite2_macAgent                        = make_agent(premis,[capture_uuid] , '75a0b9ff-1f04-43bd-aa87-c31b73b1b61c')
    m2000pAgent                                 = make_agent(premis,[capture_uuid] , '60ae3a85-b595-45e0-8e4a-b95e90a6c422')
    elcapitanAgent                              = make_agent(premis,[capture_uuid] , '68f56ede-a1cf-48aa-b1d8-dc9850d5bfcc')
    print capture_station
    if capture_station == 'es2':
        capture_agents = [j30sdiAgent, bm4kAgent, edit_suite2_macAgent, elcapitanAgent]
    if capture_station == 'loopline':
        capture_agents = [j30sdiAgent, bm4kAgent, edit_suite2_macAgent, elcapitanAgent]
    make_event(premis, 'creation', 'tape capture', capture_agents, capture_uuid,xml_info[4], 'outcome', 'now-placeholder')
    make_event(premis, 'compression', 'transcode to ffv1 (figure out wording later)', capture_agents, transcode_uuid,xml_info[4], 'outcome', 'now-placeholder')
    make_event(premis, 'fixity check', 'lossless verification via framemd5 (figure out wording later)', capture_agents, framemd5_uuid,xml_info[4], 'source', 'now-placeholder')
    make_event(premis, 'message digest calculation', 'whole file checksum manifest of SIP', capture_agents, manifest_uuid,xml_info[4], 'source', 'now-placeholder')
    
    
def get_checksum(manifest):
    if os.path.isfile(manifest):
        with open(manifest, 'r') as fo:
            manifest_lines = fo.readlines()
            for md5 in manifest_lines:
                if md5[-5:].rsplit()[0] == '.mkv':
                    return md5[:32]

def get_times(sourcexml):

    mediaxml_object         = ET.parse(sourcexml)
    mxml      = mediaxml_object.getroot()
    capture_date =  mxml.xpath('//File_Modified_Date_Local')[0].text #encoded date is probably better
    print capture_date
def get_capture_workstation(mediaxml):
    mediaxml_object         = ET.parse(mediaxml)
    mxml      = mediaxml_object.getroot()
    mediaExpress_check =  len(mxml.xpath('//COMAPPLEPROAPPSLOGNOTE'))
    fcp7_check =  len(mxml.xpath('//COMAPPLEFINALCUTSTUDIOMEDIAUUID'))
    if mediaExpress_check > 0:
        print 'this was probably Media Express?'
        capture_station = 'es2'
    elif fcp7_check > 0:
        print 'this was probably FCP7?'
        capture_station = 'loopline'
    else:
        # i can't find any meaningful distinctive metadata that control room writes.
        print 'this was probably Control Room?'
        capture_station = 'ingest1'
    print 'Does this sound ok? Y/N?'
    print capture_station
    station_confirm = ''    
    while station_confirm not in ('Y','y','N','n'):
            station_confirm = raw_input()
            if station_confirm not in ('Y','y','N','n'):
                print 'Incorrect input. Please enter Y or N'
            elif station_confirm not in ('Y','y'):
                capture_station = ''
                if not capture_station == '1' or capture_station == '2' or capture_station == '3':
                    capture_station =  raw_input('\n\n**** Where was tape captured?\nPress 1, 2 or 3\n\n1. es2\n2. loopline\n3. ingest 1\n' )
                    while capture_station not in ('1','2','3'):
                        capture_station =  raw_input('\n\n**** Where was tape captured?\nPress 1, 2 or 3\n\n1. es2\n2. loopline\n3. ingest 1\n' )
                if capture_station == '1':
                    capture_station = 'es2'
                elif capture_station == '2':
                    capture_station = 'loopline'
                elif capture_station == '3':
                    capture_station = 'ingest1'
    return capture_station


def main():
    premisxml, premis_namespace, doc, premis = setup_xml(sys.argv[1])
    
    source_file = sys.argv[1]
    sip_dir = os.path.dirname(source_file)
    parent_dir = os.path.dirname(sip_dir)
    metadata_dir = os.path.join(parent_dir, 'metadata')
    ffv1_xml = os.path.join(metadata_dir, os.path.basename(sys.argv[1] + '_mediainfo.xml'))
    # the replace here is a terrible hack. Sad! Fix!
    source_xml = os.path.join(metadata_dir, os.path.basename(sys.argv[1].replace('.mkv', '.mov') + '_source_mediainfo.xml'))
    get_times(source_xml)
    if os.path.isfile(ffv1_xml):
        capture_station = get_capture_workstation(ffv1_xml)
    else:
        print('Can\'t find XML of FFv1 file. Exiting!')
        sys.exit() 
    '''
    /home/kieranjol/ifigit/ifiscripts/massive/objects sip
    /home/kieranjol/ifigit/ifiscripts/massive parent

    '''
    manifest = parent_dir + '_manifest.md5'
    if not os.path.isfile(manifest):
        print 'no manifest found'
        sys.exit()
    md5 = get_checksum(manifest)
    items = {"workflow":"raw audio","oe":os.path.basename(source_file), "filmographic":'n/a', "sourceAccession":os.path.basename(source_file), "interventions":['placeholder'], "prepList":['placeholder'], "user":'Kieran O\' Leary'}
    representation_uuid = str(uuid.uuid4())
    # the final argument here is 'loopline' which tells premis.py to not generate a checksum
    xml_info = make_premis(source_file, items, premis, premis_namespace, premisxml,representation_uuid,md5)
    capture_description(premis, xml_info, capture_station)
    
    
    
    write_premis(doc, premisxml)

if __name__ == '__main__':
    main()
