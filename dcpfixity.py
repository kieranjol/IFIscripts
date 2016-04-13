'''
WORK IN PROGRESS - BROKEN RIGHT NOW
'''
import subprocess
import sys
import os
import pdb

filename = sys.argv[1]

#pdb.set_trace()

dict = {}
def get_count(variable,typee):
       
    variable = subprocess.check_output(['xml', 'sel', 
                                             '-N', 'x=http://www.smpte-ra.org/schemas/429-8/2007/PKL',
                                             '-t', '-v', typee,
                                             filename ])
    return variable
count = get_count('count',"count(//x:Asset)")

def get_hash(variable,typee,element):
    
    
        variable = subprocess.check_output(['xml', 'sel', 
                                                 '-N', 'x=http://www.smpte-ra.org/schemas/429-8/2007/PKL',
                                                 '-t', '-m', typee,
                                                 '-v', element,
                                                 '-n', filename ])
        return variable
    
counter = 1    
while counter <= int(count):
    picture_files = get_hash('picture_files',"//x:Asset" + "[" + str(counter) + "]" , "x:Hash").replace('\n', '').replace('\r', '')
    print picture_files
    urn = get_hash('picture_files',"//x:Asset" + "[" + str(counter) + "]" , "x:Id")
    print urn
    counter += 1
    urn = urn.replace('\n', '').replace('\r', '')
    dict[urn[-36:]] = [picture_files]

print dict

                   
