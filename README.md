# fs2couch
## utilities to work with CouchDB design documents

There are a lot of tools out there that work with CouchDB design documents --
mostly built around the concept of CouchApps. Some of them work well with
design documents written in languages other than Javascript. Some of them work
well with multiple design documents at a time. Few do both, and the one I found
that does (Erica) requires an Erlang environment on my deployment machine.

Seems a bit much to deploy a Django application.

So I wrote my own -- `fs2couch` provides a couple of useful functions in the
`fs2couch` module, a command-line script (called, creatively, `fs2couch`), and
a Django management command `sync2couch` (with support for Django's
`settings.py`) that makes deployment easier.
