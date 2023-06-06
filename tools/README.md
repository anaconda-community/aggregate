# TOOLS

## crawl_deptree.py

This project was copied from https://github.com/anaconda-distribution/distro-incubator/tree/main/akabanovs/pkg_check_availability and modified.

This Python script generates a dependency tree for a specified feedstock found on the conda-forge. The tool inspects the
run, host, and build dependencies required to build the package and checks for the existence of these dependencies conda-forge. It will output a list feedstocks in build order

To run provide feedstock name

`python crawl_deptree.py -f urllib3-feedstock`

### Issues
* This is considered a temporary solution to get a build order
* Architecture is ignored
* Version is ignored - always reads the latest commit in main branch
* Using recipes from conda-forge
* Using pyyaml to render and will not find all dependencies accurately
* Excludes any package in `conda_build_config_anacondarecipes.yaml` because we won't be building the latest version of pinned packages.

## find_deps.py
This was an earlier attempt at crawl_deptree.py that is now broken. We left the code in place for reference.