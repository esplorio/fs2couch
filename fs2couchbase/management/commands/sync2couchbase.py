import os

from django.core.management.base import BaseCommand
from django.core.exceptions import ImproperlyConfigured

from couchbase import Couchbase
from fs2couchbase import script_main


class Command(BaseCommand):
    args = '[<input> <output>]'
    help = """Sync Couchbase design document(s) from <input> to <output> --
defaults for which can be set in settings.py"""
    can_import_settings = True

    def handle(self, *args, **options):

        targets = []  # The target to sync

        # Sync the design documents over.  Just use the settings.py config,
        # as it's the easiest.
        from django.conf import settings
        input_root = getattr(settings, 'FS2COUCHBASE_INPUT_ROOT', None)
        if not input_root:
            raise ImproperlyConfigured('fs2couchbase needs input & output targets!')
        else:
            design_docs_labels = getattr(settings, 'COUCHBASE_DESIGN_DOC_LABELS', None)
            if not design_docs_labels:
                raise ValueError('Design docs must be mapped to app labels using '
                                 'settings.COUCHBASE_DESIGN_DOC_LABELS. Aborting...')

            buckets = getattr(settings, 'COUCHBASE_BUCKETS', None)
            if not buckets:
                raise ValueError('settings.COUCHBASE_BUCKETS is not available. Aborting...')

            for design_doc, app_label in design_docs_labels:
                subdirs = os.listdir(input_root)
                for sd in subdirs:
                    if sd == design_doc:
                        # Always check if the design doc matches up with the subdirectory found
                        sd_path = os.path.join(input_root, sd)
                        if os.path.isdir(sd_path):
                            # The output can be obtained by using the corresponding app label
                            output = buckets[app_label]
                            connection = Couchbase.connect(**output)
                            # Now populate the sync target
                            targets.append((sd_path, output, connection))

        for arguments in targets:
            script_main(*arguments)
