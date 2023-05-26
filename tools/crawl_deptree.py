#!/usr/bin/env python
# This was derived from https://github.com/anaconda-distribution/distro-incubator/blob/main/akabanovs/pkg_check_availability/pkg_check_availability.py
import argparse
import collections
import re
import warnings
from typing import Set, Dict

import requests
import yaml
from cachetools import Cache, LRUCache, cached

import sort
from render import render

metadata_cache: Cache = LRUCache(maxsize=1000)
feedstock_cache: Cache = LRUCache(maxsize=1000)


warnings.simplefilter("ignore")

excluded_packages = [
    "openblas","ice","gdal","arrow","boost","llvm","gcc","python","numpy","protobuf","abseil","thrift","hdf5","netcdf","libblas","libcblas","liblapack","liblapacke"
]


def get_requirements(data, name, section, attribute):
    reqs = data.get(section, {}).get(attribute, [])
    if section == "requirements":
        for out in data.get("outputs", {}):
            if out.get("name","") == name:
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


def get_default_location(pkg_name):
    return [f"{github_base_url}/conda-forge/{pkg_name}-feedstock/main/recipe/meta.yaml"]


def get_location_by_lookup(pkg_name):
    for feedstock_name in lookup_feedstock_name(pkg_name):
        yield f"{github_base_url}/conda-forge/{feedstock_name}-feedstock/main/recipe/meta.yaml"


location_probes = [get_default_location, get_location_by_lookup]


@cached(metadata_cache)
def get_metadata(pkg_name: str):
    if not include_dependency(pkg_name):
        return None

    for location_provider in location_probes:
        for url in location_provider(pkg_name):
            response = session.get(url, allow_redirects=False)
            if response.status_code == 200:
                data = response.text
                return render(data, {'target_platform': 'linux-64'})

    return None


def extract_deps(data, name):
    deps_collection = read_requirements(data, name, "requirements", "build") \
                      + read_requirements(data, name, "requirements", "run") \
                      + read_requirements(data, name, "requirements", "host")
    dependencies = {dep.split()[0] for dep in deps_collection if isinstance(dep, str)}
    return set(filter(include_dependency, dependencies))


@cached(feedstock_cache)
def lookup_feedstock_name(dep):
    if len(dep) < 3:
        return ""
    url = f"{github_base_url}/conda-forge/feedstock-outputs/main/outputs/{dep[0]}/{dep[1]}/{dep[2]}/{dep}.json"
    response = session.get(url, allow_redirects=False)
    if response.status_code != 200:
        print(f"Could not find feedstock at {url}")
        print(f"Error [{response.status_code}]: {response.reason}")
        return ""
    return response.json()["feedstocks"][0]


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
    popt = parser.add_mutually_exclusive_group(required=True)

    popt.add_argument(
        "-f",
        "--feedstock_name",
        type=check_dep_name,
        help="Feedstock name available on conda-forge. Should be a string, comma separated",
    )
    return parser


github_base_url = "https://raw.githubusercontent.com"
session = requests.Session()


def include_dependency(dep):
    return not (dep == "python" or
                dep.startswith("ctng-compilers-") or
                dep.startswith("_") or
                dep.startswith("r-") or
                dep == "None" or
                len(dep) < 3 or
                dep in get_pinned_packages())


def generate_initial_roots(feedstocks_csv):
    for feedstock in feedstocks_csv.split(","):
        if feedstock:
            package_name = feedstock[:-10]
            metadata = get_metadata(package_name)
            if not metadata:
                print("unable to locate the {} feedstock on conda-forge".format(package_name))
                continue
            yield (feedstock, metadata)


def filter_map(f, source):
    return filter(lambda item: f(item[0], item[1]), source.items())


@cached(metadata_cache)
def get_pinned_packages():
    # We don't want to include any packages that are pinned by anacondarecipes
    with open('conda_build_config_anacondarecipes.yaml') as f:
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

    dependency_map: Dict[str, Set[str]] = {}
    to_process = collections.deque()

    for feedstock, metadata in generate_initial_roots(args.feedstock_name):
        if metadata is not None:
            to_process.append((feedstock, metadata))

    while to_process:
        feedstock, metadata = to_process.popleft()
        package_name = feedstock[:-10]

        # deps = extract_deps(metadata, package_name)
        # Want only things with metadata as the dependencies of the current feedstock
        # However, we also don't need to process anything already visited
        deps = {lookup_feedstock_name(d): get_metadata(d) for d in extract_deps(metadata, package_name)}
        dependency_feedstocks = {f"{d}-feedstock": metadata for d, metadata in deps.items() if metadata is not None and len(d) > 0}
        dependency_map[feedstock] = set(dependency_feedstocks.keys())
        to_process.extend([(d, metadata) for d, metadata in dependency_feedstocks.items() if d not in dependency_map])

    dependency_order = [
        feedstock
        for group in sort.topological_sort(dependency_map)
        # Emit sorted to provide deterministic results
        # Also helps with imputing group boundaries in output
        for feedstock in sorted(group.members)
    ]
    print(",".join(dependency_order))

