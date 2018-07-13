Contributing
============

Issues
------

Contributions are very much welcome in any form. Feel free to raise an issue requesting a new feature, or to report a bug. If reporting a bug, please copy/paste the full, complete, uncut terminal output. You can raise the issue in the github issue tracker: https://github.com/kieranjol/IFIscripts/issues

Pull Requests
-------------

Pull requests are welcome. If contributing code, it can be nice to run it through ``pylint`` first, as this will check for PEP-08 compliance. I'd rather get the code contribution in pretty much any form, so this is not necessary. Pull requests can be raised here:  https://github.com/kieranjol/IFIscripts/pulls

Generally, we try to limit the use of external dependencies, so we try to do as much in ``python`` as possible. This can be seen in any scripts that generate checksums. We slowly moved away from using the wonderful ``md5deep`` and used the internal python ``hashlib`` libraries instead. Previously, we limited the use of external python libraries, and only really use ``lxml``. This is probably going to change going forward, especially as we move towards managing installs and updates via ``pip`` and ``setup.py``.

Contributions Needed
--------------------

Some good first contributions could be adding explanatory docstrings to libraries like ``ififuncs.py``, or revising older scripts, such as ``validate.py`` so that they are more in line with the coding style of recent scripts. Some of our ``main()`` functions are far too long and are doing too much, so they are in need of being split up into smaller functions.

Overall, the project needs to grow in the following ways:

* Reduce code duplication across scripts. These duplications continue to be difficult to maintain. Moving regularly used functions to ififuncs definitely helps.
* ``unittests`` are desperately needed! Scripts are becoming more and more linked, so automated testing is needed in order to find errors in  areas that we might not expect. This should also allow integration with something like ``Travis``.
* A config file is needed in some way shape or form. For example, logs and old manifests are stored on the desktop. It isn't really cool that these folders just appear without the user even knowing. This could also allow the scripts to be more generic, as IFI specific options could be enabled here.
* It would probably be a good idea to introduce classes into IFIscripts. Some functions return and call an embarrasing number of values.
* Have some sort of integration with a mysql database for tracking objects and logging events.
