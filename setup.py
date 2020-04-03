#!/usr/bin/env python3
import sys
from setuptools import setup

if sys.version_info < (3, 8):
    print("Python 3.8 or higher is required - earlier python 3 versions may work but were not tested.")
    sys.exit(1)
setup(
    author='Kieran O\'Leary',
    author_email='kieran.o.leary@gmail.com',
    description="Scripts for processing moving image material in the Irish Film Institute/Irish Film Archive",
    long_description=("""\
Scripts for use in the IFI Irish Film Archive. Scripts have been tested in OSX/Windows 7/10 and Ubuntu 18.04. The aim is to make cross-platform scripts, but please get in touch with any issues. It is best to download all scripts, as some of them share code.

Most scripts take either a file or a directory as their input, for example makeffv1.py filename.mov or premis.py path/to/folder_of_stuff. (It's best to just drag and drop the folder or filename into the terminal)

Note: Documentation template has been copied from mediamicroservices

NOTE: Objects.py has been copied from https://github.com/simsong/dfxml. walk_to_dfxml.py has also been copied but has been customised in order to add command line arguments for optionally turning off checksum generation. For more context, see https://github.com/simsong/dfxml/pull/28
"""),
    scripts=[
        'Objects.py',
        'accession.py',
        'accession_register.py',
        'batchaccession.py',
        'batchsipcreator.py',
        'bitc.py',
        'concat.py',
        'copyit.py',
        'dcpaccess.py',
        'dcpfixity.py',
        'deletefiles.py',
        'dfxml.py',
        'durationcheck.py',
        'ffv1mkvvalidate.py',
        'framemd5.py',
        'ififuncs.py',
        'loopline_repackage.py',
        'makedfxml.py',
        'makedip.py',
        'makeffv1.py',
        'makepbcore.py',
        'makeuuid.py',
        'makezip.py',
        'manifest.py',
        'masscopy.py',
        'massqc.py',
        'mergepbcore.py',
        'multicopy.py',
        'normalise.py',
        'order.py',
        'package_update.py',
        'packagecheck.py',
        'prores.py',
        'seq2ffv1.py',
        'sipcreator.py',
        'strongbox_fixity.py',
        'subfolders.py',
        'testfiles.py',
        'validate.py',
        'walk_to_dfxml.py'
    ],
    license='MIT',
    install_requires=[
        'lxml',
        'bagit',
        'dicttoxml',
        'future',
        'clairmeta'
    ],
    data_files=[('', ['film_scan_aip_documentation.txt', '26_XYZ-22_Rec709.cube'])],
    include_package_data=True,
    name='ifiscripts',
    version='v2020.04.03.1',
    python_requires='>=3.8'
)
