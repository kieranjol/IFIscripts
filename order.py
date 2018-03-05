#!/usr/bin/env python
'''
Audits logfiles to determine the parent of a derivative package.
This script can aid in automating large accessioning procedures that involve
the accessioning of derivatives along with masters, eg a Camera Card and
a concatenated derivative, or a master file and a mezzanine.
'''
import sys
import os
import ififuncs


def main():
    '''
    Analyzes a directory containing Object Entry packages and returns their
    parent or lack thereof.
    '''
    source = args
    if os.path.basename(source)[:2] == 'oe':
        oe_uuid_dict = ififuncs.group_ids(os.path.dirname(source))
        for root, _, filenames in os.walk(source):
            for filename in filenames:
                if filename.endswith('_sip_log.log'):
                    uuid_search = ififuncs.find_parent(
                        os.path.join(root, filename), oe_uuid_dict
                    )
                    if 'not a child' in uuid_search:
                        return None
                    elif 'has a parent' in uuid_search:
                        parent = uuid_search[-7:-1]
                        print parent[:2].upper() + '-' + parent[2:]
                        return parent



if __name__ == '__main__':
    main(sys.argv[1])
