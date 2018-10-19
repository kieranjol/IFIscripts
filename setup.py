from setuptools import setup
setup(
    author='Kieran O\'Leary',
    author_email='kieran.o.leary@gmail.com',
    description="Scripts for processing moving image material in the Irish Film Institute/Irish Film Archive",
    long_description=("""\
Scripts for use in the IFI Irish Film Archive. Scripts have been tested in OSX/Windows 7 (sometimes windows 10) and Ubuntu 14.04. The aim is to make cross-platform scripts, but please get in touch with any issues. It is best to download all scripts, as some of them share code.

Most scripts take either a file or a directory as their input, for example makeffv1.py filename.mov or premis.py path/to/folder_of_stuff. (It's best to just drag and drop the folder or filename into the terminal)

Note: Documentation template has been copied from mediamicroservices

NOTE: Objects.py has been copied from https://github.com/simsong/dfxml. walk_to_dfxml.py has also been copied but has been customised in order to add command line arguments for optionally turning off checksum generation. For more context, see https://github.com/simsong/dfxml/pull/28
"""),
    scripts=[
        'sipcreator.py',
        'ififuncs.py',
        'copyit.py',
        'masscopy.py',
        'accession.py',
        'accession_register.py',
        'batchaccession.py',
        'concat.py',
        'makeffv1.py',
        'loopline.py',
        'makepbcore.py',
        'manifest.py',
        'validate.py',
        'Objects.py',
        'makedfxml.py',
        'dfxml.py',
        'walk_to_dfxml.py',
        'bitc.py',
        'prores.py',
        'dcpfixity.py',
        'dcpaccess.py',
        'deletefiles.py',
        'package_update.py',
        'durationcheck.py',
        'ffv1mkvvalidate.py',
        'loopline_repackage.py',
        'seq2ffv1.py',
        'makeuuid.py',
        'masscopy.py',
        'packagecheck.py',
        'testfiles.py',
        'normalise.py'
    ],
    license='MIT',
    install_requires=[
       'lxml',
       'bagit'
    ],
    name='ifiscripts',
    version='v2018.10.18',
    include_package_data=True
)
