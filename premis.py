import lxml.etree as ET
import lxml.builder as builder
import uuid
import time
import sys
import subprocess
import os
from glob import glob
import hashlib
from collections import OrderedDict
import csv
from ififuncs import append_csv
from ififuncs import create_csv


def hashlib_md5(source_file,filename):
   read_size = 0
   last_percent_done = 0
   m = hashlib.md5()
   total_size = os.path.getsize(filename)
   with open(str(filename), 'rb') as f:
       while True:
           buf = f.read(2**20)
           if not buf:
               break
           read_size += len(buf)
           m.update(buf)
           percent_done = 100 * read_size / total_size
           if percent_done > last_percent_done:
               sys.stdout.write('[%d%%]\r' % percent_done)
               sys.stdout.flush()


               last_percent_done = percent_done
   md5_output = m.hexdigest()
   return md5_output

def add_value(value, element):
    element.text = value


def write_premis(doc, premisxml):
    with open(premisxml,'w') as outFile:
        doc.write(outFile,pretty_print=True)


def create_unit(index,parent, unitname):
    premis_namespace = "http://www.loc.gov/premis/v3"
    unitname = ET.Element("{%s}%s" % (premis_namespace, unitname))
    parent.insert(index,unitname)
    return unitname


def get_input(filename):
    # Input, either file or firectory, that we want to process.
    input = filename
    # Store the directory containing the input file/directory.
    wd = os.path.dirname(os.path.abspath(input))
    # Change current working directory to the value stored as "wd"
    os.chdir(wd)
    # Store the actual file/directory name without the full path.
    file_without_path = os.path.basename(input)
    # Check if input is a file.
    # AFAIK, os.path.isfile only works if full path isn't present.
    if os.path.isfile(input):
        video_files = []                       # Create empty list
        video_files.append(file_without_path)  # Add filename to list
    # Check if input is a directory.
    elif os.path.isdir(file_without_path):
        os.chdir(file_without_path)
        video_files = (
            glob('*.tif') +
            glob('*.tiff') +
            glob('*.dpx') +
            glob('*.wav')

        )
    # Prints some stuff if input isn't a file or directory.
    else:
        print "Your input isn't a file or a directory."
    return video_files


def make_premis(source_file, items, premis, premis_namespace, premisxml,representation_uuid,sequence):
    # the sequence argument determines if a sequence counter is launched
    xml_info = create_object(source_file, items, premis, premis_namespace, premisxml, representation_uuid, sequence)
    return xml_info


def make_agent(premis,linkingEventIdentifier_values, agentId ):
    csv_file = os.path.expanduser("~/ifigit/ifiscripts/premis_agents.csv")
    if os.path.isfile(csv_file):
        read_object = open(csv_file)
        reader = csv.reader(read_object)
        csv_list = list(reader)
        read_object.close()
    for lists in csv_list:
        for item in lists:
            if item == agentId:
                agent_info = lists
    agentIdType_value,agentIdValue_value,agentName_value,agentType_value, agentVersion_value,agentNote_value,agentRole = agent_info

    if agentVersion_value == 'ffmpeg_autoextract':
        agentVersion_value = subprocess.check_output(['ffmpeg','-version','-v','0']).splitlines()[0]
    premis_namespace            = "http://www.loc.gov/premis/v3"
    agent                       = ET.SubElement(premis, "{%s}agent" % (premis_namespace))
    premis.insert(-1, agent)
    agentIdentifier             = create_unit(1,agent,'agentIdentifier')
    agentIdType                 = create_unit(2,agentIdentifier,'agentIdentifierType')
    agentIdValue                = create_unit(2,agentIdentifier,'agentIdentifierValue')
    agentName                   = create_unit(2,agent,'agentName')
    agentName.text              = agentName_value
    if not agentNote_value == '':
        agentNote                   = create_unit(5,agent,'agentNote')
        agentNote.text              = agentNote_value
    agentType                   = create_unit(3,agent,'agentType')
    if not agentVersion_value == '':
        agentVersion                = create_unit(4,agent,'agentVersion')
        agentVersion.text           = agentVersion_value
    agentIdType.text            = agentIdType_value
    agentIdValue.text           = agentIdValue_value
    agentType.text              = agentType_value
    for event_link in linkingEventIdentifier_values:
        linkingEventIdentifier      = create_unit(6,agent,'linkingEventIdentifier')
        linkingEventIdentifierType = create_unit(1,linkingEventIdentifier, 'linkingEventIdentifierType')
        linkingEventIdentifierValue = create_unit(1,linkingEventIdentifier, 'linkingEventIdentifierValue')
        linkingEventIdentifierValue.text = event_link
        linkingEventIdentifierType.text = 'UUID'
    agent_info                  = [agentIdType_value,agentIdValue_value]
    return agent_info

def make_event(premis,event_type, event_detail, agentlist, eventID, eventLinkingObjectIdentifier, eventLinkingObjectRole, event_time):
        premis_namespace                    = "http://www.loc.gov/premis/v3"
        event = ET.SubElement(premis, "{%s}event" % (premis_namespace))
        premis.insert(-1,event)
        event_Identifier                    = create_unit(1,event,'eventIdentifier')
        event_id_type                       = ET.Element("{%s}eventIdentifierType" % (premis_namespace))
        event_Identifier.insert(0,event_id_type)
        event_id_value                      = ET.Element("{%s}eventIdentifierValue" % (premis_namespace))
        event_Identifier.insert(0,event_id_value)
        event_Type                          = ET.Element("{%s}eventType" % (premis_namespace))
        event.insert(2,event_Type)
        event_DateTime                      = ET.Element("{%s}eventDateTime" % (premis_namespace))
        event.insert(3,event_DateTime)
        if event_time == 'now':
            event_DateTime.text             = time.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            event_DateTime.text             = event_time
        event_Type.text                     = event_type
        event_id_value.text                 = eventID
        event_id_type.text                  = 'UUID'
        eventDetailInformation              = create_unit(4,event,'eventDetailInformation')
        eventDetail                         = create_unit(0,eventDetailInformation,'eventDetail')
        eventDetail.text                    = event_detail
        for i in eventLinkingObjectIdentifier:
            linkingObjectIdentifier             = create_unit(5,event,'linkingObjectIdentifier')
            linkingObjectIdentifierType         = create_unit(0,linkingObjectIdentifier,'linkingObjectIdentifierType')
            linkingObjectIdentifierValue        = create_unit(1,linkingObjectIdentifier,'linkingObjectIdentifierValue')
            linkingObjectIdentifierValue.text   = i
            linkingObjectRole                   = create_unit(2,linkingObjectIdentifier,'linkingObjectRole')
            linkingObjectIdentifierType.text    = 'UUID'
            linkingObjectRole.text              = eventLinkingObjectRole
        for i in agentlist:
            linkingAgentIdentifier              = create_unit(-1,event,'linkingAgentIdentifier')
            linkingAgentIdentifierType          = create_unit(0,linkingAgentIdentifier,'linkingAgentIdentifierType')
            linkingAgentIdentifierValue         = create_unit(1,linkingAgentIdentifier,'linkingAgentIdentifierValue')
            linkingAgentIdentifierRole          = create_unit(2,linkingAgentIdentifier,'linkingAgentRole')
            linkingAgentIdentifierRole.text     = 'implementer'
            linkingAgentIdentifierType.text     = i[0]
            linkingAgentIdentifierValue.text    = i[1]


def main():
    print 'This is not a standalone script. It is a library of functions that other scripts can use'
    sys.exit()

def setup_xml(source_file):
    premisxml           = os.path.dirname(os.path.dirname(source_file)) + '/metadata' '/' + os.path.basename(os.path.dirname(os.path.dirname(source_file))) + '_premis.xml'
    namespace           = '<premis:premis xmlns:premis="http://www.loc.gov/premis/v3" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/premis/v3 https://www.loc.gov/standards/premis/premis.xsd" version="3.0"></premis:premis>'
    premis_namespace    = "http://www.loc.gov/premis/v3"
    xsi_namespace       = "http://www.w3.org/2001/XMLSchema-instance"
    print premisxml
    if os.path.isfile(premisxml):
        print 'looks like premis already exists?'
        parser      = ET.XMLParser(remove_blank_text=True)
        doc         = ET.parse(premisxml,parser=parser)
        premis      = doc.getroot()
    else:
        premis              = ET.fromstring(namespace)
        doc                 = ET.ElementTree(premis)
    return premisxml, premis_namespace, doc, premis


def representation_uuid_csv(filmographic, source_accession, uuid):
    uuid_csv = os.path.expanduser('~/Desktop/uuid.csv')
    if not os.path.isfile(uuid_csv):
        create_csv(uuid_csv, ('reference number','source accession number' 'uuid'))
    append_csv(uuid_csv, (filmographic, source_accession, uuid) )

def create_intellectual_entity(premisxml, premis_namespace, doc, premis, items, intellectual_entity_uuid):
    object_parent                                           = create_unit(0, premis, 'object')
    object_identifier_uuid                                  = create_unit(2,object_parent, 'objectIdentifier')
    object_identifier_uuid_type                             = create_unit(1,object_identifier_uuid, 'objectIdentifierType')
    object_identifier_uuid_type.text                        = 'UUID'
    object_identifier_uuid_value                            = create_unit(2,object_identifier_uuid, 'objectIdentifierValue')
    object_identifier_uuid_value.text                       = intellectual_entity_uuid
    # add uuids to csv so that other workflows can use them as linking identifiers.
    representation_uuid_csv(items['filmographic'],items['sourceAccession'], intellectual_entity_uuid)
    object_identifier_filmographic                          = create_unit(3,object_parent, 'objectIdentifier')
    object_identifier_filmographic_reference_number         = create_unit(1,object_identifier_filmographic, 'objectIdentifierType')
    object_identifier_filmographic_reference_number.text    = 'Irish Film Archive Filmographic Database'
    object_identifier_filmographic_reference_value          = create_unit(2,object_identifier_filmographic, 'objectIdentifierValue')
    object_identifier_filmographic_reference_value.text     = items['filmographic']
    objectCategory                                          = create_unit(4,object_parent, 'objectCategory')
    objectCategory.text                                     = 'intellectual entity'
def create_representation(premisxml, premis_namespace, doc, premis, items, linkinguuids, representation_uuid, sequence, intellectual_entity_uuid):
        object_parent                                           = create_unit(1, premis, 'object')
        object_identifier_parent                                = create_unit(1,object_parent, 'objectIdentifier')
        object_identifier_uuid                                  = create_unit(0,object_parent, 'objectIdentifier')
        object_identifier_uuid_type                             = create_unit(1,object_identifier_uuid, 'objectIdentifierType')
        object_identifier_uuid_type.text                        = 'UUID'
        object_identifier_uuid_value                            = create_unit(2,object_identifier_uuid, 'objectIdentifierValue')
        object_identifier_uuid_value.text                       = representation_uuid
        # add uuids to csv so that other workflows can use them as linking identifiers.
        representation_uuid_csv(items['filmographic'],items['sourceAccession'], representation_uuid)
        object_parent.insert(1,object_identifier_parent)
        ob_id_type                                              = ET.Element("{%s}objectIdentifierType" % (premis_namespace))
        ob_id_type.text                                         = 'Irish Film Archive Object Entry Register'
        objectIdentifierValue                                   = create_unit(1, object_identifier_parent, 'objectIdentifierValue')
        objectIdentifierValue.text                              = items['oe']
        object_identifier_parent.insert(0,ob_id_type)
        objectCategory                                          = create_unit(2,object_parent, 'objectCategory')
        objectCategory.text                                     = 'representation'
        # These hardcoded relationships do not really belong here. They should be stipulated by another microservice
        if sequence == 'sequence':
            representation_relationship(object_parent, premisxml, items, 'structural', 'has root',linkinguuids[1][0], 'root_sequence', 'UUID')
            for i in linkinguuids[1]:
                representation_relationship(object_parent, premisxml, items, 'structural', 'includes',i, 'includes', 'UUID')

        representation_relationship(object_parent, premisxml, items, 'structural', 'includes',linkinguuids[0], 'n/a', 'UUID')
        representation_relationship(object_parent, premisxml, items, 'derivation', 'has source',linkinguuids[2], 'n/a', 'Irish Film Archive Film Accession Register 2010 -')
        representation_relationship(object_parent, premisxml, items, 'structural', 'represents',intellectual_entity_uuid, 'n/a', 'UUID')

def representation_relationship(object_parent, premisxml, items, relationshiptype, relationshipsubtype, linking_identifier, root_sequence, linkingtype):
        relationship                                            = create_unit(-1,object_parent, 'relationship')
        representationrelatedObjectIdentifier                   = create_unit(2,relationship, 'relatedObjectIdentifier')
        representationrelatedObjectIdentifierType               = create_unit(2,representationrelatedObjectIdentifier, 'relatedObjectIdentifierType')
        representationrelatedObjectIdentifierValue              = create_unit(3,representationrelatedObjectIdentifier,'relatedObjectIdentifierValue')
        if root_sequence == 'root_sequence':
            relatedObjectSequence                                   = create_unit(4,relationship,'relatedObjectSequence')
            relatedObjectSequence.text                              = '1'
        relationshipType                                        = create_unit(0,relationship, 'relationshipType')
        relationshipType.text                                   = relationshiptype
        relationshipSubType                                     = create_unit(1,relationship, 'relationshipSubType')
        relationshipSubType.text                                = relationshipsubtype
        representationrelatedObjectIdentifierType.text          = linkingtype
        representationrelatedObjectIdentifierValue.text          = linking_identifier

def create_object(source_file, items, premis, premis_namespace, premisxml, representation_uuid, sequence):
    video_files         = get_input(source_file)
    mediainfo_counter   = 1

    image_uuids = []
    rep_counter = 0
    print 'Generating PREMIS metadata about each file object - this may take some time if on a network and/or working with an image sequence'
    for image in video_files:
        object_parent                                           = create_unit(-1,premis, 'object')
        object_identifier_uuid                                  = create_unit(1,object_parent, 'objectIdentifier')
        object_identifier_uuid_type                             = create_unit(1,object_identifier_uuid, 'objectIdentifierType')
        object_identifier_uuid_type.text                        = 'UUID'
        object_identifier_uuid_value                            = create_unit(2,object_identifier_uuid, 'objectIdentifierValue')
        file_uuid                                               = str(uuid.uuid4())
        image_uuids.append(file_uuid)
        object_identifier_uuid_value.text                       = file_uuid
        objectCategory                                          = ET.Element("{%s}objectCategory" % (premis_namespace))
        object_parent.insert(5,objectCategory)
        objectCategory.text                                     = 'file'

        if rep_counter == 0:
            root_uuid = file_uuid

        rep_counter +=1
        format_ = ET.Element("{%s}format" % (premis_namespace))
        objectCharacteristics                                   = create_unit(10,object_parent, 'objectCharacteristics')
        objectCharacteristics.insert(2,format_)

        mediainfo                       = subprocess.check_output(['mediainfo', '-f', '--language=raw', '--Output=XML', image])
        parser                          = ET.XMLParser(remove_blank_text=True)
        mediainfo_xml                   = ET.fromstring((mediainfo),parser=parser)
        fixity                          = create_unit(0,objectCharacteristics,'fixity')
        size                            = create_unit(1,objectCharacteristics,'size')
        size.text                       = str(os.path.getsize(image))
        formatDesignation               = create_unit(0,format_,'formatDesignation')
        formatName                      = create_unit(1,formatDesignation,'formatName')
        formatName_mediainfo            = subprocess.check_output(['mediainfo', '--Inform=General;%InternetMediaType%', image]).rstrip()
        if formatName_mediainfo == '':
            formatName_mediainfo        = subprocess.check_output(['mediainfo', '--Inform=General;%Format_Commercial%', image]).rstrip()
        formatName.text                 = formatName_mediainfo
        messageDigestAlgorithm          = create_unit(0,fixity, 'messageDigestAlgorithm')
        messageDigest                   = create_unit(1,fixity, 'messageDigest')
        messageDigestOriginator         = create_unit(2,fixity, 'messageDigestOriginator')
        messageDigestOriginator.text    = 'internal'
        objectCharacteristicsExtension  = create_unit(4,objectCharacteristics,'objectCharacteristicsExtension')
        objectCharacteristicsExtension.insert(mediainfo_counter, mediainfo_xml)
        relationship                        = create_unit(7,object_parent, 'relationship')
        relatedObjectIdentifier             = create_unit(2,relationship, 'relatedObjectIdentifier')
        relatedObjectIdentifierType         = create_unit(2,relatedObjectIdentifier , 'relatedObjectIdentifierType')
        relatedObjectIdentifierType.text    = 'UUID'
        relatedObjectIdentifierValue        = create_unit(3,relatedObjectIdentifier ,'relatedObjectIdentifierValue')
        relatedObjectIdentifierValue.text   = representation_uuid
        if sequence == 'sequence':
            relatedObjectSequence               = create_unit(4,relationship,'relatedObjectSequence')
            relatedObjectSequence.text          = str(mediainfo_counter)
        relationshipType                    = create_unit(0,relationship, 'relationshipType')
        relationshipType.text               = 'structural'
        relationshipSubType                 = create_unit(1,relationship, 'relationshipSubType')
        relationshipSubType.text            = 'is included in'

        md5_output                              = hashlib_md5(source_file, image)
        messageDigest.text                      = md5_output
        messageDigestAlgorithm.text             = 'md5'
        mediainfo_counter                       += 1
    # When the image info has been grabbed, add info about the representation to the wav file. This may be problematic if makedpx is run first..

    doc                 = ET.ElementTree(premis)
    xml_info                                    = [doc, premisxml, root_uuid,sequence, image_uuids]

    return xml_info

if __name__ == "__main__":
        main()

