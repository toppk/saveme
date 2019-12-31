#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path

import setuptools
from setuptools import setup

print(setuptools.__file__)


def get_long_description():
    """
    Return the README.
    """
    long_description = ""
    with open("README.md", encoding="utf8") as f:
        long_description += f.read()
    long_description += "\n\n"
    with open("CHANGELOG.md", encoding="utf8") as f:
        long_description += f.read()
    return long_description


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [str(path.parent) for path in Path(package).glob("**/__init__.py")]


about = {}
base_dir = os.path.dirname(__file__)
src_dir = os.path.join(base_dir, "lib")
with open(os.path.join(src_dir, "saveme", "__about__.py")) as f:
    exec(f.read(), about)

setup(
    name=about["__title__"],
    python_requires=">=3.6",
    version=about["__version__"],
    url=about["__uri__"],
    license=about["__license__"],
    description=about["__description__"],
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email=about["__email__"],
    package_data={"saveme": ["py.typed"]},
    packages=get_packages("saveme"),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    extras_require={
        "compression": ["python-snappy", "lz4"],
        "docs": ["mkdocs", "mkdocs-material", "mkautodoc", "snakefood3"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
