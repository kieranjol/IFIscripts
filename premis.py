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

source_file = sys.argv[1]
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
            glob('*.dpx')
        )

    # Prints some stuff if input isn't a file or directory.
    else: 
        print "Your input isn't a file or a directory."   
    return video_files
def make_premis(source_file):
    main(source_file)    

def make_event(event_type, event_detail, *args):
        global event_Type
        
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
        event_id_value.text = str(uuid.uuid4())
        event_id_type.text = 'UUID'    
        eventDetailInformation = create_unit(4,event,'event_DetailInformation')
        eventDetail = create_unit(0,eventDetailInformation,'event_Detail')
        eventDetail.text = event_detail
        linkingObjectIdentifier = create_unit(5,event,'linkingObjectIdentifier')
        linkingObjectIdentifierType = create_unit(0,linkingObjectIdentifier,'linkingObjectIdentifierType')
        linkingObjectIdentifierValue = create_unit(1,linkingObjectIdentifier,'linkingObjectIdentifierValue')
        linkingObjectRole = create_unit(2,linkingObjectIdentifier,'linkingObjectRole')
        linkingObjectIdentifierType.text = 'IFI Irish Film Archive Object Entry Number'
        linkingObjectIdentifierValue.text = 'OE1234'
        linkingObjectRole.text = 'source'  
        if event_type == 'capture':
            print 123123123123123
            eventDetailExtension = create_unit(1, eventDetailInformation, 'event_DetailExtension')
            eventDetailExtension.insert(0,*args)  
            
        

def main(source_file):
    global premis_namespace
    global premis
    global messageDigestAlgorithm
    global messageDigest
    global doc    
    namespace = '<premis:premis xmlns:premis="http://www.loc.gov/premis/v3" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/premis/v3 https://www.loc.gov/standards/premis/premis.xsd" version="3.0"></premis:premis>'
    premis = ET.fromstring(namespace)
    premis_namespace = "http://www.loc.gov/premis/v3"
    xsi_namespace = "http://www.w3.org/2001/XMLSchema-instance"
    doc = ET.ElementTree(premis)
    #new_element = ET.Element('premis:object', namespaces={'ns': 'premis'})

    video_files = get_input(source_file)
    print video_files
    object_parent = create_unit(0, premis, 'object')
    object_identifier_parent = create_unit(0,object_parent, 'objectIdentifier')

    object_parent.insert(1,object_identifier_parent)
    ob_id_type = ET.Element("{%s}objectIdentifierType" % (premis_namespace))
    ob_id_type.text = 'IFI Irish Film Archive Object Entry Number'
    object_identifier_parent.insert(0,ob_id_type)  
    objectCategory = create_unit(1,object_parent, 'objectCategory')  
    objectCategory.text = 'representation'
    relationship = create_unit(2,object_parent, 'relationship')
    relatedObjectIdentifierType = create_unit(2,relationship, 'relatedObjectIdentifierType')
    relatedObjectIdentifierType.text = 'Filename'
    relatedObjectIdentifierValue = create_unit(3,relationship,'relatedObjectIdentifierValue')
    relatedObjectIdentifierValue.text = video_files[0]
    relatedObjectSequence = create_unit(4,relationship,'relatedObjectSequence')
    relatedObjectSequence.text = '1'
    relationshipType = create_unit(0,relationship, 'relationshipType')
    relationshipType.text = 'structural'
    relationshipSubType = create_unit(1,relationship, 'relationshipSubType')
    relationshipSubType.text = 'has root'

    print video_files 
    mediainfo_counter = 1
    for image in video_files:

        
        print image
        object_parent = create_unit(mediainfo_counter,premis, 'object')
        object_identifier_parent = create_unit(0,object_parent, 'objectIdentifier')
        ob_id_type = ET.Element("{%s}objectIdentifierType" % (premis_namespace))
        ob_id_type.text = 'IFI Irish Film Archive Object Entry Number'
        object_identifier_parent.insert(0,ob_id_type)
        objectCharacteristics = ET.Element("{%s}objectCharacteristics" % (premis_namespace))
        object_parent.insert(2,objectCharacteristics)
        objectIdentifierValue = create_unit(1, object_identifier_parent, 'objectIdentifierValue')
        format_ = ET.Element("{%s}format" % (premis_namespace))
        objectCharacteristics.insert(2,format_)
        filename_identifier = create_unit(1, object_parent, 'objectIdentifier')
        filename_identifier_type = create_unit(1,filename_identifier, 'objectIdentifierType')
        filename_identifier_type.text = 'Filename'
        filename_identifier_value = create_unit(2,filename_identifier, 'objectIdentifierValue') 
        filename_identifier_value.text = image
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

        objectCategory = ET.Element("{%s}objectCategory" % (premis_namespace))
        objectCharacteristicsExtension = create_unit(3,objectCharacteristics,'objectCharacteristicsExtension')
        
        objectCharacteristicsExtension.insert(mediainfo_counter, mediainfo_xml)
        object_parent.insert(2,objectCategory)
        objectCategory.text = 'file'
        relationship = create_unit(2,object_parent, 'relationship')
        relatedObjectIdentifierType = create_unit(2,relationship, 'relatedObjectIdentifierType')
        relatedObjectIdentifierType.text = 'IFI Irish Film Archive Object Entry Number'
        relatedObjectIdentifierValue = create_unit(3,relationship,'relatedObjectIdentifierValue')
        relatedObjectIdentifierValue.text = 'OE1234'
        relatedObjectSequence = create_unit(4,relationship,'relatedObjectSequence')
        relatedObjectSequence.text = str(mediainfo_counter)
        relationshipType = create_unit(0,relationship, 'relationshipType')
        relationshipType.text = 'structural'
        relationshipSubType = create_unit(1,relationship, 'relationshipSubType')
        relationshipSubType.text = 'is part of'
        create_hash(image)
        mediainfo_counter += 1

    
        
        

        
        
        
    #make_event('Compression')

    make_event('Message Digest Calculation', 'Program="md5deep" Version="4.4"')
    #make_event('Capture')

    
    '''
    >>> parser = etree.XMLParser(remove_blank_text=True)
    >>> tree = etree.parse(filename, parser)
    '''

    #print(ET.tostring(doc, pretty_print=True))
    
    
if __name__ == "__main__":
        make_premis(source_file)
        write_premis()
'''
from lxml import etree


PREMIS_NS   =  "http://www.loc.gov/premis/v3"
NS_MAP = {'premis': PREMIS_NS}


namespace = '<premis:premis xmlns:premis="http://www.loc.gov/premis/v3" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/premis/v3 https://www.loc.gov/standards/premis/premis.xsd" version="3.0"></premis:premis>'
page = etree.fromstring(namespace)

#page = etree.Element(ns)
doc = etree.ElementTree(page)

a = page.append(etree.Element("fixityEvent"))
new_element = etree.Element('premis:object', type="premis:file", nsmap='premis')
page.insert(0,new_element)

premiso = etree.Element('premis')

new_element.insert(0, premiso) 
premiso.text = 'TESTSTSTSTSTST'
outFile = open('premis.xml','w')
doc.write(outFile)


'''
'''
import lxml.etree as ET
import lxml.builder as builder
E = builder.ElementMaker(namespace='http://www.loc.gov/premis/v3',
                         nsmap={None: 'http://www.loc.gov/premis/v3',
                         'premis': 'http://www.loc.gov/premis/v3',
                         'xlink': 'http://www.w3.org/1999/xlink',
                         'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                         
                          })
premis = E.premis(version="3.0")
print(ET.tostring(premis, pretty_print=True))




'''
