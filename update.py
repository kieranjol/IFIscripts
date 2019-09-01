#!/usr/bin/env python3
import os
import subprocess
import sys



def install_check(directory):
    if os.path.isdir(directory):
        return True
    else:
        print('\nWARNING - %s does not exist!\nCreate a directory in your home directory called `ifigit` and git clone the repository in there' % directory)
        return False

def main():
    home = os.path.expanduser("~/")
    os.chdir(home)
    if install_check('ifigit/ifiscripts'):
        os.chdir('ifigit/ifiscripts')
        print("Updating IFIScripts - Changing directory to %s and running `git pull`" % os.getcwd())
        subprocess.call(['git', 'checkout', 'master'])
        subprocess.call(['git', 'pull'])
    if install_check('../premisviewer'):
        os.chdir('../premisviewer')
        print('Updating PREMISviewer - Changing directory to %s and running `git pull`' % os.getcwd())
        subprocess.call(['git', 'pull'])
    print('\nNotice - 2017-01-13')
    print('********** PREMISVIEWER is now part of update.py \n***************')

if __name__ == '__main__':
    main()
