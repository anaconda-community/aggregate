#!/usr/bin/env python
# Use this tool to find feedstocks that contain pinned packages
import json

import warnings
import requests
import yaml
from cachetools import Cache, LRUCache, cached


cache: Cache = LRUCache(maxsize=1000)

warnings.simplefilter("ignore")
github_base_url = "https://raw.githubusercontent.com"

session = requests.Session()
rdata = {}
ordered_feedstocks = dict()
excluded_packages = [
    "openblas","ice","gdal","arrow","boost","llvm","gcc","python","numpy","protobuf","abseil","thrift","hdf5","netcdf"
]


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
        return ','.join(json.loads(response.text)["feedstocks"])
    except:
        return ""


def get_manifest_feedstocks():
    with open('manifest.yaml') as f:
        my_list = yaml.safe_load(f)

    return my_list['feedstocks']


def get_pinned_packages():
    with open('conda_build_config.yaml') as f:
        my_list = yaml.safe_load(f)

    return my_list


# Start the program.
if __name__ == "__main__":

    feedstocks = get_manifest_feedstocks()
    packages = get_pinned_packages()
    for p in excluded_packages:
        packages[p] = ""

    print(packages)

    for package in packages:
        if package == "":
            continue
        feedstock_name = lookup_feedstock_name(package)
        feedstock_names = feedstock_name.split(",")
        for f in feedstock_names:
            if f"{f}-feedstock" in feedstocks:
                ordered_feedstocks[f"{f}-feedstock"] = ''

    print(','.join(reversed(list(ordered_feedstocks.keys()))))
