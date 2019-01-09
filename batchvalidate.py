#!/usr/bin/env python
import validate
import sys
import os
import subprocess
source = sys.argv[1]
results = []
for root, dirname, filenames in os.walk(source):
    error_counter = 0
    for files in filenames:
        if files.endswith('_manifest.md5'):
            if  os.path.basename(root) != 'logs':
                manifest = os.path.join(root, files)
                print manifest
                if os.path.isfile(manifest):
                    error_counter = validate.main([manifest])
                    if error_counter == 0:
                        results.append([root, 'success'])
                    else:
                        results.append([root, 'failure'])
                    for result in results:
                        print result
            else:
                continue

for result in results:
        print result
    
                
    