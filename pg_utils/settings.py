import os

from django.conf import settings


def get_backup_path():
    """
    Returns the path to the backup files.
    """

    return getattr(
        settings,
        'PG_UTILS_BACKUP_PATH',
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'db_backup',
        )
    )
