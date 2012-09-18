#!/usr/bin/env python
from setuptools import setup

setup(
    name="fs2couch",
    version="0.1",
    py_modules=["fs2couch"],
    scripts=["fs2couch"],
    # metadata for upload to PyPI
    author="Rami Chowdhury",
    author_email="rami.chowdhury@gmail.com",
    description="Push / pull CouchDB design documents from the filesystem",
    license="MIT",
    keywords="couchdb design tool",
    # could also include long_description, download_url, classifiers, etc.
)
