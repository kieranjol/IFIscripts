Contributing
============

Contributions are very much welcome in any form. Feel free to raise an issue requesting a new feature, or to report a bug. If reporting a bug, please copy/paste the full, complete, uncut terminal output.

Pull requests are welcome. If contributing code, it can be nice to run it through `pylint` first, as this will check for PEP-08 compliance. I'd rather get the code contribution in pretty much any form, so this is not necessary.

Generally, we try to limit the use of dependencies, so we try to do as much in `python` as possible. This can be seen in any scripts that generate checksums. We slowly moved away from using the wonder `md5deep` and used the python internal `hashlib` libraries instead. 

Some good first contributions could be adding explanatory docstrings to libraries like ``ififuncs.py``, or revising older scripts, such as ``validate.py`` so that they are more in line with the coding style of recent scripts. Some of our ``main()`` functions are far too long and are doing too much, so they are in need of being split up into smaller functions.
