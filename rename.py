import sys 
import subprocess
import os
from glob import glob
import lxml.etree as ET
import uuid
import time

premis_xml = sys.argv[1] + '/premis.xml'

def create_unit(index,parent, unitname):
    premis_namespace = "http://www.loc.gov/premis/v3"
    unitname = ET.Element("{%s}%s" % (premis_namespace, unitname))
    parent.insert(index,unitname)
    return unitname
    
def create_sibling(sibling, unitname):
    premis_namespace = "http://www.loc.gov/premis/v3"
    unitname = ET.Element("{%s}%s" % (premis_namespace, unitname))
    parent.insert(index,unitname)
    return unitname
def make_event(event_type, event_detail, related_id, *args):
        global linkingObjectIdentifierValue
        global event_Type
        global revtmd_capture_history
        premis_namespace = "http://www.loc.gov/premis/v3"
        print premis_xml
        parser = ET.XMLParser(remove_blank_text=True)

        premis = ET.parse(premis_xml, parser=parser)
        premisRoot =  premis.getroot()
        bla = premisRoot.xpath('//ns:event',namespaces={'ns': premis_namespace})
        event = ET.Element("{%s}%s" % (premis_namespace, 'event'))
        bla[-1].addnext(event)

        
        premis_namespace = "http://www.loc.gov/premis/v3"
        
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
        linkingObjectIdentifierValue.text = related_id
        linkingObjectRole = create_unit(2,linkingObjectIdentifier,'linkingObjectRole')
        linkingObjectIdentifierType.text = 'UUID'
        linkingObjectRole.text = 'source'  
        print(ET.tostring(premis, pretty_print=True))
        
def get_input():
    
    input = sys.argv[1]
    return input
def ask_user():
    global input
    accession_number = raw_input('--> Enter Accession Number, eg: DAA10001')
    print accession_number.upper() + '_' + sys.argv[1]
    return accession_number.upper() + '_'
    
def check_manifest():
    global manifest
    manifest = os.path.dirname(input) + '/' + os.path.basename(input) + '_manifest.md5'
    if os.path.isfile(manifest):
        print 'EXISTO'
        return True
    else:
        return False
  
def rename_files():
    os.chdir(input)  

    tiffs = glob('*.tiff') + glob('*.tif')

    for i in tiffs:
        filename = i
        # create new variable which trims the first 18 characters.
        filename_fix = accession_number 
        
        new_filename = filename_fix + filename
        print new_filename
        os.rename(filename, new_filename)

def main():
    global input
    global accession_number
    make_event('rename', 'changed stuff', 'iuruio3')
    accession_number = ask_user()
    input = get_input()
    rename_files()
    manifest_check = check_manifest()
    if manifest_check == True:
        print 'YRAHAHAH'
    
    
if __name__ == "__main__":
    
    main()  # run the main function

