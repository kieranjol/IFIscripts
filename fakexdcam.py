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
    mxf = os.path.join(clip_dir, clip_name + '.MXF')
    smi = os.path.join(clip_dir, clip_name + '.SMI')
    ppn = os.path.join(clip_dir, clip_name + 'I01.PPN')
    xml = os.path.join(clip_dir, clip_name + 'M01.XML')
    bim = os.path.join(clip_dir, clip_name + 'R01.BIM')
    subprocess.call(
        ['ffmpeg',
         '-f', 'lavfi',
         '-i', 'mandelbrot',
         '-f', 'lavfi',
         '-i', 'sine=sample_rate=48000',
         '-c:v', 'mpeg2video',
         '-c:a', 'pcm_s16le', '-t', '1',
         mxf
        ])
    for files in [xml, ppn, smi, xml, bim]:
        open(files, 'w')


def main():
    '''
    Launches functions that makes a dummy XDCAM structure.
    '''
    source = sys.argv[1]
    bpav = os.path.join(source, 'BPAV')
    clpr = os.path.join(bpav, 'CLPR')
    takr = os.path.join(clpr, 'TAKR')
    clip1 = os.path.join(clpr, '338_0011_06')
    clip2 = os.path.join(clpr, '338_0011_07')
    clip3 = os.path.join(clpr, '338_0011_08')
    for folder in [bpav, clpr, takr, clip1, clip2, clip3]:
        print(folder)
        os.makedirs(folder)
    cueup = os.path.join(bpav, 'CUEUP.XML')
    mediapro = os.path.join(bpav, 'MEDIAPRO.XML')
    for clip in [clip1, clip2, clip3]:
        make_clip(clip)
    for files in [cueup, mediapro]:
        open(files, 'w')


if __name__ == '__main__':
    main()
