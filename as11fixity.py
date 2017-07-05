'''
WORK IN PROGRESS WORKSHOP SCRIPT!!!
'''

import sys
import subprocess
import os
from glob import glob
import csv
from lxml import etree
from datetime import datetime
import hashlib
import time
from time import sleep
import unidecode
import codecs

#1




starting_dir = sys.argv[1]
#2

startTime = datetime.now()


csv_report_filename = os.path.basename(starting_dir) + "_report"
csv_report = os.path.expanduser("~/Desktop/%s.csv") % csv_report_filename 

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
        
def append_csv(csv_file, *args):
    f = open(csv_file, 'ab')
    try:
        writer = csv.writer(f)
        writer.writerow(*args)
    finally:
        f.close()
#6   
def digest_with_progress(filename, chunk_size):
    read_size = 0
    last_percent_done = 0
    digest = hashlib.md5()
    total_size = os.path.getsize(filename)

    data = True
    f = open(filename, 'rb')
    while data:
        # Read and update digest.
        data = f.read(chunk_size)
        read_size += len(data)
        digest.update(data)

        # Calculate progress.
        percent_done = 100 * read_size / total_size
        if percent_done > last_percent_done:
            sys.stdout.write('[%d%%]\r' % percent_done) 
            sys.stdout.flush()
            
            
            last_percent_done = percent_done
    f.close()
    return digest.hexdigest()

create_csv(csv_report, ('Filename' , 'Series_Title', 'Prog_Title' , 'Episode_Number' , 'Md5_From_Xml' , 'Md5_from_Mxf' , 'Checksum_Result'))
#6

if checkfile == True:
    print "CSV file already exists."
    
#3 

for dirpath, dirnames, filenames in os.walk(starting_dir):
    for filename in [f for f in filenames if f.endswith(".mxf")]:
        
        full_path = os.path.join(dirpath, filename)
        #7
        
        file_no_path = os.path.basename(full_path)
        #8.1
        
        file_no_extension = os.path.splitext(os.path.basename(file_no_path))[0]
        #8.2
        
        xml_file = file_no_extension + '.xml'
        
        full_xml_path = os.path.join(dirpath,xml_file)
        
        checkfile = os.path.isfile(os.path.join(dirpath,xml_file))
        if checkfile == False:
            print 'No XML file exists.'
        #8.3
        
        
        dpp_xml_parse = etree.parse(full_xml_path)
        dpp_xml_namespace = dpp_xml_parse.xpath('namespace-uri(.)')
        
        #parsed values
        series_title = dpp_xml_parse.findtext('//ns:SeriesTitle', namespaces={'ns':dpp_xml_namespace })
        prog_title = dpp_xml_parse.findtext('//ns:ProgrammeTitle', namespaces={'ns':dpp_xml_namespace })
        ep_num = dpp_xml_parse.findtext('//ns:EpisodeTitleNumber', namespaces={'ns':dpp_xml_namespace })
        checksum = dpp_xml_parse.findtext('//ns:MediaChecksumValue', namespaces={'ns':dpp_xml_namespace })
        #12
     
        
        
        print "Generating md5 for ", filename
        
    #print digest_with_progress(full_path, 1024)  
        mxf_checksum = str(digest_with_progress(full_path, 1024))
                
        
        dpp_xml_parse = etree.parse(full_xml_path)
        dpp_xml_namespace = dpp_xml_parse.xpath('namespace-uri(.)')
        
        #parsed values
        series_title = dpp_xml_parse.findtext('//ns:SeriesTitle', namespaces={'ns':dpp_xml_namespace })
        prog_title = dpp_xml_parse.findtext('//ns:ProgrammeTitle', namespaces={'ns':dpp_xml_namespace })
        ep_num = dpp_xml_parse.findtext('//ns:EpisodeTitleNumber', namespaces={'ns':dpp_xml_namespace })
        checksum = dpp_xml_parse.findtext('//ns:MediaChecksumValue', namespaces={'ns':dpp_xml_namespace })
        #12
        
        #13
        print 'Generating Report....  \n'

        if mxf_checksum == checksum:
            append_csv(csv_report,(filename, series_title, prog_title, ep_num, checksum, mxf_checksum, 'CHECKSUM MATCHES!'))
        else:
            append_csv(csv_report,(filename, series_title, prog_title, ep_num, checksum, mxf_checksum, 'CHECKSUM DOES NOT MATCH!'))
         #14
        
        #13
        print 'Generating Report....  \n',

        
        

       

print "Report complete - Time elaspsed : ", datetime.now() - startTime
        
        
   
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




