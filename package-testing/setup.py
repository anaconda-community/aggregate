"""setup.py is Python's answer to a multi-platform make file and installer"""

# prefer setuptools over distutils
from setuptools import find_packages, setup

import versioneer

setup(
    name="packages-testing",
    version=versioneer.get_version(),
    description="Test suite package with top priority packages",
    packages=find_packages(),
    # for requirements see environment.yml
    entry_points={"console_scripts": ["samples-print-date=pysamples.samples:main"]},
    python_requires=">=3.7",
    include_package_data=True,
)
