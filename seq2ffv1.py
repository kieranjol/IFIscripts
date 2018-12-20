#!/usr/bin/env python

'''
Usage: seq2ffv1.py source_parent_directory output_directory
The script will look through all subdirectories beneath the
source_parent_directory for a DPX or image sequence.
The script will then:
Create folder structure for each image sequence in
your designated output_directory.
Create framemd5 values of the source sequence
Transcode to a single FFV1 in Matroska file
Create framemd5 values for the FFV1 in Matroska file
Verify losslessness
(There will most likely be a warning about pixel aspect ratio
- https://www.ietf.org/mail-archive/web/cellar/current/msg00739.html)

the rawcooked option should just replace the ffmpeg encode with rawcooked
then perform the same losslessness checks via framemd5.
however there should be a whole file md5 option, and a basic test
that just tests the md5s of the first 24 frames.
'''
import subprocess
import os
import argparse
import tempfile
import shutil
import time
import ififuncs
import sipcreator
import makezip

def short_test(images, args):
    '''
    Perform a test on the first 24 frames that will encode via Rawcooked,
    then decode back to the original form,
    and the whole file checksums of the original 24 frames
    and the restored 24 frames are compared.
    maybe all that needs to happen is that 24 frames are copied to a temp
    location, then the functions run, and use ififuncs to check the sums
    '''
    temp_uuid = ififuncs.create_uuid()
    temp_dir = os.path.join(tempfile.gettempdir(), temp_uuid)
    os.makedirs(temp_dir)
    for image in images[:24]:
        full_path = os.path.join(args.i, image)
        shutil.copy(full_path, temp_dir)
    mkv_uuid = ififuncs.create_uuid()
    mkv_file = os.path.join(tempfile.gettempdir(), mkv_uuid + '.mkv')
    subprocess.call(['rawcooked', temp_dir, '-o', mkv_file])
    converted_manifest = os.path.join(temp_dir, '123.md5')
    ififuncs.hashlib_manifest(temp_dir, converted_manifest, temp_dir)
    subprocess.call(['rawcooked', mkv_file])
    rawcooked_dir = mkv_file + '.RAWcooked'
    restored_dir = os.path.join(rawcooked_dir, temp_uuid)
    restored_manifest = os.path.join(restored_dir, '456.md5')
    ififuncs.hashlib_manifest(restored_dir, restored_manifest, restored_dir)
    ififuncs.diff_textfiles(converted_manifest, restored_manifest)

def reversibility_verification(ffv1_mkv, source_manifest, reversibility_dir):
    '''
    Restore the MKV back to DPX, create a checksum, and compare to source DPX
    checksums.
    Return a value of lossy or lossless.
    '''
    temp_uuid = ififuncs.create_uuid()
    temp_dir = os.path.join(reversibility_dir, temp_uuid)
    os.makedirs(temp_dir)
    subprocess.call(['rawcooked', ffv1_mkv, '-o', temp_dir])
    converted_manifest = os.path.join(temp_dir, '123.md5')
    ififuncs.hashlib_manifest(temp_dir, converted_manifest, temp_dir)
    judgement = ififuncs.diff_textfiles(converted_manifest, source_manifest)
    print(' - Deleting temp directory %s' % temp_dir)
    shutil.rmtree(temp_dir)
    return judgement
def run_loop(args):
    '''
    This will only process one sequence. Batch processing will come later.
    '''
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
    verdicts = []
    for source_directory, _, _ in os.walk(args.i):
        output_dirname = args.o
        images = ififuncs.get_image_sequence_files(source_directory)
        if images == 'none':
            continue
        (ffmpeg_friendly_name,
         _, root_filename, _) = ififuncs.parse_image_sequence(images)
        short_test(images, args)
        source_abspath = os.path.join(source_directory, ffmpeg_friendly_name)
        judgement = make_ffv1(
            source_abspath,
            output_dirname,
            args,
            log_name_source,
            user,
            object_entry
        )
        judgement, sipcreator_log, sipcreator_manifest = judgement
        verdicts.append([root_filename, judgement])
        for verdict in verdicts:
            print("%-*s   : %s" % (50, args.i, verdict[1]))
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
        source_abspath,
        output_dirname,
        args,
        log_name_source,
        user,
        object_entry
    ):
    '''
    This launches the image sequence to FFV1/Matroska process
    as well as framemd5 losslessness verification.
    '''
    uuid = ififuncs.create_uuid()
    files_to_move = []
    temp_dir = tempfile.gettempdir()
    ffv1_path = os.path.join(output_dirname, uuid + '.mkv')
    # Just perform framemd5 at this stage
    rawcooked_logfile = os.path.join(
        temp_dir, '%s_rawcooked.log' % uuid
    )
    normalisation_tool = ififuncs.get_rawcooked_version()
    files_to_move.append(rawcooked_logfile)
    rawcooked_logfile = "\'" + rawcooked_logfile + "\'"
    env_dict = ififuncs.set_environment(rawcooked_logfile)
    rawcooked_cmd = ['rawcooked', os.path.dirname(source_abspath), '--check', 'full', '-o', ffv1_path]
    if args.audio:
        rawcooked_cmd.extend([args.audio, '-c:a', 'copy'])
    ffv12dpx = (rawcooked_cmd)
    print(ffv12dpx)
    if args.zip:
        uuid = ififuncs.create_uuid()
        # ugly hack until i recfactor. this is the zip_path, not ffv1_path
        ffv1_path = os.path.join(output_dirname, uuid + '.zip')
        ififuncs.generate_log(
            log_name_source,
            'EVENT = packing, status=started, eventType=packing, agentName=makezip.py, eventDetail=Source object to be packed=%s' % os.path.dirname(source_abspath)
        )
        makezip_judgement = makezip.main([
            '-i', os.path.dirname(source_abspath),
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
    sip_dir = os.path.join(
        os.path.dirname(ffv1_path), os.path.join(object_entry, uuid)
    )
    inputxml, inputtracexml, dfxml = ififuncs.generate_mediainfo_xmls(os.path.dirname(source_abspath), args.o, uuid, log_name_source)
    source_manifest = os.path.join(
        args.o,
        os.path.basename(args.i) + '_manifest-md5.txt'
    )
    ififuncs.generate_log(
        log_name_source,
        'EVENT = message digest calculation, status=started, eventType=messageDigestCalculation, agentName=hashlib, eventDetail=MD5 checksum of source files'
    )
    ififuncs.hashlib_manifest(args.i, source_manifest, os.path.dirname(args.i))
    ififuncs.generate_log(
        log_name_source,
        'EVENT = message digest calculation, status=finished, eventType=messageDigestCalculation, agentName=hashlib, eventDetail=MD5 checksum of source files'
    )
    ififuncs.generate_log(
        log_name_source,
        'EVENT = losslessness verification, status=started, eventType=messageDigestCalculation, agentName=%s, eventDetail=Full reversibility of %s back to its original form, followed by checksum verification using %s ' % (normalisation_tool, ffv1_path, source_manifest)
    )
    if args.reversibility_dir:
        reversibility_dir = args.reversibility_dir
    else:
        reversibility_dir = args.o
    judgement = reversibility_verification(ffv1_path, source_manifest, reversibility_dir)
    ififuncs.generate_log(
        log_name_source,
        'EVENT = losslessness verification, status=finished, eventType=messageDigestCalculation, agentName=%s, eventDetail=Full reversibilty of %s back to its original form, followed by checksum verification using %s , eventOutcome=%s' % (normalisation_tool, ffv1_path, source_manifest, judgement)
    )
    supplement_cmd = ['-supplement', inputxml, inputtracexml, dfxml, source_manifest]
    sipcreator_cmd = [
        '-i',
        ffv1_path,
        '-u',
        uuid,
        '-quiet',
        '-move',
        '-user',
        user,
        '-oe',
        object_entry,
        '-o', os.path.dirname(ffv1_path)
    ]
    sipcreator_cmd.extend(supplement_cmd)
    sipcreator_log, sipcreator_manifest = sipcreator.main(sipcreator_cmd)
    logs_dir = os.path.join(sip_dir, 'logs')
    metadata_dir = os.path.join(sip_dir, 'metadata')

    for files in files_to_move:
        if files.endswith('.log'):
            shutil.move(files, logs_dir)
            ififuncs.manifest_update(
                sipcreator_manifest,
                os.path.join(logs_dir, os.path.basename(files))
            )
        elif files.endswith('.framemd5'):
            shutil.move(files, metadata_dir)
            ififuncs.manifest_update(
                sipcreator_manifest,
                os.path.join(metadata_dir, os.path.basename(files))
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
        '-audio',
        help='Full path to audio file.')
    parser.add_argument(
        '-reversibility_dir',
        help='This argument requires the full path of the location that you want to use for the reversibility directory. By default, seq2ffv1 will use your output dir for storing the temporary reversibility files.')
    parser.add_argument(
        '-zip',
        help='Use makezip.py to generate an uncompressed zip file', action='store_true'
    )
    args = parser.parse_args()
    return args

def main():
    '''
    Overly long main function that does most of the heavy lifting.
    '''
    args = setup()
    run_loop(args)


if __name__ == '__main__':
    main()
