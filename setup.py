#!/usr/bin/env python3

from distutils.core import setup

setup(
    name="psfs",
    version="0.0.1",
    description="A python script of proportional scale of financial statements",
    long_description=open("README.md", "rb").read().decode("utf-8"),
    author="ugos",
    url="https://github.com/ugohsu/propScale",
    packages=["psfs"],
    scripts=["bin/psfs"]
)
