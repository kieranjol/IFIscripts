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
Document identifier assignment for files and IE. Probably in events sheet?
Allow for derivation to be entered
Link with events sheet
Link mediainfo xml in /metadata to the objectCharacteristicsExtension field.


Assumptions for now: representation UUID already exists as part of the
SIP/AIP folder structure. Find a way to supply this, probably via argparse.
'''

import os
import sys
import ififuncs


def get_checksum(manifest, filename):
    '''
    Extracts the checksum and path within a manifest, returning both as a tuple.
    '''
    if os.path.isfile(manifest):
        with open(manifest, 'r') as manifest_object:
            manifest_lines = manifest_object.readlines()
            for md5 in manifest_lines:
                if 'objects' in md5:
                    if filename in md5:
                        return md5[:32], md5[34:].rstrip()


def make_skeleton_csv():
    '''
    Generates a CSV with PREMIS-esque headings. Currently it's just called
    'cle.csv' but it will probably be called:
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
    ififuncs.create_csv('objects.csv', premis_object_units)


def file_description(source, manifest, representation_uuid):
    '''
    Generate PREMIS descriptions for items and write to CSV.
    '''
    item_ids = []
    for root, _, filenames in os.walk(source):
        if os.path.basename(root) == 'objects':
            for root, _, filenames in os.walk(root):
                filenames = [f for f in filenames if f[0] != '.']
                for item in filenames:
                    md5, uri = get_checksum(manifest, item)
                    item_uuid = ififuncs.create_uuid()
                    full_path = os.path.join(root, item)
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
                    ififuncs.append_csv('objects.csv', file_data)
    return item_ids
def representation_description(representation_uuid, item_ids):
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
    ififuncs.append_csv('objects.csv', representation_data)


def intellectual_entity_description():
    '''
    Generate PREMIS descriptions for Intellectual Entities and write to CSV.
    '''
    intellectual_entity_dictionary = {}
    intellectual_entity_dictionary['objectIdentifier'] = ['UUID', ififuncs.create_uuid()]
    intellectual_entity_dictionary['objectCategory'] = 'intellectual entity'
    #print intellectual_entity_dictionary
def find_representation_uuid(source):
    '''
    This extracts the representation UUID from a directory name.
    This should be moved to ififuncs as it can be used by other scripts.
    '''
    for root, _, _ in os.walk(source):
        if 'objects' in root:
            return os.path.basename(os.path.dirname(root))


def main():
    '''
    Launches all the other functions when run from the command line.
    '''
    make_skeleton_csv()
    source = sys.argv[1]
    manifest = sys.argv[2]
    representation_uuid = find_representation_uuid(source)
    item_ids = file_description(source, manifest, representation_uuid)
    #intellectual_entity_description()
    representation_description(representation_uuid, item_ids)

if __name__ == '__main__':
    main()

