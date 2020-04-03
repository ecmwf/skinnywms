#!/usr/bin/env python
#
# Copyright 2017-2018 European Centre for Medium-Range Weather Forecasts (ECMWF).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import os

import setuptools


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return io.open(file_path, encoding="utf-8").read()


version = "0.5.4"

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="skinnywms",
    version=version,
    description="A light WMS server to visualise your NetCDf and Grib data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="European Centre for Medium-Range Weather Forecasts (ECMWF)",
    author_email="software.support@ecmwf.int",
    license="Apache License Version 2.0",
    url="https://github.com/sylvielamythepaut/skinnywms",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["magics", "Flask",],
    entry_points={"console_scripts": ["skinny-wms=skinnywms.skinny:main"],},
    tests_require=["pytest",],
    test_suite="tests",
    zip_safe=True,
    keywords="magics grib WMS visualisation NetCDF climate meteorology",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
    ],
)
