'''
Work in progress. I think this will just be a bunch of functions that other scripts can call on in order to use as a growing log file.
'''
#http://stackoverflow.com/questions/7703018/how-to-write-namespaced-element-attributes-with-lxml
import lxml.etree as ET
import lxml.builder as builder
import uuid
import time
import sys
import subprocess

def create_unit(parent, unitname):
    unitname = ET.Element("{%s}%s" % (DCNS, unitname))
    parent.insert(0,unitname)
    return unitname
    
E = builder.ElementMaker(namespace='http://www.loc.gov/premis/v3',
                         nsmap={None: 'http://www.loc.gov/premis/v3',
                         'premis': 'http://www.loc.gov/premis/v3',
                         'xlink': 'http://www.w3.org/1999/xlink',
                         'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                         'schemaLocation':'http://www.loc.gov/premis/v3'
                          })
premis = E.premis(version="3.0")
DCNS = "http://www.loc.gov/premis/v3"

doc = ET.ElementTree(premis)
#new_element = ET.Element('premis:object', namespaces={'ns': 'premis'})
object_parent = ET.SubElement(premis, "{%s}object" % (DCNS))
object_identifier_parent = ET.SubElement(premis, "{%s}objectIdentifier" % (DCNS))


#t = ET.Element("{%s}objectIdentifierType" % (DCNS))
#print new_element

premis.insert(0,object_parent)
object_parent.insert(1,object_identifier_parent)
ob_id_type = ET.Element("{%s}objectIdentifierType" % (DCNS))
ob_id_type.text = 'oe'
object_identifier_parent.insert(0,ob_id_type)
objectCharacteristics = ET.Element("{%s}objectCharacteristics" % (DCNS))
object_parent.insert(2,objectCharacteristics)
object_identifier_parent.insert(1,ET.Element("{%s}objectIdentifierValue" % (DCNS)))
format_ = ET.Element("{%s}format" % (DCNS))
objectCharacteristics.insert(0,format_)



fixity = create_unit(objectCharacteristics,'fixity')
messageDigestAlgorithm = create_unit(fixity, 'messageDigestAlgorithm')
messageDigest = create_unit(fixity, 'messageDigest')

objectCategory = ET.Element("{%s}objectCategory" % (DCNS))

object_parent.insert(1,objectCategory)
objectCategory.text = 'file'

def make_event(event_type):
    global event_Type
    
    event = ET.SubElement(premis, "{%s}event" % (DCNS))
    premis.insert(1,event)
    #event_Identifier = ET.Element("{%s}eventIdentifier" % (DCNS))
    #event.insert(1,event_Identifier)
    event_Identifier = create_unit(event,'event_Identifier')
    event_id_type = ET.Element("{%s}eventIdentifierType" % (DCNS))
    event_Identifier.insert(0,event_id_type)
    event_id_value = ET.Element("{%s}eventIdentifierValue" % (DCNS))
    
    event_Identifier.insert(0,event_id_value)
    event_Type = ET.Element("{%s}eventType" % (DCNS))
    event.insert(1,event_Type)
    event_DateTime = ET.Element("{%s}eventDateTime" % (DCNS))
    event.insert(1,event_DateTime)
    event_DateTime.text = time.strftime("%Y-%m-%dT%H:%M:%S")
    event_Type.text = event_type
    event_id_value.text = str(uuid.uuid4())
    event_id_type.text = 'UUID'

def create_hash(filename):
    md5 = subprocess.check_output(['md5deep', filename])[:32]
    messageDigestAlgorithm.text = 'md5'
    messageDigest.text = md5
    return md5
    
    
    
make_event('Compression')

make_event('Message Digest Calculation')
make_event('Capture')
create_hash(sys.argv[1])
outFile = open('premis.xml','w')
doc.write(outFile,pretty_print=True)

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
