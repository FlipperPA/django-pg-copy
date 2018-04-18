import errno
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
    help='The filename of the input backup file to restore.',
)
def command(database, filename):
    """
    Django management command to restore a PostgreSQL database.
    """

    if filename is None:
        backup_path = get_backup_path()
        backup_files = [f for f in os.listdir(backup_path) if os.path.isfile(os.path.join(backup_path, f))]
        num_backup_files = len(backup_files)

        if num_backup_files:
            click.secho(
                "There are {num} backup files in '{backup_path}'. Which would you like to restore?".format(
                    num=num_backup_files,
                    backup_path=backup_path,
                )
            )

            for key, value in enumerate(backup_files, 1):
                click.secho(
                    '{option_number}: {file}'.format(
                        option_number=key,
                        file=value,
                    )
                )
            file_choice = click.prompt('Enter the number of the file to restore', type=int)
            filename = '{path}/{file}'.format(
                path=backup_path,
                file=backup_files[file_choice - 1],
            )
        else:
            raise ValueError(
                'No input file was provided by the "--file" parameter, and there are no files in {backup_path}.'.format(
                    backup_path=backup_path,
                )
            )

    if not os.path.isfile(filename):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)

    click.secho(
        "About to restore '{db}' on host '{host}' from the file '{filename}'. THIS WILL OVERWRITE THE DATABASE.".format(
            db=settings.DATABASES[database]['NAME'],
            host=settings.DATABASES[database]['HOST'],
            filename=filename,
        ),
        fg="red",
        bold=True,
    )

    confirm = click.prompt('Type "yes" to start the restore', default='no')

    if confirm == "yes":
        os.environ["PGPASSWORD"] = settings.DATABASES[database]['PASSWORD']

        os.system(
            'psql -h {host} -U {username} -d {db} -c "DROP OWNED BY {username};"'.format(
                host=settings.DATABASES[database]['HOST'],
                username=settings.DATABASES[database]['USER'],
                db=settings.DATABASES[database]['NAME'],
            )
        )

        os.system(
            'pg_restore -c --if-exists -h {host} -U {username} -d {db} {file}'.format(
                host=settings.DATABASES[database]['HOST'],
                username=settings.DATABASES[database]['USER'],
                db=settings.DATABASES[database]['NAME'],
                file=filename,
            )
        )

        os.environ["PGPASSWORD"] = ''
    else:
        click.secho(
            'Bailing out; you did not type "yes".',
            fg="green",
        )
