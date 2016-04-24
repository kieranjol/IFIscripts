# IFIscripts
Scripts for use in the IFI Irish Film Archive

reVTMD script is in beta. and is very much geared around one specific workflow.<br><br>
Dcpfixity works well as long as there is one CPL. It currently can't verify fonts as I do not know how to extract a UUID from a font. Please get in touch if you know how.<br>

<h1>Usage for pretty much all scripts:<br></h1>
python scriptname.py filename<br>
<br>
<b>EXCEPT:</b> <br>

Some scripts, such as bitc.py or prores.py also accept a directory as input in order to batch process files.<br>
<br>
As for  dcpfixity.py, it accepts the DCP directory as input <br>
python dcpfixity.py dcp_directory
<br><br>
dcpfixity requires openssl and lxml. The latter can be installed with pip.
