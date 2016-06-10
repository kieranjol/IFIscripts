import sys
import subprocess
import os
from glob import glob
import csv
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
        
        
        
        




"""
As-11 Fixity

1. Import all relevant modules x
2. Define path to starting folder x
3. Check if CSV report already exists x
4. Allow option to overwrite
5. Define name for CSv file
6. Create CSV file with headings x
7. Search through subfolders to verify mxf file exists
8.1 harvest filname eg GAA.MXF, remove extension eg MXF
8.2 store new filname eg GAA
8.3 make new filename variable
8.4 check if GAA with .XML extension exists
9. Check if same filename
10. Check if folder is empty, note in CSV report 
11. If only MXF, note in CSV report. MXF FILENAME + "No sidecar"
12. Extract MD5 from xml file and store as variable
13. Generate MD5 checksum on MXF file
14. Compare the 2 MD5s
15. Write to CSV report


8.1 harvest filname eg GAA.MXF, - file_no_path = 
8.2 remove extension eg MXF store new filname eg GAA filename_no_extention
8.3 check if GAA with .XML extension exists  - xml_filename
"""



