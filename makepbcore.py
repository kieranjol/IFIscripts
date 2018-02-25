#!/usr/bin/env python

import sys
import subprocess
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
        'instantiationPhysica',
        'instantiationDigital',
        'instantiationStandar',
        'instantiationLocatio',
        'instantMediaty',
        'instantGenerations',
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
        'audio_fmt'
    ])

def main():


    # if multiple file are present, this script will treat them as a single
    # instantiation/representation and get aggregate metadata about the whole
    # package. For now, this will be a clumsy implementation - the first file
    # will provide most metadata. Things like duration/bitrate/filesize
    # will be calculated as a whole.
    # Although another way would be that every call is looped, and if
    # this could catch files that should not be in the package, eg. a 4:2:2
    # file in a 4:2:0 package..
    # yup - do it that way!
    all_files = ififuncs.recursive_file_list(sys.argv[1])
    csv_filename = 'blaa.csv'
    make_csv(csv_filename)
    ms = 0
    FrameCount = 0
    instantFileSize = 0
    instantFileSize_gigs = 0
    for source in all_files:
        metadata = subprocess.check_output(['mediainfo', '--Output=PBCore2', source])
        root = etree.fromstring(metadata)
        pbcore_namespace = root.xpath('namespace-uri(.)')
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
        instantiationDigital = get_metadata(
            "//ns:instantiationAnnotation[@annotationType='Format_Commercial_IfAny']",
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
    tc = ififuncs.convert_millis(ms)
    instantiationDuratio = ififuncs.convert_timecode(25, tc)
    Reference_Number = ''
    Donor = ''
    Edited_By = ''
    Date_Created = ''
    Date_Last_Modified = ''
    Film_Or_Tape = 'Digital File'
    Date_Of_Donation = ''
    Accession_Number = ''
    Habitat = ''
    Type_Of_Deposit = ''
    Depositor_Reference = ''
    Master_Viewing = 'Preservation Master'
    Language_Version = ''
    Condition_Rating = ''
    Companion_Elements = ''
    EditedNew = ''
    FIO = 'In'
    CollectionTitle = ''
    Created_By = ''
    instantiationIdentif = ''
    instantiationDimensi = ''
    instantiationPhysica = 'n/a'
    instantiationLocatio = ''
    instantGenerations = ''
    instantTimeStart = ''
    instantFileSize_gigs = round(
        float(instantFileSize)  / 1024 / 1024 / 1024, 2
    )
    instantColors = ''
    instantLanguage = ''
    instantAltMo = 'n/a'
    essenceTrackEncodvid = ''
    essenceBitDepth_vid = ififuncs.get_mediainfo(
        'duration', '--inform=Video;%BitDepth%', source
    )
    essenceTrackEncod_au = ''
    essenceBitDepth_au = ififuncs.get_mediainfo(
        'duration', '--inform=Audio;%BitDepth%', source
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
        instantiationPhysica,
        instantiationDigital,
        instantiationStandar,
        instantiationLocatio,
        instantMediaty,
        instantGenerations,
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
        audio_fmt])
if __name__ == '__main__':
    main()

