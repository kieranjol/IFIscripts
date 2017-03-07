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


def capture_description(premis, xml_info):
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
    m200pAgent                                 = make_agent(premis,[transcode_uuid] , '60ae3a85-b595-45e0-8e4a-b95e90a6c422')
    
    capture_agents = [ffmpegAgent, m200pAgent]
    make_event(premis, 'creation', 'transcode to ffv1 (figure out wording later)', capture_agents, transcode_uuid,xml_info[4], 'outcome', 'now-placeholder')
    
    
def get_checksum(manifest):
    if os.path.isfile(manifest):
        with open(manifest, 'r') as fo:
            manifest_lines = fo.readlines()
            for md5 in manifest_lines:
                if md5[-5:].rsplit()[0] == '.mkv':
                    return md5[:32]


def get_capture_workstation(mediaxml):
    mediaxml_object         = ET.parse(mediaxml)
    mxml      = mediaxml_object.getroot()
    mediaExpress_check =  len(mxml.xpath('//COMAPPLEPROAPPSLOGNOTE'))
    fcp7_check =  len(mxml.xpath('//COMAPPLEFINALCUTSTUDIOMEDIAUUID'))
    if mediaExpress_check > 0:
        print 'this was probably Media Express?'
    elif fcp7_check > 0:
        print 'this was probably FCP7?'
    else:
        # i can't find any meaningful distinctive metadata that control room writes.
        print 'this was probably Control Room?'

    sys.exit()
    capture_station = ''
    if not capture_station == '1' or capture_station == '2' or capture_station == '3':
        capture_station =  raw_input('\n\n**** Where was tape captured?\nPress 1, 2 or 3\n\n1. es2\n2. loopline\n3. ingest 1\n' )
        while capture_station not in ('1','2','3'):
            capture_station =  raw_input('\n\n**** Where was tape captured?\nPress 1, 2 or 3\n\n1. es2\n2. loopline\n3. ingest 1\n' )
    if capture_station == '1':
        capture_station = 'telecine'
    elif capture_station == '2':
        capture_station = 'ca_machine'
    elif capture_station == '3':
        capture_station = 'ca_machine'
    return capture_station


def main():
    premisxml, premis_namespace, doc, premis = setup_xml(sys.argv[1])
    
    source_file = sys.argv[1]
    sip_dir = os.path.dirname(source_file)
    parent_dir = os.path.dirname(sip_dir)
    metadata_dir = os.path.join(parent_dir, 'metadata')
    ffv1_xml = os.path.join(metadata_dir, os.path.basename(sys.argv[1] + '_mediainfo.xml'))
    if os.path.isfile(ffv1_xml):
        get_capture_workstation(ffv1_xml)
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
    capture_description(premis, xml_info)
    
    
    
    write_premis(doc, premisxml)

if __name__ == '__main__':
    main()
