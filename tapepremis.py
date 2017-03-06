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
from ififuncs import hashlib_manifest
from ififuncs import get_date_modified
from premis import make_premis
from premis import write_premis
from premis import make_agent
from premis import make_event
from premis import setup_xml
from premis import create_representation
from premis import create_intellectual_entity

def get_checksum(manifest):
    if os.path.isfile(manifest):
        with open(manifest, 'r') as fo:
            manifest_lines = fo.readlines()
            for md5 in manifest_lines:
                if md5[-5:].rsplit()[0] == '.mkv':
                    return md5[:32]


def get_capture_workstation():
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
    get_capture_workstation()
    source_file = sys.argv[1]
    sip_dir = os.path.dirname(source_file)
    parent_dir = os.path.dirname(sip_dir)
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
    capture_uuid                                = str(uuid.uuid4())
    transcode_uuid                              = str(uuid.uuid4())
    framemd5_uuid                               = str(uuid.uuid4())
    manifest_uuid                               = str(uuid.uuid4())
    ffmpegAgent                                 = make_agent(premis,[transcode_uuid] , 'ee83e19e-cdb1-4d83-91fb-7faf7eff738e')
    make_event(premis, 'creation', 'transcode to ffv1 (figure out wording later)', [ffmpegAgent], transcode_uuid,xml_info[4], 'outcome', 'now-placeholder')
    
    write_premis(doc, premisxml)

if __name__ == '__main__':
    main()
