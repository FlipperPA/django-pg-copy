import datetime
from os import environ, system

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

    environ["PGPASSWORD"] = settings.DATABASES[database]['PASSWORD']
    system(
        'pg_dump -h {host} -U {username} --format=c --file={filename} {database}'.format(
            host=settings.DATABASES[database]['HOST'],
            username=settings.DATABASES[database]['USER'],
            database=settings.DATABASES[database]['NAME'],
            filename=filename,
        )
    )
