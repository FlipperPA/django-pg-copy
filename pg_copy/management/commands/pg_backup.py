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
    "-f",
    "filename",
    default=datetime.datetime.now().strftime(
        "{backup_path}/%Y-%m-%d-%H-%M-%S.sqlc".format(
            backup_path=get_backup_path(),
        ),
    ),
    help="The filename of the output backup file.",
)
@click.option(
    "--ignore-table",
    "-i",
    "ignore_table",
    multiple=True,
    default=[],
    help="Excludes the table completely during the backup file creation.",
)
@click.option(
    "--exclude-table-data",
    "-e",
    "exclude_table_data",
    multiple=True,
    default=[],
    help="Excludes the table data during the backup file creation.",
)
@click.option(
    "--jobs",
    "-j",
    "jobs",
    default=0,
    help="How many parallel jobs to run. This can drastically increase execution speed,"
    "and requires the --directory parameter to be used.",
)
@click.option(
    "--directory",
    "-d",
    "directory",
    default=datetime.datetime.now().strftime(
        "{backup_path}/%Y-%m-%d-%H-%M-%S/".format(
            backup_path=get_backup_path(),
        ),
    ),
    help="The directory to backup to when the --jobs parameter is used.",
)
def command(
    database,
    db_override,
    host_override,
    pg_home,
    filename,
    ignore_table,
    exclude_table_data,
    jobs,
    directory,
):
    """
    Django management command to make a backup of a PostgreSQL database.
    """

    db = db_override or settings.DATABASES[database]["NAME"]
    host = host_override or settings.DATABASES[database]["HOST"]
    pg_dump = os.path.join(pg_home, "bin", "pg_dump") if pg_home else "pg_dump"

    ignore_table_cmd = ""
    for table in ignore_table:
        ignore_table_cmd = " -T {table}{ignore_table_cmd}".format(
            table=table,
            ignore_table_cmd=ignore_table_cmd,
        )

    exclude_table_cmd = ""
    for table in exclude_table_data:
        exclude_table_cmd = f" --exclude-table-data {table}{exclude_table_cmd}"

    if jobs:
        click.secho(
            f"Backing up database '{db}' on host '{host}' to directory '{directory}' "
            f"with {jobs} parallel processes..."
        )
    else:
        click.secho(
            f"Backing up database '{db}' on host '{host}' to file '{filename}'..."
        )
    # Make sure the backup path exists
    backup_path = get_backup_path()
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)

    os.environ["PGPASSWORD"] = settings.DATABASES[database]["PASSWORD"]
    os.system(
        "{pg_dump} -Fc -c -x -h {host} -U {username} {ignore_table_cmd} {exclude_table_cmd} --file={file} {database}".format(
            pg_dump=pg_dump,
            host=host,
            username=settings.DATABASES[database]["USER"],
            ignore_table_cmd=ignore_table_cmd,
            exclude_table_cmd=exclude_table_cmd,
            database=db,
            file=filename,
        )
    )
    os.environ["PGPASSWORD"] = ""
