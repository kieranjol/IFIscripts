#!/usr/bin/env python
'''
Describe AV objects using PBCore in CSV form.
Ideas for improvement:
Have the PBCore get metadata function return the value, and
just append it to the element list in the one call.
Also, have a consistent method for extracting metadata,
I'd suggest just parsing a single raw -f mediainfo, which should
alleviate the need to use --Inform and the PBCore output.

Also - better handling of multiple audio tracks.
The audio_format and the PBCore calls are all just analyzing the first track.
Get rid of this technical debt!

'''
import sys
import os
import subprocess
import argparse
from lxml import etree
import ififuncs


def process_mixed_values(value_list):
    '''
    Checks if multiple conflicting metadata values exist,
    for example, an instantiation that has multiple files that have
    different framerates.
    '''
    mixed_values = ''
    # Check if just a single value exists. If so, just return that one value.
    if len(set(value_list)) is 1:
        print value_list
        value = value_list[0]
    else:
        # Return the mixed values with pipe delimiter.
        for x in value_list:
            mixed_values += x + '|'
        if mixed_values[-1] == '|':
            mixed_values = mixed_values[:-1]
        value = mixed_values
    return value

def get_timecode(pbcore_namespace, root, source):
    ''''
    Gets starting timecode and source of timecode
    This is awkward cos it can be in the instantation or essence
    mediainfo output for matroska tags.
    It can also just be a tmcd or mxf tmcd track. In which case
    the value is extracted from TimeStart.
    ugh - though it's only for FCP 7 originated captures
    that have the timecode info in the instantiation and essence
    sections. so always grabbing it from essence should work
    for the most part.
    '''
    # test if the timecode is a metadata tag.
    timecode_source = 'n/a'
    starting_timecode = 'n/a'
    tag_test = get_metadata(
        "//ns:essenceTrackAnnotation[@annotationType='TimeCode_Source']",
        root, pbcore_namespace
    )
    # check if timecode is stored in a data track
    track_test = ififuncs.get_mediainfo(
            'bla', '--inform=Other;%TimeCode_FirstFrame%', source
        )
    if not tag_test == 'n/a':
        timecode_source = tag_test
        starting_timecode = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='TimeCode_FirstFrame']",
            root, pbcore_namespace
        )
    elif track_test != '':
        starting_timecode = track_test
        # Uh, this will be inconsistent if we ever get data tracks
        # other than timecode. MXF in particular could be weird.
        timecode_source = ififuncs.get_mediainfo(
            'bla', '--inform=Other;%Format%', source
        )
    if starting_timecode == 'n/a':
        pass
    else:
        starting_timecode = os.path.basename(source) + '=' + starting_timecode
    return timecode_source, starting_timecode

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
    elif len(value) > 1:
        mixed_values = ''
        value_list = []
        for i in value:
            # Checks if multiple audio tracks have different values.
            if i.getparent().find(
                'ns:essenceTrackType',
                namespaces={'ns':pbcore_namespace}
            ).text == 'Audio':
                value_list.append(i.text)
        # Checks if values in the list are the same(1) or different (2)
        if len(set(value_list)) is 1:
            value = value[0].text
        else:
            # Return the mixed values with pipe delimiter.
            for x in value_list:
                mixed_values += x + '|'
            if mixed_values[-1] == '|':
                mixed_values = mixed_values[:-1]
            value = mixed_values

    else:
        value = value[0].text
    return value


def get_attributes(root, pbcore_namespace):
    '''
    Extracts values from PBCore2 XML MediaInfo outputs.
    '''
    value = root.xpath(
        "ns:essenceTrackEncoding",
        namespaces={'ns':pbcore_namespace}
    )[0].attrib
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
    parser.add_argument(
        '-parent',
        help='Enter the accession number of the parent object (useful for reproductions)'
    )
    parser.add_argument(
        '-acquisition_type',
        help='Enter the Type of Acquisition in the form of a number referring to the IFI controlled vocabulary.'
    )
    parser.add_argument(
        '-donor',
        help='Enter a string that represents the source of acquisition'
    )
    parser.add_argument(
        '-depositor_reference',
        help='Enter a number that represents the identifier for the source of acquisition'
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
        'backup_habitat',
        'TTape Origin',
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
        'instantDate_other',
        'instantDate_type',
        'instantiationDate_mo',
        'instantiationStandar',
        'instantMediaty',
        'instantFileSize_byte',
        'instantFileSize_gigs',
        'instantTimeStart',
        'instantDataRate',
        'instantTracks',
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
        'video_codec_profile',
        'channels',
        'colour_range',
        'format_version',
        'TimeCode_FirstFrame',
        'TimeCode_Source',
        'app_company_name',
        'app_name',
        'app_version',
        'library_name',
        'library_version',
        'reproduction_creator',
        'reproduction_reason',
        'dig_object_descrip'
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
    acquisition_type = ''
    if args.acquisition_type:        
        acquisition_type = ififuncs.get_acquisition_type(args.acquisition_type)[0]
    for dirs in os.listdir(args.input):
        if ififuncs.validate_uuid4(dirs) is None:
            instantiationIdentif = dirs
    Accession_Number = get_accession_number(args.input)
    if args.reference:
        Reference_Number = args.reference.upper()
    else:
        Reference_Number = get_reference_number(args.input)
    if args.p:
        for root, _, filenames in os.walk(args.input):
            if os.path.basename(root) == 'metadata':
                metadata_dir = root
            elif os.path.basename(root) == 'logs':
                logs_dir = root
        csv_filename = os.path.join(metadata_dir, Accession_Number + '_pbcore.csv')
        sipcreator_log = os.path.join(
            logs_dir, instantiationIdentif + '_sip_log.log'
        )
        ififuncs.generate_log(
            sipcreator_log,
            'EVENT = makepbcore.py started'
        )
        ififuncs.generate_log(
            sipcreator_log,
            'eventDetail=makepbcore.py %s' % ififuncs.get_script_version('makepbcore.py')
        )
        ififuncs.generate_log(
            sipcreator_log,
            'Command line arguments: %s' % args
        )
        ififuncs.generate_log(
            sipcreator_log,
            'EVENT = agentName=%s' % user
        )
    else:
        csv_filename = 'blaa.csv'
    print ' - Metadata will be stored in %s' % csv_filename
    for filenames in os.listdir(args.input):
        if '_manifest.md5' in filenames:
            md5_manifest = os.path.join(args.input, filenames)
        elif'manifest-sha512.txt' in filenames:
            sha512_manifest = os.path.join(args.input, filenames)
    make_csv(csv_filename)
    ms = 0
    FrameCount = 0
    instantFileSize_byte = 0
    instantFileSize_gigs = 0
    scan_types = []
    matrix_list = []
    transfer_list = []
    colour_primaries_list = []
    color_spaces = []
    chroma = []
    frame_sizes = []
    par_list = []
    container_list = []
    fps_list = []
    sample_rate_list = []
    track_count_list = []
    interlace_list = []
    compression_list = []
    pix_fmt_list = []
    audio_fmt_list = []
    audio_codecid_list = []
    audio_codec_list = []
    au_bitdepth_list = []
    video_codecid_list = []
    video_codec_version_list = []
    video_codec_profile_list = []
    timecode_list = []
    channels_list = []
    for source in all_files:
        metadata = subprocess.check_output(['mediainfo', '--Output=PBCore2', source])
        root = etree.fromstring(metadata)
        print(' - Analysing  %s') % source
        pbcore_namespace = root.xpath('namespace-uri(.)')
        track_type = root.xpath('//ns:essenceTrackType', namespaces={'ns':pbcore_namespace})
        if len(track_type) > 0:
            for track in track_type:
                if track.text == 'Video':
                    essenceTrackEncodvid = get_metadata(
                        "ns:essenceTrackEncoding",
                        track.getparent(), pbcore_namespace
                    )
                    vcodec_attributes = get_attributes(track.getparent(), pbcore_namespace)
                elif track.text == 'Audio':
                    silence = False
                    essenceTrackEncod_au = get_metadata(
                        "ns:essenceTrackEncoding",
                        track.getparent(), pbcore_namespace
                    )
                    audio_codec_list.append(essenceTrackEncod_au)
                    acodec_attributes = get_attributes(track.getparent(), pbcore_namespace)
                    try:
                        audio_codecid = acodec_attributes['ref']
                    except KeyError:
                        audio_codecid = 'n/a'
                    essenceTrackSampling = ififuncs.get_mediainfo(
                        'samplerate',
                        '--inform=Audio;%SamplingRate_String%', source
                    )
                    sample_rate_list.append(essenceTrackSampling)
                    essenceBitDepth_au = get_metadata(
                        "ns:essenceTrackBitDepth",
                        track.getparent(), pbcore_namespace
                    )
                    audio_codecid_list.append(audio_codecid)
                    au_bitdepth_list.append(essenceBitDepth_au)
                    channels = get_metadata(
                        "//ns:essenceTrackAnnotation[@annotationType='Channel(s)']",
                        track.getparent(), pbcore_namespace
                    )
                    channels_list.append(channels)
        ScanType = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='ScanType']",
            root, pbcore_namespace
        )
        scan_types.append(ScanType)
        matrix_coefficients = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='matrix_coefficients']",
            root, pbcore_namespace
        )
        timecode_source,starting_timecode = get_timecode(pbcore_namespace, root, source)
        timecode_list.append(starting_timecode)
        matrix_list.append(matrix_coefficients)
        transfer_characteris = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='transfer_characteristics']",
            root, pbcore_namespace
        )
        transfer_list.append(transfer_characteris)
        colour_primaries = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='colour_primaries']",
            root, pbcore_namespace
        )
        colour_primaries_list.append(colour_primaries)
        FrameCount += int(get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='FrameCount']",
            root, pbcore_namespace
        ))
        instantFileSize_byte += int(get_metadata(
            "//ns:instantiationFileSize",
            root, pbcore_namespace
        ))
        instantDataRate = round(float(ififuncs.get_mediainfo(
            'OverallBitRate', '--inform=General;%OverallBitRate%', source
        ))  / 1000 / 1000, 2)
        instantTracks = ififuncs.get_number_of_tracks(source)
        track_count_list.append(instantTracks)
        ms += ififuncs.get_milliseconds(source)
        ColorSpace = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='ColorSpace']",
            root, pbcore_namespace
        )
        color_spaces.append(ColorSpace)
        ChromaSubsampling = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='ChromaSubsampling']",
            root, pbcore_namespace
        )
        chroma.append(ChromaSubsampling)
        instantMediaty = get_metadata(
            "//ns:instantiationMediaType",
            root, pbcore_namespace
        )
        essenceFrameSize = get_metadata(
            "//ns:essenceTrackFrameSize",
            root, pbcore_namespace
        )
        frame_sizes.append(essenceFrameSize)
        PixelAspectRatio = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='PixelAspectRatio']",
            root, pbcore_namespace
        )
        par_list.append(PixelAspectRatio)
        instantiationStandar = get_metadata(
            "//ns:instantiationAnnotation[@annotationType='Format']",
            root, pbcore_namespace
        )
        container_list.append(instantiationStandar)
        essenceFrameRate = get_metadata(
            "//ns:essenceTrackFrameRate",
            root, pbcore_namespace
        )
        fps_list.append(essenceFrameRate)
        essenceAspectRatio = ififuncs.get_mediainfo(
            'DAR', '--inform=Video;%DisplayAspectRatio_String%', source
        )
        Interlacement = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='Interlacement']",
            root, pbcore_namespace
        )
        # FFV1/MKV seems to have this scanorder metadata here rather than Interlacement
        # FFV1/MKV is the only example I've seen so far that behaves like this :|
        # It could be that Interlacement is set at a codec level for FFV1, but others are
        # declared at the container level..
        if Interlacement == 'n/a':
            Interlacement = get_metadata(
                "//ns:essenceTrackAnnotation[@annotationType='ScanOrder']",
                root, pbcore_namespace
            )
        interlace_list.append(Interlacement)
        Compression_Mode = get_metadata(
            "//ns:instantiationAnnotation[@annotationType='Compression_Mode']",
            root, pbcore_namespace
        )
        colour_range = get_metadata(
            "//ns:essenceTrackAnnotation[@annotationType='colour_range']",
            root, pbcore_namespace
        )
        format_version = get_metadata(
            "//ns:instantiationAnnotation[@annotationType='Format_Version']",
            root, pbcore_namespace
        )
        app_company_name = get_metadata(
            "//ns:instantiationAnnotation[@annotationType='Encoded_Application_CompanyName']",
            root, pbcore_namespace
        )
        app_name = get_metadata(
            "//ns:instantiationAnnotation[@annotationType='Encoded_Application_Name']",
            root, pbcore_namespace
        )
        app_version = get_metadata(
            "//ns:instantiationAnnotation[@annotationType='Encoded_Application_Version']",
            root, pbcore_namespace
        )
        library_name = get_metadata(
            "//ns:instantiationAnnotation[@annotationType='Encoded_Library_Name']",
            root, pbcore_namespace
        )
        library_version = get_metadata(
            "//ns:instantiationAnnotation[@annotationType='Encoded_Library_Version']",
            root, pbcore_namespace
        )
        compression_list.append(Compression_Mode)
        instantiationDate_mo = get_metadata(
            "//ns:instantiationDate[@dateType='file modification']",
            root, pbcore_namespace
        )
        instantDate_other = 'n/a'
        instantDate_type = 'n/a'
        pix_fmt = ififuncs.get_ffmpeg_fmt(source, 'video')
        pix_fmt_list.append(pix_fmt)
        audio_fmt = ififuncs.get_ffmpeg_fmt(source, 'audio')
        audio_fmt_list.append(audio_fmt)
    if silence:
        audio_codecid = 'n/a'
        essenceBitDepth_au = 'n/a'
        essenceTrackEncod_au = 'n/a'
        essenceTrackSampling = 'n/a'
        channels = 'n/a'
    video_codecid = vcodec_attributes['ref']
    video_codecid_list.append(video_codecid)
    try:
        video_codec_version = vcodec_attributes['version']
    except KeyError:
        video_codec_version = 'n/a'
    try:
        video_codec_profile = vcodec_attributes['annotation'][8:]
    except KeyError:
        video_codec_profile = 'n/a'
    video_codec_version_list.append(video_codec_version)
    video_codec_profile_list.append(video_codec_profile)
    metadata_error = ''
    metadata_list = [
        scan_types,
        matrix_list,
        transfer_list,
        colour_primaries_list,
        color_spaces,
        chroma,
        frame_sizes,
        par_list,
        container_list,
        fps_list,
        sample_rate_list,
        track_count_list,
        interlace_list,
        compression_list,
        pix_fmt_list,
        audio_fmt_list,
        audio_codecid_list,
        audio_codec_list,
        au_bitdepth_list,
        video_codecid_list,
        video_codec_version_list,
        video_codec_profile_list,
        channels_list,
        timecode_list
    ]
    for i in metadata_list:
        if len(set(i)) > 1:
            metadata_error += 'WARNING - Your metadata values are not the same for all files: %s\n' % set(i)
            print metadata_error
            if args.p:
                ififuncs.generate_log(
                    sipcreator_log,
                    'EVENT = Metadata mismatch - Your metadata values are not the same for all files: %s' % set(i)
                )
    tc = ififuncs.convert_millis(ms)
    instantiationDuratio = ififuncs.convert_timecode(25, tc)
    if args.donor:
        Donor = args.donor
    else:
        Donor = ''
    Edited_By = user
    Date_Created = ''
    Date_Last_Modified = ''
    Film_Or_Tape = 'Digital AV Object'
    Date_Of_Donation = ''
    reproduction_creator = ''
    if args.acquisition_type:
        if acquisition_type == 'Reproduction':
            Date_Of_Donation = instantiationDate_mo.split('T')[0]
            # if a reproduction, then there's no Donor/transfer of title.
            Donor = 'n/a'
            if ififuncs.find_concat_user(sipcreator_log) == 'Aoife Fitzmaurice':
                reproduction_creator = 'Aoife Fitzmaurice (2016)'
            elif ififuncs.find_concat_user(sipcreator_log) == 'Kieran O\'Leary':
                reproduction_creator = 'Kieran O\'Leary (2013)'
    Habitat = ''
    backup_habitat = ''
    Type_Of_Deposit = acquisition_type
    if args.depositor_reference:
        Depositor_Reference = args.depositor_reference
    else:
        Depositor_Reference = ''
    Master_Viewing = 'Preservation Object'
    Language_Version = ''
    Condition_Rating = ''
    Companion_Elements = ''
    TTape_Origin = args.parent
    EditedNew = user
    FIO = 'In'
    CollectionTitle = ''
    Created_By = user
    instantTimeStart = 'n/a'
    instantFileSize_gigs = round(
        float(instantFileSize_byte)  / 1024 / 1024 / 1024, 3
    )
    instantColors = 'n/a'
    instantLanguage = 'n/a'
    instantAltMo = 'n/a'
    essenceBitDepth_vid = ififuncs.get_mediainfo(
        'duration', '--inform=Video;%BitDepth%', source
    )
    instantiationChanCon = 'n/a'
    colour_range = colour_range
    format_version = format_version
    TimeCode_FirstFrame = process_mixed_values(timecode_list)
    TimeCode_Source = timecode_source
    reproduction_reason = ''
    dig_object_descrip = ififuncs.get_digital_object_descriptor(args.input)
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
        backup_habitat,
        TTape_Origin,
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
        instantDate_other,
        instantDate_type,
        instantiationDate_mo,
        instantiationStandar,
        instantMediaty,
        instantFileSize_byte,
        instantFileSize_gigs,
        instantTimeStart,
        instantDataRate,
        instantTracks,
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
        video_codec_profile,
        channels,
        colour_range,
        format_version,
        TimeCode_FirstFrame,
        TimeCode_Source,
        app_company_name,
        app_name,
        app_version,
        library_name,
        library_version,
        reproduction_creator,
        reproduction_reason,
        dig_object_descrip,
    ])
    if args.p:
        ififuncs.generate_log(
            sipcreator_log,
            'EVENT = Metadata extraction - eventDetail=Technical record creation using PBCore, eventOutcome=%s, agentName=makepbcore' % (csv_filename))
        ififuncs.generate_log(
            sipcreator_log,
            'EVENT = makepbcore.py finished')
        ififuncs.checksum_replace(md5_manifest, sipcreator_log, 'md5')
        ififuncs.checksum_replace(sha512_manifest, sipcreator_log, 'sha512')
        ififuncs.manifest_update(md5_manifest, csv_filename)
        print ' - Updating %s with %s' % (md5_manifest, csv_filename)
        ififuncs.sha512_update(sha512_manifest, csv_filename)
        print ' - Updating %s with %s' % (sha512_manifest, csv_filename)
        print metadata_error
if __name__ == '__main__':
    main(sys.argv[1:])

