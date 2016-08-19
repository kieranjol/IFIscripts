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
    
    
def manifest_file_count(manifest2check):
    if os.path.isfile(manifest2check):
        print 'A manifest already exists'
        with open(manifest2check, "r") as fo:
            manifest_lines = [line.split(',') for line in fo.readlines()]
            count_in_manifest =  len(manifest_lines)
    return count_in_manifest  

    
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
 
def check_manifest():
    global manifest
    new_list = []
    manifest = os.path.dirname(input) + '/' + os.path.basename(input) + '_manifest.md5'
    if os.path.isfile(manifest):
        print 'EXISTO'
        with open(manifest, 'r') as fo:
            a = fo.readlines()
            print a
            for i in a:
                 new_list.append(i.replace('tiff_scans/','tiff_scans/%s' % accession_number))
        for x in new_list:  
            print x 
            with open(manifest + '_newwww.txt', 'a') as fo:      
                if '.tif' in x:
                    fo.write(x)
        '''
        with open(manifest, "r") as fo:
            manifest_lines = [line.split(',') for line in fo.readlines()]
            for i in manifest_lines:
                
                
                for a in i:
                    b =  a.split('/')
                    b[-1] =  accession_number + b[-1]
                    for i in b:
                        
                        # print " ".join(i), '12312'
                        
                        new_list.append(i + '/')
            #print new_list                   
               
                    
                    
                    
            count_in_manifest =  len(manifest_lines)
        return count_in_manifest  
        '''
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

def make_manifest(relative_manifest_path, manifest_textfile):
    print relative_manifest_path
    os.chdir(relative_manifest_path)
    manifest_generator = subprocess.check_output(['md5deep', '-ler', '.'])
    manifest_list = manifest_generator.splitlines()
    
    for root, directories, filenames in os.walk(sys.argv[1]):   
        for files in filenames:
            print files  
            print os.path.realpath(root)          
    
    '''
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list,  key=lambda x:(x[34:])) 
    with open(manifest_textfile,"wb") as fo:
        for i in manifest_list:
            fo.write(i + '\n')
    '''
def main():
    
    global input
    
    input = get_input()
    global manifest
    global accession_number
    normpath = os.path.normpath(os.path.dirname(input))
    relative_path = normpath.split(os.sep)[-1]
    print relative_path
    accession_number = ask_user()
    #rename_files()
    manifest =  '%s_newmanifest.md5' % (relative_path)
    
    make_manifest(os.path.dirname(input),manifest) 
    manifest_check = check_manifest()
    #make_event('rename', 'changed stuff', 'iuruio3')
    
    
    
    
    
    
if __name__ == "__main__":
    
    main()  # run the main function

