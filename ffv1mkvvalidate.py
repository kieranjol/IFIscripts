#!/usr/bin/env python
'''
Runs mediaconch on FFV1/MKV files.
The process will validate the files against the FFV1/MKV/PCM standards.
'''
import os
import subprocess
import sys
import time
from lxml import etree
import ififuncs

def log_results(manifest, log, parent_dir):
    '''
    Updates the existing log file. This is copy pasted from validate.py.
    Eventally, both functions should be merged and moved into ififuncs.
    '''
    updated_manifest = []
    basename = os.path.basename(manifest).replace('_manifest.md5', '')
    logname = basename + '.mov_log.log'
    sip_dir = parent_dir
    logs_dir = os.path.join(sip_dir, 'logs')
    logfile = os.path.join(logs_dir, logname)
    print logfile
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
            if logname in lines:
                lines = lines[:31].replace(lines[:31], ififuncs.hashlib_md5(logfile)) + lines[32:]
            updated_manifest.append(lines)
    with open(manifest, 'wb') as fo:
        for lines in updated_manifest:
            fo.write(lines)

def launch_mediaconch(source, user):
    '''
    Run mediaconch on files.
    '''
    desktop_logs_dir = ififuncs.make_desktop_logs_dir()
    log_name_source_ = os.path.basename(source) + time.strftime("_%Y_%m_%dT%H_%M_%S")
    log_name_source = "%s/%s_mediaconch_validation.log" % (desktop_logs_dir, log_name_source_)
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
    full_path = source
    filename = os.path.basename(full_path)
    object_dir = os.path.dirname(full_path)
    parent_dir = os.path.dirname(object_dir)
    sip_root = os.path.dirname(parent_dir)
    manifest = os.path.join(sip_root, os.path.basename(parent_dir) + '_manifest.md5')
    metadata_dir = os.path.join(parent_dir, 'metadata')
    if os.path.isdir(metadata_dir):
        mediaconch_xmlfile_basename = '%s_mediaconch_validation.xml' % filename
        mediaconch_xmlfile = os.path.join(metadata_dir, mediaconch_xmlfile_basename)
        if not os.path.isfile(mediaconch_xmlfile):
            mediaconch_cmd = [
                'mediaconch',
                '-fx',
                full_path
            ]
            print 'Mediaconch is analyzing %s' % full_path
            mediaconch_output = subprocess.check_output(mediaconch_cmd)
            with open(mediaconch_xmlfile, 'wb') as xmlfile:
                xmlfile.write(mediaconch_output)
            ififuncs.manifest_update(manifest, mediaconch_xmlfile)
        else:
            print 'mediaconch xml already exists'
    else:
        print 'no metadata directory found. Exiting.'
    return log_name_source, mediaconch_xmlfile, manifest, parent_dir

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


def main():
    '''
    Launches the functions that will validate your FFV1/MKV files.
    '''
    user = ififuncs.get_user()
    for root, _, filenames in os.walk(sys.argv[1]):
        for filename in filenames:
            if filename[0] != '.':
                if filename.endswith('.mkv'):
                    log_name_source, mediaconch_xmlfile, manifest, parent_dir = launch_mediaconch(
                        os.path.join(root, filename), user
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
                        'EVENT = eventType=validation, eventOutcome=%s, eventDetail=%s' % (event_outcome, str(validation_outcome))
                    )
                    log_results(manifest, log_name_source, parent_dir)


if __name__ == '__main__':
    main()


