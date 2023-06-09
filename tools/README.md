# TOOLS

## crawl_deptree.py

This code was copied from https://github.com/anaconda-distribution/distro-incubator/tree/main/akabanovs/pkg_check_availability and modified.

This Python script generates a dependency tree for a specified feedstock found on the conda-forge. The tool inspects the
run, host, and build dependencies required to build the package and checks for the existence of these dependencies conda-forge. It will output a list feedstocks in build order

To run provide a comma separated list of feedstock names

`python crawl_deptree.py -f urllib3-feedstock`

### Notes
We exclude some packages we don't intend to ever build. This includes some compilers and any package in `conda_build_config_anacondarecipes.yaml` because we won't be building the latest version of pinned packages.


### Issues / Bugs
* This is considered a temporary solution to get a build order. Not expected to be a long term solution nor get 100% of the build order for 100% of feedstocks. Expect the number of missing dependencies to be minimal enough to handle manually until a better solution can be developed.
* `target_platform` is fixed to `linux-64`
* Assumes default branch is `main`. This appears to be a requirement for `conda-forge` repos
* Dependency version is ignored as we only build the latest version of feedstocks. Assume we will need to take manual action for any previous versions.
* Using recipes from `conda-forge` when parsing dependencies so any `community` modifications will not be considered.
* Using **pyyaml** to render and will not find all dependencies accurately
* If we fail to find the recipe, render the recipe, or any other error we just continue
* We use `conda-forge/feedstock-outputs` to find the mapping from package name to feedstock. Sometimes this returns multiple feedstocks and we just use the first one.

## find_deps.py
This was an earlier attempt at crawl_deptree.py that is now broken. We left the code in place for reference.