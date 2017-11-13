from django.conf import settings


def get_backup_path():
    """
    Returns the path to the backup files.
    """

    return getattr(settings, "PG_UTILS_BACKUP_PATH", 'db_backup')
