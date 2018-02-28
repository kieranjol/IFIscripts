#!/usr/bin/env python
'''
Describe AV objects using PBCore in CSV form.
'''
import sys
import os
import subprocess
import argparse
from lxml import etree
import ififuncs

def get_metadata(xpath_path, root, pbcore_namespace):
    '''
    Extracts values from PBCore2 XML MediaInfo outputs.
    '''
    value = root.xpath(
        xpath_path,
        namespaces={'ns':pbcore_namespace}
    )
    if value == []:
        value = 'n/a'
    else:
        value = value[0].text
    return value

def get_attributes(root, pbcore_namespace):
    '''
    Extracts values from PBCore2 XML MediaInfo outputs.
    '''
    value = root.xpath("ns:essenceTrackEncoding",
        namespaces={'ns':pbcore_namespace})[0].attrib
    return value # a dict

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Describes AV objects using a combination of the PBCore 2 metadata standard and the mandatory fields from the IFI technical database.'
        'This script takes a folder as input. Either a single file or multiple objects will be described.'
        'This will produce a single PBCore CSV record per package, even if multiple objects are within a package.'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'input', help='Input directory'
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.'
    )
    parser.add_argument(
        '-accession',
        help='Enter the Accession number for the representation.'
    )
    parser.add_argument(
        '-reference',
        help='Enter the Filmographic reference number for the representation.'
    )
    parser.add_argument(
        '-p', action='store_true',
        help='Adds the PBCore CSV to the metadata folder'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def get_accession_number(source):
    '''
    Checks if the package has been accessioned.
    Returns the accession number if this is the case, otherwise the script exits.
    '''
    basename = os.path.basename(source)
    if len(basename) == 7:
        if basename[:3] == 'aaa':
            return basename
    else:
        print('looks like your package has not been accessioned? Exiting!')
        sys.exit()

def get_reference_number(source):
    '''
    Checks if the reference number is in the folder path.
    This check is not sustainable, will have to be made more flexible!
    '''
    basename = os.path.basename(os.path.dirname(source))
    if len(basename) == 7:
        if basename[:3] == 'af1':
            return basename
    else:
        basename = ififuncs.get_reference_number()
        return basename

def make_csv(csv_filename):
    '''
    Writes a CSV with IFI database headings.
    '''
    ififuncs.create_csv(csv_filename, [
        'Reference Number',
        'Donor',
        'Edited By',
        'Date Created',
        'Date Last Modified',
        'Film Or Tape',
        'Date Of Donation',
        'Accession Number',
        'Habitat',
        'Type Of Deposit',
        'Depositor Reference',
        'Master Viewing',
        'Language Version',
        'Condition Rating',
        'Companion Elements',
        'EditedNew',
        'FIO',
        'CollectionTitle',
        'Created By',
        'instantiationIdentif',
        'instantiationDate_modified',
        'instantiationDimensi',
        'instantiationStandar',
        'instantiationLocatio',
        'instantMediaty',
        'instantFileSize',
        'instantFileSize_gigs',
        'instantTimeStart',
        'instantDataRate',
        'instantColors',
        'instantLanguage',
        'instantAltMo',
        'essenceTrackEncodvid',
        'essenceFrameRate',
        'essenceTrackSampling',
        'essenceBitDepth_vid',
        'essenceFrameSize',
        'essenceAspectRatio',
        'essenceTrackEncod_au',
        'essenceBitDepth_au',
        'instantiationDuratio',
        'instantiationChanCon',
        'PixelAspectRatio',
        'FrameCount',
        'ColorSpace',
        'ChromaSubsampling',
        'ScanType',
        'Interlacement',
        'Compression_Mode',
        'colour_primaries',
        'transfer_characteris',
        'matrix_coefficients',
        'pix_fmt',
        'audio_fmt',
        'audio_codecid',
        'video_codecid',
        'video_codec_version',
        'video_codec_profile'
    ])

def main(args_):


    # if multiple file are present, this script will treat them as a single
    # instantiation/representation and get aggregate metadata about the whole
    # package. For now, this will be a clumsy implementation - the first file
    # will provide most metadata. Things like duration/bitrate/filesize
    # will be calculated as a whole.
    # Although another way would be that every call is looped, and if
    # this could catch files that should not be in the package, eg. a 4:2:2
    # file in a 4:2:0 package..
    # yup - do it that way!
    args = parse_args(args_)
    all_files = ififuncs.recursive_file_list(args.input)
    silence = True
    if args.user:
        user = args.user
    else:
        user = ififuncs.get_user()
    Accession_Number = get_accession_number(args.input)
    Reference_Number = get_reference_number(args.input)
    if args.p:
        for root, dirnames, filenames in os.walk(args.input):
            if os.path.basename(root) == 'metadata':
                metadata_dir = root
        csv_filename = os.path.join(metadata_dir, Accession_Number + '.csv')
    else:
        csv_filename = 'blaa.csv'
    for filenames in os.listdir(args.input):
        if '_manifest.md5' in filenames:
            md5_manifest = os.path.join(args.input, filenames)
        elif'manifest-sha512.txt' in filenames:
            sha512_manifest = os.path.join(args.input, filenames)
    make_csv(csv_filename)
    ms = 0
    FrameCount = 0
    instantFileSize = 0
    instantFileSize_gigs = 0
    for source in all_files:
        metadata = subprocess.check_output(['mediainfo', '--Output=PBCore2', source])
        root = etree.fromstring(metadata)
        print('Analysing  %s') % source
        pbcore_namespace = root.xpath('namespace-uri(.)')
        track_type = root.xpath('//ns:essenceTrackType', namespaces={'ns':pbcore_namespace})
        if len(track_type) > 0:
            for track in track_type:
                if track.text == 'Video':
                    essenceTrackEncodvid = get_metadata(
                        "ns:essenceTrackEncoding",
                        track.getparent(), pbcore_namespace
                    )
                    vcodec_attributes = get_attributes(track.getparent(),pbcore_namespace)
                elif track.text == 'Audio':
                    silence = False
                    essenceTrackEncod_au = get_metadata(
                        "ns:essenceTrackEncoding",
                        track.getparent(), pbcore_namespace
                    )
                    acodec_attributes = get_attributes(track.getparent(),pbcore_namespace)
        ScanType = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='ScanType']",
            root, pbcore_namespace
        )
        matrix_coefficients = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='matrix_coefficients']",
            root, pbcore_namespace
        )
        transfer_characteris = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='transfer_characteristics']",
            root, pbcore_namespace
        )
        colour_primaries = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='color_primaries']",
            root, pbcore_namespace
        )
        FrameCount += int(get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='FrameCount']",
            root, pbcore_namespace
        ))
        instantFileSize += int(get_metadata(
            "//ns:instantiationFileSize",
            root, pbcore_namespace
        ))
        instantDataRate = round(float(ififuncs.get_mediainfo(
            'OverallBitRate', '--inform=General;%OverallBitRate%', source
        ))  / 1000 / 1000, 2)
        ms += ififuncs.get_milliseconds(source)
        ColorSpace = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='ColorSpace']",
            root, pbcore_namespace
        )
        ChromaSubsampling = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='ChromaSubsampling']",
            root, pbcore_namespace
        )
        instantMediaty = get_metadata(
            "//ns:instantiationMediaType",
            root, pbcore_namespace
        )
        essenceFrameSize = get_metadata(
            "//ns:essenceTrackFrameSize",
            root, pbcore_namespace
        )
        essenceAspectRatio = get_metadata(
            "//ns:essenceTrackAspectRatio",
            root, pbcore_namespace
        )
        PixelAspectRatio = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='PixelAspectRatio']",
            root, pbcore_namespace
        )
        instantiationStandar = get_metadata(
            "//ns:instantiationAnnotation[@annotationType='Format']",
            root, pbcore_namespace
        )
        essenceFrameRate = get_metadata(
            "//ns:essenceTrackFrameRate",
            root, pbcore_namespace
        )
        essenceTrackSampling = get_metadata(
            "//ns:essenceTrackSamplingRate",
            root, pbcore_namespace
        )
        Interlacement = get_metadata(
            "//ns:instantiationAnnotation[@annotationType='Interlacement']",
            root, pbcore_namespace
        )
        Compression_Mode = get_metadata(
            "//ns:instantiationAnnotation[@annotationType='Compression_Mode']",
            root, pbcore_namespace
        )
        instantiationDate_modified = get_metadata(
            "//ns:instantiationDate[@dateType='file modification']",
            root, pbcore_namespace
        )
        pix_fmt = ififuncs.get_ffmpeg_fmt(source, 'video')
        audio_fmt = ififuncs.get_ffmpeg_fmt(source, 'audio')
    if not silence:
        audio_codecid = acodec_attributes['ref']
        essenceBitDepth_au = ififuncs.get_mediainfo(
            'duration', '--inform=Audio;%BitDepth%', source
        )
    else:
        audio_codecid = 'n/a'
        essenceBitDepth_au = 'n/a'
        essenceTrackEncod_au = 'n/a'
    video_codecid = vcodec_attributes['ref']
    try:
        video_codec_version = vcodec_attributes['version']
    except KeyError:
        video_codec_version = 'n/a'
    video_codec_profile = vcodec_attributes['annotation'][8:]
    tc = ififuncs.convert_millis(ms)
    instantiationDuratio = ififuncs.convert_timecode(25, tc)
    Donor = ''
    Edited_By = user
    Date_Created = ''
    Date_Last_Modified = ''
    Film_Or_Tape = 'Digital File'
    Date_Of_Donation = ''
    Habitat = ''
    Type_Of_Deposit = ''
    Depositor_Reference = ''
    Master_Viewing = 'Preservation Master'
    Language_Version = ''
    Condition_Rating = ''
    Companion_Elements = ''
    EditedNew = user
    FIO = 'In'
    CollectionTitle = ''
    Created_By = user
    instantiationIdentif = ''
    instantiationDimensi = ''
    instantiationLocatio = ''
    instantTimeStart = ''
    instantFileSize_gigs = round(
        float(instantFileSize)  / 1024 / 1024 / 1024, 3
    )
    instantColors = ''
    instantLanguage = ''
    instantAltMo = 'n/a'
    essenceBitDepth_vid = ififuncs.get_mediainfo(
        'duration', '--inform=Video;%BitDepth%', source
    )
    instantiationChanCon = ''
    ififuncs.append_csv(csv_filename, [
        Reference_Number,
        Donor,
        Edited_By,
        Date_Created,
        Date_Last_Modified,
        Film_Or_Tape,
        Date_Of_Donation,
        Accession_Number,
        Habitat,
        Type_Of_Deposit,
        Depositor_Reference,
        Master_Viewing,
        Language_Version,
        Condition_Rating,
        Companion_Elements,
        EditedNew,
        FIO,
        CollectionTitle,
        Created_By,
        instantiationIdentif,
        instantiationDate_modified,
        instantiationDimensi,
        instantiationStandar,
        instantiationLocatio,
        instantMediaty,
        instantFileSize,
        instantFileSize_gigs,
        instantTimeStart,
        instantDataRate,
        instantColors,
        instantLanguage,
        instantAltMo,
        essenceTrackEncodvid,
        essenceFrameRate,
        essenceTrackSampling,
        essenceBitDepth_vid,
        essenceFrameSize,
        essenceAspectRatio,
        essenceTrackEncod_au,
        essenceBitDepth_au,
        instantiationDuratio,
        instantiationChanCon,
        PixelAspectRatio,
        FrameCount,
        ColorSpace,
        ChromaSubsampling,
        ScanType,
        Interlacement,
        Compression_Mode,
        colour_primaries,
        transfer_characteris,
        matrix_coefficients,
        pix_fmt,
        audio_fmt,
        audio_codecid,
        video_codecid,
        video_codec_version,
        video_codec_profile
    ])
    if args.p:
        ififuncs.manifest_update(md5_manifest, csv_filename )
        ififuncs.sha512_update(sha512_manifest, csv_filename)
if __name__ == '__main__':
    main(sys.argv[1:])

