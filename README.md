# Django PostgreSQL Copy

The package `django-pg-copy` provides Django management commands for backing up and restoring PostgreSQL databases. These were developed for copying production databases to development, to allow developers to share images with one another, or bring local development databases up to date. It can also be handy for creating different local databases for different branches, and for only creating one migration after tweaking models to get them the way they need to be.

We also use it with Jenkins to automatically back up production, and restore to a staging database environment, so we can test new migrations repeatedly to ensure they'll work when we run them in production.

## Installation

`pip install django-pg-copy`

Then add `'pg_copy',` to your `INSTALLED_APPS` list. It is recommended that it is used in all environments (development, production) so that you can use it against different instances of your database.

## Settings

`PG_COPY_BACKUP_PATH = 'db_backup'`

By default, PostgreSQL backups will be stored in a directory called `db_backup` where you run the command. This setting will override that location.

It is also recommended to add this path to your `.gitignore` file, if the path falls under your version control repository.

## Parameters

* `--database [TEXT]`: The database defined in the DATABASES settings to backup from or restore to.
* `--db-override [TEXT]`: A value to override the db argument sent to psql.
* `--host-override [TEXT]`: A value to override the host argument sent to psql.
* `--pg-home [TEXT]`: The path to the PostgreSQL installation, if it is not on your path.
* `--file [TEXT]`: The filename to backup to, or restore from.
* `--no-confirm`: Restores the database without confirmation: be careful! (**pg_restore** only)

## Example Commands

`python manage.py pg_backup --settings=config.settings.production --database=default --filename=my_backup.sqlc`

This command will create a backup in the same directory as `manage.py` called `my_backup.sqlc` using the `default` settings from `DATABASES` using the Django settings file located at `config/settings/production.py`.

`python manage.py pg_backup`

This command will create a backup in the directory `./db_backup/` (or the directory you specified with `PG_COPY_BACKUP_PATH`) called `[timestamp].sqlc` using the `default` settings from `DATABASES` using the default Django settings file resolved by `manage.py`.

`python manage.py pg_restore`

This command will provide a list of backup files in `PG_COPY_BACKUP_PATH` that can be restored. After selecting a backup file, it will confirm that the user wants to overwrite the destination database by showing which server and database will be overwritten from the settings.

`python manage.py pg_restore --filename=my_file.sqlc --no-confirm`

This command will read the file `my_file.sqlc` and confirm that the user wants to overwrite the destination database by showing which server and database will be overwritten from the settings.

## Known Issues

* When restoring, PostgreSQL's `pg_restore` command will output some warnings. I haven't figured out a command line option to make these warnings disappear, but they can be safely ignored if you read them. TODO: include a paste of the output here.

## Release Notes

* 0.2.0: Added new command line options: `--db-override`, `--host-override`, `--pg-home`, `--no-confirm`.
* 0.1.0: Initial release.

## Contributors

* Timothy Allen (https://github.com/FlipperPA)
* Ryan Sullivan (https://github.com/rgs258)
* Noel Victor (https://github.com/noeldvictor)
