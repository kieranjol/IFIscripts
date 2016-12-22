#!/usr/bin/env python

import argparse
import subprocess
import sys
import os
from ififuncs import hashlib_md5
from glob import glob
from sys import platform as _platform


def getffprobe(variable, streamvalue, which_file):
    variable = subprocess.check_output(['ffprobe',
                                                '-v', 'error',
                                                '-select_streams', 'v:0',
                                                '-show_entries',
                                                streamvalue,
                                                '-of', 'default=noprint_wrappers=1:nokey=1',
                                                which_file])
    return variable


def set_options(input):
    parser = argparse.ArgumentParser(description='IFI Irish Film Institute H264 FFMPEG Encoder.'
                                     ' Written by Kieran O\'Leary.')
    parser.add_argument('input')
    parser.add_argument(
                        '-clean',
                        action='store_true',help='Disables watermark and timecode for a clean image')
    parser.add_argument(
                        '-yadif',
                        action='store_true',help='Yet Another DeInterlace Filter')
    parser.add_argument(
                        '-crf',
                        help='Set quality. Default is 23, lower number = large file/high quality, high number = small file/poor quality')
    parser.add_argument(
                        '-o',
                        help='Set output directory. The default directory is the same directory as input.')
    parser.add_argument(
                        '-scale',
                        help='Rescale video.'
                        ' Usage: -scale 1920x1080 or -scale 720x576 etc')
    parser.add_argument(
                        '-md5',
                        action='store_true',
                        help='Get md5 sidecar for your output file')
    parser.add_argument(
                        '-map',
                        action='store_true',
                        help='Force default mapping, eg. 1 audio/video stream')

    parser.add_argument(
                        '-player',
                        action='store_true',
                        help='uses yadif, 4:3 DAR with 1:1 PAR, with no watermark or timecode.')
    args = parser.parse_args()

    h264_options = []

    if args.yadif:
        h264_options.append('-yadif')
    if args.crf:
        crf_value = args.crf
    else:
        crf_value = '23'

    if args.scale:
        h264_options.append('-scale')
        width_height = args.scale
    if args.player:
        args.clean = True
        args.yadif = True
        crf_value = '18'

    if args.clean:
        bitc = False
        drawtext_options = []
    else:
        bitc = True
        h264_options.append('bitc')

    number_of_effects =  len(h264_options)

     # Input, either file or firectory, that we want to process.
    input = args.input

    # Store the directory containing the input file/directory.
    wd = os.path.dirname(input)
    if wd == '':
        wd = os.getcwd()
    # Change current working directory to the value stored as "wd"
    os.chdir(wd)

    # Store the actual file/directory name without the full path.
    file_without_path = os.path.basename(input)

    # Check if input is a file.
    # AFAIK, os.path.isfile only works if full path isn't present.
    if os.path.isfile(file_without_path):
        video_files = []                       # Create empty list
        video_files.append(file_without_path)  # Add filename to list

    # Check if input is a directory.
    elif os.path.isdir(file_without_path):
        os.chdir(file_without_path)
        video_files = (
            glob('*.mov') +
            glob('*.mp4') +
            glob('*.mxf') +
            glob('*.mkv') +
            glob('*.avi')
        )

    # Prints some stuff if input isn't a file or directory.
    else:
        print "Your input isn't a file or a directory."
    return video_files,crf_value, number_of_effects, args,bitc

def main(sidecar):
    video_files,crf_value, number_of_effects, args,bitc = set_options(sys.argv[1])
    get_bitc(video_files, crf_value, number_of_effects, args, bitc, sidecar)

def get_bitc(video_files, crf_value, number_of_effects, args, bitc, sidecar):
    drawtext_options = []
    for filename in video_files:
        if args.o:
            output = args.o + '/' + filename + "_h264.mov"
        elif sidecar == 'proxy_folder':
            proxy_folder = os.path.dirname(os.path.abspath(filename)) + '/proxy'
            if not os.path.isdir(proxy_folder):
                os.makedirs(proxy_folder)
            output = proxy_folder + '/' + filename + "_h264.mov"
        else:
            output = filename + "_h264.mov"

        height = subprocess.check_output(['mediainfo','--Language=raw','--Full',"--Inform=Video;%Height%", filename]).rstrip()
        pixel_aspect_ratio = subprocess.check_output(['mediainfo','--Language=raw','--Full',"--Inform=Video;%PixelAspectRatio%", filename]).rstrip()

        ffmpeg_args =   ['ffmpeg',
                '-i', filename,
                '-c:a', 'aac',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-crf', crf_value]

        if not args.map:
            ffmpeg_args.append('-map')
            ffmpeg_args.append('0:a?')
            ffmpeg_args.append('-map')
            ffmpeg_args.append('0:v')

        if args.yadif or args.scale or args.player or bitc :
            ffmpeg_args.append('-vf')

            if bitc:
                video_height = float(getffprobe('video_height','stream=height', filename))
                video_width  = float(getffprobe('video_width','stream=width', filename))

                # Calculate appropriate font size
                font_size = video_height / 12
                watermark_size = video_height / 14

                if _platform == "darwin":
                    font_path= "fontfile=/Library/Fonts/AppleGothic.ttf"
                elif _platform == "linux2":
                    font_path= "fontfile=/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
                elif _platform == "win32":
                    font_path = "'fontfile=C\:\\\Windows\\\Fonts\\\\'arial.ttf'"

                # Get starting timecode in a raw state that requires processing further on in the script.
                timecode_test_raw = getffprobe('timecode_test_raw','format_tags=timecode:stream_tags=timecode', filename)
                get_framerate = getffprobe('get_frame_rate','stream=avg_frame_rate', filename)

                # This tests if there is actually a timecode present in the file.
                if not timecode_test_raw:
                    # The timecode needs to be phrased in a way unique to each operating system.
                    # Note the backslashes.
                    # This section makes up a timecode if none is present in the file.
                    if _platform == "darwin" or _platform == "linux2":
                        timecode_test = '01\\\:00\\\:00\\\:00'
                    elif _platform == "win32":
                        timecode_test = '01\:00\:00\:00'

                else:
                    # If timecode is present, this will escape the colons
                    # so that it is compatible with each operating system.
                    if _platform == "darwin" or _platform == "linux2":
                        timecode_test = timecode_test_raw.replace(':', '\\\:').replace('\n', '')
                    elif _platform == "win32":
                        timecode_test = timecode_test_raw.replace(':', '\\:').replace('\n', '').replace('\r', '')

                # This removes the new line character from the framemrate.
                fixed_framerate = get_framerate.rstrip()
                filter_options = ''
                #all these prints are just for testing. Will be removed later.

                if _platform == "darwin" or _platform == "linux2":
                    placeholder = ''
                    drawtext_options = ["drawtext=%s:fontcolor=white:fontsize=%s:timecode=%s:rate=%s:boxcolor=0x000000AA:box=1:x=(w-text_w)/2:y=h/1.2,drawtext=%s:fontcolor=white:text='IFI IRISH FILM ARCHIVE':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=%s:alpha=0.4"  % (font_path,font_size, timecode_test, fixed_framerate, font_path,watermark_size)]

                elif _platform == "win32":
                    drawtext_options = ["drawtext=%s:fontcolor=white:fontsize=%s:timecode=%s:rate=%s:boxcolor=0x000000AA:box=1:x=(w-text_w)/2:y=h/1.2',drawtext=%s:fontcolor=white:text='IFI IRISH FILM ARCHIVE':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=%s:alpha=0.4'"  % (font_path,font_size, timecode_test, fixed_framerate, font_path,watermark_size)]

            if args.yadif:
                if args.player:
                    if height =='576':
                        if pixel_aspect_ratio == '1.000':
                            ffmpeg_args.append('yadif,scale=768:576')
                elif args.clean:
                    ffmpeg_args.append(' yadif')
                else:
                    drawtext_options[-1] += ',yadif'
            if args.scale:
                if args.clean:
                    if number_of_effects > 1:
                        ffmpeg_args[-1] += (',scale=%s' % width_height)
                    else:
                        ffmpeg_args.append('scale=%s' % width_height)
                else:
                    drawtext_options[-1] += (',scale=%s' % width_height)
            if len(drawtext_options) > 0:
                for i in drawtext_options:
                    ffmpeg_args.append(i)

        ffmpeg_args.append(output)
        print ffmpeg_args
        subprocess.call(ffmpeg_args)
        if args.md5:
            manifest =  '%s_manifest.md5' % filename
            h264_md5 = hashlib_md5(filename)
            with open(manifest,'wb') as fo:
                fo.write('%s  %s' % (h264_md5, filename))

if __name__ == "__main__":
    main('sidecar')