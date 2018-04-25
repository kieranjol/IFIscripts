## Detailed documentation is available here: http://ifiscripts.readthedocs.io/en/latest/index.html

# Building the docs

* Install Sphinx (http://www.writethedocs.org/guide/tools/sphinx/)
* Install the `sphinx-rtd-theme`  with `sudo pip install sphinx_rtd_theme`
* `cd` into the `docs` directory
* run `make` to get the list of options
* `make html` will produce html builds in the `_build` directory.
* If you wish to build the lovely PDF output, you may have to install `texlive-latex`. installing the basic package resulted in failed builds, but the following command on Ubuntu 16.04 produced a PDF file: `$ sudo apt-get install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended latexmk`. A more limited install may be sufficient, but I will need to test this further.
* Once `texlive` has been installed, `make latexpdf` should produce a PDF in the `_build` directory.
* `make clean` will remove all files from your `build` directory.

