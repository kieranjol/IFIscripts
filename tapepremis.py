#!/usr/bin/env python
import sys
import os
import uuid
import csv
import lxml.etree as ET
from ififuncs import get_date_modified
from premis import make_premis
from premis import make_agent
from premis import write_premis
from premis import setup_xml
from premis import create_representation
from premis import create_unit


def make_event(
    premis,event_type, event_detail,
    agentlist, eventID, eventLinkingObjectIdentifier,
    eventLinkingObjectRole, event_time
    ):
    # This is really only here because the premis.py version handles the \
    # linkingAgentIdentifiers differently.
    premis_namespace = "http://www.loc.gov/premis/v3"
    event = ET.SubElement(premis, "{%s}event" % (premis_namespace))
    premis.insert(-1,event)
    event_Identifier = create_unit(1,event,'eventIdentifier')
    event_id_type = ET.Element("{%s}eventIdentifierType" % (premis_namespace))
    event_Identifier.insert(0,event_id_type)
    event_id_value = ET.Element("{%s}eventIdentifierValue" % (premis_namespace))
    event_Identifier.insert(0,event_id_value)
    event_Type = ET.Element("{%s}eventType" % (premis_namespace))
    event.insert(2,event_Type)
    event_DateTime = ET.Element("{%s}eventDateTime" % (premis_namespace))
    event.insert(3,event_DateTime)
    if event_time == 'now':
        event_DateTime.text = time.strftime("%Y-%m-%dT%H:%M:%S")
    else:
        event_DateTime.text = event_time
    event_Type.text = event_type
    event_id_value.text = eventID
    event_id_type.text = 'UUID'
    eventDetailInformation = create_unit(
        4,event,'eventDetailInformation'
        )
    eventDetail = create_unit(
        0,eventDetailInformation,'eventDetail'
        )
    eventDetail.text = event_detail
    for i in eventLinkingObjectIdentifier:
        linkingObjectIdentifier = create_unit(
            5,event,'linkingObjectIdentifier'
            )
        linkingObjectIdentifierType = create_unit(
            0,linkingObjectIdentifier,'linkingObjectIdentifierType'
            )
        linkingObjectIdentifierValue = create_unit(
            1,linkingObjectIdentifier,'linkingObjectIdentifierValue'
            )
        linkingObjectIdentifierValue.text = i
        linkingObjectRole = create_unit(
            2,linkingObjectIdentifier,'linkingObjectRole'
            )
        linkingObjectIdentifierType.text = 'UUID'
        linkingObjectRole.text = eventLinkingObjectRole
    for i in agentlist:
        linkingAgentIdentifier = create_unit(
            -1,event,'linkingAgentIdentifier'
            )
        linkingAgentIdentifierType = create_unit(
            0,linkingAgentIdentifier,'linkingAgentIdentifierType'
            )
        linkingAgentIdentifierValue = create_unit(
            1,linkingAgentIdentifier,'linkingAgentIdentifierValue'
            )
        linkingAgentIdentifierRole = create_unit(
            2,linkingAgentIdentifier,'linkingAgentRole'
            )
        linkingAgentIdentifierRole.text = 'implementer'
        linkingAgentIdentifierType.text = 'UUID'
        linkingAgentIdentifierValue.text = i


def capture_description(premis, xml_info, capture_station, times, total_agents, engineer):
    '''
    Events:
    1. capture - glean from v210 mediainfo xml
    2. ffv1 - ffmpeg logs but get time from sip log also user input
    3. lossless verification - ffmpeg logs and time/judgement from sip log
    4. whole file manifest - sip log
    that's it?
    '''
    if engineer == 'Kieran O\'Leary':
        engineer_agent = '0b3b7e69-80e1-48ec-bf07-62b04669117d'
    elif engineer == 'Aoife Fitzmaurice':
        engineer_agent = '9e59e772-14b0-4f9e-95b3-b88b6e751c3b'
    elif engineer == 'Raelene Casey':
        engineer_agent = 'b342d3f7-d87e-4fe3-8da5-89e16a30b59e'
    
  
    capture_uuid = str(uuid.uuid4())
    capture_dict = {}
    if capture_station == 'es2':
        j30sdi_agent = 'e2ca7ad2-8edf-4e4e-a3c7-36e970c796c9'
        bm4k_agent = 'f47b98a2-b879-4786-9f6b-11fc3234a91e'
        edit_suite2_mac_agent = '75a0b9ff-1f04-43bd-aa87-c31b73b1b61c'
        elcapitan_agent = '68f56ede-a1cf-48aa-b1d8-dc9850d5bfcc'
        capture_agents = [
            j30sdi_agent, bm4k_agent,
            edit_suite2_mac_agent, elcapitan_agent,
            engineer_agent 
            ]
    elif capture_station == 'loopline':
        m2000p_agent = '60ae3a85-b595-45e0-8e4a-b95e90a6c422'
        kona3_agent = 'c5e504ca-b4d5-410f-b87b-4b7ed794e44d'
        loopline_mac_agent = 'be3060a8-6ccf-4339-97d5-a265687c3a5a'
        osx_lion_agent = 'c5fc84fc-cc96-42a1-a5be-830b4e3012ae'
        capture_agents = [
            m2000p_agent, kona3_agent,
            loopline_mac_agent, osx_lion_agent,
            engineer_agent
            ]
            
    elif capture_station == 'ingest1':
        sony510p_agent = 'dbdbb06b-ab10-49db-97a1-ff2ad285f9d2'
        ingest1_agent = '5fd99e09-63d7-4e9f-8383-1902f727d2a5'
        windows7_agent = '192f61b1-8130-4236-a827-a194a20557fe'
        ingest1kona_agent = 'c93ee9a5-4c0c-4670-b857-8726bfd23cae'
        capture_agents = [
            sony510p_agent, ingest1kona_agent,
            ingest1_agent, windows7_agent,
            engineer_agent
            ]
    make_event(
        premis, 'creation', 'tape capture',
        capture_agents, capture_uuid, xml_info[4], 'outcome', times[0]
        )
    event_dict = {}
    for agent in capture_agents:
        # Just the UUID is returned.
        event_dict[agent] = [capture_uuid]
    return event_dict


def ffv1_description(premis, xml_info, capture_station, times, event_dict, script_user):
    if script_user == 'Kieran O\'Leary':
        script_user_agent = '0b3b7e69-80e1-48ec-bf07-62b04669117d'
    elif script_user == 'Aoife Fitzmaurice':
        script_user_agent = '9e59e772-14b0-4f9e-95b3-b88b6e751c3b'
    elif script_user == 'Raelene Casey':
        script_user_agent = 'b342d3f7-d87e-4fe3-8da5-89e16a30b59e'    
    transcode_uuid = str(uuid.uuid4())
    framemd5_uuid = str(uuid.uuid4())
    manifest_uuid = str(uuid.uuid4())
    if capture_station == 'es2':
        edit_suite2_mac_agent = '75a0b9ff-1f04-43bd-aa87-c31b73b1b61c'
        elcapitan_agent = '68f56ede-a1cf-48aa-b1d8-dc9850d5bfcc'
        ffv1_agents = [
            edit_suite2_mac_agent, elcapitan_agent, script_user_agent
            ]    
        make_event(
            premis, 'compression',
            'transcode to FFV1/Matroska (figure out wording later)',
            ffv1_agents, transcode_uuid, xml_info[4], 'outcome', times[1]
            )
        
    elif capture_station == 'ingest1':
        ingest1_agent = '5fd99e09-63d7-4e9f-8383-1902f727d2a5'
        windows7_agent = '192f61b1-8130-4236-a827-a194a20557fe'
        ffv1_agents = [
            ingest1_agent, windows7_agent, script_user_agent
            ]
        make_event(
            premis, 'compression',
            'transcode to FFV1/Matroska (figure out wording later)',
            ffv1_agents, transcode_uuid, xml_info[4], 'outcome', times[1]
            )
    elif capture_station == 'loopline':
        osx_lion_agent = 'c5fc84fc-cc96-42a1-a5be-830b4e3012ae'
        loopline_mac_agent = 'be3060a8-6ccf-4339-97d5-a265687c3a5a'
        ffv1_agents = [
            osx_lion_agent, loopline_mac_agent, script_user_agent
            ]  
        make_event(
            premis, 'compression',
            'transcode to FFV1/Matroska while specifying 4:3 DAR '
            'and Top Field First interlacement',
            ffv1_agents, transcode_uuid, xml_info[4], 'outcome', times[1]
            )  
    make_event(
        premis, 'fixity check',
        'lossless verification via framemd5 (figure out wording later)',
        ffv1_agents, framemd5_uuid, xml_info[4], 'source', 'now-placeholder'
        )
    make_event(
        premis, 'message digest calculation',
        'whole file checksum manifest of SIP', ffv1_agents,
        manifest_uuid, xml_info[4], 'source', 'now-placeholder'
        )
    print ffv1_agents    
    for agent in ffv1_agents:
    # Just the UUID is returned.
        if agent in event_dict:
            event_dict[agent] += [transcode_uuid]
            event_dict[agent] += [framemd5_uuid]
            event_dict[agent] += [manifest_uuid]
        else:
            event_dict[agent] = [transcode_uuid]
            event_dict[agent] += [framemd5_uuid]
            event_dict[agent] += [manifest_uuid]
    for agent in event_dict:
        make_agent(
            premis, event_dict[agent],agent
            )


def get_checksum(manifest):
    if os.path.isfile(manifest):
        with open(manifest, 'r') as fo:
            manifest_lines = fo.readlines()
            for md5 in manifest_lines:
                if md5[-5:].rsplit()[0] == '.mkv':
                    return md5[:32]


def get_times(sourcexml):
    mediaxml_object = ET.parse(sourcexml)
    mxml = mediaxml_object.getroot()
    # encoded date is probably better
    capture_date = mxml.xpath('//File_Modified_Date_Local')[0].text
    return capture_date


def get_capture_workstation(mediaxml):
    mediaxml_object = ET.parse(mediaxml)
    mxml = mediaxml_object.getroot()
    mediaexpress_check = len(mxml.xpath('//COMAPPLEPROAPPSLOGNOTE'))
    fcp7_check = len(mxml.xpath('//COMAPPLEFINALCUTSTUDIOMEDIAUUID'))
    if mediaexpress_check > 0:
        print 'this was probably Media Express?'
        capture_station = 'es2'
    elif fcp7_check > 0:
        print 'this was probably FCP7?'
        capture_station = 'loopline'
    else:
        # i can't find any distinctive metadata that control room writes.
        print 'this was probably Control Room?'
        capture_station = 'ingest1'
    print 'Does this sound ok? Y/N?'
    station_confirm = ''
    while station_confirm not in ('Y', 'y', 'N', 'n'):
        station_confirm = raw_input()
        if station_confirm not in ('Y', 'y', 'N', 'n'):
            print 'Incorrect input. Please enter Y or N'
        elif station_confirm not in ('Y', 'y'):
            capture_station = ''
            if capture_station not in range(1, 4):
                capture_station = raw_input(
                    '\n\n**** Where was tape captured?\n'
                    'Press 1, 2 or 3\n\n1. es2\n2. loopline\n3. ingest 1\n'
                    )
                while int(capture_station) not in range(1, 4):
                    capture_station = raw_input(
                        '\n\n**** Where was tape captured?\n'
                        'Press 1, 2 or 3\n\n1. es2\n2. loopline\n3. ingest 1\n'
                        )
            if capture_station == '1':
                capture_station = 'es2'
            elif capture_station == '2':
                capture_station = 'loopline'
            elif capture_station == '3':
                capture_station = 'ingest1'
    return capture_station


    
def get_user(question):
    user = ''
    if not user == '1' or user == '2' or user =='3':
        user =  raw_input(
            '\n\n%s'
            '\nPress 1 or 2 or 3\n\n'
            '1. Kieran O\'Leary\n2. Aoife Fitzmaurice\n3. Raelene Casey\n' % question)
        while user not in ('1', '2', '3'):
            user =  raw_input(
            '\n\n%s'
            '\nPress 1 or 2 or 3\n\n'
            '1. Kieran O\'Leary\n2. Aoife Fitzmaurice\n3. Raelene Casey\n' % question)
    if user == '1':
        user = 'Kieran O\'Leary'
    elif user == '2':
        user = 'Aoife Fitzmaurice'
    elif user == '3':
        user = 'Raelene Casey'
    return user


def main():
    total_agents = []
    script_user = get_user('**** Who is running this script?')
    engineer = get_user('**** Who captured the actual tape?')
    premisxml, premis_namespace, doc, premis = setup_xml(sys.argv[1])
    source_file = sys.argv[1]
    sip_dir = os.path.dirname(source_file)
    parent_dir = os.path.dirname(sip_dir)
    metadata_dir = os.path.join(parent_dir, 'metadata')
    ffv1_xml = os.path.join(
        metadata_dir, os.path.basename(
            sys.argv[1]
            + '_mediainfo.xml'
            )
        )
    # the replace here is a terrible hack. Sad! Fix!
    source_xml = os.path.join(
        metadata_dir,
        os.path.basename(
            sys.argv[1].replace('.mkv', '.mov')
            + '_source_mediainfo.xml'))
    capture_time = get_times(source_xml)
    transcode_time = get_times(ffv1_xml)
    times = [capture_time, transcode_time]
    if os.path.isfile(ffv1_xml):
        capture_station = get_capture_workstation(ffv1_xml)
    else:
        print 'Can\'t find XML of FFv1 file. Exiting!'
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
    # this items var is sad,clearly there's hardcoded workflow crap in premis.py
    # I don't even know if any of these are relevant anymore
    items = {
        "workflow":"raw audio",
        "oe":os.path.basename(source_file),
        "filmographic":'n/a',
        "sourceAccession":os.path.basename(source_file),
        "interventions":['placeholder'],
        "prepList":['placeholder'],
        "user":'Kieran O\' Leary'
        }
    representation_uuid = str(uuid.uuid4())
    # looks like loopline isn't the keyword any longer. it's len = 32?
    xml_info = make_premis(
        source_file, items, premis,
        premis_namespace, premisxml, representation_uuid, md5
        )
    linkinguuids = [xml_info[4][0], 'n/a', os.path.basename(source_file)]
    create_representation(
        premisxml, premis_namespace, doc, premis,
        items, linkinguuids, representation_uuid, 'no_sequence', 'n/a'
        )
    event_dict = capture_description(
        premis, xml_info, capture_station, times, total_agents, engineer
        )
    ffv1_description(
        premis, xml_info, capture_station, times, event_dict, script_user
        )
    write_premis(doc, premisxml)

if __name__ == '__main__':
    main()
