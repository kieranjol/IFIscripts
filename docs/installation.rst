Installation
===========

General
------------
In general, you can just clone or download the whole repository (https://github.com/kieranjol/IFIscripts)  and run the scripts from your cloned path. In the Irish Film Institute, on linux, OSX and Windows, we create a folder in the home directory called ``ifigit``, then we run ``git clone https://github.com/kieranjol/ifiscripts``. Then we add the ``ifiscripts`` folder to ``$PATH`` which allows us to access the scripts from any directory, not just ``ifigit/ifiscripts``. We will be moving to using ``pip`` and ``setup.py`` for installs and updates in the future.

However some folks just ``cd`` into the cloned repository and run the scripts from there, for example to run ``makeffv1.py`` you might run:
``python makeffv1.py path/to.filename.mov``.

External dependencies are listed below, but ``lxml`` is the main python library that must be installed for most scripts.
``pip install lxml`` should work fine.

Using pip/setup.py
------------

the following is currently experimental, but it should work fine:

You can get a selection of scripts by making sure that ``pip`` installed, then running:
``pip install ifiscripts``
or ``cd`` into the ``ifiscripts`` cloned folder and run
``python setup.py install``

The pip installation methods have the added benefit of installing the python dependencies such as ``lxml``.

External Dependencies
---------------------
There are some external `subprocess` dependencies for most of the scripts. The most frequently used ones are:

* ffmpeg
* mediainfo

but the following are also needed for many scripts:

* mkvpropedit
* siegfried
* exiftool




