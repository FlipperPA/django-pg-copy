import errno
import os
import subprocess
import sys

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
    "--file",
    "filename",
    help="The filename of the input backup file to restore.",
)
@click.option(
    "--jobs",
    "-j",
    "jobs",
    default=1,
    help="How many parallel jobs to run. This can drastically increase execution "
    "speed.",
)
@click.option(
    "--directory",
    "-d",
    "directory",
    default=None,
    help="The directory to restore. Overrides the --file parameter.",
)
@click.option(
    "--no-confirm",
    "no_confirm",
    is_flag=True,
    help="Restores the database without confirmation: be careful!",
)
def command(
    database, db_override, host_override, pg_home, filename, jobs, directory, no_confirm
):
    """
    Django management command to restore a PostgreSQL database.
    """

    db = db_override or settings.DATABASES[database]["NAME"]
    host = host_override or settings.DATABASES[database]["HOST"]
    psql = os.path.join(pg_home, "bin", "psql") if pg_home else "psql"
    pg_restore = os.path.join(pg_home, "bin", "pg_restore") if pg_home else "pg_restore"

    if directory:
        if not os.path.isdir(directory):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), directory)

        restore = f"--format=directory {directory}"
    else:
        if filename is None and directory is None:
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
                        num=num_backup_files,
                        backup_path=backup_path,
                    )
                )

                for key, value in enumerate(backup_files, 1):
                    click.secho(
                        "{option_number}: {file}".format(
                            option_number=key,
                            file=value,
                        )
                    )
                file_choice = click.prompt(
                    "Enter number of the file to restore", type=int
                )
                filename = "{path}/{file}".format(
                    path=backup_path,
                    file=backup_files[file_choice - 1],
                )
            else:
                raise ValueError(
                    'No input file was provided by the "--file" parameter, and there '
                    "are no files in {backup_path}.".format(
                        backup_path=backup_path,
                    )
                )

        if not os.path.isfile(filename):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)

        restore = f"--format=custom {filename}"

    if no_confirm:
        confirm = "yes"
    else:
        if directory:
            message = (
                f"About to restore '{db}' on host '{host}' from the directory:\n"
                f"'{directory}'\n"
            )
        else:
            message = (
                f"About to restore '{db}' on host '{host}' from the file:\n"
                f"'{filename}'\n"
            )

        click.secho(
            f"{message}THIS WILL OVERWRITE THE DATABASE.",
            fg="red",
            bold=True,
        )

        confirm = click.prompt('Type "yes" to start the restore', default="no")

    if confirm == "yes":
        os.environ["PGPASSWORD"] = settings.DATABASES[database]["PASSWORD"]

        try:
            subprocess.check_output(
                f'{psql} -h {host} -U {settings.DATABASES[database]["USER"]} -d {db} '
                f'-c "DROP OWNED BY {settings.DATABASES[database]["USER"]};"',
                shell=True,
            )

            subprocess.check_output(
                f"{pg_restore} -c --if-exists -h {host} -d {db} --jobs {jobs} "
                f"""-U {settings.DATABASES[database]["USER"]} {restore}""",
                shell=True,
            )
            click.secho("The database has been restored.", fg="green")
        except subprocess.CalledProcessError as e:
            print(e)
            sys.exit(e.returncode)
        finally:
            os.environ["PGPASSWORD"] = ""
    else:
        click.secho(
            "Bailing out; you did not type 'yes'.",
            fg="green",
        )
