#!/usr/bin/env python
# Utilities for pushing Couchbase design documents from the filesystem, and
# vice-versa. Dependent on the Couchbase Python SDK.

import os
import json
from itertools import ifilter

from couchbase import Couchbase, exceptions


def _makedirs(path, mode=0755):
    try:
        os.makedirs(path, mode)
    except OSError as e:
        if e.errno == 17:
            # Already exists. Ignore
            pass
        else:
            raise


def _kv_to_fs(key, value, root='.', context=None):
    """
    Write a key and value to the filesystem as a directory containing a file
    (or recurse if the value is a nested dictionary).
    """
    if not isinstance(key, basestring) or '/' in key:
        raise ValueError("Invalid key '%s'" % key)
    context = context or {}
    if isinstance(value, dict):
        # Create the directory to hold it
        path = os.path.join(root, key)
        _makedirs(path)
        # Recurse for each key and value
        for k, v in value.iteritems():
            _kv_to_fs(k, v, root=path, context=context)
    else:
        # Otherwise, assume it's easily stringifiable and just write to file
        ext = ".js"  # Couchbase only supports Javascript
        path = os.path.join(root, key) + ext
        str_val = value
        if not isinstance(value, basestring):
            str_val = repr(value)
        with open(path, "w") as f:
            f.write(str_val)


def ddoc_to_fs(doc, path='.', raise_errors=False):
    """
    Convert a design document (as a dictionary) into a filesystem structure of
    directories (keys) containing files (values).
    """
    directory_parts = doc['_id'].split('/', 1)
    root = os.path.join(path, *directory_parts)
    _makedirs(root, mode=0755)
    context = doc
    for k, v in ifilter(lambda p: p[0] != '_id', doc.iteritems()):
        _kv_to_fs(k, v, root, context)


def fs_to_ddoc(path):
    """
    Read a filesystem directory structure into a design-document-style object.
    """
    # Assume the final part of the path is the design document name
    head, tail = os.path.split(path)
    name = tail or head
    if not name:
        raise ValueError("Invalid path '%s'" % path)

    ddoc = {}
    ddoc['_id'] = "/".join(("_design", name))

    for dirpath, dirnames, filenames in os.walk(path):
        if not filenames:
            continue
        keys = dirpath[len(path):].split(os.sep)
        subdoc = ddoc
        for k in keys:
            if k == '':
                continue
            if k not in subdoc:
                subdoc[k] = {}
            subdoc = subdoc[k]
        for fn in filenames:
            if fn.endswith('~') or fn.endswith('.DS_Store'):
                # Ignore filesystem clutter
                continue
            name, ext = os.path.splitext(fn)
            # Couchbase only supports Javascript, no need to fiddle with
            # the 'language' field in the design document
            with open(os.path.join(dirpath, fn), "r") as f:
                content = f.read()
                if name == 'options':
                    # the 'options' key needs to be a JSON object, not a string
                    content = json.loads(content)
                subdoc[name] = content
    return ddoc


def script_main(input, output, connection=None, ddoc_name=None):
    if os.path.isdir(input):
        # Read from the filesystem to a design doc, and try to put it into
        # Couchbase. Expects 'input' to be a directory readable by the script,
        # and 'output' to be a set of arguments with which to connect to the
        # Couchbase server.
        cb = connection or Couchbase.connect(**output)
        ddoc = fs_to_ddoc(input)

        # Now on with design documents
        url = ddoc.pop('_id')

        try:
            response = cb.bucket_view(url, body=ddoc, method="PUT")
        except exceptions.HTTPError as e:
            raise e
    else:
        # Output to the filesystem from the given input Couchbase instance and
        # the design document name
        cb = connection or Couchbase.connect(**input)
        if not ddoc_name:
            raise AssertionError("No design document name supplied")
        try:
            response = cb.bucket_view(ddoc_name, method="GET")
        except exceptions.HTTPError as e:
            if e.status == 404:
                raise AssertionError("No such design document in %s" % input)
            else:
                raise
        ddoc = response
        ddoc_to_fs(ddoc, output)
