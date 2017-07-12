#!/usr/bin/env python
'''
Simple DCI DCP XML subtitle to SRT convertor.
Usage:
dcpsubs2srt.py /path/to/subtitle.xml
Output will be a sidecar SRT file in the same directory as input.
'''

import sys
from lxml import etree


def main():
    '''
    Converts the input XML to SRT
    '''
    filename = sys.argv[1]
    srt_file = filename +'.srt'
    dcp_subtitle = etree.parse(filename)
    total_subtitles = int(dcp_subtitle.xpath('count(//Subtitle)'))
    counter = 0
    with open(srt_file, "w") as myfile:
        print srt_file, 'created'
    while counter < total_subtitles:
        xpath_counter = counter + 1
        in_point = dcp_subtitle.xpath('//Subtitle')[counter].attrib['TimeIn']
        out_point = dcp_subtitle.xpath('//Subtitle')[counter].attrib['TimeOut']
        in_point = in_point[:8]  + '.' + in_point[9:]
        out_point = out_point[:8] + '.' + out_point[9:]
        with open(srt_file, "a") as myfile:
            myfile.write(str(counter + 1) + '\n')
            myfile.write(in_point + ' --> ' + out_point + '\n')
            subtitle_text = [subtitle_text.text for subtitle_text in dcp_subtitle.iterfind('.//Subtitle[%s]/Text' % int(xpath_counter))]
            for i in subtitle_text:
                myfile.write(i + '\n')
            myfile.write('\n')
        counter += 1


if __name__ == '__main__':
    main()
