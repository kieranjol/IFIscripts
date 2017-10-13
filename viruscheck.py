#!/usr/bin/env python

#Requires ClamAV to be installed

import sys
import subprocess



def clamscan():
    scan = subprocess.call([
        'clamscan',
        '-r',
        starting_dir
    ])
    
    print scan
    

starting_dir = sys.argv[1]

print "Running scan.........."
clamscan()



