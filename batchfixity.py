#!/usr/bin/env python
from ififuncs import hashlib_manifest
import argparse
import os
import sys


def make_parser():
    parser = argparse.ArgumentParser(description='Batch MD5 checksum generator.Accepts a parent folder as input and will generate manifest for each subfolder. Designed for a specific IFI Irish Film Archive workflow'
                                 ' Written by Kieran O\'Leary.')
    parser.add_argument('input', help='file path of parent directory')
    return parser


def create_manifest(input):
    os.chdir(input)
    for dirname in os.walk('.').next()[1]:
        full_path = os.path.join(input, dirname)
        manifest_textfile = '%s/%s_manifest.md5' % (full_path,dirname)
        hashlib_manifest(full_path, manifest_textfile, full_path)


def main():
    parser = make_parser()
    args = parser.parse_args()
    create_manifest(args.input)
if __name__ == '__main__':
   main()

