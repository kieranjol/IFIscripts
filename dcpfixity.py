from lxml import etree
import sys
from glob import glob
import csv
import os
from os import listdir
from os.path import isfile, join
import subprocess
import base64
import time
import re


dcp_dir = sys.argv[1]
# Two csv functions. One to create a csv, the other to add info to.
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

# Create a new .csv file with headings.  
# CSV filename will be DCp directory name + time/date.
csv_filename = os.path.basename(dcp_dir) +  '_item_level' + time.strftime("_%Y_%m_%dT%H_%M_%S")
# CSV will be saved to your Desktop.
csvfile = os.path.expanduser("~/Desktop/%s.csv") % csv_filename

csv_report_filename = os.path.basename(dcp_dir) + '_dcp_level' + time.strftime("_%Y_%m_%dT%H_%M_%S")
# CSV will be saved to your Desktop.
csv_report = os.path.expanduser("~/Desktop/%s.csv") % csv_report_filename        
create_csv(csvfile, ('MXF HASH', 'STORED HASH', 'FILENAME', 'JUDGEMENT'))
create_csv(csv_report, ('DCP NAME', 'DIRECTORY NAME', 'JUDGEMENT'))
for root,dirnames,filenames in os.walk(dcp_dir):
    if ("ASSETMAP.xml"  in filenames) or ("ASSETMAP"  in filenames) :
        dir = root
        
        # Changing directory makes globbing easier (from my experience anyhow).
        os.chdir(dir)

        # Scan the main DCP directory for an assetmap.
        dcp_files = [f for f in listdir(dir) if isfile(join(dir, f))]
        if 'ASSETMAP' in dcp_files:
            assetmap = 'ASSETMAP'
        elif 'ASSETMAP.xml' in dcp_files:
            assetmap = 'ASSETMAP.xml'

        # Parse the assetmap in order to find the namespace.  
        try:  
            assetmap_xml = etree.parse(assetmap)
        except SyntaxError:
            append_csv(csvfile,('NOT A VALID ASSETMAP', 'NOT A VALID ASSETMAP', dir,'NOT A VALID ASSETMAP'))
            append_csv(csv_report,(os.path.basename(dir), dir, 'NOT A VALID ASSETMAP'))
            print 'not an assetmap!!!!'
            continue
           
        print assetmap_xml
        assetmap_namespace = assetmap_xml.xpath('namespace-uri(.)')

        

        # Get a list of all XML files in the main DCP directory.
        xmlfiles = glob('*.xml')

        # Generate an empty list as there may be multiple PKLs.
        pkl_list = []

        # Loop through xmlfiles in order to find any PKL files.
        for i in xmlfiles:
            try:  
                xmlname = etree.parse(i)
            except SyntaxError:
                append_csv(csvfile,('NOT A VALID PKL', 'NOT A VALID PKL', dir,'NOT A VALID PKL'))
                append_csv(csv_report,(os.path.basename(dir), dir, 'NOT A VALID PKL'))
                print 'not a valid PKL!!!!'
                continue
            except KeyError:
                append_csv(csvfile,('PKL APPEARS TO BE MISSING', 'PKL APPEARS TO BE MISSING', dir,'PKL APPEARS TO BE MISSING'))
                append_csv(csv_report,(os.path.basename(dir), dir, 'PKL APPEARS TO BE MISSING'))
                print 'Missing PKL!!!!'
                continue
            
            is_pkl = xmlname.xpath('namespace-uri(.)')
            print is_pkl
            if 'PKL' in is_pkl:
                pkl_list.append(i)
            
        if len(pkl_list) == 0:
            
            append_csv(csvfile,('PKL APPEARS TO BE MISSING', 'PKL APPEARS TO BE MISSING', dir,'PKL APPEARS TO BE MISSING'))
            append_csv(csv_report,(os.path.basename(dir), dir, 'PKL APPEARS TO BE MISSING'))
            continue
        
              
        # Generate an empty dictionary that will link the PKL hashes to each UUID.        
        pkl_hashes = {}

        # Loop through the PKLs and link each hash to a UUID.
        for i in pkl_list: 
            pkl_parse = etree.parse(i)
            pkl_namespace = pkl_parse.xpath('namespace-uri(.)') 
            hashes =  pkl_parse.findall('//ns:Hash',namespaces={'ns': pkl_namespace})
            xmluuid =  pkl_parse.findall('//ns:Asset/ns:Id',namespaces={'ns': pkl_namespace})

            counter = 0
            
            while counter <= len(hashes) -1 : # The -1 is there because of lxml's zero indexing.
                pkl_hashes[xmluuid[counter].text] = hashes[counter].text # {pkl_uuid:pkl_hash}
                counter +=1
                
        # Begin analysis of assetmap xml.
        counter = 0
        assetmap_paths =  assetmap_xml.findall('//ns:Path',namespaces={'ns': assetmap_namespace})
        assetmap_uuids =  assetmap_xml.findall('//ns:Asset/ns:Id',namespaces={'ns': assetmap_namespace})
        #while counter <= len(assetmap_paths) -1 :
            
        counter = 0

        file_paths = {}
        
        while counter <= len(assetmap_paths) -1 :
            print assetmap_paths[counter].text
            if 'file:///' in assetmap_paths[counter].text:
                remove_this = 'file:///'
                assetmap_paths[counter].text =  assetmap_paths[counter].text.replace(remove_this,"")
            elif 'file://' in assetmap_paths[counter].text:
                remove_this = 'file://'
                assetmap_paths[counter].text =  assetmap_paths[counter].text.replace(remove_this,"")            

            elif 'file:/' in assetmap_paths[counter].text:
                remove_this = 'file:/'
                assetmap_paths[counter].text =  assetmap_paths[counter].text.replace(remove_this,"")
            

            file_paths[assetmap_uuids[counter].text] = [assetmap_paths[counter].text] # {assetmapuuid:assetmapfilename}
            counter +=1

        # Removes PKLs from list of files to hash, as these files are not in manifest.
        keys_to_remove = [] 

        for i in file_paths:
            if file_paths[i][0] in pkl_list:
                keys_to_remove.append(i)
        # PKL files are deleted from the file_paths dictionary. 
        for i in keys_to_remove:
            del file_paths[i]       

        # Check if there are any files missing from the DCP.

        missing_files = []
        for i in file_paths:
            if not os.path.isfile(file_paths[i][0]): # This checks if the file exists.
                print time.strftime("%Y-%m-%dT%H:%M:%S") + ' - **********' + file_paths[i][0] + ' is missing **********'
                missing_files.append(i)
                # Add missing file info to the csv.
                append_csv(csvfile,('MISSING FILE', pkl_hashes[i], os.path.abspath(file_paths[i][0]),'MISSING FILE'))

        # This removes the missing files from the hashable list. 
        for i in missing_files:
            del file_paths[i]
            del pkl_hashes[i]

        # Generate fresh hashes on the actual files in the DCP.           
        for i in file_paths:  
            print time.strftime("%Y-%m-%dT%H:%M:%S") + ' - Generating fresh hash for ' + file_paths[i][0]
            # Create SHA-1 binary hashes with OPENSSL.
            
            openssl_hash = subprocess.check_output(['openssl',
                                                    'sha1',
                                                    '-binary',
                                                     file_paths[i][0]])
            # Encode the hashes as base64.
            b64hash =  base64.b64encode(openssl_hash)
            # Append hashes to the list within the file_paths dictionary. 
            file_paths[i].append(b64hash)

        # Compare the hashes in the PKL manifest to the fresh hashes. 
        hash_mismatches = []       
        for i in file_paths:
            if file_paths[i][1] == pkl_hashes[i]:
                print file_paths[i][0] + ' is ok'
                append_csv(csvfile,(file_paths[i][1], pkl_hashes[i], os.path.abspath(file_paths[i][0]),'HASH MATCH'))
            else:
                print file_paths[i][0] + ' mismatch'
                hash_mismatches.append(file_paths[i][0])
                append_csv(csvfile,(file_paths[i][1], pkl_hashes[i], os.path.abspath(file_paths[i][0]),'HASH MISMATCH'))
            
                
        if len(hash_mismatches) > 0:
            report = ' but THERE ARE HASH MISMATCHES. SCROLL UP FOR MORE INFO OR CHECK THE CSV'
        else:
            report = ' and all hashes match.'

        if len(missing_files) > 0:
            print time.strftime("%Y-%m-%dT%H:%M:%S") + ' - WARNING - THERE ARE FILES MISSING FROM THIS DCP. SCROLL UP FOR MORE INFO OR CHECK THE CSV'
            append_csv(csv_report,(os.path.basename(dir), dir, 'FILES MISSING - CHECK REPORT'))
        else: 
            print time.strftime("%Y-%m-%dT%H:%M:%S") + ' - All files are present in your DCP' + report
            append_csv(csv_report,(os.path.basename(dir), dir,'All files present ' + report))
