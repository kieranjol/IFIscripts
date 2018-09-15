#!/usr/bin/env python
'''
Performs normalisation to FFV1/Matroska.
This performs a basic normalisation and does not enforce any folder structure.
This supercedes makeffv1 within our workflows. This is mostly because makeffv1 imposes a specific, outdated
folder structure, and it's best to let SIPCREATOR handle the folder structure and let normalise.py handle
the actual normalisation.
'''
import sys
import os
import subprocess
import argparse
import shutil
import time
import ififuncs
import sipcreator

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Performs normalisation to FFV1/Matroska.'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        '-i',
        help='full path of input file or directory', required=True
    )
    parser.add_argument(
        '-o', '-output',
        help='full path of output directory', required=True
    )
    parser.add_argument(
        '-sip',
        help='Run sipcreator.py on the resulting file.', action='store_true'
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.')
    parser.add_argument(
        '-oe',
        help='Enter the Object Entry number for the representation.SIP will be placed in a folder with this name.'
    )
    parser.add_argument(
        '-supplement', nargs='+',
        help='Enter the full path of files or folders that are to be added to the supplemental subfolder within the metadata folder. Use this for information that supplements your preservation objects but is not to be included in the objects folder.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def normalise_process(filename, output_folder):
    '''
    Begins the actual normalisation process using FFmpeg
    '''
    output_uuid = ififuncs.create_uuid()
    print(' - The following UUID has been generated: %s' % output_uuid)
    output = "%s/%s.mkv" % (
        output_folder, output_uuid
        )
    print(' - The normalised file will have this filename: %s' % output)
    fmd5 = "%s/%s_source.framemd5" % (
        output_folder, os.path.basename(filename)
        )
    print(' - Framemd5s for each frame of your input file will be stored in: %s' % fmd5)

    ffv1_logfile = os.path.join(output_folder, '%s_normalise.log' % output_uuid)
    print(' - The FFmpeg logfile for the transcode will be stored in: %s' % ffv1_logfile)
    print(' - FFmpeg will begin normalisation now.')
    ffv1_env_dict = ififuncs.set_environment(ffv1_logfile)
    ffv1_command = [
        'ffmpeg',
        '-i', filename,
        '-c:v', 'ffv1',         # Use FFv1 codec
        '-g', '1',              # Use intra-frame only aka ALL-I aka GOP=1
        '-level', '3',          # Use Version 3 of FFv1
        '-c:a', 'copy',         # Copy and paste audio bitsream with no transcoding
        '-map', '0',
        '-dn',
        '-report',
        '-slicecrc', '1',
        '-slices', '16',
    ]
    if ififuncs.check_for_fcp(filename) is True:
        print(' - A 720/576 file with no Pixel Aspect Ratio and scan type metadata has been detected.')
        ffv1_command += [
            '-vf',
            'setfield=tff, setdar=4/3'
            ]
        print(' - -vf setfield=tff, setdar=4/3 will be added to the FFmpeg command.')
        ffprobe_dict = ififuncs.get_ffprobe_dict(filename)
        # let's stipulate the colour metadata if not present for SD PAL material.
        if not ififuncs.get_colour_metadata(ffprobe_dict):
            ffv1_command += ['-color_primaries', 'bt470bg', '-color_trc', 'bt709', '-colorspace', 'bt470bg' ]
    ffv1_command += [
        output,
        '-f', 'framemd5', '-an',  # Create decoded md5 checksums for every frame of the input. -an ignores audio
        fmd5
        ]
    print(ffv1_command)
    subprocess.call(ffv1_command, env=ffv1_env_dict)
    return output, output_uuid, fmd5, ffv1_logfile

def verify_losslessness(output_folder, output, output_uuid, fmd5):
    '''
    Verify the losslessness of the process using framemd5.
    An additional metadata check should also occur.
    '''
    verdict = 'undeclared'
    fmd5_logfile = os.path.join(output_folder, '%s_framemd5.log' % output_uuid)
    fmd5ffv1 = "%s/%s.framemd5" % (output_folder, output_uuid)
    print(' - Framemd5s for each frame of your output file will be stored in: %s' % fmd5ffv1)
    fmd5_env_dict = ififuncs.set_environment(fmd5_logfile)
    print(' - FFmpeg will attempt to verify the losslessness of the normalisation by using Framemd5s.')
    fmd5_command = [
        'ffmpeg',    # Create decoded md5 checksums for every frame
        '-i', output,
        '-report',
        '-f', 'framemd5', '-an',
        fmd5ffv1
        ]
    print fmd5_command
    subprocess.call(fmd5_command, env=fmd5_env_dict)
    checksum_mismatches = ififuncs.diff_framemd5s(fmd5, fmd5ffv1)
    if len(checksum_mismatches) == 1:
        if checksum_mismatches[0] == 'sar':
            print('Image is lossless, but the Pixel Aspect Ratio is different than the source - this may have been intended.')
            verdict = 'Image is lossless, but the Pixel Aspect Ratio is different than the source - this may have been intended.'
        else:
            print 'not lossless'
            verdict = 'not lossless'
    elif len(checksum_mismatches) > 1:
        print 'not lossless'
        verdict = 'not lossless'
    elif len(checksum_mismatches) == 0:
        print 'YOUR FILES ARE LOSSLESS YOU SHOULD BE SO HAPPY!!!'
        verdict = 'lossless'
    return fmd5_logfile, fmd5ffv1, verdict

def main(args_):
    print('\n - Normalise.py started')
    args = parse_args(args_)
    print(args)
    source = args.i
    output_folder = args.o
    log_name_source = os.path.join(args.o, '%s_normalise_log.log' % time.strftime("_%Y_%m_%dT%H_%M_%S"))
    ififuncs.generate_log(log_name_source, 'normalise.py started.')
    ififuncs.generate_log(
        log_name_source,
        'Command line arguments: %s' % args
    )
    if args.sip:
        if args.user:
            user = args.user
        else:
            user = ififuncs.get_user()
        if args.oe:
            if args.oe[:2] != 'oe':
                print 'First two characters must be \'oe\' and last four characters must be four digits'
                object_entry = ififuncs.get_object_entry()
            elif len(args.oe[2:]) not in range(4, 6):
                print 'First two characters must be \'oe\' and last four characters must be four digits'
                object_entry = ififuncs.get_object_entry()
            elif not args.oe[2:].isdigit():
               object_entry = ififuncs.get_object_entry()
               print 'First two characters must be \'oe\' and last four characters must be four digits'
            else:
                object_entry = args.oe
        else:
            object_entry = ififuncs.get_object_entry()
        ififuncs.generate_log(
            log_name_source,
            'EVENT = agentName=%s' % user
        )
    file_list = ififuncs.get_video_files(source)
    for filename in file_list:
        print('\n - Processing: %s' % filename)
        ififuncs.generate_log(
            log_name_source,
            'EVENT = Normalization, status=started, eventType=Normalization, agentName=ffmpeg, eventDetail=Source object to be normalised=%s' % filename)
        output, output_uuid, fmd5, ffv1_logfile = normalise_process(filename, output_folder)
        ififuncs.generate_log(
            log_name_source,
            'EVENT = Normalization, status=finished, eventType=Normalization, agentName=ffmpeg, eventDetail=Source object normalised into=%s' % output)
        inputxml, inputtracexml = ififuncs.generate_mediainfo_xmls(filename, output_folder, output_uuid, log_name_source)
        fmd5_logfile, fmd5ffv1, verdict = verify_losslessness(output_folder, output, output_uuid, fmd5)
        ififuncs.generate_log(
            log_name_source,
            'EVENT = losslessness verification, status=finished, eventType=messageDigestCalculation, agentName=ffmpeg, eventDetail=MD5s of AV streams of output file generated for validation, eventOutcome=%s' % verdict)
        if args.sip:
            supplement_cmd = ['-supplement', inputxml, inputtracexml]
            sipcreator_cmd = ['-i', output, '-move', '-u', output_uuid, '-user', user, '-oe', object_entry, '-o', args.o]
            if args.supplement:
                supplement_cmd.extend(args.supplement)
            sipcreator_cmd.extend(supplement_cmd)
            sipcreator_log, sipcreator_manifest = sipcreator.main(sipcreator_cmd)
            metadata_dir  = os.path.join(os.path.dirname(os.path.dirname(sipcreator_log)), 'metadata')
            shutil.move(fmd5, metadata_dir)
            shutil.move(fmd5_logfile, os.path.dirname(sipcreator_log))
            shutil.move(fmd5ffv1, metadata_dir)
            shutil.move(ffv1_logfile.replace('\\\\', '\\').replace('\:', ':'), os.path.dirname(sipcreator_log))
            logs_dir = os.path.dirname(sipcreator_log)
            ififuncs.manifest_update(sipcreator_manifest, os.path.join(metadata_dir, os.path.basename(fmd5)))
            ififuncs.manifest_update(sipcreator_manifest, os.path.join(metadata_dir, os.path.basename(fmd5ffv1)))
            ififuncs.manifest_update(sipcreator_manifest, os.path.join(logs_dir, os.path.basename(ffv1_logfile.replace('\\\\', '\\').replace('\:', ':'))))
            ififuncs.manifest_update(sipcreator_manifest, os.path.join(logs_dir, os.path.basename(fmd5_logfile.replace('\\\\', '\\').replace('\:', ':'))))
            ififuncs.merge_logs(log_name_source, sipcreator_log, sipcreator_manifest)

if __name__ == '__main__':
    main(sys.argv[1:])
