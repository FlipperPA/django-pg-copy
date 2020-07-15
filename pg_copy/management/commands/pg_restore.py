import errno
import os

import djclick as click
from django.conf import settings

from ...settings import get_backup_path


@click.command()
@click.option(
    "--database",
    "database",
    default="default",
    help="The database defined in Django's DATABASES settings to restore to.",
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
    "--file", "filename", help="The filename of the input backup file to restore.",
)
@click.option(
    "--no-confirm",
    "no_confirm",
    is_flag=True,
    help="Restores the database without confirmation: be careful!",
)
def command(database, db_override, host_override, pg_home, filename, no_confirm):
    """
    Django management command to restore a PostgreSQL database.
    """

    db = db_override or settings.DATABASES[database]["NAME"]
    host = host_override or settings.DATABASES[database]["HOST"]
    psql = os.path.join(pg_home, "bin", "psql") if pg_home else "psql"
    pg_restore = os.path.join(pg_home, "bin", "pg_restore") if pg_home else "pg_restore"

    if filename is None:
        backup_path = get_backup_path()
        backup_files = [
            f
            for f in os.listdir(backup_path)
            if os.path.isfile(os.path.join(backup_path, f))
        ]
        num_backup_files = len(backup_files)

        if num_backup_files:
            click.secho(
                "There are {num} backup files in '{backup_path}'. "
                "Which would you like to restore?".format(
                    num=num_backup_files, backup_path=backup_path,
                )
            )

            for key, value in enumerate(backup_files, 1):
                click.secho(
                    "{option_number}: {file}".format(option_number=key, file=value,)
                )
            file_choice = click.prompt("Enter number of the file to restore", type=int)
            filename = "{path}/{file}".format(
                path=backup_path, file=backup_files[file_choice - 1],
            )
        else:
            raise ValueError(
                'No input file was provided by the "--file" parameter, and there are '
                "no files in {backup_path}.".format(backup_path=backup_path,)
            )

    if not os.path.isfile(filename):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)

    if no_confirm:
        confirm = "yes"
    else:
        click.secho(
            "About to restore '{db}' on host '{host}' from the file:\n"
            "'{file}'\n"
            "THIS WILL OVERWRITE THE DATABASE.".format(
                db=db, host=host, file=filename,
            ),
            fg="red",
            bold=True,
        )

        confirm = click.prompt('Type "yes" to start the restore', default="no")

    if confirm == "yes":
        os.environ["PGPASSWORD"] = settings.DATABASES[database]["PASSWORD"]

        os.system(
            '{psql} -h {host} -U {user} -d {db} -c "DROP OWNED BY {user};"'.format(
                psql=psql, host=host, user=settings.DATABASES[database]["USER"], db=db,
            )
        )

        os.system(
            "{pg_restore} -c --if-exists -h {host} -U {user} -d {db} {file}".format(
                pg_restore=pg_restore,
                host=host,
                user=settings.DATABASES[database]["USER"],
                db=db,
                file=filename,
            )
        )

        os.environ["PGPASSWORD"] = ""
    else:
        click.secho(
            'Bailing out; you did not type "yes".', fg="green",
        )
