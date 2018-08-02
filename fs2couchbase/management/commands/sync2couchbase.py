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
            buckets = getattr(settings, 'COUCHBASE_BUCKETS', None)
            if not buckets:
                raise ValueError('settings.COUCHBASE_BUCKETS is not available. Aborting...')

            # The first level contains app_labels
            app_labels = os.listdir(input_root)

            # Each app_label will map to a set of design docs under its subdirectory and
            # bucket connection config in COUCHBASE_BUCKETS
            for app_label in app_labels:
                # Get the connection config
                output = buckets[app_label]
                # Then go through the design docs to sync
                app_label_path = os.path.join(input_root, app_label)
                design_doc_dirs = os.listdir(app_label_path)
                for design_doc_dir in design_doc_dirs:
                    sd_path = os.path.join(app_label_path, design_doc_dir)
                    if os.path.isdir(sd_path):
                        # Set up the connection
                        connection = Couchbase.connect(**output)
                        # Now populate the sync target
                        targets.append((sd_path, output, connection))

        for arguments in targets:
            script_main(*arguments)
