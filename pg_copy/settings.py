import os

from django.conf import settings


def get_backup_path():
    """
    Returns the path to the backup files.
    """

    return getattr(
        settings, "PG_COPY_BACKUP_PATH", os.path.join(os.getcwd(), "db_backup",)
    )
