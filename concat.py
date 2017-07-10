#!/usr/bin/env python
'''
Concatenates video files using ffmpeg stream copy
'''
import sys
import subprocess
import os
import argparse
import time
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
        '-s', '-sip',
        help='Run sipcreator.py on the resulting file.', action='store_true'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def ffmpeg_concat(concat_file, args, uuid):
    '''
    Launch the actual ffmpeg concatenation command
    '''
    cmd = [
        'ffmpeg', '-f', 'concat', '-safe', '0',
        '-i', concat_file,
        '-c', 'copy', '-map', '0:v', '-map', '0:a?',
        os.path.join(args.o, '%s.mkv' % uuid),
        '-f', 'md5', '-map', '0:v', '-map', '0:a?','-c', 'copy',  '-'
    ]
    print cmd
    source_bitstream_md5 = subprocess.check_output(
        cmd
    )
    return source_bitstream_md5.rstrip()

def recursive_file_list(video_files):
    '''
    Recursively search through directories for AV files and add to list.
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
                    if filename.endswith(('.MP4', '.mp4', '.mov', '.mkv', '.mxf')):
                        recursive_list.append(os.path.join(root, filename))
    print recursive_list
    return recursive_list

def make_chapters(video_files):
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
    log_name_source = os.path.join(args.o, '%s_concat_log.log' % time.strftime("_%Y_%m_%dT%H_%M_%S"))
    ififuncs.generate_log(log_name_source, 'concat.py started.')
    ififuncs.generate_log(
        log_name_source,
        'eventDetail=concat.py %s' % ififuncs.get_script_version('concat.py'))
    user = ififuncs.get_user()
    ififuncs.generate_log(
        log_name_source,
        'EVENT = agentName=%s' % user
    )
    source_uuid = ififuncs.get_source_uuid()
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
        'EVENT = Concatenation, status=started, eventType=Creation, agentName=ffmpeg, eventDetail=Source media concatenated into a single file output=%s' % os.path.join(args.o, '%s.mkv' % uuid))
    source_bitstream_md5 = ffmpeg_concat(concat_file, args, uuid)
    output_file = os.path.join(args.o, '%s.mkv' % uuid)
    ififuncs.generate_log(
        log_name_source,
        'EVENT = Concatenation, status=finished, eventType=Creation, agentName=ffmpeg, eventDetail=Source media concatenated into a single file output=%s' % os.path.join(args.o, '%s.mkv' % uuid))
    ififuncs.generate_log(
        log_name_source,
        'EVENT = losslessness verification, status=started, eventType=messageDigestCalculation, agentName=ffmpeg, eventDetail=MD5s of AV streams of output file generated for validation')
    output_bitstream_md5 = subprocess.check_output([
        'ffmpeg',
        '-i', output_file,
        '-f', 'md5', '-map', '0:v', '-map', '0:a?', '-c', 'copy', '-'
    ]).rstrip()
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
    subprocess.call(['mkvpropedit', output_file, '-c', 'chapters.txt'])
    ififuncs.generate_log(
        log_name_source,
        'EVENT = eventType=modification, agentName=mkvpropedit, eventDetail=Chapters added to file detailing start point of source clips.')
    ififuncs.concat_textfile(video_files, concat_file)
    with open(log_name_source, 'r') as concat_log:
        concat_lines = concat_log.readlines()
    if args.s:
        sipcreator_log = sipcreator.main(['-i', output_file, '-u', uuid, '-user', user, '-o', args.o])
        with open(sipcreator_log, 'r') as sipcreator_log_object:
            sipcreator_lines = sipcreator_log_object.readlines()
        with open(sipcreator_log, 'wb') as fo:
            for lines in concat_lines:
                fo.write(lines)
            for remaining_lines in sipcreator_lines:
                fo.write(remaining_lines)

if __name__ == '__main__':
    main(sys.argv[1:])
