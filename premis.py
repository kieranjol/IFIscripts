#!/usr/bin/env python
'''
Work in progress. I think this will just be a bunch of functions that other scripts can call on in order to use as a growing log file.
Representation:
1.1
1.2
1.4
1.6 - original name
1.7 - storage
1.13 - Relationship - each image should relate to the representation.
'''
#http://stackoverflow.com/questions/7703018/how-to-write-namespaced-element-attributes-with-lxml
import lxml.etree as ET
import lxml.builder as builder
import uuid
import time
import sys
import subprocess
import os
from glob import glob
import pg
import hashlib 
from collections import OrderedDict
import csv


source_file = sys.argv[1]
global items
global revtmd
items = pg.main()
print items,'whatver'
global manifest
global csv_file
manifest = os.path.dirname(os.path.abspath(source_file)) + '/' + os.path.basename(source_file) + '_manifest.md5'
csv_file = os.path.expanduser("~/Desktop/premis_agents.csv")
if os.path.isfile(csv_file):
                    read_object = open(csv_file)
                    reader = csv.reader(read_object)
                    csv_list = list(reader)
                    read_object.close()


def hashlib_md5(filename, manifest):
   print filename
   print manifest
   m = hashlib.md5()
   with open(str(filename), 'rb') as f:
       while True:
           buf = f.read(2**20)
           if not buf:
               break
           m.update(buf)
   md5_output = m.hexdigest()
   messageDigestAlgorithm.text = 'md5'
   messageDigest.text = md5_output
   with open(manifest, "ab") as fo:
       fo.write(md5_output + '  ' + source_file.split(os.sep)[-1] + '/' + filename +  '\n')

    
def add_value(value, element):
    element.text = value
    
def write_premis():
    outFile = open('premis.xml','w')
    doc.write(outFile,pretty_print=True)

def create_unit(index,parent, unitname):
    premis_namespace = "http://www.loc.gov/premis/v3"
    unitname = ET.Element("{%s}%s" % (premis_namespace, unitname))
    parent.insert(index,unitname)
    return unitname
def create_hash(filename):
    md5 = subprocess.check_output(['md5deep', filename])[:32]
    messageDigestAlgorithm.text = 'md5'
    messageDigest.text = md5
    return md5    

def get_input(filename):
    global video_files
    # Input, either file or firectory, that we want to process.
    input = filename
    # Store the directory containing the input file/directory.
    wd = os.path.dirname(os.path.abspath(input))
    print wd
    # Change current working directory to the value stored as "wd"
    os.chdir(wd)

    # Store the actual file/directory name without the full path.
    file_without_path = os.path.basename(input)

    # Check if input is a file.
    # AFAIK, os.path.isfile only works if full path isn't present.
    if os.path.isfile(file_without_path):      
        video_files = []                       # Create empty list 
        video_files.append(file_without_path)  # Add filename to list

    # Check if input is a directory. 
    elif os.path.isdir(file_without_path):  
        os.chdir(file_without_path)
        video_files = (
            glob('*.tif') +
            glob('*.tiff') +
            glob('*.dpx')
        )

    # Prints some stuff if input isn't a file or directory.
    else: 
        print "Your input isn't a file or a directory."   
    return video_files
    
def make_premis(source_file):
    main(source_file)   

def make_agent(agentIdType_value,agentIdValue_value,agentName_value,agentVersion_value, agentType_value, agentNote_value, linkingEventIdentifier_value ):
    agent = ET.SubElement(premis, "{%s}agent" % (premis_namespace))
    premis.insert(-1, agent)
    agentIdentifier = create_unit(1,agent,'agentIdentifier')
    agentIdType = create_unit(2,agentIdentifier,'agentIdentifierType')
    agentIdValue = create_unit(2,agentIdentifier,'agentIdentifierValue')
    agentName = create_unit(2,agent,'agentName')
    agentType = create_unit(3,agent,'agentType')
    agentVersion = create_unit(4,agent,'agentVersion')
    agentNote = create_unit(5,agent,'agentNote')
    linkingEventIdentifier = create_unit(6,agent,'linkingEventIdentifier')
    agentIdType.text = agentIdType_value
    agentIdValue.text = agentIdValue_value
    agentName.text = agentName_value
    agentType.text = agentType_value
    agentVersion.text = agentVersion_value
    agentNote.text = agentNote_value
    linkingEventIdentifier.text = linkingEventIdentifier_value
    agent_info = [agentIdType_value,agentIdValue_value]
    return agent_info
''''    
def make_environment(agentIdType_value,agentIdValue_value,agentName_value,agentVersion_value, agentType_value, agentNote_value, linkingEventIdentifier_value ):
    object_parent = create_unit(0, premis, 'object')
    object_identifier_parent = create_unit(1,object_parent, 'objectIdentifier')
    object_identifier_uuid_type = create_unit(1,object_identifier_uuid, 'objectIdentifierType')
    object_identifier_uuid_type.text = 'locally defined identifier'
    object_identifier_uuid_value = create_unit(2,object_identifier_uuid, 'objectIdentifierValue') 
    object_identifier_uuid_value.text = 'Environment 1'
    objectCategory = create_unit(2, object_parent, 'objectCategory')
    objectCategory.text = 'intellectual entity'
    environmentFunction = create_unit(2,object_parent,'environmentFunction')
    environmentFunctionType = create_unit(1,environmentFunction,'environmentFunctionType')
    environmentFunctionLevel = create_unit(2,environmentFunction,'environmentFunctionLevel')
    environmentDesignation = create_unit(3,object_parent,'environmentDesignation')
    environmentName = create_unit(1,environmentDesignation,'environmentName')
    environmentVersion = create_unit(2,environmentDesignation,'environmentVersion')
    environmentOrigin = create_unit(3,environmentDesignation,'environmentOrigin')
    environmentDesignationNote = create_unit(4,environmentDesignation,'DesignationNote')
    environmentDesignationExtension = create_unit(5,environmentDesignation,'environmentDesignationExtension')
    relationship = create_unit(4, object_parent, 'relationship')
    relationshipType = create_unit(0,relationship, 'relationshipType')
    relationshipType.text = 'structural'
    relationshipSubType = create_unit(0,relationship, 'relationshipSubType')
    relationshipSubType.text = '???'
    
'''    
def make_event(event_type, event_detail, agent1, agent2, eventID ):
        print agent1, agent2
        agent1type =agent1[0]
        agent1value =agent1[1]
        agent2type =agent2[0]
        agent2value =agent2[1]
        global linkingObjectIdentifierValue
        global event_Type
        
        global revtmd_capture_history
        
        event = ET.SubElement(premis, "{%s}event" % (premis_namespace))
        premis.insert(-1,event)
        #event_Identifier = ET.Element("{%s}eventIdentifier" % (premis_namespace))
        #event.insert(1,event_Identifier)
        event_Identifier = create_unit(1,event,'event_Identifier')
        event_id_type = ET.Element("{%s}eventIdentifierType" % (premis_namespace))
        event_Identifier.insert(0,event_id_type)
        event_id_value = ET.Element("{%s}eventIdentifierValue" % (premis_namespace))
        
        event_Identifier.insert(0,event_id_value)
        event_Type = ET.Element("{%s}eventType" % (premis_namespace))
        event.insert(2,event_Type)
        event_DateTime = ET.Element("{%s}eventDateTime" % (premis_namespace))
        event.insert(3,event_DateTime)
        event_DateTime.text = time.strftime("%Y-%m-%dT%H:%M:%S")
        event_Type.text = event_type
        event_id_value.text = eventID
        event_id_type.text = 'UUID'    
        eventDetailInformation = create_unit(4,event,'event_DetailInformation')
        eventDetail = create_unit(0,eventDetailInformation,'eventDetail')
        eventDetail.text = event_detail
        linkingObjectIdentifier = create_unit(5,event,'linkingObjectIdentifier')
        linkingObjectIdentifierType = create_unit(0,linkingObjectIdentifier,'linkingObjectIdentifierType')
        linkingObjectIdentifierValue = create_unit(1,linkingObjectIdentifier,'linkingObjectIdentifierValue')
        linkingObjectRole = create_unit(2,linkingObjectIdentifier,'linkingObjectRole')
        linkingObjectIdentifierType.text = 'IFI Irish Film Archive Object Entry Number'
        linkingObjectRole.text = 'source'  
        linkingAgentIdentifier = create_unit(6,event,'linkingAgentIdentifier')
        linkingAgentIdentifierType = create_unit(0,linkingAgentIdentifier,'linkingAgentIdentifierType')
        linkingAgentIdentifierValue = create_unit(1,linkingAgentIdentifier,'linkingAgentIdentifierValue')
        linkingAgentIdentifier= create_unit(1,linkingAgentIdentifier,'linkingAgentIdentifier')
        linkingAgentIdentifier.text = 'implementer'
        linkingAgentIdentifier2 = create_unit(7,event,'linkingAgentIdentifier')
        linkingAgentIdentifierType2 = create_unit(0,linkingAgentIdentifier2,'linkingAgentIdentifierType')
        linkingAgentIdentifierValue2 = create_unit(1,linkingAgentIdentifier2,'linkingAgentIdentifierValue')
        linkingAgentIdentifier2 = create_unit(1,linkingAgentIdentifier2,'linkingAgentIdentifier')
        linkingAgentIdentifier2.text = 'implementer'
        linkingAgentIdentifierType.text = agent1type 
        linkingAgentIdentifierValue.text = agent1value
        linkingAgentIdentifierType2.text = agent2type 
        linkingAgentIdentifierValue2.text = agent2value


        
        '''''
        if event_type == 'capture':
            
            eventDetailExtension = create_unit(1, eventDetailInformation, 'eventDetailExtension')
            revtmd_first = create_revtmd_unit(0, eventDetailExtension, 'object')
            revtmd_filename = create_revtmd_unit(1, revtmd_first, 'filename')
            revtmd_organisation = create_revtmd_unit(2, revtmd_first, 'organisation')
            revtmd_organisation_main = create_revtmd_unit(0, revtmd_organisation, 'organisation_main')
            revtmd_organisation_main_name = create_revtmd_unit(0, revtmd_organisation_main, 'name')
            revtmd_organisation_main_role = create_revtmd_unit(0, revtmd_organisation_main, 'role')
    
            revtmd_organisation_division = create_revtmd_unit(1, revtmd_organisation, 'organisation_divsion')
            revtmd_organisation_division_name = create_revtmd_unit(0, revtmd_organisation_division, 'name')
            revtmd_use = create_revtmd_unit(3, revtmd_first, 'use')
            revtmd_use.text = 'Preservation Master'
            revtmd_capture_history = create_revtmd_unit(4, revtmd_first, 'captureHistory')
            revtmd_digitizationDate = create_revtmd_unit(1, revtmd_capture_history, 'digitizationDate')
            revtmd_digitizationEngineer = create_revtmd_unit(2, revtmd_capture_history, 'digitizationEngineer')
            if items["workflow"] == 'scanning':
                for i in items['prepList']:
                    counter = 3
                    x = create_revtmd_unit(counter, revtmd_capture_history, 'preparationActions')
                    x.text = i
                    counter += 1
                process_history(revtd_basement_2k_scanner, 1)
                process_history(revtd_basement_2k_scanner_host_computer, 2) 
                process_history(revtd_basement_2k_scanner_host_computer_os, 3)
                process_history(revtd_basement_2k_scanner_software, 4) 
                process_history(revtmd_basement_content_agent_pc, 5) 
                process_history(revtmd_basement_content_agent_os, 6) 
                
            if items["workflow"] == 'tape':
                revtmd_edit_2_computer = (('role','Host Computer'), ('manufacturer','Apple'), ('modelName','Mac Pro'), ('serialNumber','???'))
                revtmd_edit_2_computer_os = (('role','Host Computer Operating System'), ('manufacturer','Apple'), ('version','El Capitan'))
                revtmd_edit_2_blackmagic_hardware = (('role','Capture Card'), ('manufacturer','Blackmagic'), ('modelName','Ultrastudio 4k'),('signal','SDI'), ('serialNumber','2965997'))
                revtmd_edit_2_ffmpeg = (('role','Scanner'), ('manufacturer','P&S Techniks'), ('modelName','Steadyframe'),('signal','Ethernet'), ('serialNumber','601-0101'))
                revtmd_edit_2_monitor = (('role','Host Computer Monitor'), ('manufacturer','LG'), ('modelName','???'),('signal','HDMI'), ('serialNumber','???'))
                revtmd_edit_2_speakers = (('role','Scanner'), ('manufacturer','P&S Techniks'), ('modelName','Steadyframe'),('signal','Ethernet'), ('serialNumber','601-0101'))
                revtmd_edit_2_headphones = (('role','Scanner'), ('manufacturer','P&S Techniks'), ('modelName','Steadyframe'),('signal','Ethernet'), ('serialNumber','601-0101'))
                revtmd_edit_2_blackmagic_capture_software = (('role','Capture Software'), ('manufacturer','Blackmagic'), ('modelName','Media Express'),('signal','SDI'), ('serialNumber','???'))
                
                
                process_history(OrderedDict(revtmd_edit_2_computer), 1)
                process_history(OrderedDict(revtmd_edit_2_computer_os), 2)
                process_history(OrderedDict(revtmd_edit_2_blackmagic_hardware), 3)
                process_history(OrderedDict(revtmd_edit_2_monitor), 4)
                process_history(OrderedDict(revtmd_edit_2_blackmagic_capture_software), 5)
        '''
        '''
                parser = ET.XMLParser(remove_blank_text=True)
                blaa = ET.fromstring(*args, parser=parser)
            
                eventDetailExtension.insert(0,blaa)  
        '''
        return doc
global vtr        
vtr = {'role':'playback', 'manufacturer':'Sony', 'signal':'composite', 'serialNumber':'abc123'}

vtr2 = {'role':'playback', 'manufacturer':'Panasonic', 'signal':'composite', 'serialNumber':'abc123'}
revtmd_basement_content_agent_pc = {'role':'Host Computer', 'manufacturer':'Hewlett-Packard Company', 'modelName':'Z800 Workstation', 'serialNumber':'CZC2082R1Z'}
revtmd_basement_content_agent_os = {'role':'Host Computer Operating System', 'manufacturer':'Microsoft', 'version':'Windows 7 Professional'}
revtd_basement_2k_scanner = (('role','Scanner'), ('manufacturer','P&S Techniks'), ('modelName','Steadyframe'),('signal','Ethernet'), ('serialNumber','601-0101'))
revtd_basement_2k_scanner = OrderedDict(revtd_basement_2k_scanner)
revtd_basement_2k_scanner_host_computer = {'role':'Scanner Host Computer', 'manufacturer':'???', 'modelName':'???', 'serialNumber':'???'}
revtd_basement_2k_scanner_host_computer_os = {'role':'Scanner Host Computer Operating System', 'manufacturer':'Debian', 'modelName':'???', 'serialNumber':'???'}
revtd_basement_2k_scanner_software = {'role':'Captures Image Sequence', 'manufacturer':'P&S Techniks', 'modelName':'???', 'serialNumber':'???'}


        
def process_history(coding_dict, process_history_placement):
    
    process = create_revtmd_unit(process_history_placement, revtmd_capture_history, 'codingprocessHistory')
    counter1 = 1
    for i in OrderedDict(coding_dict):
        print i, coding_dict[i]
        a = create_revtmd_unit(counter1, process, i)
        
        a.text = coding_dict[i]
        counter1 += 1
        
        
def main(source_file):
    global premis_namespace
    global premis
    global messageDigestAlgorithm
    global messageDigest
    global doc    
    namespace = '<premis:premis xmlns:premis="http://www.loc.gov/premis/v3" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:revtmd="http://nwtssite.nwts.nara/schema/" xsi:schemaLocation="http://www.loc.gov/premis/v3 https://www.loc.gov/standards/premis/premis.xsd http://nwtssite.nwts.nara/schema/  " version="3.0"></premis:premis>'
    premis = ET.fromstring(namespace)
    premis_namespace = "http://www.loc.gov/premis/v3"
    xsi_namespace = "http://www.w3.org/2001/XMLSchema-instance"
    doc = ET.ElementTree(premis)
    video_files = get_input(source_file)
    mediainfo_counter = 1
    #new_element = ET.Element('premis:object', namespaces={'ns': 'premis'})
    # Assuming that directory input means image sequence...
    if os.path.isdir(source_file):
        
        print video_files
        object_parent = create_unit(0, premis, 'object')
        object_identifier_parent = create_unit(1,object_parent, 'objectIdentifier')
        object_identifier_uuid = create_unit(0,object_parent, 'objectIdentifier')
        object_identifier_uuid_type = create_unit(1,object_identifier_uuid, 'objectIdentifierType')
        object_identifier_uuid_type.text = 'UUID'
        object_identifier_uuid_value = create_unit(2,object_identifier_uuid, 'objectIdentifierValue') 
        representation_uuid = str(uuid.uuid4())
        object_identifier_uuid_value.text = representation_uuid
        object_parent.insert(1,object_identifier_parent)
        ob_id_type = ET.Element("{%s}objectIdentifierType" % (premis_namespace))
        ob_id_type.text = 'IFI Irish Film Archive Object Entry Number'
        objectIdentifierValue = create_unit(1, object_identifier_parent, 'objectIdentifierValue')
        objectIdentifierValue.text = items['oe']
        object_identifier_parent.insert(0,ob_id_type)  
        object_identifier_filmographic = create_unit(3,object_parent, 'objectIdentifier')
        object_identifier_filmographic_reference_number = create_unit(1,object_identifier_filmographic, 'objectIdentifierType') 
        object_identifier_filmographic_reference_number.text = 'IFI Irish Film Archive Filmographic Reference Number'
        object_identifier_filmographic_reference_value = create_unit(2,object_identifier_filmographic, 'objectIdentifierValue') 
        object_identifier_filmographic_reference_value.text = items['filmographic']
        objectCategory = create_unit(1,object_parent, 'objectCategory')  
        objectCategory.text = 'representation'
        relationship = create_unit(4,object_parent, 'relationship')
        representationrelatedObjectIdentifierType = create_unit(2,relationship, 'relatedObjectIdentifierType')
        representationrelatedObjectIdentifierValue = create_unit(3,relationship,'relatedObjectIdentifierValue')
        relatedObjectSequence = create_unit(4,relationship,'relatedObjectSequence')
        relatedObjectSequence.text = '1'
        relationshipType = create_unit(0,relationship, 'relationshipType')
        relationshipType.text = 'structural'
        relationshipSubType = create_unit(1,relationship, 'relationshipSubType')
        relationshipSubType.text = 'has root'
        representationrelatedObjectIdentifierType.text = 'UUID'
        root_uuid = str(uuid.uuid4())
        representationrelatedObjectIdentifierValue.text = root_uuid
    rep_counter = 0
    for image in video_files:
        object_parent = create_unit(mediainfo_counter,premis, 'object')
        object_identifier_parent = create_unit(1,object_parent, 'objectIdentifier')
        ob_id_type = ET.Element("{%s}objectIdentifierType" % (premis_namespace))
        ob_id_type.text = 'IFI Irish Film Archive Object Entry Number'
        object_identifier_parent.insert(0,ob_id_type)
        object_identifier_filmographic = create_unit(3,object_parent, 'objectIdentifier')
        object_identifier_filmographic_reference_number = create_unit(1,object_identifier_filmographic, 'objectIdentifierType') 
        object_identifier_filmographic_reference_number.text = 'IFI Irish Film Archive Filmographic Reference Number'
        object_identifier_filmographic_reference_value = create_unit(2,object_identifier_filmographic, 'objectIdentifierValue') 
        object_identifier_filmographic_reference_value.text = items['filmographic']
        filename_identifier = create_unit(4, object_parent, 'objectIdentifier')
        filename_identifier_type = create_unit(1,filename_identifier, 'objectIdentifierType')
        filename_identifier_type.text = 'Filename'
        filename_identifier_value = create_unit(2,filename_identifier, 'objectIdentifierValue') 
        filename_identifier_value.text = image
        objectCategory = ET.Element("{%s}objectCategory" % (premis_namespace))
        object_parent.insert(5,objectCategory)
        objectCategory.text = 'file'
        objectCharacteristics = create_unit(10,object_parent, 'objectCharacteristics')
        objectIdentifierValue = create_unit(1, object_identifier_parent, 'objectIdentifierValue')
        objectIdentifierValue.text = items['oe']
        object_identifier_uuid = create_unit(2,object_parent, 'objectIdentifier')
        object_identifier_uuid_type = create_unit(1,object_identifier_uuid, 'objectIdentifierType')
        object_identifier_uuid_type.text = 'UUID'
        object_identifier_uuid_value = create_unit(2,object_identifier_uuid, 'objectIdentifierValue') 
        file_uuid = str(uuid.uuid4())
        if rep_counter == 0:
            object_identifier_uuid_value.text = root_uuid
        else:
            object_identifier_uuid_value.text = file_uuid
        rep_counter +=1
        format_ = ET.Element("{%s}format" % (premis_namespace))
        objectCharacteristics.insert(2,format_)
        
        mediainfo = subprocess.check_output(['mediainfo', '-f', '--language=raw', '--Output=XML', image])
        parser = ET.XMLParser(remove_blank_text=True)
        mediainfo_xml = ET.fromstring((mediainfo),parser=parser)
        fixity = create_unit(0,objectCharacteristics,'fixity')
        size = create_unit(1,objectCharacteristics,'size')
        size.text = str(os.path.getsize(image))
        formatDesignation = create_unit(0,format_,'formatDesignation')
        formatName = create_unit(1,formatDesignation,'formatName')

        messageDigestAlgorithm = create_unit(0,fixity, 'messageDigestAlgorithm')
        messageDigest = create_unit(1,fixity, 'messageDigest')

        
        objectCharacteristicsExtension = create_unit(4,objectCharacteristics,'objectCharacteristicsExtension')
        
        objectCharacteristicsExtension.insert(mediainfo_counter, mediainfo_xml)
        
        if os.path.isdir(source_file):
            relationship = create_unit(7,object_parent, 'relationship')
            relatedObjectIdentifierType = create_unit(2,relationship, 'relatedObjectIdentifierType')
            relatedObjectIdentifierType.text = 'IFI Irish Film Archive Object Entry Number'
            relatedObjectIdentifierValue = create_unit(3,relationship,'relatedObjectIdentifierValue')
            relatedObjectIdentifierValue.text = items['oe']
            relatedObjectSequence = create_unit(4,relationship,'relatedObjectSequence')
            relatedObjectSequence.text = str(mediainfo_counter)
            relationshipType = create_unit(0,relationship, 'relationshipType')
            relationshipType.text = 'structural'
            relationshipSubType = create_unit(1,relationship, 'relationshipSubType')
            relationshipSubType.text = 'is included in'
        #create_hash(image)
        hashlib_md5(image, manifest)
        mediainfo_counter += 1

    #make_event('Compression')
    
    if items["workflow"] == 'scanning':
        for lists in csv_list:
            for item in lists:
                if items['user'] == item:
                    user_info = lists
                    print user_info
                    
        capture_uuid = str(uuid.uuid4())
        scannerAgent  = make_agent('locally defined identifier','agent_001','P&S Technicks Steadyframe','601-0101', 'hardware', 'stuff in here', capture_uuid )
        operatorAgent = make_agent(user_info[0],user_info[1], user_info[2],'', user_info[3], '', capture_uuid )
        #make_event('Message Digest Calculation', 'Program="md5deep" Version="4.4"', scannerAgent,operatorAgent)
        make_event('capture', '', scannerAgent, operatorAgent, capture_uuid)

    '''
    >>> parser = etree.XMLParser(remove_blank_text=True)
    >>> tree = etree.parse(filename, parser)
    '''

    #print(ET.tostring(doc, pretty_print=True))
    
    
if __name__ == "__main__":
        make_premis(source_file)
        write_premis()
