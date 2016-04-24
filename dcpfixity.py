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

dcp_dir = sys.argv[1]
print listdir(dcp_dir)
filename_without_path = os.path.basename(dcp_dir)
csv_filename = filename_without_path + time.strftime("_%Y_%m_%dT%H_%M_%S")

csvfile               = os.path.expanduser("~/Desktop/%s.csv") % csv_filename
os.chdir(dcp_dir)
dcp_files = [f for f in listdir(dcp_dir) if isfile(join(dcp_dir, f))]
if 'ASSETMAP' in dcp_files:
    print 'interop'
    assetmap = 'ASSETMAP'
elif 'ASSETMAP.xml' in dcp_files:
    assetmap = 'ASSETMAP.xml'
assetmap_xml = etree.parse(assetmap)
assetmap_namespace = assetmap_xml.xpath('namespace-uri(.)')
root = assetmap_xml.getroot()   
#print dcp_files
xmlfiles = glob('*.xml')

def create_csv(csv_file, *args):
    f = open(csv_file, 'wt')
    try:
        writer = csv.writer(f)
        writer.writerow(*args)
    finally:
        f.close()
        
def append_csv(csv_file, *args):
    f = open(csv_file, 'a')
    try:
        writer = csv.writer(f)
        writer.writerow(*args)
    finally:
        f.close()
        
create_csv(csvfile, ('MXF HASH', 'STORED HASH', 'FILENAME', 'JUDGEMENT'))
#print xmlfiles
pkl_list = []
for i in xmlfiles:

    xmlname = etree.parse(i)
    is_pkl = xmlname.xpath('namespace-uri(.)')
    if 'PKL' in is_pkl:
        #print  str(i) + 'blablablba'
        pkl_list.append(i)
        
        #print 'pkl_file is ' + i
#print pkl_list  
pkl_hashes = {}
for i in pkl_list: 
    pkl_parse = etree.parse(i)
    pkl_namespace = pkl_parse.xpath('namespace-uri(.)') 
    #print pkl_namespace  
    #print 'asdasdasd' + i
    hashes =  pkl_parse.findall('//ns:Hash',namespaces={'ns': pkl_namespace})

    xmluuid =  pkl_parse.findall('//ns:Asset/ns:Id',namespaces={'ns': pkl_namespace})
    #print len(var) - 1
    counter = 0
    
    while counter <= len(hashes) -1 :
        #print var[counter].text
        pkl_hashes[xmluuid[counter].text] = hashes[counter].text # {pkl_uuid:pkl_hash}
        #print pkl_hashes
        counter +=1
    #print assetmap_xml.xpath('//ns:Path',namespaces={'ns': "http://www.smpte-ra.org/schemas/429-9/2007/AM"})
#print pkl_hashes    
var =  assetmap_xml.findall('//ns:Path',namespaces={'ns': assetmap_namespace})

xmlid =  assetmap_xml.findall('//ns:Asset/ns:Id',namespaces={'ns': assetmap_namespace})
#print len(var) - 1
counter = 0
file_paths = {}

while counter <= len(var) -1 :
    #print var[counter].text
    file_paths[xmlid[counter].text] = [var[counter].text] # {assetmapuuid:assetmapfilename}
    counter +=1
#print pkl_list 
keys_to_remove = [] 
print len(file_paths)
for i in file_paths:
    #print file_paths[i][0]
    if file_paths[i][0] in pkl_list:
        keys_to_remove.append(i)
print  keys_to_remove 
for i in keys_to_remove:
    del file_paths[i]       
print len(file_paths)

missing_files = []
for i in file_paths:
    if not os.path.isfile(file_paths[i][0]):
    
        print file_paths[i][0] + 'is missing'
        missing_files.append(i)
        append_csv(csvfile,('MISSING FILE', pkl_hashes[i], file_paths[i][0],'MISSING FILE'))
 
print  missing_files
for i in missing_files:
    del file_paths[i]
    del pkl_hashes[i]       
for i in file_paths:
    
    
    if os.path.isfile(file_paths[i][0]):
    
        openssl_hash = subprocess.check_output(['openssl', 'sha1', '-binary', file_paths[i][0]])
        b64hash =  base64.b64encode(openssl_hash)
        #print b64hash  
        file_paths[i].append(b64hash)
    else:
        print file_paths[i][0] + 'is missing'

        
for i in file_paths:
    if file_paths[i][1] == pkl_hashes[i]:
        print file_paths[i][0] + ' is ok'
        append_csv(csvfile,(file_paths[i][1], pkl_hashes[i], file_paths[i][0],'HASH MATCH'))
    else:
        print file_paths[i][0] + ' mismatch'


'''
    if file_paths[i][1] == pkl_hashes[i]:
        print 'all is well'
   
else: 
    print 'something wronggg'  
# get real hashes
print file_paths
for i in pkl_hashes:
    print pkl_hashes[i]
for i in pkl_hashes:
    print file_paths[i][1]
    '''
'''for i in xmlid:
    print i.text
print var[7].text
'''
#print xmlid


#print file_paths
'''for elt in assetmap_xml.getiterator():
   
    print elt.tag
'''
'''
f = etree.parse(dcp_dir)
root = f.getroot()
namespace = f.xpath('namespace-uri(.)')


print namespace
print f.xpath("//Path",namespaces={'ns': "http://www.smpte-ra.org/schemas/429-9/2007/AM"})
#all = f.findall('//ns:Chunk', namespaces={'ns': namespace})
print all
'''
'''
y = root.tag('//*/Path')
print y
root = f.getroot()
print root.findall("Chunk")

'''
