from lxml import etree
import sys
from glob import glob
import os
from os import listdir
from os.path import isfile, join

myfile = sys.argv[1]
#os.chdir(myfile)
onlyfiles = [f for f in listdir(myfile) if isfile(join(myfile, f))]
    
print onlyfiles
if 'ASSETMAP' in onlyfiles:
    print 'interop'
elif 'ASSETMAP.xml' in onlyfiles:
    print 'smpte'
doc = etree.parse(myfile)
root = doc.getroot()
#print doc.xpath('//ns:Path',namespaces={'ns': "http://www.smpte-ra.org/schemas/429-9/2007/AM"})

var =  doc.findall('//ns:Path',namespaces={'ns': "http://www.smpte-ra.org/schemas/429-9/2007/AM"})
xmlid =  doc.findall('//ns:Asset/ns:Id',namespaces={'ns': "http://www.smpte-ra.org/schemas/429-9/2007/AM"})
print len(var) - 1
counter = 0
file_paths = {}
while counter <= len(var) -1 :
    print var[counter].text
    file_paths[var[counter].text] = xmlid[counter].text
    counter +=1
'''for i in xmlid:
    print i.text
print var[7].text
'''
#print xmlid


print file_paths
'''for elt in doc.getiterator():
   
    print elt.tag
'''
'''
f = etree.parse(myfile)
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
