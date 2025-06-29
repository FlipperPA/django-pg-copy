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
    "--port-override",
    "port_override",
    default=None,
    help="A value to override the port argument sent to psql.",
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
    "--drop/--no-drop",
    "drop",
    default=True,
    help="Drops objects in the target database before restoring to avoid errors.",
)
@click.option(
    "--cascade/--no-cascade",
    "cascade",
    default=False,
    help="If --drop is set, passes the --cascade option to the DROP OWNED BY command. ",
)
@click.option(
    "--no-confirm",
    "no_confirm",
    is_flag=True,
    help="Restores the database without confirmation: be careful!",
)
def command(
    database,
    db_override,
    host_override,
    port_override,
    pg_home,
    filename,
    jobs,
    directory,
    drop,
    cascade,
    no_confirm,
):
    """
    Django management command to restore a PostgreSQL database.
    """

    db = db_override or settings.DATABASES[database]["NAME"]
    host = host_override or settings.DATABASES[database]["HOST"]
    port = port_override or settings.DATABASES[database].get("PORT", None)
    port_cmd = f"-p {port}" if port else ""
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
                f"About to restore '{db}' on host '{host}:{port}' from the directory:\n"
                f"'{directory}'\n"
            )
        else:
            message = (
                f"About to restore '{db}' on host '{host}:{port}' from the file:\n"
                f"'{filename}'\n"
            )

        click.secho(
            f"{message}THIS WILL OVERWRITE THE DATABASE.",
            fg="red",
            bold=True,
        )

        confirm = click.prompt("Type 'yes' to start the restore", default="no")

    if confirm == "yes":
        os.environ["PGPASSWORD"] = settings.DATABASES[database]["PASSWORD"]

        try:
            DB_USER = settings.DATABASES[database]["USER"]

            if DB_USER == "postgres":
                click.secho(
                    "WARNING! User is set to 'postgres'. This is a bad practice, as the "
                    "'postgres' role is the default superuser account in PostgreSQL. "
                    "Not dropping any owned objects before the restore for safety.",
                    fg="yellow",
                )
            elif drop:
                drop_command = (
                    f"{psql} -h {host} -U {DB_USER} -d {db} {port_cmd} "
                    f'-c "SET ROLE {DB_USER}; DROP OWNED BY {DB_USER} '
                    f'{"CASCADE" if cascade else ""};"'
                )
                click.secho(
                    f"Dropping all objects owned by '{DB_USER}' in database '{db}' on "
                    f"host '{host}:{port}' before restoring.",
                    fg="yellow",
                )
                click.secho(
                    f"Command to drop owned objects: {drop_command}",
                    fg="white",
                    bold=True,
                )
                subprocess.check_output(
                    drop_command,
                    shell=True,
                )

            restore_command = (
                f"{pg_restore} -c -O -x --if-exists -h {host} -d {db} --jobs {jobs} "
                f"{port_cmd} -U {DB_USER} {restore}"
            )
            click.secho(
                f"Restoring database '{db}' on host '{host}:{port}'.",
                fg="yellow",
            )
            click.secho(
                f"Command to restore database: {restore_command}",
                fg="white",
                bold=True,
            )
            subprocess.check_output(
                restore_command,
                shell=True,
            )

            click.secho("The database has been restored.", fg="green")
        except subprocess.CalledProcessError as e:
            click.secho(e, fg="red")
            sys.exit(e.returncode)
        finally:
            os.environ["PGPASSWORD"] = ""
    else:
        click.secho(
            "Bailing out; you did not type 'yes'.",
            fg="green",
        )
