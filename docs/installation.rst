Installation
============

General
-------

This is a python 3.8 project.

In general, you can just clone or download the whole repository (https://github.com/kieranjol/IFIscripts)  and run the scripts from your cloned path. In the Irish Film Institute, on linux, OSX and Windows, we create a folder in the home directory called ``ifigit``, then we run ``git clone https://github.com/kieranjol/ifiscripts``. Then we add the ``ifiscripts`` folder to ``$PATH`` which allows us to access the scripts from any directory, not just ``ifigit/ifiscripts``. We will be moving to using ``pip`` and ``setup.py`` for installs and updates in the future.

However some folks just ``cd`` into the cloned repository and run the scripts from there, for example to run ``makeffv1.py`` you might run:
``python makeffv1.py path/to.filename.mov``.

External dependencies are listed below, but ``lxml`` is the main python library that must be installed for most scripts.
``pip install lxml`` should work fine.

Using pip/setup.py
------------------

the following is currently experimental, but it should work fine:

You can get a selection of scripts by making sure that ``pip`` installed, then running:
``pip install ifiscripts``
or ``cd`` into the ``ifiscripts`` cloned folder and run
``pip install .``

You may need to run the ``pip`` commands with ``sudo``.

The pip installation methods have the added benefit of installing the python dependencies such as ``lxml``.

External Dependencies
---------------------
There are some external ``subprocess`` dependencies for most of the scripts. The most frequently used ones are:

* ffmpeg
* ffprobe
* mediainfo

but the following are also needed for many scripts:

* mkvpropedit (installed via mkvtoolnix)
* siegfried aka sf
* exiftool
* git
* clairmeta (this requires other dependencies - https://github.com/Ymagis/ClairMeta)
* qcli
* openssl
* rsync
* gcp (installed via gnu-coreutils on OSX)
* rawcooked
* 7zip aka 7za aka p7zip
* md5deep
* mediaconch

A lot of these can be installed on Ubuntu with a single line:
sudo apt update && sudo apt install ffmpeg mkvtoolnix exiftool git md5deep p7zip
In order to add the rest, refer to the installation instructions of the relevant tools.
For mediaarea tools, it can be easiest to use their own snapshot repository:
``wget https://mediaarea.net/repo/deb/repo-mediaarea-snapshots_1.0-13_all.deb && sudo dpkg -i repo-mediaarea-snapshots_1.0-13_all.deb && sudo apt update && sudo apt install mediainfo dvrescue qcli rawcooked mediaconch``
