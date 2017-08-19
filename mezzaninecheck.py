#!/usr/bin/env python
'''
Checks folders in order to see if either 0 or >1
files exist in a mezzanine/objects folder.
This script is very specific to Irish Film Institute workflows.
'''
import sys
import os


def main():
    '''
    Launches recursive check for mezzanine files.
    '''
    for root, _, filenames in os.walk(sys.argv[1]):
        if os.path.basename(root) == 'objects':
            if os.path.basename(
                os.path.dirname(os.path.dirname(root))
            ) == 'mezzanine':
                counter = 0
                for i in filenames:
                    if i[0] != '.':
                        counter += 1
                if counter == 0:
                    print 'no mezzanine in ', root
                if counter > 1:
                    print 'multiple files in', root


if __name__ == '__main__':
    main()

