#!/usr/bin/env python
# Utilities for pushing CouchDB design documents from the filesystem, and
# vice-versa. Dependent only on the Python (2.6+) standard library.

import os
import json
import urllib2
from itertools import ifilter

LANG2EXT = {
    'javascript': '.js',
    'erlang': '.erl',
    'python': '.py',
}

EXT2LANG = dict((v, k) for k, v in LANG2EXT.items())


class CouchError(AssertionError):
    def __init__(self, response):
        status = response.get('status_code', None)
        reason = response.get('reason', None)
        msg = "HTTP %d; %s" % (status, reason)
        super(CouchError, self).__init__(msg)


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
        try:
            ext = LANG2EXT[context.get('language', 'javascript')]
        except KeyError:
            lang = context['language']
            raise ValueError("Unknown design document language: '%s'" % lang)
        path = os.path.join(root, key) + ext
        str_val = value
        if not isinstance(value, basestring):
            str_val = repr(value)
        with open(path, "w") as f:
            f.write(str_val)


def _make_request(url, data=None):
    '''
    Wrap urllib2 to make it less painful.
    '''
    req = urllib2.Request(url)
    req.add_header('Accept', 'application/json')
    if data:
        req.add_data(json.dumps(data))
        req.add_header('Content-Type', 'application/json')
        # If there's data, it'll be an HTTP PUT
        req.get_method = lambda: 'PUT'
    try:
        res = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        res = e
    ret = {
        'status_code': res.getcode(),
        'headers': dict(zip(res.headers.keys(), res.headers.values())),
        'content': res.read(),
    }

    if hasattr(res, 'msg'):
        ret['reason'] = res.msg

    try:
        ret['json'] = json.loads(ret['content'])
    except ValueError:
        pass
    return ret


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
            if ext not in EXT2LANG:
                raise ValueError("Unknown file type '%s'" % fn)
            if 'language' not in ddoc:
                ddoc['language'] = EXT2LANG[ext]
            elif EXT2LANG[ext] != ddoc['language']:
                msg = "'%s' doesn't match design document language (%s)"
                raise ValueError(msg % (fn, ddoc['language']))
            with open(os.path.join(dirpath, fn), "r") as f:
                subdoc[name] = f.read()
    return ddoc


def script_main(input, output):
    if os.path.isdir(input):
        # Read from the filesystem to a design doc, try to put it into CouchDB
        ddoc = fs_to_ddoc(input)

        url = output
        if not url.endswith('/'):
            url += '/'
        url += ddoc['_id']

        # Check if the document exists in CouchDB
        response = _make_request(url)
        if response['status_code'] == 404:
            # New document -- remove the rev
            if '_rev' in ddoc:
                del ddoc['_rev']
        else:
            # It exists. Need to update the document revision, to make sure it
            # 'takes' when we POST it
            current_ddoc = response.get(
                'json', json.loads(response['content']))
            ddoc['_rev'] = current_ddoc['_rev']
        response = _make_request(url, data=ddoc)
        if response['status_code'] != 201:
            raise CouchError(response)
    else:
        # Output to the filesystem from the given input CouchDB instance
        response = _make_request(input)
        if response['status_code'] == 404:
            raise AssertionError("No such design document in %s" % input)
        ddoc = response.get('json', json.loads(response['content']))
        ddoc_to_fs(ddoc, output)
