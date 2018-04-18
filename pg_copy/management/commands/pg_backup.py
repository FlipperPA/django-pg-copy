import datetime
import os

from django.conf import settings

import djclick as click

from ...settings import get_backup_path


@click.command()
@click.option(
    '--database',
    'database',
    default='default',
    help='The database defined in the DATABASES settings to backup.',
)
@click.option(
    '--file',
    'filename',
    default=datetime.datetime.now().strftime(
        '{backup_path}/%Y-%m-%d-%H-%M-%S.sqlc'.format(
            backup_path=get_backup_path(),
        ),
    ),
    help='The filename of the output backup file.',
)
def command(database, filename):
    """
    Django management command to make a backup of a PostgreSQL database.
    """

    click.secho(
        "Backing up the database '{database}' on host '{host}' to file '{filename}'...".format(
            database=settings.DATABASES[database]['NAME'],
            host=settings.DATABASES[database]['HOST'],
            filename=filename,
        )
    )
    # Make sure the backup path exists
    backup_path = get_backup_path()
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)

    os.environ["PGPASSWORD"] = settings.DATABASES[database]['PASSWORD']
    os.system(
        'pg_dump -Fc -c -x -h {host} -U {username} --file={filename} {database}'.format(
            host=settings.DATABASES[database]['HOST'],
            username=settings.DATABASES[database]['USER'],
            database=settings.DATABASES[database]['NAME'],
            filename=filename,
        )
    )
    os.environ["PGPASSWORD"] = ''
