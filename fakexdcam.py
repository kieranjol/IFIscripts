#!/usr/bin/env python
'''
Creates a fake XDCAM EX structure for testing purposes
'''
import os
import sys
import subprocess

def make_clip(clip_dir):
    '''
    Creates some dummy clips.
    '''
    clip_name = os.path.basename(clip_dir)
    mp4 = os.path.join(clip_dir, clip_name + '.MP4')
    smi = os.path.join(clip_dir, clip_name + '.SMI')
    ppn = os.path.join(clip_dir, clip_name + 'I01.PPN')
    xml = os.path.join(clip_dir, clip_name + 'M01.XML')
    bim = os.path.join(clip_dir, clip_name + 'R01.BIM')
    subprocess.call(
        ['ffmpeg',
         '-f', 'lavfi',
         '-i', 'mandelbrot',
         '-c:v', 'mpeg2video', '-t', '1',
         mp4
        ])
    for files in [xml, ppn, smi, xml, bim]:
        open(files, 'w')


def main():
    '''
    Launches functions that makes a dummy XDCAM structure.
    '''
    source = sys.argv[1]
    bpav = os.path.join(source, 'BPAV')
    takr = os.path.join(source, 'TAKR')
    clpr = os.path.join(bpav, 'CLPR')
    clip1 = os.path.join(clpr, '338_0011_06')
    clip2 = os.path.join(clpr, '338_0011_07')
    clip3 = os.path.join(clpr, '338_0011_08')
    for folder in [bpav, takr, clpr, clip1, clip2, clip3]:
        os.makedirs(folder)
    cueup = os.path.join(clpr, 'CUEUP.XML')
    mediapro = os.path.join(clpr, 'MEDIAPRO.XML')
    for clip in [clip1, clip2, clip3]:
        make_clip(clip)
    for files in [cueup, mediapro]:
        open(files, 'w')


if __name__ == '__main__':
    main()
