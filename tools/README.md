# TOOLS

## find_deps.py

This project was copied from https://github.com/anaconda-distribution/distro-incubator/tree/main/akabanovs/pkg_check_availability and modified.

This Python script generates a dependency tree for a specified feedstock found on the conda-forge channel by default. The tool inspects the
run dependencies required to build the package and checks for the existence of these dependencies conda-forge. It will output a list feedstocks in build order

To install, create a new conda environment and install:
	- pyyaml
	- jinja2

To run provide feedstock name

`python find_deps.py -f urllib3-feedstock`

### Issues
* This is considered a temporary solution to get a build order
* Architecture is ignored
* Version is ignored - always looks for latest
* Nothing is being done to detect a circular dependency - this will likely crash if it occurs
* Using recipes from conda-forge
* Not a graph, just prints an ordered list