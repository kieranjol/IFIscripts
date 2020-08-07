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
    f = open(csv_file, 'w', encoding='utf8', newline='')
    try:
        writer = csv.writer(f)
        writer.writerow(*args)
    finally:
        f.close()


def append_csv(csv_file, *args):
    f = open(csv_file, 'a', encoding='utf-8', newline='')
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

def count_files(starting_dir):
    dicto = {}
    previous_oe = ''
    for dirpath, dirss, filenames in os.walk(starting_dir):
        oe = False
        aaa = False
        try:
            current_oe = dirpath.split('oe')[1][:5]
            if current_oe[-1] == '/':
                current_oe = current_oe[:4]
            oe = True
        except IndexError:
            try:
                current_oe = dirpath.split('aaa')[1][:4]
                aaa = True
            except IndexError:
                continue
        if previous_oe != current_oe:
            filename_counter = 0
            dir_counter = 0
        for filename in filenames:
            if filename[0] != '.':
                filename_counter += 1
        dir_counter += len(dirss)
        previous_oe = current_oe
        if oe:
            dicto['oe' + previous_oe] = [filename_counter, dir_counter]
        elif aaa:
            dicto['aaa' + previous_oe] = [filename_counter, dir_counter]
        ''''
        except KeyError:
            print 'hi'
            dicto['aaa' + previous_oe] = [filename_counter, dir_counter]
        '''
    print(dicto)
    return dicto
def main():
    starting_dir = sys.argv[1]
    dicto = count_files(starting_dir)
    print(dicto, 12312312123)
    startTime = datetime.now()
    csv_report_filename = os.path.basename(starting_dir) + "_report"
    csv_report = os.path.expanduser("~/Desktop/%s.csv") % csv_report_filename
    checkfile = os.path.isfile(csv_report)
    counter = 0
    create_csv(
        csv_report,
        (
            'ID',
            'oe',
            'accessionnumber',
            'files_count',
            'directory_count',
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
        print("CSV file already exists.")
    for dirpath, dirss, filenames in sorted(os.walk(starting_dir)):
        for filename in filenames:
            if filename.endswith('.xml'):
                if os.path.basename(dirpath) == 'supplemental':
                    full_xml_path = os.path.join(dirpath, filename)
                else:
                    continue
                uuid_dir = os.path.dirname(os.path.dirname(dirpath))
                objects_dir = os.path.join(uuid_dir, 'objects')
                logs_dir = os.path.join(uuid_dir, 'logs')
                log = os.path.join(logs_dir, os.path.basename(uuid_dir) + '_sip_log.log')
                
                objects_list = os.listdir(objects_dir)

                manifest_basename = os.path.basename(uuid_dir) + '_manifest.md5'
                manifest = os.path.join(os.path.dirname(uuid_dir), manifest_basename)
                with open(manifest, 'r', encoding='utf-8') as fo:
                    manifest_lines = fo.readlines()
                    for line in manifest_lines:
                        if line.lower().replace('\n', '').endswith('.mxf'):
                        
                            mxf_checksum = line[:32]
                            print(mxf_checksum)
                #mxf_checksum = str(digest_with_progress(mxf, 1024))
                try:
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
                    accession_number_id = ''
                    print('Generating Report....  \n')
                    if os.path.isfile(log):
                        print(log)
                        with open(log, 'r', encoding='utf-8') as log_object:
                            log_lines = log_object.readlines()
                            for lines in log_lines:
                                if 'eventIdentifierType=object entry,' in lines:
                                    source_oe = lines.split('=')[-1].replace('\n', '')
                                if 'eventIdentifierType=accession number,' in lines:
                                    accession_number_id = lines.split('=')[-1].replace('\n', '')
                    if mxf_checksum == checksum:
                        print(dicto,7897897897)
                        append_csv(
                            csv_report,
                            (
                                os.path.basename(os.path.dirname(uuid_dir)),
                                source_oe,
                                accession_number_id,
                                dicto[os.path.basename(os.path.dirname(uuid_dir))][0],
                                dicto[os.path.basename(os.path.dirname(uuid_dir))][1],
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
                                os.path.basename(os.path.dirname(uuid_dir)),
                                source_oe,
                                accession_number_id,
                                dicto[os.path.basename(os.path.dirname(uuid_dir))][0],
                                dicto[os.path.basename(os.path.dirname(uuid_dir))][1],
                                filename,
                                unidecode.unidecode(series_title),
                                unidecode.unidecode(prog_title),
                                unidecode.unidecode(ep_num),
                                checksum,
                                mxf_checksum,
                                'CHECKSUM DOES NOT MATCH!'
                                )
                        )
                except AttributeError:
                    append_csv(
                        csv_report,
                        (
                            os.path.basename(os.path.dirname(uuid_dir)),
                            source_oe,
                            accession_number_id,
                            dicto[os.path.basename(os.path.dirname(uuid_dir))][0],
                            dicto[os.path.basename(os.path.dirname(uuid_dir))][1],
                            filename,
                            'error',
                            'error',
                            'error',
                            'error',
                            'error',
                            'CHECKSUM DOES NOT MATCH!'
                            )
                        )
    print("Report complete - Time elaspsed : ", datetime.now() - startTime)


if __name__ == '__main__':
    main()