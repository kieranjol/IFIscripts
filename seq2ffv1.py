#!/usr/bin/env python3

'''
Usage: seq2ffv1.py source_parent_directory output_directory
The script will fnd a single reel, multi-reel (with or without sidecar WAV)
image sequence beneath the source_parent_directory.
The script will then:
* Create a folder structure for each image sequence in
your designated output_directory.
* Transcode to a single FFV1 in Matroska file, or multiple Matroska files
for multi-reel films.
* Verify losslessness by fully reversing the FFV1/MKV file and validating
the source checksums.
'''
import subprocess
import os
import argparse
import tempfile
import shutil
import time
import sys
import ififuncs
import sipcreator
import makezip
import deletefiles

def short_test(images):
    '''
    Perform a test on the first 24 frames that will encode via Rawcooked,
    then decode back to the original form,
    and the whole file checksums of the original 24 frames
    and the restored 24 frames are compared.
    '''
    temp_uuid = ififuncs.create_uuid()
    temp_dir = os.path.join(tempfile.gettempdir(), temp_uuid)
    os.makedirs(temp_dir)
    # Only analyse the first 24 frames.
    for image in sorted(os.listdir(images))[:24]:
        full_path = os.path.join(images, image)
        shutil.copy(full_path, temp_dir)
    mkv_uuid = ififuncs.create_uuid()
    mkv_file = os.path.join(tempfile.gettempdir(), mkv_uuid + '.mkv')
    subprocess.call(['rawcooked', temp_dir, '-c:a', 'copy', '-o', mkv_file])
    converted_manifest = os.path.join(temp_dir, '123.md5')
    ififuncs.hashlib_manifest(temp_dir, converted_manifest, temp_dir)
    subprocess.call(['rawcooked', mkv_file])
    rawcooked_dir = mkv_file + '.RAWcooked'
    restored_dir = os.path.join(rawcooked_dir, temp_uuid)
    restored_manifest = os.path.join(restored_dir, '456.md5')
    ififuncs.hashlib_manifest(restored_dir, restored_manifest, restored_dir)
    judgement = ififuncs.diff_textfiles(converted_manifest, restored_manifest)
    print((' - Deleting temp directory %s' % temp_dir))
    try:
        shutil.rmtree(temp_dir)
    except WindowsError:
        print('Sorry, we do not have permission to delete these files')
    print((' - Deleting temp reversibility directory %s' % rawcooked_dir))
    try:
        shutil.rmtree(rawcooked_dir)
    except WindowsError:
        print('Sorry, we do not have permission to delete these files')
    print((' - Deleting temp FFV1/MKV %s' % mkv_file))
    os.remove(mkv_file)
    return judgement

def reversibility_verification(objects, source_manifest, reversibility_dir):
    '''
    Restore the MKV back to DPX, create a checksum, and compare to source DPX
    checksums.
    Return a value of lossy or lossless.
    '''
    temp_uuid = ififuncs.create_uuid()
    temp_dir = os.path.join(reversibility_dir, temp_uuid)
    os.makedirs(temp_dir)
    for ffv1_mkv in objects:
        subprocess.call(['rawcooked', ffv1_mkv, '-o', temp_dir])
    converted_manifest = os.path.join(temp_dir, '123.md5')
    ififuncs.hashlib_manifest(temp_dir, converted_manifest, temp_dir)
    judgement = ififuncs.diff_textfiles(converted_manifest, source_manifest)
    print((' - Deleting temp directory %s' % temp_dir))
    try:
        shutil.rmtree(temp_dir)
    except WindowsError:
        print('Unable to delete temp directory, sorry!')
    return judgement

def run_loop(args):
    '''
    This will only process one sequence. Batch processing will come later.
    '''
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    if args.user:
        user = args.user
    else:
        user = ififuncs.get_user()
    object_entry = ififuncs.get_object_entry()
    log_name_source = os.path.join(
        args.o, '%s_seq2ffv1_log.log' % time.strftime("_%Y_%m_%dT%H_%M_%S")
    )
    ififuncs.generate_log(log_name_source, 'seq2ffv1.py started.')
    ififuncs.generate_log(
        log_name_source,
        'eventDetail=seq2ffv1.py %s' % ififuncs.get_script_version('seq2ffv1.py'))
    ififuncs.generate_log(
        log_name_source,
        'Command line arguments: %s' % args
    )
    ififuncs.generate_log(
        log_name_source,
        'EVENT = agentName=%s' % user
    )
    uuid = ififuncs.create_uuid()
    verdicts = []
    multi_reeler = False
    source_directory = args.i
    images = ififuncs.get_image_sequence_files(source_directory)
    if images == 'none':
        print('no images found in directory - checking for multi-reel sequence')
        images = ififuncs.check_multi_reel(source_directory)
        multi_reeler = True
        if images == 'none':
            sys.exit()
    # this is checking for a single reeler.
    else:
        images = [source_directory]
    reel_number = 1
    objects = []
    short_test_reports = []
    rawcooked_logfiles = []
    for reel in images:
        short_test_reports.append(short_test(reel))
        for i in short_test_reports:
            print((' - 24 frame reversibility test for %s is %s' % (os.path.basename(reel), i)))
            if i == 'lossy':
                print('It appears that this sequence is not reversible - exiting')
                sys.exit()
        time.sleep(2)
        # check for a/b rolls
        if reel[-1] in ['a', 'b']:
            reel_number = reel[-2]
        ffv1_path, source_abspath, args, log_name_source, normalisation_tool, rawcooked_logfile = make_ffv1(
            reel,
            args,
            log_name_source,
            reel_number,
            uuid,
            multi_reeler
        )
        objects.append(ffv1_path)
        rawcooked_logfiles.append(rawcooked_logfile)
        # check for a/b rolls
        if not reel[-1] in ['a', 'b']:
            reel_number += 1
    judgement = package(objects, object_entry, uuid, source_abspath, args, log_name_source, normalisation_tool, user, rawcooked_logfiles, multi_reeler, current_dir)
    judgement, sipcreator_log, sipcreator_manifest = judgement
    verdicts.append([source_directory, judgement])
    for verdict in verdicts:
        print(("%-*s   : %s" % (50, args.i, verdict[1])))
    ififuncs.generate_log(log_name_source, 'seq2ffv1.py finished.')
    ififuncs.merge_logs(log_name_source, sipcreator_log, sipcreator_manifest)


def verify_losslessness(source_textfile, ffv1_md5):
    '''
    Compares two framemd5 documents in order to determine losslessness.
    '''
    judgement = ififuncs.diff_textfiles(source_textfile, ffv1_md5)
    checksum_mismatches = []
    with open(source_textfile) as source_md5_object:
        with open(ffv1_md5) as ffv1_md5_object:
            for (line1), (line2) in zip(
                    ififuncs.read_lines(
                        source_md5_object
                    ), ififuncs.read_lines(ffv1_md5_object)
            ):
                if line1 != line2:
                    if 'sar' in line1:
                        checksum_mismatches = ['sar']
                    else:
                        checksum_mismatches.append(1)
    return judgement

def make_ffv1(
        reel,
        args,
        log_name_source,
        reel_number,
        uuid,
        multi_reeler
    ):
    '''
    This launches the image sequence to FFV1/Matroska process
    as well as framemd5 losslessness verification.
    '''
    output_dirname = args.o
    if multi_reeler:
        if reel[-1] in ['a', 'b']:    
            mkv_basename = uuid + '_reel%s%s.mkv' % (str(reel_number), reel[-1])
        else:
            mkv_basename = uuid + '_reel%s.mkv' % str(reel_number)
    else:
        mkv_basename = uuid + '.mkv'
    ffv1_path = os.path.join(output_dirname, mkv_basename)
    rawcooked_logfile = os.path.join(
        args.o, '%s_rawcooked.log' % mkv_basename
    )
    normalisation_tool = ififuncs.get_rawcooked_version()
    rawcooked_logfile = "\'" + rawcooked_logfile + "\'"
    env_dict = ififuncs.set_environment(rawcooked_logfile)
    rawcooked_cmd = ['rawcooked', reel, '--check', 'full', '-c:a', 'copy', '-o', ffv1_path]
    if args.framerate:
        rawcooked_cmd.extend(['-framerate', args.framerate])
    ffv12dpx = (rawcooked_cmd)
    print(ffv12dpx)
    if args.zip:
        uuid = ififuncs.create_uuid()
        # ugly hack until i recfactor. this is the zip_path, not ffv1_path
        ffv1_path = os.path.join(output_dirname, uuid + '.zip')
        ififuncs.generate_log(
            log_name_source,
            'EVENT = packing, status=started, eventType=packing, agentName=makezip.py, eventDetail=Source object to be packed=%s' % reel
        )
        makezip_judgement = makezip.main([
            '-i', reel,
            '-o', output_dirname,
            '-basename', os.path.basename(ffv1_path)
        ])[0]
        ififuncs.generate_log(
            log_name_source,
            'EVENT = packing, status=finished, eventType=packing, agentName=makezip.py, Source object packed into=%s' % ffv1_path
        )
        if makezip_judgement is None:
            judgement = 'lossless'
        else:
            judgement = makezip_judgement
        ififuncs.generate_log(
            log_name_source,
            'EVENT = losslessness verification, status=finished, eventType=messageDigestCalculation, agentName=makezip.py, eventDetail=embedded crc32 checksum validation, eventOutcome=%s' % judgement
        )
    if not args.zip:
        ififuncs.generate_log(
            log_name_source,
            'EVENT = normalisation, status=started, eventType=Creation, agentName=%s, eventDetail=Image sequence normalised to FFV1 in a Matroska container'
            % normalisation_tool
        )
        subprocess.call(ffv12dpx, env=env_dict)
        ififuncs.generate_log(
            log_name_source,
            'EVENT = normalisation, status=finshed, eventType=Creation, agentName=%s, eventDetail=Image sequence normalised to FFV1 in a Matroska container'
            % normalisation_tool
        )
    return ffv1_path, reel, args, log_name_source, normalisation_tool, rawcooked_logfile

def package(objects, object_entry, uuid, source_abspath, args, log_name_source, normalisation_tool, user, rawcooked_logfiles, multi_reeler, current_dir):
    '''
    Package the MKV using sipcreator.py
    '''
    sip_dir = os.path.join(
        args.o, os.path.join(object_entry, uuid)
    )
    inputxml, inputtracexml, dfxml = ififuncs.generate_mediainfo_xmls(source_abspath, args.o, uuid, log_name_source)
    source_manifest = os.path.join(
        args.o,
        os.path.basename(args.i) + '_manifest-md5.txt'
    )
    ififuncs.generate_log(
        log_name_source,
        'EVENT = message digest calculation, status=started, eventType=messageDigestCalculation, agentName=hashlib, eventDetail=MD5 checksum of source files'
    )
    if multi_reeler:
        ififuncs.hashlib_manifest(args.i, source_manifest, args.i)
    else:
        ififuncs.hashlib_manifest(args.i, source_manifest, os.path.dirname(args.i))
    ififuncs.generate_log(
        log_name_source,
        'EVENT = message digest calculation, status=finished, eventType=messageDigestCalculation, agentName=hashlib, eventDetail=MD5 checksum of source files'
    )
    ififuncs.generate_log(
        log_name_source,
        'EVENT = losslessness verification, status=started, eventType=messageDigestCalculation, agentName=%s, eventDetail=Full reversibility of %s back to its original form, followed by checksum verification using %s ' % (normalisation_tool, objects, source_manifest)
    )
    if args.reversibility_dir:
        reversibility_dir = args.reversibility_dir
    else:
        reversibility_dir = args.o

    judgement = reversibility_verification(objects, source_manifest, reversibility_dir)
    ififuncs.generate_log(
        log_name_source,
        'EVENT = losslessness verification, status=finished, eventType=messageDigestCalculation, agentName=%s, eventDetail=Full reversibilty of %s back to its original form, followed by checksum verification using %s , eventOutcome=%s' % (normalisation_tool, objects, source_manifest, judgement)
    )
    supplement_cmd = ['-supplement', inputxml, inputtracexml, dfxml, source_manifest]
    if args.supplement:
        supplement_cmd.extend(args.supplement)
    sipcreator_cmd = [
        '-i',
    ]
    for i in objects:
        sipcreator_cmd.append(i)
    sipcreator_cmd += [
        '-u',
        uuid,
        '-quiet',
        '-move',
        '-user',
        user,
        '-oe',
        object_entry,
        '-o', args.o
    ]
    sipcreator_cmd.extend(supplement_cmd)
    sipcreator_log, sipcreator_manifest = sipcreator.main(sipcreator_cmd)
    logs_dir = os.path.join(sip_dir, 'logs')
    for files in os.listdir(logs_dir):
        if files.endswith('.md5'):
            deletefiles.main(['-i', os.path.join(logs_dir, files), '-uuid_path', sip_dir, '-user', user])
    for rawcooked_logfile in rawcooked_logfiles:
        rawcooked_logfile = rawcooked_logfile.replace('\'', '')
        shutil.move(rawcooked_logfile, logs_dir)
        ififuncs.manifest_update(
            sipcreator_manifest,
            os.path.join(logs_dir, os.path.basename(rawcooked_logfile))
        )
    metadata_dir = os.path.join(sip_dir, 'metadata')
    os.chdir(current_dir)
    shutil.copy(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'film_scan_aip_documentation.txt'), metadata_dir)
    ififuncs.manifest_update(
        sipcreator_manifest,
        os.path.join(metadata_dir, 'film_scan_aip_documentation.txt')
    )
    os.remove(dfxml)
    os.remove(inputtracexml)
    os.remove(inputxml)
    return judgement, sipcreator_log, sipcreator_manifest

def setup():
    '''
    Sets up a lot of the variables and filepaths.
    '''
    parser = argparse.ArgumentParser(description='Transcode all DPX or TIFF'
                                     ' image sequence in the subfolders of your'
                                     ' source directory to FFV1 Version 3'
                                     ' in a Matroska Container.'
                                     ' Written by Kieran O\'Leary.')
    parser.add_argument(
        '-i',
        help='Input directory'
    )
    parser.add_argument(
        '-o',
        help='Destination directory'
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.')
    parser.add_argument(
        '-reversibility_dir',
        help='This argument requires the full path of the location that you want to use for the reversibility directory. By default, seq2ffv1 will use your output dir for storing the temporary reversibility files.')
    parser.add_argument(
        '-framerate',
        help='This argument triggers the -framerate option in rawcooked and allows you to override the default fps value, eg -framerate 16')
    parser.add_argument(
        '-zip',
        help='Use makezip.py to generate an uncompressed zip file', action='store_true'
    )
    parser.add_argument(
        '-supplement', nargs='+',
        help='Enter the full path of files or folders that are to be added to the supplemental subfolder within the metadata folder. Use this for information that supplements your preservation objects but is not to be included in the objects folder.'
    )
    args = parser.parse_args()
    return args

def main():
    '''
    Overly long main function that does most of the heavy lifting.
    '''
    ififuncs.check_existence(['rawcooked', 'ffmpeg'])
    args = setup()
    run_loop(args)

if __name__ == '__main__':
    main()
