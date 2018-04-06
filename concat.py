#!/usr/bin/env python
'''
Concatenates video files using FFmpeg stream copy for general use but
particularly for XDCAM workflows in the IFI Irish Film Institute.
Uses mkvpropedit to insert chapter markers for each source file.
Optionally wraps the file into a package structure with checksum manifests.

Written by Kieran O'Leary.
'''
import sys
import subprocess
import os
import argparse
import time
import shutil
import sipcreator
import ififuncs

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Concatenate video files using ffmpeg stream copy'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        '-i', nargs='+',
        help='full path of input directory', required=True
    )
    parser.add_argument(
        '-o', '-output',
        help='full path of output directory', required=True
    )
    parser.add_argument(
        '-r', '-recursive',
        help='recursively process all files in subdirectories. This could be potentially a disaster - so use with caution or with XDCAM', action='store_true'
    )
    parser.add_argument(
        '--no-sip',
        help='Do not run sipcreator.py on the resulting file.', action='store_true'
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.')
    parser.add_argument(
        '-oe',
        help='Enter the Object Entry number for the representation.SIP will be placed in a folder with this name.'
    )
    parser.add_argument(
        '-mov',
        help='Uses MOV container instead of Matroska', action='store_true'
    )
    parser.add_argument(
        '-nochapters',
        help='Skips the mkvpropedit chapter creation function', action='store_true'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def ffmpeg_concat(concat_file, args, uuid, container):
    '''
    Launch the actual ffmpeg concatenation command.
    '''
    fmd5_logfile = os.path.join(args.o, '%s_concat.log' % uuid).replace('\\', '\\\\').replace(':', '\:')
    fmd5_env_dict = ififuncs.set_environment(fmd5_logfile)
    print fmd5_logfile
    print fmd5_env_dict
    cmd = [
        'ffmpeg', '-report', '-f', 'concat', '-safe', '0',
        '-i', concat_file,
        '-c', 'copy', '-map', '0:v', '-map', '0:a?',
        os.path.join(args.o, '%s.%s' % (uuid, container)),
        '-f', 'md5', '-map', '0:v', '-map', '0:a?','-c', 'copy',  '-'
    ]
    print cmd
    source_bitstream_md5 = subprocess.check_output(
        cmd, env=fmd5_env_dict
    )
    return source_bitstream_md5.rstrip(), fmd5_logfile.replace('\\\\', '\\').replace('\:', ':')

def recursive_file_list(video_files):
    '''
    Recursively searches through directories for AV files and adds to a list.
    '''
    # check if all inputs are actually directories
    recursive_list = []
    for directory in video_files:
        if not os.path.isdir(directory):
            print 'You have selected the recursive option, but not all of your inputs are directories.'
            sys.exit()
        else:
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    if filename.endswith(('.MP4', '.mp4', '.mov', '.mkv', '.mxf', 'MXF')):
                        recursive_list.append(os.path.join(root, filename))
    print recursive_list
    return recursive_list

def make_chapters(video_files):
    '''
    Use mkvpropedit to insert chapter markers for each source video.
    Each chapter's name will reflect the source filename of each clip.
    '''
    millis = ififuncs.get_milliseconds(video_files[0])
    timestamp = ififuncs.convert_millis(int(millis))
    chapter_list = [['00:00:00.000', os.path.basename(video_files[0])], [timestamp, os.path.basename(video_files[1])]]
    count = 2
    for video in video_files[1:]:
        millis += ififuncs.get_milliseconds(video)
        timestamp = ififuncs.convert_millis(int(millis))
        if count == len(video_files):
            continue
        else:
            chapter_list.append([timestamp, os.path.basename(video_files[count])])
        count+=1
    chapter_counter = 1
    # uh use a real path/filename.
    with open('chapters.txt', 'wb') as fo:
        for i in chapter_list:
            fo.write('CHAPTER%s=%s\nCHAPTER%sNAME=%s\n' % (str(chapter_counter).zfill(2), i[0], str(chapter_counter).zfill(2), i[1]))
            chapter_counter += 1


def main(args_):
    '''
    Launches the functions that prepare and execute the concatenation.
    '''
    uuid = ififuncs.create_uuid()
    args = parse_args(args_)
    print args
    log_name_source = os.path.join(args.o, '%s_concat_log.log' % time.strftime("_%Y_%m_%dT%H_%M_%S"))
    ififuncs.generate_log(log_name_source, 'concat.py started.')
    if args.mov:
        container = 'mov'
    else:
        container = 'mkv'
    ififuncs.generate_log(
        log_name_source,
        'eventDetail=concat.py %s' % ififuncs.get_script_version('concat.py'))
    ififuncs.generate_log(
        log_name_source,
        'Command line arguments: %s' % args
    )
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
    source_uuid_check = ''
    if os.path.isfile(args.i[0]):
        source_uuid = ififuncs.get_source_uuid()
    elif os.path.isdir(args.i[0]):
        source_uuid_check = ififuncs.check_for_uuid(args)
    if source_uuid_check == False:
        source_uuid = ififuncs.get_source_uuid()
    else: source_uuid = source_uuid_check
    ififuncs.generate_log(
        log_name_source,
        'Relationship, derivation, has source=%s' % source_uuid
    )
    video_files = args.i
    concat_file = ififuncs.get_temp_concat('concat_stuff')
    ififuncs.generate_log(
        log_name_source,
        'concatenation file=%s' % concat_file)
    if args.r:
        video_files = recursive_file_list(video_files)
    video_files = ififuncs.sanitise_filenames(video_files)
    for source_files in video_files:
        ififuncs.generate_log(
            log_name_source,
            'source_files = %s' % source_files)
    make_chapters(video_files)
    ififuncs.concat_textfile(video_files, concat_file)
    ififuncs.generate_log(
        log_name_source,
        'EVENT = Concatenation, status=started, eventType=Creation, agentName=ffmpeg, eventDetail=Source media concatenated into a single file output=%s' % os.path.join(args.o, '%s.%s' % (uuid, container)))
    source_bitstream_md5, fmd5_logfile = ffmpeg_concat(concat_file, args, uuid, container)
    output_file = os.path.join(args.o, '%s.%s' % (uuid, container))
    ififuncs.generate_log(
        log_name_source,
        'EVENT = Concatenation, status=finished, eventType=Creation, agentName=ffmpeg, eventDetail=Source media concatenated into a single file output=%s' % os.path.join(args.o, '%s.%s' % (uuid, container)))
    ififuncs.generate_log(
        log_name_source,
        'EVENT = losslessness verification, status=started, eventType=messageDigestCalculation, agentName=ffmpeg, eventDetail=MD5s of AV streams of output file generated for validation')
    validation_logfile = os.path.join(args.o, '%s_validation.log' % uuid).replace('\\', '\\\\').replace(':', '\:')
    validation_env_dict = ififuncs.set_environment(validation_logfile)
    output_bitstream_md5 = subprocess.check_output([
        'ffmpeg', '-report',
        '-i', output_file,
        '-f', 'md5', '-map', '0:v', '-map', '0:a?', '-c', 'copy', '-'
    ], env=validation_env_dict).rstrip()
    ififuncs.generate_log(
        log_name_source,
        'EVENT = losslessness verification, status=finished, eventType=messageDigestCalculation, agentName=ffmpeg, eventDetail=MD5s of AV streams of output file generated for validation')
    if source_bitstream_md5 == output_bitstream_md5:
        print 'process appears to be lossless'
        print source_bitstream_md5, output_bitstream_md5
        ififuncs.generate_log(
        log_name_source,
        'EVENT = losslessness verification, eventOutcome=pass')
    else:
        print 'something went wrong - not lossless!'
        print source_bitstream_md5,output_bitstream_md5
        ififuncs.generate_log(
        log_name_source,
        'EVENT = losslessness verification, eventOutcome=fail')
    if args.nochapters != True:
        subprocess.call(['mkvpropedit', output_file, '-c', 'chapters.txt'])
        ififuncs.generate_log(
            log_name_source,
            'EVENT = eventType=modification, agentName=mkvpropedit, eventDetail=Chapters added to file detailing start point of source clips.')
        ififuncs.concat_textfile(video_files, concat_file)
        with open(log_name_source, 'r') as concat_log:
            concat_lines = concat_log.readlines()
    if not args.no_sip:
        sipcreator_log, sipcreator_manifest = sipcreator.main(['-i', output_file, '-u', uuid, '-oe', object_entry, '-user', user, '-o', args.o])
        shutil.move(fmd5_logfile, os.path.dirname(sipcreator_log))
        shutil.move(validation_logfile.replace('\\\\', '\\').replace('\:', ':'), os.path.dirname(sipcreator_log))
        logs_dir = os.path.dirname(sipcreator_log)
        ififuncs.manifest_update(sipcreator_manifest, os.path.join(logs_dir, os.path.basename(fmd5_logfile)))
        ififuncs.manifest_update(sipcreator_manifest, os.path.join(logs_dir,(os.path.basename(validation_logfile.replace('\\\\', '\\').replace('\:', ':')))))
        ififuncs.merge_logs(log_name_source, sipcreator_log, sipcreator_manifest)

if __name__ == '__main__':
    main(sys.argv[1:])
