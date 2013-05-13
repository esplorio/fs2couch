import os

from django.core.management.base import BaseCommand
from django.core.exceptions import ImproperlyConfigured

from couchbase import Couchbase
from fs2couchbase import script_main


class Command(BaseCommand):
    args = "[<input> <output>]"
    help = """Sync Couchbase design document(s) from <input> to <output> --
defaults for which can be set in settings.py"""
    can_import_settings = True

    def handle(self, *args, **options):
        # Sync the design documents over.  Just use the settings.py config,
        # as it's the easiest.
        from django.conf import settings
        input = getattr(settings, "FS2COUCHBASE_INPUT", None)
        input_root = getattr(settings, "FS2COUCHBASE_INPUT_ROOT", None)
        output = getattr(settings, "FS2COUCHBASE_OUTPUT", None)
        if (input is None and input_root is None) or output is None:
            raise ImproperlyConfigured(
                "fs2couchbase needs input & output targets!")

        elif input is not None:
            targets = [(input, output)]
        elif input_root is not None:
            connection = Couchbase.connect(**output)
            subdirs = os.listdir(input_root)
            targets = []
            for sd in subdirs:
                sd_path = os.path.join(input_root, sd)
                if os.path.isdir(sd_path):
                    targets.append((sd_path, output, connection))

        for arguments in targets:
            script_main(*arguments)
