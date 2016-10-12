IFIscripts documentation
==================

table of contents
-------------------

1. [summary](https://github.com/kieranjol/IFIscripts#summary)
2. [Script documentation](https://github.com/kieranjol/IFIscripts#functions)
	* [dcpaccess.py](https://github.com/kieranjol/IFIscripts#dcpaccesspy)
    * [dcpfixity.py](https://github.com/kieranjol/IFIscripts#dcpfixitypy)
    * [dcpsubs2srt.py](https://github.com/kieranjol/IFIscripts#dcpsubs2srtpy)
    * [makedpx.py](https://github.com/kieranjol/IFIscripts#makedpxpy)
    * [bitc.py](https://github.com/kieranjol/IFIscripts#bitcpy)
    * [prores.py](https://github.com/kieranjol/IFIscripts#prorespy)
    * [makeffv1.py](https://github.com/kieranjol/IFIscripts#makeffv1py)
    * [seq.py](https://github.com/kieranjol/IFIscripts#seqpy)
    * [moveit.py](https://github.com/kieranjol/IFIscripts#moveitpy)
3. [Experimental scripts documentation](https://github.com/kieranjol/IFIscripts#experimental)
	* [oeremove.py](https://github.com/kieranjol/IFIscripts#oeremovepy)
    * [renumber.py](https://github.com/kieranjol/IFIscripts#renumberpy)
    * [seq2ffv1.py](https://github.com/kieranjol/IFIscripts#seq2ffv1py)
    * [seq2prores.py](https://github.com/kieranjol/IFIscripts#seq2prorespy)
    * [premis.py](https://github.com/kieranjol/IFIscripts#premispy)

## summary ##
    
Scripts for use in the IFI Irish Film Archive. Scripts have been tested in OSX/Windows 7 (sometimes windows 10)  and Ubuntu 14.04. The aim is to make cross-platform scripts, but please get in touch with any issues. It is best to download all scripts, as some of them share code.

Most scripts take either a file or a directory as their input, for example `makeffv1.py filename.mov` or `premis.py path/to/folder_of_stuff` 
## functions ##

#### dcpaccess.py ####
* Usage: `dcpaccess.py dcp_directory`- Create h264 or prores transcodes (with optional subtitles) for unencrypted, single/multi reel Interop/SMPTE DCPs. The script will search for all DCPs in subdirectories, process them one at a time and export files to your Desktop. 

Further options can be viewed with `dcpaccess.py -h`

#### dcpaccess.py ####
<b>dcpfixity.py</b> - Verify internal hashes in a DCP and write report to CSV. Optional (experimental) bagging if hashes validate. The script will search for all DCPs in subdirectories, process them one at a time and generate a CSV report.

<b>Usage:</b> `dcpfixity.py dcp_directory`

Further options can be viewed with `dcpfixity.py -h`

#### dcpsubs2srt.py ####
<b>dcpsubs2srt.py</b> - Super basic but functional DCP XML subtitle to SRT conversion. This code is also contained in dcpaccess.py

#### makedpx.py ####
<b>makedpx.py</b> - Transcode TIFFs losslessly to DPX. Framemd5s of source and output are created and verified for losslessness. Whole file manifest is created for all files.

#### bitc.py ####
<b>bitc.py</b> - Create timecoded/watermarked h264s for single files or a batch process.

#### prores.py ####
<b>prores.py</b> - Transcode to prores.mov for single/multiple files. Type `prores.py -h` for instructions.

#### makeffv1.py ####
<b>makeffv1.py</b> Transcodes to FFV1.mkv and performs framemd5 validation. Accepts single files or directories (all video files in a directory will be processed). CSV report is generate which gives details on losslessness. 

#### seq.py ####
<b>seq.py</b> Transcodes a TIFF sequence to 24fps v210.mov Usage: ` seq.py first_file_00001.tiff` and output will be stored in the parent directory.

#### moveit.py ####
<b>move.py</b> Copies a directory, creating a md5 manifest at source and destination and comparing the two. Usage: ` move.py source_dir destination_dir` 

## experimental ##

#### oeremove.py ####
<b>oeremove.py</b> Usage - `oeremove.py directory`. IFI specific script that removes OE#### numbers from the head of an image sequence filename. <br><br>

#### renumber.py ####
<b>renumber.py</b> Usage - `renumber.py directory`. Renames TIFF files in an image sequence so that they start from ZERO (000000) <br><br>

#### seq2ffv1.py ####
<b>seq2ffv1.py</b> Usage - `seq2ffv1.py directory`. Recursively batch process image sequence folders and transcode to a single ffv1.mkv. Framemd5 files are generated and validated for losslessness. Whole file manifests of the SIP are also created. Work in progress -more testing to be done. <br><br>

#### seq2prores.py ####
<b>seq2prores.py</b> Usage - `seq2prores.py directory`. Recursively batch process image sequence folders with seperate WAV files and transcode to a single Apple Pro Res HQ file in a MOV container. It expects a specific directory path where an audio folder contains a WAV file. A whole file MD5 manifest of everything in the SIP are also created. Work in progress - more testing to be done. <br><br>

#### premis.py ####
<b>premis.py</b> Usage - `premis.py filename`. Work in progress PREMIS implementation. This PREMIS document will hopefully function as a growing log file as an asset makes its way through a workflow.<br><br>

<b>move.py</b> Usage - `move.py source destination`. Creates manifest before and after copying and diffs the two manifests.<br><br>
<b>reVTMD.py</b> is in beta. and is very much geared around one specific workflow.<br><br>

<b>as11fixity.py</b> - Work in progress that we are working on as a training exercise. There is a bash script in a different repository that works quite well for this purpose.

<h1>Usage for pretty much all scripts:<br></h1>
python scriptname.py filename<br>
<br>
<b>EXCEPT:</b> <br>

Some scripts, such as bitc.py or prores.py also accept a directory as input in order to batch process files.<br>
<br>
`dcpfixity.py` and `dcpaccess.py` accept the DCP directory as input <br>

`python dcpfixity.py dcp_directory`
<br><br>
dcpfixity requires openssl and lxml. The latter can be installed with pip.
