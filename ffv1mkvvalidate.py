#!/usr/bin/env python
'''
Runs mediaconch on FFV1/MKV files.
The process will validate the files against the FFV1/MKV/PCM standards.
'''
import os
import subprocess
import sys
import time
import argparse
from lxml import etree
import ififuncs


def logname_check(basename, logs_dir):
    '''
    Currently we have a few different logname patterns in our packages.
    This attempts to return the appropriate one.
    '''
    makeffv1_logfile = os.path.join(
        logs_dir, basename +'.mov_log.log')
    generic_logfile = os.path.join(
        logs_dir, basename +'_log.log')
    mxf_logfile = os.path.join(
        logs_dir, basename +'.mxf_log.log')
    sipcreator_logfile = os.path.join(
        logs_dir, basename + '_sip_log.log')
    mkv_log = os.path.join(
        logs_dir, basename +'.mkv_log.log')
    if os.path.isfile(makeffv1_logfile):
        return makeffv1_logfile
    if os.path.isfile(generic_logfile):
        return generic_logfile
    if os.path.isfile(mxf_logfile):
        return mxf_logfile
    if os.path.isfile(sipcreator_logfile):
        return sipcreator_logfile
    if os.path.isfile(mkv_log):
        return mkv_log


def log_results(manifest, log, parent_dir):
    '''
    Updates the existing log file. This is copy pasted from validate.py.
    Eventally, both functions should be merged and moved into ififuncs.
    '''
    updated_manifest = []
    basename = os.path.basename(manifest).replace('_manifest.md5', '')
    sip_dir = parent_dir
    logs_dir = os.path.join(sip_dir, 'logs')
    logname = logname_check(basename, logs_dir)
    logfile = os.path.join(logs_dir, logname)
    ififuncs.generate_log(
        log,
        'EVENT = Logs consolidation - Log from %s merged into %s' % (log, logfile)
    )
    if os.path.isfile(logfile):
        with open(log, 'r') as fo:
            validate_log = fo.readlines()
        with open(logfile, 'ab') as ba:
            for lines in validate_log:
                ba.write(lines)
    with open(manifest, 'r') as manifesto:
        manifest_lines = manifesto.readlines()
        for lines in manifest_lines:
            if os.path.basename(logname) in lines:
                lines = lines[:31].replace(lines[:31], ififuncs.hashlib_md5(logfile)) + lines[32:]
            updated_manifest.append(lines)
    with open(manifest, 'wb') as fo:
        for lines in updated_manifest:
            fo.write(lines)
def setup(full_path, user):
    '''
    Sets up filepaths for the rest of the script.
    This also checks if a mediaconch xml already exists.
    '''
    desktop_logs_dir = ififuncs.make_desktop_logs_dir()
    log_name_source_ = os.path.basename(full_path) + time.strftime("_%Y_%m_%dT%H_%M_%S")
    log_name_source = "%s/%s_mediaconch_validation.log" % (desktop_logs_dir, log_name_source_)
    filename = os.path.basename(full_path)
    object_dir = os.path.dirname(full_path)
    parent_dir = os.path.dirname(object_dir)
    sip_root = os.path.dirname(parent_dir)
    metadata_dir = os.path.join(parent_dir, 'metadata')
    manifest = os.path.join(
        sip_root, os.path.basename(parent_dir) + '_manifest.md5'
    )
    if not os.path.isfile(manifest):
        print 'manifest does not exist %s' % manifest
        return 'skipping'
    if os.path.isdir(metadata_dir):
        mediaconch_xmlfile_basename = '%s_mediaconch_validation.xml' % filename
        mediaconch_xmlfile = os.path.join(
            metadata_dir, mediaconch_xmlfile_basename
        )
        if os.path.isfile(mediaconch_xmlfile):
            print 'mediaconch xml already exists'
            return 'skipping'
    else:
        print 'no metadata directory found. Exiting.'
    return log_name_source, user, mediaconch_xmlfile, manifest, full_path, parent_dir


def launch_mediaconch(log_name_source, user, mediaconch_xmlfile, manifest, full_path):
    '''
    Run mediaconch on files.
    '''
    ififuncs.generate_log(
        log_name_source,
        'EVENT = ffv1mkvvalidate.py started'
    )
    ififuncs.generate_log(
        log_name_source,
        'agentName=%s' % user
    )
    ififuncs.generate_log(
        log_name_source,
        'eventDetail=ffv1mkvvalidate.py %s' % ififuncs.get_script_version('ffv1mkvvalidate.py')
    )
    mediaconch_version = subprocess.check_output(['mediaconch', '-v']).rstrip()
    ififuncs.generate_log(
        log_name_source,
        'agentName=mediaconch, agentversion=%s' % mediaconch_version
    )
    if not os.path.isfile(mediaconch_xmlfile):
        ififuncs.make_mediaconch(full_path, mediaconch_xmlfile)
        ififuncs.manifest_update(manifest, mediaconch_xmlfile)


def parse_mediaconch(mediaconch_xml):
    '''
    Parses the mediaconch implementation check report.
    Returns a dictionary containing the overview of the PASS/FAILs.
    '''
    mediaconch_xml_object = etree.parse(mediaconch_xml)
    mediaconch_namespace = mediaconch_xml_object.xpath('namespace-uri(.)')
    validation_outcome = mediaconch_xml_object.xpath(
        '/ns:MediaConch/ns:media/ns:implementationChecks',
        namespaces={'ns':mediaconch_namespace}
    )
    return validation_outcome[0].attrib

def parse_args():
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Recursively validates all MKV files using mediaconch'
        'Report is written in XML format to the metadata folder and'
        'manifests and logs are updated'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'input',
        help='full path of input directory. All mkv files will be processed.'
    )
    parsed_args = parser.parse_args()
    return parsed_args
def main():
    '''
    Launches the functions that will validate your FFV1/MKV files.
    '''
    args = parse_args()
    source = args.input
    user = ififuncs.get_user()
    for root, _, filenames in os.walk(source):
        for filename in filenames:
            if filename[0] != '.' and filename.endswith('.mkv'):
                if setup(os.path.join(root, filename), user) == 'skipping':
                    continue
                else:
                    log_name_source, user, mediaconch_xmlfile, manifest, full_path, parent_dir = setup(
                        os.path.join(root, filename), user
                    )
                    launch_mediaconch(
                        log_name_source, user, mediaconch_xmlfile, manifest, full_path,
                    )
                    validation_outcome = parse_mediaconch(mediaconch_xmlfile)
                    print str(validation_outcome)
                    if int(validation_outcome['fail_count']) > 0:
                        print 'Validation failed!'
                        event_outcome = 'fail'
                    elif int(validation_outcome['fail_count']) == 0:
                        print 'validation successful'
                        event_outcome = 'pass'
                    ififuncs.generate_log(
                        log_name_source,
                        'EVENT = eventType=validation, eventOutcome=%s, eventDetail=%s' % (
                            event_outcome, str(validation_outcome)
                        )
                    )
                    log_results(manifest, log_name_source, parent_dir)


if __name__ == '__main__':
    main()
