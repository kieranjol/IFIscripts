#!/usr/bin/env python

# Written by Kieran O'Leary, with a major review and overhaul/cleanup by Zach Kelling aka @Zeekay
# Makes a single ffv1.mkv

import subprocess
import sys
import filecmp
import os
import shutil
import csv
import time
import itertools
import getpass
from glob import glob
try:
    from ififuncs import set_environment
    from ififuncs import hashlib_manifest
    from ififuncs import make_mediatrace
    from ififuncs import make_mediainfo
    from ififuncs import get_mediainfo
    from ififuncs import append_csv
    from ififuncs import create_csv
    from ififuncs import generate_log
except ImportError:
    print '*** ERROR - IFIFUNCS IS MISSING - *** \n'
    'Makeffv1 requires that ififuncs.py is located in the same directory'
    ' as some functions are located in that script -'
    'https://github.com/kieranjol/IFIscripts/blob/master/ififuncs.py'
    sys.exit()

def read_non_comment_lines(infile):
    # Adapted from Andrew Dalke - http://stackoverflow.com/a/8304087/2188572
    for lineno, line in enumerate(infile):
        #if line[:1] != "#":
        yield lineno, line

def get_input():
    if len(sys.argv) < 2:
        print 'IFI FFV1.MKV SCRIPT'
        print 'USAGE: PYTHON makeffv1.py FILENAME'
        print 'OR'
        print 'USAGE: PYTHON makeffv1.py DirectoryNAME'
        print 'If input is a directory, all files will be processed'
        print 'If input is a file, only that file will be processed'
        sys.exit()
    else:
        # Input, either file or firectory, that we want to process.
        input = sys.argv[1]
        # Store the directory containing the input file/directory.
        wd = os.path.dirname(input)
        # Change current working directory to the value stored as "wd"
        os.chdir(os.path.abspath(wd))
        # Store the actual file/directory name without the full path.
        file_without_path = os.path.basename(input)
        csv_report_filename = (
            os.path.basename(input)
            + 'makeffv1_results'
            + time.strftime("_%Y_%m_%dT%H_%M_%S") + '.csv'
            )
        # Check if input is a file.
        # AFAIK, os.path.isfile only works if full path isn't present.
        if os.path.isfile(file_without_path):
            print "single file found"
            video_files = []                       # Create empty list
            video_files.append(file_without_path)  # Add filename to list
        # Check if input is a directory.
        elif os.path.isdir(file_without_path):
            os.chdir(file_without_path)
            video_files = (
                glob('*.mov')
                + glob('*.mp4')
                + glob('*.mxf')
                + glob('*.mkv')
                + glob('*.avi')
                + glob('*.y4m')
                )
        else:
            print "Your input isn't a file or a directory."
            print "What was it? I'm curious."
        # temporary hack to stop makeffv1 from processing DV
        dv_test = []
        for test_files in video_files:
            codec =  get_mediainfo(
                'codec', '--inform=Video;%Codec%',
                 test_files
                 ).rstrip()
            if codec == 'DV':
                dv_test.append(test_files)
                print 'DV file found, skipping'
        for i in dv_test:
            if i in video_files:
                video_files.remove(i)
        create_csv(
            csv_report_filename,
            (
                'FILENAME', 'Lossless?',
                'Source size in bits', 'FFV1 size in bits',
                ' Compression ratio'
                )
            )
        return video_files, csv_report_filename
def make_ffv1(video_files, csv_report_filename):
    for filename in video_files: #loop all files in directory
        filenoext = os.path.splitext(filename)[0]
        # Generate new directory names
        metadata_dir = "%s/metadata" % filenoext
        log_dir = "%s/logs" % filenoext
        data_dir = "%s/objects" % filenoext
        # Actually create the directories.
        os.makedirs(metadata_dir)
        os.makedirs(data_dir)
        os.makedirs(log_dir)
        #Generate filenames for new files.
        inputxml = "%s/%s_source_mediainfo.xml" % (
            metadata_dir, os.path.basename(filename)
            )
        inputtracexml = "%s/%s_source_mediatrace.xml" % (
            metadata_dir, os.path.basename(filename)
            )
        output = "%s/%s.mkv" % (
            data_dir, os.path.splitext(os.path.basename(filename))[0]
            )
        # Generate filename of ffv1.mkv without the path.
        outputfilename = os.path.basename(output)
        outputxml = "%s/%s_mediainfo.xml" % (metadata_dir, outputfilename)
        outputtracexml = "%s/%s_mediatrace.xml" % (metadata_dir, outputfilename)
        fmd5 = "%s/%s_source.framemd5" % (
            metadata_dir, os.path.basename(filename)
            )
        fmd5ffv1 = "%s/%s_ffv1.framemd5" % (metadata_dir, outputfilename)
        log = "%s/%s_log.log" %  (log_dir, filename)
        generate_log(log, 'Input = %s' % filename)
        generate_log(log, 'Output = %s' % output)
        generate_log(
            log, 'makeffv1.py transcode to FFV1 and framemd5 generation of source started.'
            )
        ffv1_logfile = log_dir + '/%s_ffv1_transcode.log' % filename
        ffv1_env_dict = set_environment(ffv1_logfile)
        par = subprocess.check_output(
            [
                'mediainfo', '--Language=raw', '--Full',
                "--Inform=Video;%PixelAspectRatio%", filename
            ]
            ).rstrip()
        field_order = subprocess.check_output(
            [
                'mediainfo', '--Language=raw',
                '--Full', "--Inform=Video;%ScanType%", filename
            ]
            ).rstrip()
        height = subprocess.check_output(
            [
                'mediainfo', '--Language=raw',
                '--Full', "--Inform=Video;%Height%",
                filename
            ]
            ).rstrip()
        # Transcode video file writing frame md5 and output appropriately
        ffv1_command = [
            'ffmpeg',
            '-i', filename,
            '-c:v', 'ffv1',        # Use FFv1 codec
            '-g', '1',              # Use intra-frame only aka ALL-I aka GOP=1
            '-level', '3',          # Use Version 3 of FFv1
            '-c:a', 'copy',         # Copy and paste audio bitsream with no transcoding
            '-map', '0',
            '-dn',
            '-report',
            '-slicecrc', '1',
            '-slices', '16',
            ]
        # check for FCP7 lack of description and PAL
        if par == '1.000':
            if field_order == '':
                if height == '576':
                    ffv1_command += [
                        '-vf',
                        'setfield=tff, setdar=4/3'
                        ]
        ffv1_command += [
            output,
            '-f', 'framemd5', '-an',  # Create decoded md5 checksums for every frame of the input. -an ignores audio
            fmd5
            ]
        print ffv1_command
        subprocess.call(ffv1_command, env=ffv1_env_dict)
        generate_log(
            log, 'makeffv1.py transcode to FFV1 and framemd5 generation completed.'
            )
        generate_log(
            log, 'makeffv1.py Framemd5 generation of output file started.'
            )
        fmd5_logfile = log_dir + '/%s_framemd5.log' % outputfilename
        fmd5_env_dict = set_environment(fmd5_logfile)
        fmd5_command = [
            'ffmpeg',    # Create decoded md5 checksums for every frame
            '-i', output,
            '-report',
            '-f', 'framemd5', '-an',
            fmd5ffv1
            ]
        print fmd5_command
        subprocess.call(fmd5_command, env=fmd5_env_dict)
        generate_log(
            log,
            'makeffv1.py Framemd5 generation of output file completed'
            )
        source_video_size = get_mediainfo(
            'source_video_size', "--inform=General;%FileSize%", filename
            )
        ffv1_video_size = get_mediainfo(
            'ffv1_video_size', '--inform=General;%FileSize%', output
            )
        compression_ratio = float(source_video_size) / float(ffv1_video_size)
        if os.path.basename(sys.argv[0]) == 'makeffv1.py':
            shutil.copy(sys.argv[0], log_dir)
        print 'Generating mediainfo xml of input file and saving it in %s' % inputxml
        make_mediainfo(inputxml, 'mediaxmlinput', filename)
        print 'Generating mediainfo xml of output file and saving it in %s' % outputxml
        make_mediainfo(outputxml, 'mediaxmloutput', output)
        print 'Generating mediatrace xml of input file and saving it in %s' % inputtracexml
        make_mediatrace(inputtracexml, 'mediatracexmlinput', filename)
        print 'Generating mediatrace xml of output file and saving it in %s' % outputtracexml
        make_mediatrace(outputtracexml, 'mediatracexmloutput', output)
        source_parent_dir = os.path.dirname(os.path.abspath(filename))
        manifest = '%s/%s_manifest.md5' % (source_parent_dir, filenoext)
        generate_log(log, 'makeffv1.py MD5 manifest started')
        checksum_mismatches = []
        with open(fmd5) as f1:
            with open(fmd5ffv1) as f2:
                for (lineno1, line1), (lineno2, line2) in itertools.izip(
                        read_non_comment_lines(f1),
                        read_non_comment_lines(f2)
                        ):
                    if line1 != line2:
                        if 'sar' in line1:
                            checksum_mismatches = ['sar']
                        else:
                            checksum_mismatches.append(1)
        if len(checksum_mismatches) == 0:
            print 'LOSSLESS'
            append_csv(
                csv_report_filename, (
                    output,
                    'LOSSLESS', source_video_size,
                    ffv1_video_size, compression_ratio
                    )
                )
            generate_log(log, 'makeffv1.py Transcode was lossless')
        elif len(checksum_mismatches) == 1:
            if checksum_mismatches[0] == 'sar':
                print 'Image content is lossless,'
                ' Pixel Aspect Ratio has been altered.'
                ' Update ffmpeg in order to resolve the PAR issue.'
                append_csv(
                    csv_report_filename,
                    (
                        output,
                        'LOSSLESS - different PAR',
                        source_video_size, ffv1_video_size, compression_ratio
                        )
                    )
                generate_log(
                    log,
                    'makeffv1.py Image content is lossless but Pixel Aspect Ratio has been altered.Update ffmpeg in order to resolve the PAR issue.'
                    )
        elif len(checksum_mismatches) > 1:
            print 'NOT LOSSLESS'
            append_csv(
                csv_report_filename,
                (
                    output, 'NOT LOSSLESS',
                    source_video_size, ffv1_video_size, compression_ratio
                    )
                )
            generate_log(log, 'makeffv1.py Not Lossless.')
        hashlib_manifest(filenoext, manifest, source_parent_dir)
        if filecmp.cmp(fmd5, fmd5ffv1, shallow=False):
            print "YOUR FILES ARE LOSSLESS YOU SHOULD BE SO HAPPY!!!"
        else:
            print "The framemd5 text files are not completely identical."
            " This may be because of a lossy transcode,"
            " or a change in metadata, most likely pixel aspect ratio."
            " Please analyse the framemd5 files for source and output."

def main():
    video_files, csv_report_filename = get_input()
    make_ffv1(video_files, csv_report_filename)


if __name__ == "__main__":
    main()
