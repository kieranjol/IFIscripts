#!/usr/bin/env python

import sys
import os
import subprocess

def main():
    for root, dirs, filenames in os.walk(sys.argv[1]):
        if os.path.basename(root) == 'objects':
            if os.path.basename(os.path.dirname(os.path.dirname(root))) == 'mezzanine':
                counter = 0
                for i in filenames:
                    if not i[0] == '.':
                        counter += 1
                if counter == 0:
                    print 'no mezzanine in ', root
                if counter > 1:
                    print 'multiple files in', root

if __name__ == '__main__':
    main()