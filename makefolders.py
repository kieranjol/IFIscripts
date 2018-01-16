#!/usr/bin/env python
'''
Creates a folder structure for a film scanning workflow.
'''
import os
import argparse
import ififuncs

def parse_args():
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Creates a folder structure for a film scanning workflow.'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        '-o', '-output',
        help='full path of output directory', required=True
    )
    parser.add_argument(
        '-refno', '-r',
        help='Filmographic reference number'
    )
    parser.add_argument(
        '-source', '-s',
        help='Accession number of source item'
    )
    parser.add_argument(
        '-title', '-t',
        help='Title of source film. No spaces!'
    )
    parsed_args = parser.parse_args()
    return parsed_args


def ask_something(question):
    '''
    Asks user for an something.
    '''
    thing2ask = False
    while thing2ask is False:
        thing2ask = raw_input(
            '\n\n****%s\n\n' % question
        )
        if ' ' in thing2ask:
            print 'no spaces please!!'
            thing2ask = raw_input(
                '\n\n****%s\n\n' % question
            )
    return thing2ask

def get_input(args):
    '''
    Interview the user so that the components of foldername are revealed.
    '''
    if not args.refno:
        filmographic = ask_something('filmographic number plz')
    if not args.source:
        source = ask_something('source accesion number plz')
    if not args.title:
        title = ask_something('source title plz WITH NO SPACESSS!!!')
    parent = '%s_%s_%s' % (filmographic, source, title)
    return parent

def make_folders(parent, args):
    '''
    Actually make the folders!
    '''
    output = args.o
    parent_folder = os.path.join(output, parent)
    os.makedirs(parent_folder)
    uuid_folder = os.path.join(parent_folder, ififuncs.create_uuid())
    logs_dir = os.path.join(uuid_folder, 'logs')
    objects_dir = os.path.join(uuid_folder, 'objects')
    metadata_dir = os.path.join(uuid_folder, 'metadata')
    os.makedirs(logs_dir)
    os.makedirs(objects_dir)
    os.makedirs(metadata_dir)
    for folder in [logs_dir, objects_dir, metadata_dir]:
        print folder
        os.chdir(folder)
        os.makedirs('image')
        os.makedirs('audio')

def main():
    '''
    Launches the functions that will create your folder structure.
    '''
    args = parse_args()
    parent = get_input(args)
    make_folders(parent, args)
if __name__ == '__main__':
    main()
