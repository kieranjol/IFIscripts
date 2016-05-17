# IFIscripts
Scripts for use in the IFI Irish Film Archive

Current scripts that are useful:

<b>dcpaccess.py</b> - Create h264 or prores transcodes (with optional subtitles) for unencrypted, single/multi reel Interop/SMPTE DCPs.

<b>dcpfixity.py</b> - Verify internal hashes in a DCP and write report to CSV. Optional (experimental) bagging if hashes validate.

<b>dcpsubs2srt.py</b> - Super basic but functional DCP XML subtitle to SRT conversion. This code is also contained in dcpaccess.py

<b>bitc.py</b> - Create timecoded/watermarked h264s for single files or a batch process.

<b>prores.py</b> - Transcode to prores.mov for single/multiple files. Type `prores.py -h` for instructions.

Experimental scripts: 

<b>reVTMD.py<b/> is in beta. and is very much geared around one specific workflow.<br><br>

<b>makeffv1.py</b> needs more options and needs batch functionality built in.

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
