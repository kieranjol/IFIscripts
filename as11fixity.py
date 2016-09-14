'''
WORK IN PROGRESS WORKSHOP SCRIPT!!!
'''

import sys
import subprocess
import os
from glob import glob
import csv
from lxml import etree
import hashlib
#1

starting_dir = sys.argv[1]
#2

csv_report_filename = os.path.basename(starting_dir) + "_report"
csv_report = os.path.expanduser("~/Desktop/%s.csv") % csv_report_filename 
print csv_report
print os.path.isfile(csv_report)
#5

checkfile = os.path.isfile(csv_report)
#3

def create_csv(csv_file, *args):
    f = open(csv_file, 'wb')
    try:
        writer = csv.writer(f)
        writer.writerow(*args)
    finally:
        f.close()
#6   

create_csv(csv_report, ('Filename' , 'Title' , 'Episode_Number' , 'Md5_From_Xml' , 'Md5_from_Mxf' , 'Checksum_Result'))
#6

if checkfile == True:
    print "CSV file already exists."
    
    
if checkfile == False:
    print "No CSV file exists."
#3    

for dirpath, dirnames, filenames in os.walk(starting_dir):
    for filename in [f for f in filenames if f.endswith(".mxf")]:
        full_path = os.path.join(dirpath, filename)
        print dirpath +  ' ---DIR PATH'
        print filename + ' ---THIS IS FILEAME'
        print full_path + ' ---THIS IS THE FULL_PATH'
        #7
        
        file_no_path = os.path.basename(full_path)
        print file_no_path + ' ---THIS IS FILE_NO_PATH'
        #8.1
        
        file_no_extension = os.path.splitext(os.path.basename(file_no_path))[0]
        print file_no_extension + ' ---THIS IS FILE_NO_EXTENSION'
        #8.2
        
        xml_file = file_no_extension + '.xml'
        print xml_file + '  ---This is xml file'
        full_xml_path = os.path.join(dirpath,xml_file)
        print full_xml_path + ' ---This id the full xml path'
        checkfile = os.path.isfile(os.path.join(dirpath,xml_file))
        if checkfile == True:
            print 'XML file already exists.'
        if checkfile == False:
            print 'No XML file exists.'
        #8.3
        
        dpp_xml_parse = etree.parse(full_xml_path)
        print dpp_xml_parse, 'hahaha'
        dpp_xml_namespace = dpp_xml_parse.xpath('namespace-uri(.)')
        print dpp_xml_namespace, 'lol'
        checksum = dpp_xml_parse.findtext('//ns:MediaChecksumValue', namespaces={'ns':dpp_xml_namespace })
        print checksum
        #12 
     
        
        
def md5(full_path):
    hash_md5 = hashlib.md5()
    with open(full_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
print md5(full_path)
#13

if md5(full_path)==checksum:
    print 'Checksum matches!'
else:
    print 'CHECKSUM DONT MATCH'
 #14



"""
As-11 Fixity

1. Import all relevant modules x
2. Define path to starting folder x
3. Check if CSV report already exists x
4. Allow option to overwrite ?
5. Define name for CSv file x
6. Create CSV file with headings x
7. Search through subfolders to verify mxf file exists x
8.1 harvest filname eg GAA.MXF, remove extension eg MXF x
8.2 store new filname eg GAA x
8.3 make new filename variable x
8.4 check if GAA with .XML extension exists
9. Check if same filename
10. Check if folder is empty, note in CSV report 
11. If only MXF, note in CSV report. MXF FILENAME + "No sidecar"
12. Extract MD5 from xml file and store as variable x
13. Generate MD5 checksum on MXF file x
14. Compare the 2 MD5s x
15. Write to CSV report
15.1 xml parse title
15.2 xml parse episode title/number
15.3 xml parse programme title
15.4 append list with all findings



8.1 harvest filname eg GAA.MXF, - file_no_path = 
8.2 remove extension eg MXF store new filname eg GAA filename_no_extention
8.3 check if GAA with .XML extension exists  - xml_filename
"""



