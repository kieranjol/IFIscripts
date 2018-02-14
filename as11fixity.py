#!/usr/bin/env python
'''
WORK IN PROGRESS WORKSHOP SCRIPT!!!
'''

import sys
import os
import csv
import hashlib
from datetime import datetime
from lxml import etree
import unidecode


def create_csv(csv_file, *args):
    f = open(csv_file, 'wb')
    try:
        writer = csv.writer(f)
        writer.writerow(*args)
    finally:
        f.close()


def append_csv(csv_file, *args):
    f = open(csv_file, 'ab')
    try:
        writer = csv.writer(f)
        writer.writerow(*args)
    finally:
        f.close()


def digest_with_progress(filename, chunk_size):
    read_size = 0
    last_percent_done = 0
    digest = hashlib.md5()
    total_size = os.path.getsize(filename)
    data = True
    f = open(filename, 'rb')
    while data:
        # Read and update digest.
        data = f.read(chunk_size)
        read_size += len(data)
        digest.update(data)
        # Calculate progress.
        percent_done = 100 * read_size / total_size
        if percent_done > last_percent_done:
            sys.stdout.write('[%d%%]\r' % percent_done)
            sys.stdout.flush()
            last_percent_done = percent_done
    f.close()
    return digest.hexdigest()


def main():
    starting_dir = sys.argv[1]
    startTime = datetime.now()
    csv_report_filename = os.path.basename(starting_dir) + "_report"
    csv_report = os.path.expanduser("~/Desktop/%s.csv") % csv_report_filename
    checkfile = os.path.isfile(csv_report)
    create_csv(
        csv_report,
        (
            'Filename',
            'Series_Title',
            'Prog_Title',
            'Episode_Number',
            'Md5_From_Xml',
            'Md5_from_Mxf',
            'Checksum_Result'
            )
        )
    if checkfile is True:
        print "CSV file already exists."
    for dirpath, _, filenames in os.walk(starting_dir):
        for filename in [f for f in filenames if f.endswith(".mxf")]:
            full_path = os.path.join(dirpath, filename)
            file_no_path = os.path.basename(full_path)
            file_no_extension = os.path.splitext(os.path.basename(file_no_path))[0]
            xml_file = file_no_extension + '.xml'
            full_xml_path = os.path.join(dirpath, xml_file)
            checkfile = os.path.isfile(os.path.join(dirpath, xml_file))
            if checkfile == False:
                print 'No XML file exists.'
            print "Generating md5 for ", filename
            mxf_checksum = str(digest_with_progress(full_path, 1024))
            dpp_xml_parse = etree.parse(full_xml_path)
            dpp_xml_namespace = dpp_xml_parse.xpath('namespace-uri(.)')
            #parsed values
            series_title = dpp_xml_parse.findtext(
                '//ns:SeriesTitle',
                namespaces={'ns':dpp_xml_namespace}
            )
            prog_title = dpp_xml_parse.findtext(
                '//ns:ProgrammeTitle',
                namespaces={'ns':dpp_xml_namespace}
            )
            ep_num = dpp_xml_parse.findtext(
                '//ns:EpisodeTitleNumber',
                namespaces={'ns':dpp_xml_namespace}
            )
            checksum = dpp_xml_parse.findtext(
                '//ns:MediaChecksumValue',
                namespaces={'ns':dpp_xml_namespace}
            )
            print 'Generating Report....  \n'
            if mxf_checksum == checksum:
                append_csv(
                    csv_report,
                    (
                        filename,
                        unidecode.unidecode(series_title),
                        unidecode.unidecode(prog_title),
                        unidecode.unidecode(ep_num),
                        checksum,
                        mxf_checksum,
                        'CHECKSUM MATCHES!'
                        )
                )
            else:
                append_csv(
                    csv_report,
                    (
                        filename,
                        unidecode.unidecode(series_title),
                        unidecode.unidecode(prog_title),
                        unidecode.unidecode(ep_num),
                        checksum,
                        mxf_checksum,
                        'CHECKSUM DOES NOT MATCH!'
                        )
                )
    print "Report complete - Time elaspsed : ", datetime.now() - startTime


if __name__ == '__main__':
    main()
