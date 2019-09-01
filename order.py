#!/usr/bin/env python3
'''
Audits logfiles to determine the parent of a derivative package.
This script can aid in automating large accessioning procedures that involve
the accessioning of derivatives along with masters, eg a Camera Card and
a concatenated derivative, or a master file and a mezzanine.

order.py will be able to determine if something is a reproduction,
but it won't be able to tell if acquisitions are deposits, purchases or donations.
So leave it blank in the latter instances.
'''
import sys
import os
import ififuncs

def file_count(source):
    '''
    Checks how many mov/mp4 files are in a dir.
    '''
    count = 0
    for root, _, filenames in os.walk(source):
        for files in filenames:
            if files.lower().endswith(('.mov', '.mp4')):
                count += 1
    return count


def main(args):
    '''
    Analyzes a directory containing Object Entry packages and returns their
    parent or lack thereof.
    '''
    source = args
    if os.path.basename(source)[:2] == 'oe' or os.path.basename(source)[:3] == 'aaa' :
        oe_uuid_dict = ififuncs.group_ids(os.path.dirname(source))
        for root, _, filenames in os.walk(source):
            for filename in filenames:
                if filename.endswith('_sip_log.log'):
                    uuid_search = ififuncs.find_parent(
                        os.path.join(root, filename), oe_uuid_dict
                    )
                    if 'not a child' in uuid_search:
                        # Checks if a single AV file is in the objects dir.
                        uuid_dir = os.path.join(os.path.dirname(root))
                        if file_count(os.path.join(uuid_dir, 'objects')) == 1:
                            print('%s has no parent but this could be because it is a single file' % os.path.basename(os.path.dirname(uuid_dir)))
                            proceed = ififuncs.ask_yes_no('add %s to accession list?' % os.path.basename(os.path.dirname(uuid_dir)))
                            if proceed == 'Y':
                                print(os.path.basename(os.path.dirname(uuid_dir)))
                                return os.path.basename(os.path.dirname(uuid_dir))
                        else:
                            # master
                            return None
                    elif 'has a parent' in uuid_search:
                        parent = uuid_search.split()[-1]
                        # Commenting this out for now - this just adds the dash really.
                        # print parent[:2].upper() + '-' + parent[2:]
                        print(parent)
                        return parent

if __name__ == '__main__':
    main(sys.argv[1])
