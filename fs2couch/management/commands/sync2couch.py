import os

from django.core.management.base import BaseCommand
from django.core.exceptions import ImproperlyConfigured

from fs2couch import script_main


class Command(BaseCommand):
    args = "[<input> <output>]"
    help = """Sync CouchDB design document(s) from <input> to <output> --
defaults for which can be set in settings.py"""
    can_import_settings = True

    def handle(self, *args, **options):
        if len(args) == 2:
            # input and output specified. use them.
            input, output = args[:2]
            targets = [(input, output)]
        else:
            # ignore any arguments and try to use settings
            from django.conf import settings
            input = getattr(settings, "FS2COUCH_INPUT", None)
            input_root = getattr(settings, "FS2COUCH_INPUT_ROOT", None)
            output = getattr(settings, "FS2COUCH_OUTPUT", None)
            if (input is None and input_root is None) or output is None:
                raise ImproperlyConfigured(
                    "fs2couch needs input & output targets!")
            elif input is not None:
                targets = [(input, output)]
            elif input_root is not None:
                subdirs = os.listdir(input_root)
                targets = []
                for sd in subdirs:
                    if os.path.isdir(os.path.join(input_root, sd)):
                        targets.append((sd, output))

        for in_, out in targets:
            script_main(in_, out)
