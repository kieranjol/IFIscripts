import os
import subprocess
import sys
source = sys.argv[1]

source_count = 0
for root, directories, filenames in os.walk(source):   
    for files in filenames:   
            source_count +=1 
counter2 = 0
manifest = os.path.dirname(source) + '/manifest_sha512.txt'
for root, directories, filenames in os.walk(source):   
    for files in filenames:   
            print 'processing %d of %d\r' % (counter2, source_count)
            sha512 = subprocess.check_output(['openssl', 'sha512', '-r', os.path.join(root, files)])
            root2 = root.replace(os.path.dirname(source), '')
            
            with open(manifest, "ab") as fo:
                fo.write(sha512[:128] + ' ' + os.path.join(root2,files ).replace("\\", "/") + '\n')
            counter2 += 1
