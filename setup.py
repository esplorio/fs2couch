#!/usr/bin/env python
from setuptools import setup

setup(
    name="fs2couchbase",
    version="0.1",
    packages=["fs2couchbase"],
    scripts=["sync2couchbase"],
    # metadata for upload to PyPI
    author="Rami Chowdhury",
    author_email="rami@esplorio.com",
    description="Push / pull Couchbase design documents from the filesystem",
    license="MIT",
    keywords="couchbase design tool",
    # could also include long_description, download_url, classifiers, etc.
)
