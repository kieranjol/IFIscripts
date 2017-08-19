#!/usr/bin/env python
'''
Accept options from command line and make access copy.
Use bitc.py -h for help
'''
import argparse
import subprocess
import sys
import os
from ififuncs import hashlib_md5


def getffprobe(variable, streamvalue, which_file):
    '''
    Returns a specific ffprobe technical metadata value.
    This is a good candidate to be moved to ififuncs.
    '''
    variable = subprocess.check_output([
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries',
        streamvalue,
        '-of', 'default=noprint_wrappers=1:nokey=1',
        which_file
    ])
    return variable


def set_options():
    '''
    Parse command line options.
    '''
    parser = argparse.ArgumentParser(
        description='IFI Irish Film Institute H264 FFMPEG Encoder.'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'input'
    )
    parser.add_argument(
        '-clean',
        action='store_true',
        help='Disables watermark and timecode for a clean image'
    )
    parser.add_argument(
        '-watermark',
        action='store_true',
        help='Disables timecode and only displays watermark'
    )
    parser.add_argument(
        '-timecode',
        action='store_true',
        help='Disables watermark and only displays timecode'
    )
    parser.add_argument(
        '-yadif',
        action='store_true',
        help='Yet Another DeInterlace Filter'
    )
    parser.add_argument(
        '-crf',
        help='Set quality. Default is 23, lower number ='
        ' large file/high quality, high number = small file/poor quality'
    )
    parser.add_argument(
        '-o',
        help='Set output directory.'
        'The default directory is the same directory as input.'
    )
    parser.add_argument(
        '-scale',
        help='Rescale video.'
        ' Usage: -scale 1920x1080 or -scale 720x576 etc'
    )
    parser.add_argument(
        '-md5',
        action='store_true',
        help='Get md5 sidecar for your output file'
    )
    parser.add_argument(
        '-map',
        action='store_true',
        help='Force default mapping, eg. 1 audio/video stream'
    )

    parser.add_argument(
        '-player',
        action='store_true',
        help='uses yadif, 4:3 DAR with 1:1 PAR, with no watermark or timecode.'
    )
    return parser.parse_args()


def build_filter(args, filename):
    '''
    Builds the ffmpeg -vf filtergraph, if needed.
    '''
    h264_options = []
    filter_list = []
    filtergraph = ''
    if args.yadif:
        h264_options.append('yadif')
    if args.scale:
        h264_options.append('scale=%s' % args.scale)
        # width_height = args.scale
    if args.player:
        args.clean = True
        args.yadif = True
    if not args.clean:
        drawtext_option = setup_drawtext(args, filename)
        h264_options.append(drawtext_option)
    for option in h264_options:
        filtergraph += option + ','
    if len(filtergraph) > 0:
        if filtergraph[-1] == ',':
            filtergraph = filtergraph[:-1]
        filter_list = ['-vf', filtergraph]
        print filter_list
    return filter_list


def get_filenames(args):
    '''
    Get information about filenames, paths etc.
    '''
    cli_input = args.input
    # Input, either file or firectory, that we want to process.
    # Store the directory containing the input file/directory.
    wd = os.path.dirname(cli_input)
    video_files = []
    if wd == '':
        cli_input = os.path.join(os.getcwd(), args.input)
    # Check if input is a file.
    # AFAIK, os.path.isfile only works if full path isn't present.
    if os.path.isfile(cli_input):
        video_files.append(cli_input)  # Add filename to list
    # Check if input is a directory.
    elif os.path.isdir(cli_input):
        for files in os.listdir(cli_input):
            if files.endswith(('.mov', '.mp4', '.mxf', '.mkv', '.avi')):
                if files[0] != '.':
                    video_files.append(os.path.join(cli_input, files))
    # Prints some stuff if input isn't a file or directory.
    else:
        print "Your input isn't a file or a directory."
    return video_files


def setup_drawtext(args, filename):
    '''
    Sets up the filtergraphs for either timecode, watermark or both.
    '''
    video_height = float(getffprobe('video_height', 'stream=height', filename))
    # Calculate appropriate font size
    font_size = video_height / 12
    watermark_size = video_height / 14
    if sys.platform == "darwin":
        font_path = "fontfile=/Library/Fonts/AppleGothic.ttf"
    elif sys.platform == "linux2":
        font_path = "fontfile=/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
    elif sys.platform == "win32":
        font_path = "'fontfile=C\:\\\Windows\\\Fonts\\\\'arial.ttf'"
    # Get starting timecode
    timecode_test_raw = getffprobe(
        'timecode_test_raw',
        'format_tags=timecode:stream_tags=timecode',
        filename
    )
    framerate = getffprobe(
        'get_frame_rate',
        'stream=avg_frame_rate',
        filename
    ).rstrip()
    # This tests if there is actually a timecode present in the file.
    if not timecode_test_raw:
        # The timecode needs to be phrased in a way unique to each O.S.
        # Note the backslashes.
        # This section makes up a timecode if none is present in the file.
        if sys.platform == "darwin" or sys.platform == "linux2":
            timecode_test = '01\\\:00\\\:00\\\:00'
        elif sys.platform == "win32":
            timecode_test = '01\:00\:00\:00'
    else:
        # If timecode is present, this will escape the colons
        # so that it is compatible with each operating system.
        if sys.platform == "darwin" or sys.platform == "linux2":
            timecode_test = timecode_test_raw.replace(':', '\\\:').rstrip()
        elif sys.platform == "win32":
            timecode_test = timecode_test_raw.replace(':', '\\:').rstrip()
    # This removes the new line character from the framemrate.
    timecode_option = "drawtext=%s:fontcolor=white:fontsize=%s:timecode=%s:rate=%s:boxcolor=0x000000AA:box=1:x=(w-text_w)/2:y=h/1.2" % (font_path, font_size, timecode_test, framerate)
    watermark_option = "drawtext=%s:fontcolor=white:text='IFI IRISH FILM ARCHIVE':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=%s:alpha=0.4"  % (font_path, watermark_size)
    bitc_watermark = timecode_option + ',' + watermark_option
    if args.timecode:
        return timecode_option
    elif args.watermark:
        return watermark_option
    else:
        return bitc_watermark


def main():
    '''
    Launch the various functions that will make a h264/mp4 access copy.
    '''
    args = set_options()
    video_files = get_filenames(args)
    for filename in video_files:
        filter_list = build_filter(args, filename)
        make_h264(filename, args, filter_list)


def make_h264(filename, args, filter_list):
    '''
    Launches the actuall ffmpeg process using all the info gleaned so far.
    '''
    if args.crf:
        crf_value = args.crf
    else:
        crf_value = '23'
    if args.o:
        output = args.o + '/' + os.path.basename(filename) + "_h264.mov"
    else:
        output = filename + "_h264.mov"
    ffmpeg_args = [
        'ffmpeg',
        '-i', filename,
        '-c:a', 'aac',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-crf', crf_value
    ]
    if not args.map:
        ffmpeg_args.append('-map')
        ffmpeg_args.append('0:a?')
        ffmpeg_args.append('-map')
        ffmpeg_args.append('0:v')
    if len(filter_list) > 0:
        for _filter in filter_list:
            ffmpeg_args.append(_filter)
    ffmpeg_args.append(output)
    print ffmpeg_args
    subprocess.call(ffmpeg_args)
    if args.md5:
        manifest = '%s_manifest.md5' % filename
        print 'Generating md5 sidecar...'
        h264_md5 = hashlib_md5(filename)
        with open(manifest, 'wb') as fo:
            fo.write('%s  %s' % (h264_md5, filename))

if __name__ == "__main__":
    main()
