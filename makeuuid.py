#!/usr/bin/env python
'''
This script will create a new UUID
via ififuncs.create_uuid and print to terminal
'''
from ififuncs import create_uuid


def main():
    '''
    Prints a new UUID to the terminal
    '''
    new_uuid = create_uuid()
    print new_uuid

if __name__ == '__main__':
    main()
