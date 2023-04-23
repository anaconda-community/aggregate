# TOOLS

## find_deps.py

This project was copied from https://github.com/anaconda-distribution/distro-incubator/tree/main/akabanovs/pkg_check_availability and modified.

This Python script generates a dependency tree for a specified package found on the conda-forge channel by default. The tool inspects the
run dependencies required to build the package and checks for the existence of these dependencies conda-forge. It will output a list feedstocks in build order

To install, create a new conda environment and install:
	- pyyaml
	- jinja2

To run provide package name

`python find_deps.py -p urllib3`
