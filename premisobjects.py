#!/usr/bin/env python
'''
Creates a somewhat PREMIS compliant CSV file describing objects in a package.
A seperate script will need to be written in order to transform these
CSV files into XML.
As the flat CSV structure prevents maintaining some of the complex
relationships between units, some semantic units have been merged, for example:
relation_structural_includes is really a combination of the
relationshipType and relationshipSubType units, which each have the values:
Structural and Includes respectively.

todo:
Document identifier assignment for files and IE. Probably in events sheet?\
This would ideally just add to the log in the helper script.
Allow for derivation to be entered
Link mediainfo xml in /metadata to the objectCharacteristicsExtension field.


Assumptions for now: representation UUID already exists as part of the
SIP/AIP folder structure. Find a way to supply this, probably via argparse.
'''

import os
import sys
import argparse
import ififuncs


def make_skeleton_csv(output):
    '''
    Generates a CSV with PREMIS-esque headings. Currently it's just called
    'objects.csv' but it will probably be called:
    UUID_premisobjects.csv
    and sit in the metadata directory.
    '''
    premis_object_units = [
        'objectIdentifier',
        'objectCategory',
        'messageDigestAlgorithm', 'messageDigest', 'messageDigestOriginator',
        'size',	'formatName', 'formatVersion',
        'formatRegistryName', 'formatRegistryKey', 'formatRegistryRole',
        'objectCharacteristicsExtension', 'originalName',
        'contentLocationType', 'contentLocationValue',
        'relatedObjectIdentifierType', 'relatedObjectIdentifierValue',
        'relatedObjectSequence',
        'relatedEventIdentifierType', 'relatedEventIdentifierValue',
        'relatedEventSequence',
        'linkingEventIdentifierType', 'linkingEventIdentifierValue',
        'relationship_structural_includes',
        'relationship_structural_isincludedin',
        'relationship_structural_represents',
        'relationship_structural_hasroot',
        'relationship_derivation_hassource'
    ]
    ififuncs.create_csv(output, premis_object_units)


def file_description(source, manifest, representation_uuid, output):
    '''
    Generate PREMIS descriptions for items and write to CSV.
    '''
    item_ids = []
    for root, _, filenames in os.walk(source):
        filenames = [f for f in filenames if f[0] != '.']
        for item in filenames:
            md5, uri = ififuncs.get_checksum(manifest, item)
            item_uuid = ififuncs.create_uuid()
            full_path = os.path.join(root, item)
            print 'Using Siegfriend to analyze %s' % item
            pronom_id, authority, version = ififuncs.get_pronom_format(
                full_path
            )
            item_dictionary = {}
            item_dictionary['objectIdentifier'] = ['UUID', item_uuid]
            item_dictionary['objectCategory'] = 'file'
            item_dictionary['size'] = str(os.path.getsize(full_path))
            item_dictionary['originalName'] = item
            item_dictionary['relationship_structural_isincludedin'] = representation_uuid
            item_ids.append(item_uuid)
            file_data = [
                item_dictionary['objectIdentifier'],
                item_dictionary['objectCategory'],
                'md5', md5, 'internal',
                item_dictionary['size'], '', '',
                authority, pronom_id, 'identification',
                '', item,
                'uri', uri,
                '', '',
                '',
                '', '',
                '',
                '', '',
                '',
                item_dictionary['relationship_structural_isincludedin'],
                '',
                '',
                ''
            ]
            ififuncs.append_csv(output, file_data)
    return item_ids
def representation_description(representation_uuid, item_ids, output):
    '''
    Generate PREMIS descriptions for a representation and write to CSV.
    '''
    representation_dictionary = {}
    representation_dictionary['objectIdentifier'] = ['UUID', representation_uuid]
    representation_dictionary['objectCategory'] = 'representation'
    representation_dictionary['relationship_structural_includes'] = ''
    for item_id in item_ids:
        representation_dictionary['relationship_structural_includes'] += item_id + '|'
    representation_data = [
        representation_dictionary['objectIdentifier'],
        representation_dictionary['objectCategory'],
        '', '', '',
        '', '', '',
        '', '', '',
        '', '',
        '', '',
        '', '',
        '',
        '', '',
        '',
        '', '',
        representation_dictionary['relationship_structural_includes'],
        '',
        '',
        '',
        ''
    ]
    ififuncs.append_csv(output, representation_data)


def intellectual_entity_description():
    '''
    Generate PREMIS descriptions for Intellectual Entities and write to CSV.
    '''
    intellectual_entity_dictionary = {}
    intellectual_entity_dictionary['objectIdentifier'] = ['UUID', ififuncs.create_uuid()]
    intellectual_entity_dictionary['objectCategory'] = 'intellectual entity'
    #print intellectual_entity_dictionary


def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Describes objects using PREMIS data dictionary using CSV'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        '-i',
        help='full path of input objects directory', required=True
    )
    parser.add_argument(
        '-o', '-output',
        help='full path of output directory', required=True
    )
    parser.add_argument(
        '-m', '-manifest',
        help='full path to a pre-existing manifest', required=True
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def main(args_):
    '''
    Launches all the other functions when run from the command line.
    '''
    args = parse_args(args_)
    source = args.i
    output = args.o
    manifest = args.m
    make_skeleton_csv(output)
    representation_uuid = ififuncs.find_representation_uuid(source)
    item_ids = file_description(source, manifest, representation_uuid, output)
    #intellectual_entity_description()
    representation_description(representation_uuid, item_ids, output)


if __name__ == '__main__':
    main(sys.argv[1:])

