#!/usr/bin/env python
'''
Make a sha512 manifest
'''
import os
import subprocess
import sys


def main():
    '''
    Super basic sha512 manifest generator.
    Haven't looked at this in ages, needs a lot more work!
    '''
    source = sys.argv[1]
    total_file_count = 0
    print 'Determining number of files to be processed'
    for root, _, filenames in os.walk(source):
        for files in filenames:
            total_file_count += 1
    progress_counter = 1
    manifest = os.path.dirname(source) + '/manifest_sha512.txt'
    for root, _, filenames in os.walk(source):
        for files in filenames:
            print 'processing %s - %d of %d' % (
                files, progress_counter, total_file_count
                )
            sha512 = subprocess.check_output(
                ['openssl', 'sha512', '-r', os.path.join(root, files)]
                )
            root2 = root.replace(os.path.dirname(source), '')
            with open(manifest, "ab") as manifest_object:
                manifest_object.write(
                    sha512[:128] + ' ' + os.path.join(
                        root2, files
                        ).replace("\\", "/") + '\n'
                    )
            progress_counter += 1
    print 'Manifest created in %s' % manifest


if __name__ == '__main__':
    main()
