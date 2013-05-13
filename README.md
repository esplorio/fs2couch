### fs2couchbase
#### utilities to work with CouchDB design documents

There are a lot of tools out there that work with CouchDB design documents -- I
even [wrote one](http://github.com/necaris/fs2couch). When we needed the same sort of functionality to work with Couchbase, it was easiest to port that over to integrate with the Couchbase Python SDK.

`fs2couchbase` provides a couple of useful functions in the
`fs2couchbase` module, a command-line script (called `sync2couchbase`), and
a Django management command `sync2couchbase` (with support for Django's
`settings.py`) that makes deployment easier.

### configuration for django

Simply add `fs2couchbase` to your `INSTALLED_APPS` setting, and the `manage.py`
command should be available. For even more convenience, you can set the
`FS2COUCHBASE_INPUT` (for a single design document; `FS2COUCHBASE_INPUT_ROOT` for a parent directory that contains all your design documents) and `FS2COUCHBASE_OUTPUT` values in `settings.py`, so the command can pick those settings up and `manage.py sync2couchbase` works automagically.
