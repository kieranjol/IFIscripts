#!/usr/bin/env python

import os
import sys
import csv
from lxml import etree

def extract_metadata(csv_file):
    object_dictionaries = []
    input_file = csv.DictReader(open(csv_file))
    for rows in input_file:
        object_dictionaries.append(rows)
    return object_dictionaries

def add_value(value, element):
    element.text = value


def write_premis(doc, premisxml):
    with open(premisxml, 'w') as outFile:
        doc.write(outFile, pretty_print=True)


def create_unit(index, parent, unitname):
    premis_namespace = "http://www.loc.gov/premis/v3"
    unitname = etree.Element("{%s}%s" % (premis_namespace, unitname))
    parent.insert(index, unitname)
    return unitname

def setup_xml(object_dictionaries):
    namespace = '<premis:premis xmlns:premis="http://www.loc.gov/premis/v3" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/premis/v3 https://www.loc.gov/standards/premis/premis.xsd" version="3.0"></premis:premis>'
    premis_namespace = "http://www.loc.gov/premis/v3"
    premis = etree.fromstring(namespace)
    doc = etree.ElementTree(premis)
    for objects in object_dictionaries:
        id_list = objects['objectIdentifier'].replace(
            '[', ''
        ).replace(']', '').replace('\'', '').split(', ')
        object_parent = create_unit(0, premis, 'object')
        object_identifier_uuid = create_unit(2, object_parent, 'objectIdentifier')
        object_identifier_uuid_type = create_unit(1, object_identifier_uuid, 'objectIdentifierType')
        object_identifier_uuid_value = create_unit(2, object_identifier_uuid, 'objectIdentifierValue')
        object_category = create_unit(4, object_parent, 'objectCategory')
        add_value(id_list[0], object_identifier_uuid_type)
        add_value(id_list[1], object_identifier_uuid_value)
        add_value(objects['objectCategory'], object_category)
        if objects['objectCategory'] == 'file':
            object_characteristics = create_unit(10, object_parent, 'objectCharacteristics')
            fixity = create_unit(0, object_characteristics, 'fixity')
            size = create_unit(1, object_characteristics, 'size')
            size.text = objects['size']
            message_digest_algorithm = create_unit(0, fixity, 'messageDigestAlgorithm')
            message_digest = create_unit(1, fixity, 'messageDigest')
            message_digest_originator = create_unit(2, fixity, 'messageDigestOriginator')
            message_digest_originator.text = objects['messageDigestOriginator']
            message_digest.text = objects['messageDigest']
            message_digest_algorithm.text = objects['messageDigestAlgorithm']
    print(etree.tostring(doc, pretty_print=True))
    return premis_namespace, doc, premis
def main():
    csv_file = sys.argv[1]
    object_dictionaries = extract_metadata(csv_file)
    setup_xml(object_dictionaries)
    for x in object_dictionaries:
        for i in x:
            if x[i] != '':
                print i, x[i]
        print '\n'

if __name__ == '__main__':
    main()
