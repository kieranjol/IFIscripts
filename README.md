# IFIscripts
Scripts for use in the IFI Irish Film Archive

Scripts have been tested in OSX/Windows 7 and Ubuntu 14.04. The aim is to make cross-platform scripts, but please get in touch with any issues.

Current scripts that are useful:

<b>dcpaccess.py</b> - Create h264 or prores transcodes (with optional subtitles) for unencrypted, single/multi reel Interop/SMPTE DCPs. The script will search for all DCPs in subdirectories, process them one at a time and export files to your Desktop.

<b>Usage:</b> `dcpaccess.py dcp_directory`

Further options can be viewed with `dcpaccess.py -h`

<b>dcpfixity.py</b> - Verify internal hashes in a DCP and write report to CSV. Optional (experimental) bagging if hashes validate. The script will search for all DCPs in subdirectories, process them one at a time and generate a CSV report.

<b>Usage:</b> `dcpfixity.py dcp_directory`

Further options can be viewed with `dcpfixity.py -h`

<b>dcpsubs2srt.py</b> - Super basic but functional DCP XML subtitle to SRT conversion. This code is also contained in dcpaccess.py

<b>bitc.py</b> - Create timecoded/watermarked h264s for single files or a batch process.

<b>prores.py</b> - Transcode to prores.mov for single/multiple files. Type `prores.py -h` for instructions.

<b>makeffv1.py</b> Transcodes to FFV1.mkv and performs framemd5 validation. Accepts single files or directories (all video files in a directory will be processed). CSV report is generate which gives details on losslessness. 

<b>seq.py</b> Transcodes a TIFF sequence to 24fps v210.mov Usage: ` seq.py first_file_00001.tiff` and output will be stored in the parent directory.

<b>move.py</b> Copies a directory, creating a md5 manifest at source and destination and comparing the two. Usage: ` move.py source_dir destination_dir` 

Experimental scripts: 
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
dcpfixity.py and dcpaccess.py accept the DCP directory as input <br>

python dcpfixity.py dcp_directory
<br><br>
dcpfixity requires openssl and lxml. The latter can be installed with pip.
