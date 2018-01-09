# Django PostgreSQL Copy

The package `django-pg-copy` provides Django management commands for backing up and restoring PostgreSQL databases. These were developed for copying production databases to development, to allow developers to share images with one another, or bring local development databases up to date.

## Installation

`pip install django-pg-copy` (Coming soon)

`pip install git+https://github.com/FlipperPA/django-pg-copy.git` (For now)

## Settings

`PG_COPY_BACKUP_PATH = 'db_backup'` By default, PostgreSQL backups will be stored in a directory called `db_backup` at the root of the project. This setting will override that location.

It is also recommended to add this path to your `.gitignore` file, if the path falls under your version control repository.

## Example Commands

`python manage.py pg_backup --settings=config.settings.production --database=default --filename=my_backup.sqlc`

This command will create a backup in the same directory as `manage.py` called `my_backup.sqlc` using the `default` settings from `DATABASES` using the Django settings file `config.settings.production`.

`python manage.py pg_backup`

This command will create a backup in the directory `./db_backup/` (or the directory you specified with `PG_COPY_BACKUP_PATH`) called '[timestamp].sqlc` using the `default` settings from `DATABASES` using the default Django settings file resolved by `manage.py`.

`python manage.py pg_restore`

This command will provide a list of backup files in `PG_COPY_BACKUP_PATH` that can be restored. After selecting a backup file, it will confirm that the user wants to overwrite the destination database by showing which server and database will be overwritten from the settings.

`python manage.py pg_restore --filename=my_file.sqlc`

This command will read the file `my_file.sqlc` and confirm that the user wants to overwrite the destination database by showing which server and database will be overwritten from the settings.

## Contributors

* Timothy Allen (https://github.com/FlipperPA)
