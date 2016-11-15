#!/usr/bin/env python
import os
import subprocess
import sys

home = os.path.expanduser("~/")
os.chdir(home)
os.chdir('ifigit/ifiscripts')
print os.getcwd()
subprocess.call(['git', 'pull'])
print '\nNotice - 2016-11-15'
print '********** Logs and manifests for moveit.py and validate.py are now in subfolders on the desktop!!!***************'