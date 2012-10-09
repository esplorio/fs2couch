from django.core.management.base import BaseCommand
from django.exceptions import ImproperlyConfigured

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
        else:
            # ignore any arguments and try to use settings
            from django.conf import settings
            input = getattr(settings, "FS2COUCH_INPUT", None)
            output = getattr(settings, "FS2COUCH_OUTPUT", None)
            if input is None or output is None:
                raise ImproperlyConfigured(
                    "fs2couch needs input & output targets!")

        script_main(input, output)
