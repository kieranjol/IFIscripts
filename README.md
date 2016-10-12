IFIscripts documentation
==================

table of contents
-------------------

1. [summary](https://github.com/kieranjol/IFIscripts#summary)
2. [Transcodes](https://github.com/kieranjol/IFIscripts#transcodes)
    * [makeffv1.py](https://github.com/kieranjol/IFIscripts#makeffv1py)
    * [bitc.py](https://github.com/kieranjol/IFIscripts#bitcpy)
    * [prores.py](https://github.com/kieranjol/IFIscripts#prorespy)
3. [Digital Cinema Package Scripts](https://github.com/kieranjol/IFIscripts#digital-cinema-package-scripts)
	* [dcpaccess.py](https://github.com/kieranjol/IFIscripts#dcpaccesspy)
    * [dcpfixity.py](https://github.com/kieranjol/IFIscripts#dcpfixitypy)
    * [dcpsubs2srt.py](https://github.com/kieranjol/IFIscripts#dcpsubs2srtpy)   
4. [Fixity Scripts](https://github.com/kieranjol/IFIscripts#fixity-scripts)
    * [moveit.py](https://github.com/kieranjol/IFIscripts#moveitpy)
    * [manifest.py](https://github.com/kieranjol/IFIscripts#manifest.py)
    * [sha512deep.py](https://github.com/kieranjol/IFIscripts#sha512deep.py)    
5. [Image Sequences](https://github.com/kieranjol/IFIscripts#image-sequences)
    * [makedpx.py](https://github.com/kieranjol/IFIscripts#makedpxpy)
    * [seq2ffv1.py](https://github.com/kieranjol/IFIscripts#seq2ffv1py)
    * [seq2prores.py](https://github.com/kieranjol/IFIscripts#seq2prorespy)
    * [seq.py](https://github.com/kieranjol/IFIscripts#seqpy)
	* [oeremove.py](https://github.com/kieranjol/IFIscripts#oeremovepy)
    * [renumber.py](https://github.com/kieranjol/IFIscripts#renumberpy)
5. [Quality Control](https://github.com/kieranjol/IFIscripts#quality-control)
    * [qctools.py](https://github.com/kieranjol/IFIscripts#qctoolspy)
6. [Specific Workflows](https://github.com/kieranjol/IFIscripts#specific-workflows)
    * [rawaudio.py](https://github.com/kieranjol/IFIscripts#rawaudiopy)
    * [treatedaudio.py](https://github.com/kieranjol/IFIscripts#treatedaudiopy)
7. [Misc](https://github.com/kieranjol/IFIscripts#misc)
    * [update.py](https://github.com/kieranjol/IFIscripts#updatepy)
8. [Experimental-Premis](https://github.com/kieranjol/IFIscripts#experimental-premis)
    * [premis.py](https://github.com/kieranjol/IFIscripts#premispy)
    * [revtmd.py](https://github.com/kieranjol/IFIscripts#revtmdpy)
    * [as11fixity.py](https://github.com/kieranjol/IFIscripts#as11fixitypy)

## summary ##
    
Scripts for use in the IFI Irish Film Archive. Scripts have been tested in OSX/Windows 7 (sometimes windows 10)  and Ubuntu 14.04. The aim is to make cross-platform scripts, but please get in touch with any issues. It is best to download all scripts, as some of them share code.

Most scripts take either a file or a directory as their input, for example `makeffv1.py filename.mov` or `premis.py path/to/folder_of_stuff`. (It's best to just drag and drop the folder or filename into the terminal)

Note: Documentation template has been copied from [mediamicroservices](https://github.com/mediamicroservices/mm)

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

## Digital Cinema Package Scripts ##

### dcpaccess.py ###
* Create h264 or prores transcodes (with optional subtitles) for unencrypted, single/multi reel Interop/SMPTE DCPs. The script will search for all DCPs in subdirectories, process them one at a time and export files to your Desktop. 
* Usage: `dcpaccess.py dcp_directory`
*Further options can be viewed with `dcpaccess.py -h`

### dcpfixity.py ###
* Verify internal hashes in a DCP and write report to CSV. Optional (experimental) bagging if hashes validate. The script will search for all DCPs in subdirectories, process them one at a time and generate a CSV report.
* Usage: `dcpfixity.py dcp_directory`
* Further options can be viewed with `dcpfixity.py -h`

### dcpsubs2srt.py ###
* Super basic but functional DCP XML subtitle to SRT conversion. This code is also contained in dcpaccess.py
* Usage: `dcpsubs2srt.py subs.xml`

## Fixity Scripts ##

### moveit.py ###
* Copies a directory, creating a md5 manifest at source and destination and comparing the two. Skips hidden files and directories. 
* Usage: ` moveit.py source_dir destination_dir` 

### manifest.py ###
* Creates relative md5 checksum manifest of a directory.
* Usage: ` manifest.py directory` 

### sha512deep.py ###
* Quick proof of concept sha512 checksum manifest generator as not many command line tools support sha512 right now. name is a play on the hashdeep toolset.
* Usage: ` sha512deep.py directory` 

## Image Sequences ##

### makedpx.py ###
* Transcode TIFFs losslessly to DPX. Processess all sequeneces in every subdirectory. WARNING - Currently relies on a local config file - soon to be removed!
* Framemd5s of source and output are created and verified for losslessness. 
* Whole file manifest is created for all files.
* Usage: `makedpx.py parent_folder` - generally we have 10 sequences in subfolders, so we pass the parent folder as input.

### seq2ffv1.py ###
* Work in progress -more testing to be done.
* Recursively batch process image sequence folders and transcode to a single ffv1.mkv.
* Framemd5 files are generated and validated for losslessness.
* Whole file manifests are also created.
* Usage - `seq2ffv1.py parent_folder`

### seq2prores.py ###
* Specific IFI workflow that expects a particular folder path:
* Recursively batch process image sequence folders with seperate WAV files and transcode to a single Apple Pro Res HQ file in a MOV container.
* A whole file MD5 manifest of everything in the SIP are also created. Work in progress - more testing to be done.
* Usage - `seq2prores.py directory`

### seq.py ###
* Transcodes a TIFF sequence to 24fps v210 in a MOV container. 
* Usage: `seq.py first_file_00001.tiff` and output will be stored in the parent directory.

### oeremove.py ###
* IFI specific script that removes OE### numbers from the head of an image sequence filename.
* Usage - `oeremove.py directory`.

### renumber.py ###
* Renames TIFF files in an image sequence so that they start from ZERO (000000) 
* Usage - `renumber.py directory`

## Quality Control ##

### qctools.py ###
* Generate QCTools xml.gz sidecar files which will load immediately in QCTools.
* Usage for single file - `qctools.py filename.mov`
* Usage for batch processing all videos in a directory - `qctools.py directory_name`

## Specific Workflows ##

### rawaudio.py ###
* Performs various preservation actions on a WAV file produced from a film scan: 
    * Subfolder creation/checksum creation/framemd5 creation/file duplication/metadata extraction.
* Usage: `rawaudio.py wav_filename.wav`

### treatedaudio.py ###
* Performs various preservation actions on a restored WAV file produced from a film scan: 
    * Subfolder creation/checksum creation/framemd5 creation/file duplication/metadata extraction.
* Usage: `treatedaudio.py wav_filename.wav`

## Misc ##

### update.py ###
* Updates IFIscripts to the latest git head if the following directory structure exists in the home directory: `ifigit/ifiscripts`
* Usage: `update.py`

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
