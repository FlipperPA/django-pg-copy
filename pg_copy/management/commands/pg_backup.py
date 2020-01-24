import datetime
import os

import djclick as click
from django.conf import settings

from ...settings import get_backup_path


@click.command()
@click.option(
    "--database",
    "database",
    default="default",
    help="The database defined in the DATABASES settings to backup from.",
)
@click.option(
    "--db-override",
    "db_override",
    default=None,
    help="A value to override the db argument sent to psql.",
)
@click.option(
    "--host-override",
    "host_override",
    default=None,
    help="A value to override the host argument sent to psql.",
)
@click.option(
    "--pg-home",
    "pg_home",
    default=None,
    help="The path to the PostgreSQL installation, if it is not on your path.",
)
@click.option(
    "--file",
    "filename",
    default=datetime.datetime.now().strftime(
        "{backup_path}/%Y-%m-%d-%H-%M-%S.sqlc".format(backup_path=get_backup_path(),),
    ),
    help="The filename of the output backup file.",
)
def command(database, db_override, host_override, pg_home, filename):
    """
    Django management command to make a backup of a PostgreSQL database.
    """

    db = db_override or settings.DATABASES[database]["NAME"]
    host = host_override or settings.DATABASES[database]["HOST"]
    pg_dump = os.path.join(pg_home, "bin", "pg_dump") if pg_home else "pg_dump"

    click.secho(
        "Backing up database '{database}' on host '{host}' to file '{file}'...".format(
            database=db, host=host, file=filename,
        )
    )
    # Make sure the backup path exists
    backup_path = get_backup_path()
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)

    os.environ["PGPASSWORD"] = settings.DATABASES[database]["PASSWORD"]
    os.system(
        "{pg_dump} -Fc -c -x -h {host} -U {username} --file={file} {database}".format(
            pg_dump=pg_dump,
            host=host,
            username=settings.DATABASES[database]["USER"],
            database=db,
            file=filename,
        )
    )
    os.environ["PGPASSWORD"] = ""
