#!/usr/bin/env python
# This was modified from https://github.com/anaconda-distribution/distro-incubator/blob/main/akabanovs/pkg_check_availability/pkg_check_availability.py
import argparse
import json
import operator
import os
import re
import warnings

import requests
import yaml
from cachetools import Cache, LRUCache, cached
from pkg_resources import parse_version
from render import render

cache: Cache = LRUCache(maxsize=1000)

warnings.simplefilter("ignore")

supported_archs = [
    "linux-64",
    "linux-ppc64le",
    "linux-aarch64",
    "linux-s390x",
    "osx-64",
    "osx-arm64",
    "win-64",
    "noarch",
]
excluded_packages = [
    "openblas","ice","gdal","arrow","boost","llvm","gcc","python","numpy","protobuf","abseil","thrift","hdf5","netcdf"
]
github_base_url = "https://raw.githubusercontent.com"
username = os.getenv("GIT_USERNAME")
token = os.getenv("GIT_TOKEN")
avail_pkg = []
unavail_pkg = []

missing_deps = []
outdated_deps = []
check_manually = []
session = requests.Session()
rdata = {}
ordered_feedstocks = dict()
parent = ""


def ver_in_range(verCand, verRange):
    inRange = True
    if verRange != " ":
        for verPart in verRange.split(","):
            if ">=" in verPart:
                op = operator.ge
                ver = verPart.split(">=")[1]
            elif ">" in verPart:
                op = operator.gt
                ver = verPart.split(">")[1]
            elif "<=" in verPart:
                op = operator.le
                ver = verPart.split("<=")[1]
            elif "<" in verPart:
                op = operator.lt
                ver = verPart.split("<")[1]
            elif "!=" in verPart:
                op = operator.ne
                ver = verPart.split("!=")[1]
            elif "==" in verPart:
                op = operator.eq
                ver = verPart.split("==")[1]
            elif "=" in verPart:
                op = operator.eq
                ver = verPart.split("=")[1]
            else:
                op = operator.eq
                ver = verPart
            if not op(parse_version(verCand), parse_version(ver)):
                inRange = False
                break
    return inRange


def get_published():
    r = requests.get('https://staging.continuum.io/community/dev/noarch/repodata.json')
    my_list = yaml.safe_load(r.content)
    published = dict()
    for x in my_list['packages']:
        published[re.sub(r'-\d+\.\d+.*\.tar\.bz2', '', x)] = 'yes'
    return published


def get_requirements(data, name, section, attribute):
    reqs = data.get(section, {}).get(attribute, [])
    if section == "requirements":
        for out in data.get("outputs", {}):
            reqs = reqs + out.get(section, {}).get(attribute, [])
    return reqs


def read_requirements(data, name, section, attribute):
    try:
        req = get_requirements(data, name, section, attribute)
        if not isinstance(req, list):
            req = []
    except:
        req = []
    return req


@cached(cache)
def is_recipe_available(pkg_name: str, lookup: bool):
    if pkg_name.startswith("ctng-compilers-"):
        return False, ""

    # We already verified recipe, just move package in build order
    if f"{pkg_name}-feedstock" in ordered_feedstocks.keys():
        ordered_feedstocks.pop(f"{pkg_name}-feedstock")
    # If we haven't processed then lookup recipe
    else:
        url = f"{github_base_url}/conda-forge/{pkg_name}-feedstock/main/recipe/meta.yaml"
        try:
            response = session.get(url, allow_redirects=False)
        except:
            return False, ""
        if response.status_code != 200:
            if lookup:
                return is_recipe_available(lookup_feedstock_name(pkg_name), False)
            return False, ""
    ordered_feedstocks[f"{pkg_name}-feedstock"] = parent
    return True, "main"


@cached(cache)
def raw_text_load(name, branch, lookup):
    url = f"{github_base_url}/conda-forge/{name}-feedstock/{branch}/recipe/meta.yaml"
    response = session.get(url, allow_redirects=False)
    if response.status_code != 200:
        if lookup:
            return raw_text_load(lookup_feedstock_name(name), branch, False)
        print(f"Error [{response.status_code}]: {response.reason}")
        return ""
    env_string = response.text
    return render(env_string, {'target_platform': 'linux-64', 'ctng_target_platform': 'linux-64'})


@cached(cache)
def get_deps(name, branch):
    pinned = get_pinned_packages()
    if name in pinned:
        return {}, "0"
    try:
        data = raw_text_load(name, branch, True)
        if data == "":
            return {}, "0"
    except:
        return {}, "0"
    # Get collection of required dependencies (may not be unique)
    deps_collection = read_requirements(data, name, "requirements", "build") \
                      + read_requirements(data, name, "requirements", "run") \
                      + read_requirements(data, name, "requirements", "host")

    deps_dict = {}
    if len(deps_collection) > 0:
        for dep in deps_collection:
            if dep not in deps_dict and isinstance(dep, str) and dep not in pinned:
                deps_dict[dep] = []
    return deps_dict, get_requirements(data, name, "package", "version")


def guess_feedstock_name(dep, separator, checksep):
    if not separator in dep:
        return False, dep, ""
    dep = dep.replace(separator, checksep)
    depname_split = dep.split(separator)
    for ind, check_dep in reversed(list(enumerate(depname_split))):
        partOfPKG = separator.join(depname_split[: ind + 1])
        repo_avail, def_branch = is_recipe_available(partOfPKG, True)
        if repo_avail:
            # Found the repo! Now need to check if the package is mentioned here
            try:
                data = raw_text_load(partOfPKG, def_branch, True)
                if data is None:
                    continue
            except:
                print(f"Error loading yaml for {partOfPKG}")
                continue
            for out in data.get("outputs", {}):
                # Try both combinations
                if str(out.get("name", {})) == dep:
                    return True, partOfPKG, def_branch
                if str(out.get("name", {})) == dep.replace(checksep, separator):
                    return True, partOfPKG, def_branch
    return False, dep, ""


@cached(cache)
def lookup_feedstock_name(dep):
    try:
        deplist = list(dep)
        url = f"{github_base_url}/conda-forge/feedstock-outputs/main/outputs/{deplist[0]}/{deplist[1]}/{deplist[2]}/{dep}.json"
        response = session.get(url, allow_redirects=False)
        if response.status_code != 200:
            print(f"Could not find feedstock at {url}")
            print(f"Error [{response.status_code}]: {response.reason}")
            return ""
        return json.loads(response.text)["feedstocks"][0]
    except:
        return ""


def scan_arch(dep, ver_range, rdata):
    available = False
    in_range = False
    for r in rdata["packages"].values():
        if dep == r["name"]:
            available = True
            if ver_range:
                if ver_in_range(r["version"], ver_range):
                    in_range = True
                    break
    return available, in_range


def print_level(deps, archSupport, prefix, check_version_check_selector, expand_tree):
    for index, key in enumerate(deps.keys()):
        # Construct the full prefix:
        if index == len(deps) - 1:
            br = "└──"
            prefix2 = prefix + "    "
            comment_prefix = "\n" + prefix + "    "
        else:
            br = "├──"
            prefix2 = prefix + "│   "
            comment_prefix = "\n" + prefix + "│   "
        constrLine = prefix + br

        if len(constrLine) >= 50:
            continue

        # Derive dependency's actual name and version range
        dep = key.split()
        ver_range = ""
        if len(dep) > 1:
            ver_range = dep[1]
        if len(dep) == 0:
            continue
        dep = dep[0]
        if dep.__eq__("python"):
            continue
        if dep.startswith("ctng-compilers-"):
            continue
        if dep.startswith("_"):
            continue
        if dep.startswith("cross-python"):
            continue
        if dep.startswith("m2"):
            continue
        if dep.__eq__("make"):
            continue
        if dep.__eq__("help2man"):
            continue
        if dep.__eq__("autoconf"):
            continue
        if dep.__eq__("automake"):
            continue
        if dep.__eq__("m4"):
            continue
        if dep.__eq__("libtool"):
            continue
        if dep.__eq__("m2-patch"):
            continue
        if dep.__eq__("patch"):
            continue
        if dep.__eq__("vs2015_runtime"):
            continue
        if dep.__eq__("posix"):
            continue
        if dep.__eq__("crt-git"):
            continue
        if dep.startswith("automake"):
            continue
        if dep.__eq__("setuptools"):
            continue
        if dep.__eq__("wheel"):
            continue
        if dep.__eq__("autotools_clang_conda"):
            continue

        # Construct line:
        constrLine += dep
        if check_version_check_selector:
            constrLine += " " + ver_range

        # Initialise vars related to dependency's architecture selectors
        archSupportDep = archSupport.copy()
        extraInfo = ""

        # Further initialise some flags to track dependency availability
        pkg_avail = False
        repo_avail = True
        pkg_avail_on_noarch = False

        # Check if dependency is available and populate availability arrays
        # print("Checking " + dep)
        repo_avail, def_branch = is_recipe_available(dep, True)
        if dep in avail_pkg:
            pkg_avail = True
        elif "conda" in dep:
            repo_avail = False
        else:
            if dep not in unavail_pkg:
                # conda forge sometimes uses '-' as a separator while we use '_', and vice versa. Check:
                if not repo_avail:
                    repo_avail, dep, def_branch = guess_feedstock_name(dep, "-", "-")
                    if not repo_avail:
                        repo_avail, dep, def_branch = guess_feedstock_name(dep, "-", "_")
                    if not repo_avail:
                        repo_avail, dep, def_branch = guess_feedstock_name(dep, "_", "_")
                    if not repo_avail:
                        repo_avail, dep, def_branch = guess_feedstock_name(dep, "_", "-")
                    if repo_avail:
                        constrLine += " (subpackage of " + dep + "-feedstock)"

        if repo_avail:
            pkg_avail = is_recipe_available(dep, True)
            if pkg_avail:
                avail_pkg.append(dep)
                depsOfdep, version = get_deps(
                    dep,
                    def_branch
                )
                print_level(
                    depsOfdep,
                    archSupportDep,
                    prefix2,
                    check_version_check_selector,
                    expand_tree,
                )
            else:
                unavail_pkg.append(dep)
                unavail_pkg.append(def_branch)

        # Take into account (if specified) version range and (if specified) arch selectors:
        if check_version_check_selector:
            archSupportDep = []
            verAvailInfo = ""
            archAvailInfo = ""
            for arch in archSupport:
                if arch == "noarch":
                    continue
                arch_req = deps[key][arch]
                if arch_req:
                    archSupportDep.append(arch)

            # If package is present on anaconda.org (pkg_avail), do further refinement to see if it is
            # available for a specific version range, also taking into account arch selectors:
            if pkg_avail:
                for arch in archSupportDep:
                    available, in_range = scan_arch(dep, ver_range, rdata[arch])
                    if not available:
                        if not archAvailInfo:
                            archAvailInfo = (
                                comment_prefix
                                + "- Unavailable:"
                            )
                        archAvailInfo += arch + ";"
                    if available and (not in_range and ver_range):
                        if not verAvailInfo:
                            verAvailInfo = (
                                comment_prefix
                                + "- Version requirements not met:"
                            )
                        verAvailInfo += arch + ";"

                # If not found for any of the specified archs, try searching on noarch channel:
                if verAvailInfo or archAvailInfo:
                    available, in_range = scan_arch(dep, ver_range, rdata["noarch"])
                    if available:
                        archAvailInfo += (
                            comment_prefix
                            + "- Available on noarch"
                        )
                        if in_range or not ver_range:
                            pkg_avail_on_noarch = True
                            archAvailInfo += (
                                " and version OK"
                            )
                        else:
                            archAvailInfo += (
                                " but version NOT OK"
                            )
                    else:
                        archAvailInfo += " noarch;"
                extraInfo = verAvailInfo + archAvailInfo

        # Finally, write info to screen
        if pkg_avail:
            if not extraInfo or pkg_avail_on_noarch:
                if expand_tree:
                    print(
                        constrLine
                        + " (\u2713)"
                        + extraInfo
                       
                    )
            else:
                print(constrLine + " (^)" + extraInfo)
                if dep not in outdated_deps and not pkg_avail_on_noarch:
                    outdated_deps.append(dep)
        else:
            if repo_avail:
                def_branch = unavail_pkg[unavail_pkg.index(dep) + 1]
                depsOfdep, version = get_deps(
                    dep, def_branch
                )
                if ver_range and check_version_check_selector:
                    if not ver_in_range(version, ver_range):
                        extraInfo = (
                            comment_prefix
                            + "│   - Dependencies shown are for {} version {}.".format(
                                dep, version
                            )
                        )
                        extraInfo += (
                            comment_prefix
                            + "│     i.e. picked version does not match required version range - dependencies might be different."
                        )
                print(
                    constrLine
                    + " (!)"
                    + extraInfo
                   
                )
                if dep not in missing_deps:
                    missing_deps.append(dep)
                print_level(
                    depsOfdep,
                    archSupportDep,
                    prefix2,
                    check_version_check_selector,
                    expand_tree,
                )
            else:
                print(constrLine + " (?) ")
                if dep not in check_manually:
                    check_manually.append(dep)


def check_dep_name(value):
    pkg_name_pattern = re.compile("[a-zA-Z0-9-_]+(' '.*)*")
    if not pkg_name_pattern.match(value):
        raise argparse.ArgumentTypeError("The dependency name must be in the format <valid dependency name>")
    return value


def create_parser() -> argparse.ArgumentParser:
    # Create parser for arguments and add arguments.
    parser = argparse.ArgumentParser(
        prog="check_avail",
        description="This Python script generates an ordered list of feedstocks to build."
    )
    # popt = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument(
        "-m",
        "--manifest",
        default="False",
        help="Set to True to get all feedstocks in manifest"
    )
    parser.add_argument(
        "-s",
        "--skip_published",
        default="False",
        help="Set to True to skip published feedstocks"
    )
    parser.add_argument(
        "-f",
        "--feedstock_name",
        type=check_dep_name,
        help="Feedstock name available on conda-forge. Should be a string, comma separated",
    )
    parser.add_argument(
        "-a",
        "--archs",
        default="",
        help="A list of architectures to consider when searching for dependencies in the main channel. \
                     Should be specified as a string, space separated. E.g. 'osx-arm64 osx-64 linux-64'. If not used, \
                     all supported architectures will be considered.",
    )
    parser.add_argument(
        "--check-version-check-selector",
        help="Dependencies in the recipe may have version range or architecrture selector specified. \
                     By default these are not taken into account and script only scans for package availability. \
                     The current flag adds these checks, thus giving the user a more detailed overview of package \
                     availability and constraints.",
        action="store_true",
    )
    parser.add_argument(
        "--expand-tree",
        help="Flag to expand the dependency tree and include those packages that are available.",
        action="store_true",
    )
    return parser


def get_manifest_feedstocks():
    with open('manifest.yaml') as f:
        my_list = yaml.safe_load(f)

    return ','.join(my_list['feedstocks'])


@cached(cache)
def get_pinned_packages():
    with open('conda_build_config.yaml') as f:
        my_list = yaml.safe_load(f)

    for p in excluded_packages:
        my_list[p] = ""

    return ','.join(my_list)


# Start the program.
if __name__ == "__main__":
    # Create parser
    parser = create_parser()
    # Get the parsed arguments and get to work!
    args = parser.parse_args()

    # Prepare the list of requested archs
    archs = supported_archs.copy()
    if args.archs:
        archs = []
        for arch in args.archs.split():
            if arch in supported_archs:
                archs.append(arch)
            else:
                print("{} arch is not supported. Please use the names from the \
                      list: {}".format(arch, supported_archs))
                exit(1)

    if args.manifest.__eq__("True"):
        to_process = get_manifest_feedstocks().split(",")
    else:
        to_process = args.feedstock_name.split(",")

    for feedstock in to_process:
        if feedstock == "":
            continue
        # Remove -feedstock
        package_name = feedstock[:-10]
        parent = package_name
        # Check if the package is accessible in the conda-forge channel
        repo_avail, def_branch = is_recipe_available(package_name, True)
        if not repo_avail:
            print("unable to locate the {} feedstock on conda-forge".format(package_name))
            continue

        # Inspect and draw package's dependencies
        deps, version = get_deps(package_name, def_branch)

        print_level(deps, archs, " ", args.check_version_check_selector, args.expand_tree)

    # print_summary(package_name)
    ordered_feedstocks.pop("wheel-feedstock", "")
    ordered_feedstocks.pop("setuptools-feedstock", "")

    if args.skip_published.__eq__("True"):
        for key in get_published():
            ordered_feedstocks.pop(f"{key}-feedstock", '')

    feedstocks = ','.join(reversed(list(ordered_feedstocks.keys())))
    print(feedstocks)
