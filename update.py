#!/usr/bin/env python
import os
import subprocess
import sys

home = os.path.expanduser("~/")
os.chdir(home)
os.chdir('ifigit/ifiscripts')
print os.getcwd()
subprocess.call(['git', 'pull'])