IFIscripts documentation
==================

table of contents
-------------------

1. [summary](https://github.com/kieranjol/IFIscripts#summary)
1. [Arrangement](https://github.com/kieranjol/IFIscripts#arrangement)
    * [sipcreator.py](https://github.com/kieranjol/IFIscripts#sipcreatorpy)
    * [accession.py](https://github.com/kieranjol/IFIscripts#accessionpy)
    * [batchaccession.py](https://github.com/kieranjol/IFIscripts#batchaccessionpy)
    * [order.py](https://github.com/kieranjol/IFIscripts#orderpy)
    * [makepbcore.py](https://github.com/kieranjol/IFIscripts#makepbcorepy)
    * [deletefiles.py](https://github.com/kieranjol/IFIscripts#deletefilespy)
    * [rearrange.py](https://github.com/kieranjol/IFIscripts#rearrangepy)
1. [Transcodes](https://github.com/kieranjol/IFIscripts#transcodes)
    * [makeffv1.py](https://github.com/kieranjol/IFIscripts#makeffv1py)
    * [bitc.py](https://github.com/kieranjol/IFIscripts#bitcpy)
    * [prores.py](https://github.com/kieranjol/IFIscripts#prorespy)
    * [concat.py](https://github.com/kieranjol/IFIscripts#concatpy)
1. [Digital Cinema Package Scripts](https://github.com/kieranjol/IFIscripts#digital-cinema-package-scripts)
	* [dcpaccess.py](https://github.com/kieranjol/IFIscripts#dcpaccesspy)
    * [dcpfixity.py](https://github.com/kieranjol/IFIscripts#dcpfixitypy)
    * [dcpsubs2srt.py](https://github.com/kieranjol/IFIscripts#dcpsubs2srtpy)
1. [Fixity Scripts](https://github.com/kieranjol/IFIscripts#fixity-scripts)
    * [copyit.py](https://github.com/kieranjol/IFIscripts#copyitpy)
    * [manifest.py](https://github.com/kieranjol/IFIscripts#manifestpy)
    * [makedfxml.py](https://github.com/kieranjol/IFIscripts#makedfxmlpy)
    * [sha512deep.py](https://github.com/kieranjol/IFIscripts#sha512deeppy)
    * [validate.py](https://github.com/kieranjol/IFIscripts#validatepy)
    * [batchfixity.py](https://github.com/kieranjol/IFIscripts#batchfixitypy)
1. [Image Sequences](https://github.com/kieranjol/IFIscripts#image-sequences)
    * [makedpx.py](https://github.com/kieranjol/IFIscripts#makedpxpy)
    * [seq2ffv1.py](https://github.com/kieranjol/IFIscripts#seq2ffv1py)
    * [seq2prores.py](https://github.com/kieranjol/IFIscripts#seq2prorespy)
    * [rawbatch.py](https://github.com/kieranjol/IFIscripts#rawbatchpy)
    * [seq.py](https://github.com/kieranjol/IFIscripts#seqpy)
	* [oeremove.py](https://github.com/kieranjol/IFIscripts#oeremovepy)
    * [renumber.py](https://github.com/kieranjol/IFIscripts#renumberpy)
    * [seq2dv.py](https://github.com/kieranjol/IFIscripts#seq2dvpy)
    * [batchmetadata.py](https://github.com/kieranjol/IFIscripts#batchmetadata)
	* [batchrename.py](https://github.com/kieranjol/IFIscripts#batchrename)
1. [Quality Control](https://github.com/kieranjol/IFIscripts#quality-control)
    * [qctools.py](https://github.com/kieranjol/IFIscripts#qctoolspy)
    * [ffv1mkvvalidate.py](https://github.com/kieranjol/IFIscripts#ffv1mkvvalidatespy)
1. [Specific Workflows](https://github.com/kieranjol/IFIscripts#specific-workflows)
    * [mezzaninecheck.py](https://github.com/kieranjol/IFIscripts#mezzaninecheckpy)
    * [loopline.py](https://github.com/kieranjol/IFIscripts#looplinepy)
    * [masscopy.py](https://github.com/kieranjol/IFIscripts#masscopypy)
    * [dvsip.py](https://github.com/kieranjol/IFIscripts#dvsippy)
    * [makefolders.py](https://github.com/kieranjol/IFIscripts#makefolderspy)
    * [looplinerepackage.py](https://github.com/kieranjol/IFIscripts#loopline_repackagespy)
1. [Misc](https://github.com/kieranjol/IFIscripts#misc)
    * [update.py](https://github.com/kieranjol/IFIscripts#updatepy)
    * [giffer.py](https://github.com/kieranjol/IFIscripts#gifferpy)
    * [makeuuid.py](https://github.com/kieranjol/IFIscripts#makeuuidpy)
    * [durationcheck.py](https://github.com/kieranjol/IFIscripts#durationcheckpy)
    * [fakexdcam.py](https://github.com/kieranjol/IFIscripts#fakexdcampy)
1. [Experimental-Premis](https://github.com/kieranjol/IFIscripts#experimental-premis)
    * [premis.py](https://github.com/kieranjol/IFIscripts#premispy)
    * [revtmd.py](https://github.com/kieranjol/IFIscripts#revtmdpy)
    * [as11fixity.py](https://github.com/kieranjol/IFIscripts#as11fixitypy)
    * [viruscheck.py](https://github.com/kieranjol/IFIscripts#viruscheckpy)

## summary ##

Scripts for use in the IFI Irish Film Archive. Scripts have been tested in OSX/Windows 7 (sometimes windows 10)  and Ubuntu 14.04. The aim is to make cross-platform scripts, but please get in touch with any issues. It is best to download all scripts, as some of them share code.

Most scripts take either a file or a directory as their input, for example `makeffv1.py filename.mov` or `premis.py path/to/folder_of_stuff`. (It's best to just drag and drop the folder or filename into the terminal)

Note: Documentation template has been copied from [mediamicroservices](https://github.com/mediamicroservices/mm)

NOTE: `Objects.py` has been copied from https://github.com/simsong/dfxml. `walk_to_dfxml.py` has also been copied but has been customised in order to add command line arguments for optionally turning off checksum generation. For more context, see https://github.com/simsong/dfxml/pull/28

## Arrangement ##

### sipcreator.py ###
* Accepts one or more files or directories as input and wraps them up in a directory structure in line with IFI procedures using `copyit.py`.
* Source objects will be stored in an /objects directory. Directory structure is: parent directory named with a UUID, with three child directories (objects, logs metadata):
* Metadata is extracted for the AV material and MD5 checksums are stored for the entire package. A log records the major events in the process.
* Usage for one directory - `sipcreator.py -i /path/to/directory_name -o /path/to/output_folder`
* Usage for more than one directory - `sipcreator.py -i /path/to/directory_name1 /path/to/directory_name2 -o /path/to/output_folder`
* Run `sipcreator.py -h` for all options.

### accession.py ###
* Accessions a package that has been through the Object Entry procedure.
* Currently this just works with packages that have been generated using `sipcreator.py`. SHA512 manifests are created,the OE number is replaced by an accession number, and the sipcreator logfile is updated with the various events that have taken place.
* Usage for one directory - `accession.py /path/to/directory_name`
* Run `accession.py -h` for all options.

### batchaccession.py ###
* Batch process packages by running `accession.py` and `makepbcore.py`
* The script will only process files with `sipcreator.py` style packages. `makeffv1.py` and `dvsip.py` packages will be ignored.
* Usage for processing all subdirectories - `batchaccession.py /path/to/directory_name`
* Run `batchaccession.py -h` for all options.


### order.py ###
* Audits logfiles to determine the parent of a derivative package.
* This script can aid in automating large accessioning procedures that involve the accessioning of derivatives along with masters, eg a Camera Card and a concatenated derivative, or a master file and a mezzanine.
* Currently, this script will return a value :`None`, or the parent `OE` number. It also prints the OE number in its `OE-XXXX` just for fun.
* Usage for one directory - `order.py /path/to/directory_name`

### makepbcore.py ###
* Describes AV objects using a combination of the PBCore 2 metadata standard and the IFI technical database.
* This script takes a folder as input. Either a single file or multiple objects will be described.
* This will produce a single PBCore CSV record per package, even if multiple objects are within a package. The use case here is complex packages such as XDCAM/DCP, where we want a single metadata record for a multi-file object.
* The CSV headings are written in such a way to allow for direct import into our SQL database.
* Usage for one directory - `makepbcore.py /path/to/directory_name`
* Run `makepbcore.py -h` for all options.

### deletefiles.py ###
* Deletes files after `sipcreator.py` has been run, but before `accession.py` has been run.
* Manifests are updated, metadata is deleted and the events are all logged in the logfile.
* This script takes the parent OE folder as input. Use the `-i` argument to supply the various files that should be deleted from the package.
* Usage for deleting two example files - `deletefiles.py /path/to/oe_folder -i path/to/file1.mov path/to/file2.mov`
* Run `deletefiles.py -h` for all options.

### rearrange.py ###
* Rearranges files into a subfolder files after `sipcreator.py` has been run, but before `accession.py` has been run.
* Manifests are updated, files are moved, and the events are all logged in the logfile.
* This is useful in conjunction with `sipcreator.py` and `deletefiles.py`, in case a user wishes to impose a different ordering of the files within a large package. For example, from a folder with 1000 photographs, you may wish to create some sufolders to reflect different series/subseries within this collection. This script will track all these arrangement decisions.
* This script takes the parent OE folder as input. Use the `-i` argument to supply the various files that should be moved. The `new_folder` argument declares which folder the files should be moved into. Run `validate.py` to verify that all went well.
* Usage for moving a single file into a subfolder - `rearrange.py /path/to/oe_folder -i path/to/uuid/objects/file1.mov -new_folder path/to/uuid/objects/new_foldername`
* Run `rearrange.py -h` for all options.

## Transcodes ##

### makeffv1.py ###
* Transcodes to FFV1.mkv and performs framemd5 validation. Accepts single files or directories (all video files in a directory will be processed). CSV report is generated which gives details on losslessness and compression ratio.
* Usage for single file - `makeffv1.py filename.mov`
* Usage for batch processing all videos in a directory - `makeffv1.py directory_name`

### bitc.py ###
* Create timecoded/watermarked h264s for single files or a batch process.
* Usage for single file - `bitc.py filename.mov`
* Usage for batch processing all videos in a directory - `bitc.py directory_name`
* This script has many extra options, such as deinterlacing, quality settings, rescaling. Use `bitc.py -h` to see all options

### prores.py ###
* Transcode to prores.mov for single/multiple files.
* Usage for single file - `prores.py filename.mov`
* Usage for batch processing all videos in a directory - `prores.py directory_name`
* This script has many extra options, such as deinterlacing, quality settings, rescaling. Use `prores.py -h` to see all options

### concat.py ###
* Concatenate/join video files together using ffmpeg stream copy into a single Matroska container. Each source clip will have its own chapter marker. As the streams are copied, the speed is quite fast.
* Usage: `concat.py -i /path/to/filename1.mov /path/to/filename2.mov -o /path/to/destination_folder`
* A lossless verification process will also run, which takes stream level checksums of all streams and compares the values. This is not very reliable at the moment.
* Warning - video files must have the same technical attributes such as codec, width, height, fps. Some characters in filenames will cause the script to fail. Some of these include quotes. The script will ask the user if quotes should be renamed with underscores. Also, a temporary concatenation textfile will be stored in your temp folder. Currently only tested on Ubuntu.
* Dependencies: mkvpropedit, ffmpeg.
## Digital Cinema Package Scripts ##

### dcpaccess.py ###
* Create h264 (default)  or prores transcodes (with optional subtitles) for unencrypted, single/multi reel Interop/SMPTE DCPs. The script will search for all DCPs in subdirectories, process them one at a time and export files to your Desktop.
* Usage: `dcpaccess.py dcp_directory`
* Use `-p` for prores output, and use `-hd` to rescale to 1920:1080 while maintaining the aspect ratio.
* Dependencies: ffmpeg must be compiled with libopenjpeg -  `brew install ffmpeg --with-openjpeg`.
* Python dependencies: lxml required.
* Further options can be viewed with `dcpaccess.py -h`

### dcpfixity.py ###
* Verify internal hashes in a DCP and write report to CSV. Optional (experimental) bagging if hashes validate. The script will search for all DCPs in subdirectories, process them one at a time and generate a CSV report.
* Usage: `dcpfixity.py dcp_directory`
* Further options can be viewed with `dcpfixity.py -h`

### dcpsubs2srt.py ###
* Super basic but functional DCP XML subtitle to SRT conversion. This code is also contained in dcpaccess.py
* Usage: `dcpsubs2srt.py subs.xml`

## Fixity Scripts ##

### copyit.py ###
* Copies a file or directory, creating a md5 manifest at source and destination and comparing the two. Skips hidden files and directories.
* Usage: ` moveit.py source_dir destination_dir`
* Dependencies:  OSX requires gcp - `brew install coreutils`

### manifest.py ###
* Creates relative md5 or sha512 checksum manifest of a directory.
* Usage: ` manifest.py directory` or for sha512 hashes: ` manifest.py -sha512 directory`
* By default, these hashes are stored in a desktop directory, but use the `-s` option in order to generate a sidcecar in the same directory as your source.
* Run `manifest.py -h` to see all options.

### makedfxml.py ###
* WARNING - until this issue is resolved, this script can not work with Windows: https://github.com/simsong/dfxml/issues/29
* Prints Digital Forensics XML to your terminal. Hashes are turned off for now as these will usually already exist in a manifest. The main purpose of this script is to preserve file system metadata such as date created/date modified/date accessed.
* This is a launcher script for an edited version of 'https://github.com/simsong/dfxml/blob/master/python/walk_to_dfxml.py'. The edited version of `walk_to_dfxml.py` and the `Objects.py` library have been copied into this repository for the sake of convenience.
* Usage: ` makedfxml.py directory`.
* NOTE: This is currently a proof of concept. Further options, logging and integration into other scripts will be needed.
* There may be a python3 related error on OSX if python is installed via homebrew. This can be fixed by typing `unset PYTHONPATH` in the terminal.

### sha512deep.py ###
* Quick proof of concept sha512 checksum manifest generator as not many command line tools support sha512 right now. name is a play on the hashdeep toolset.
* Usage: ` sha512deep.py directory`

### validate.py ###
* Validate md5 or SHA512 sidecar manifests. Currently the script expects two spaces between the checksum and the filename.
* In packages that have been generated with sipcreator.py, the results of the process will be added to the logfile and the checksum for the logfile will update within the md5 and sha512 manifests
* Usage: ` validate.py /path/to/manifest.md5` or ` validate.py /path/to/_manifest-sha512.txt`

### batchfixity.py ###
* Batch MD5 checksum generator. Accepts a parent folder as input and will generate manifest for each subfolder. Designed for a specific IFI Irish Film Archive workflow.
* Usage: ` batchfixity.py /path/to/parent_folder`

## Image Sequences ##

### makedpx.py ###
* Transcode TIFFs losslessly to DPX. Processess all sequeneces in every subdirectory. WARNING - Currently relies on a local config file - soon to be removed!
* Framemd5s of source and output are created and verified for losslessness.
* Whole file manifest is created for all files.
* Usage: `makedpx.py parent_folder -o destination_folder` - generally we have 10 sequences in subfolders, so we pass the parent folder as input.

### seq2ffv1.py ###
* Work in progress -more testing to be done.
* Recursively batch process image sequence folders and transcode to a single ffv1.mkv.
* Framemd5 files are generated and validated for losslessness.
* Whole file manifests are also created.
* Usage - `seq2ffv1.py parent_folder`

### seq2prores.py ###
* Specific IFI workflow that expects a particular folder path:
* Recursively batch process image sequence folders with seperate WAV files and transcode to a single Apple Pro Res HQ file in a MOV container. PREMIS XML log files are generated with hardcoded IFI values for the source DPX sequence and the transcoded mezzanine file in the respective /metadata directory
* A whole file MD5 manifest of everything in the SIP are also created. Work in progress - more testing to be done.
* Usage - `seq2prores.py directory`
* seq2prores accepts multiple parent folders, so one can run `seq2prores.py directory1 directory2 directory3` etc

### rawbatch.py ###
* Specific IFI workflow that expects a particular folder path:
* Recursively batch processes image sequence folders with seperate WAV files, generating PREMIS XML log files with hardcoded IFI values.
* A duplicate audio WAV file is created and sent to desktop as workhorse.
* A whole file MD5 manifest of everything in the SIP are also created. Work in progress - more testing to be done.
* Usage - `rawbatch.py directory`
* rawbatch accepts multiple parent folders, so one can run `rawbatch.py directory1 directory2 directory3` etc

### seq.py ###
* Transcodes a TIFF sequence to 24fps v210 in a MOV container.
* Usage: `seq.py path/to/tiff_folder` and output will be stored in the parent directory.
* Further options can be viewed using `seq.py -h`

### playerseq.py ###
* Transcodes an image sequence & WAV to 24fps ProRes 4:2:2 HQ in a MOV container.
* Usage: `playerseq.py path/to/parent_image__folder`.The script will then ask you to drag and drop the WAV file. The location is currently hardcoded to facilitate a workflow.

### oeremove.py ###
* IFI specific script that removes OE### numbers from the head of an image sequence filename.
* Usage - `oeremove.py directory`.

### renumber.py ###
* Renames TIFF files in an image sequence so that they start from ZERO (000000)
* Usage - `renumber.py directory`

### seq2dv.py ###
* Transcodes a TIFF sequence to 24fps 720x576 DV in a MOV container.
* Usage: `seq.py path/to/tiff_folder` and output will be stored in the parent directory.

### batchmetadata.py ###
* Traverses through subdirectories trying to find DPX and TIFF files and creates mediainfo and mediatrace XML files.
* Usage: `batchmetadata.py path/to/parent_directory` and output will be stored in the parent directory.

### batchrename.py ###
* Renames TIFF files in an image sequence except for numberic sequence and file extension.
* Usage - `batchrename.py directory` - enter new filename when prompted

## Quality Control ##

### qctools.py ###
* Generate QCTools xml.gz sidecar files which will load immediately in QCTools.
* Usage for single file - `qctools.py filename.mov`
* Usage for batch processing all videos in a directory - `qctools.py directory_name`


### ffv1mkvvalidate.py ###
* Validates Matroska files using mediaconch.
* An XML report will be written to the metadata directory.
* A log will appear on the desktop, which will be merged into the SIP log in /logs.
* Usage for batch processing all videos in a directory - `ffv1mkvvalidate.py directory_name`

## Specific Workflows ##

### mezzaninecheck.py ###
* Checks folders in order to see if either 0 or >1 files exist in a mezzanine/objects folder.
* 
* Usage: `mezzaninecheck.py /path/to/parent_folder`

### loopline.py ###
* Workflow specific to the Loopline project.
* makeffv1.py and bitc.py are run on the input, unless a DV file is present, in which case bitc.py and dvsip.py will be run.
* A proxies folder for the h264 files will be created within your parent folder if it does not already exist.
* Usage: `loopline.py /path/to/parent_folder` or `loopline.py /path/to/file`

### masscopy.py ###
* Copies all directories in your input location using moveit.py ONLY if a manifest sidecar already exists.
* This is useful if a lot of SIPs produced by makeffv1 are created and you want to move them all to another location while harnessing the pre-existing checksum manifest.
* WARNING - It is essential to check the log file on the desktop/ifiscripts_logs for each folder that transferred!!
* Usage: `masscopy.py /path/to/parent_folder -o /path/to/destination_folder`

### dvsip.py ###
* Creates SIP for DV video files. Generates objects/logs/metadata dirs and creates mediatrace, mediainfo, framemd5, logfiles, MD5 sidecar and moves the DV file into the objects directory.
* Usage: `dvsip.py /path/to/parent_folder` or `dvsip.py /path/to/file`

### makefolders.py ###
* Creates a logs/objects/metadata folder structure with a UUID parent folder. This is specific to a film scanning workflow as there are seperate audio and image subfolders. You can specifiy the values on the command line or a terminal interview will appear which will prompt you for filmographic reference number, source accession number and title. Use `makefolders.py -h` for the full list of options.
* Usage: `makefolders.py -o /path/to/destination`

### loopline_repackage.py ###
* Retrospectively updates older FFV1/DV packages in order to meet our current packaging requirements. This should allow accession.py and makepbcore.py to run as expected. This will process a group of packages and each loop will result in the increment by one of the starting OE number. Use with caution.
* This script should work on files created by `makeffv1.py dvsip.py loopline.py`
* Usage: `loopline_repackage`


## Misc ##

### update.py ###
* Updates IFIscripts to the latest git head if the following directory structure exists in the home directory: `ifigit/ifiscripts`
* Usage: `update.py`

### giffer.py ###
* Makes a 24fps 500px gif of the input file.
* Usage: `giffer.py /path/to/input`

### makeuuid.py ###
* Prints a new UUID to the terminal via the UUID python module and the create_uuid() helper function within ififuncs.
* Usage: `makeuuid.py`

### durationcheck.py ###
* Recursive search through subdirectories and provides total duration in minutes. Accepts multiple inputs but provides the total duration of all inputs.
* Usage: `durationcheck.py /path/to/parent_folder` or `durationcheck.py /path/to/parent_folder1 /path/to/parent_folder2 /path/to/parent_folder3` 

### fakexdcam.py ###
* Creates a fake XDCAM EX structure for testing purposes
* Usage: `fakexdcam.py /path/to/output_folder`

## Experimental-Premis ##

### premis.py ###
* Work in progress PREMIS implementation. This PREMIS document will hopefully function as a growing log file as an asset makes its way through a workflow.
* Requries pyqt4 (GUI) and lxml (xml parsing)
* Usage - `premis.py filename`.

### revtmd.py ###
* Beta/defuncy sript that attempted to document creation process history metadata using the reVTMD standard.

### as11fixity.py ###
* Work in progress script by @mahleranja and @ecodonohoe
* There is a bash script in a different repository that works quite well for this purpose but that is OSX only.

### viruscheck.py ###
* Work in progress script by @ecodonohoe
* Scans directories recursively using ClamAV
