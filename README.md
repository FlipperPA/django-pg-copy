# Django PostgreSQL Copy

The package `django-pg-copy` provides Django management commands for backing up and restoring PostgreSQL databases. These were developed for copying production databases to development, to allow developers to share images with one another, or bring local development databases up to date. It can also be handy for creating different local databases for different branches, and for only creating one migration after tweaking models to get them the way they need to be.

We also use it with Jenkins to automatically back up production, and restore to a staging database environment, so we can test new migrations repeatedly to ensure they'll work when we run them in production.

## Installation

`pip install django-pg-copy`

Then add `'pg_copy',` to your `INSTALLED_APPS` list. It is recommended that it is used in all environments (development, production) so that you can use it against different instances of your database.

## Settings

`PG_COPY_BACKUP_PATH = 'db_backup'`

By default, PostgreSQL file backups will be stored in a directory called `db_backup` where you run the command. This setting will override that location.

It is also recommended to add this path to your `.gitignore` file, if the path falls under your version control repository.

## Parameters

* `--database`: The database defined in the DATABASES settings to backup from or restore to.
* `--db-override`: A value to override the db argument sent to psql.
* `--host-override`: A value to override the host argument sent to psql.
* `--pg-home`: The path to the PostgreSQL installation, if it is not on your path.
* `--file`, `-f`: The filename to backup to, or restore from.
* `--jobs`, `-j`: The number of parallel jobs to run. This can *drastically* increase the speed of the backup and restore. When backing up, this must use the `--directory` option. *Be careful!* This will also create multiple database connections and can slow your database down.
* `--directory`, `-d`: Restore from a directory. Overrides `--file` when used.

### Backup Only Parameters for `pg_backup`

* `--ignore-table`, `-i`: Excludes the table completely during the backup process. Can pass multiple tables: `-i bigtable1 -i bigtable2`
* `--exclude-table-data`, `-e`: Excludes the table data during the backup process. Can pass multiple tables: `-e bigtable1 -e bigtable2`

### Restore Only Parameters for `pg_restore`

* `--cascade`: Performs a `CASCADE` during the default `DROP OWNED BY` operation.
* `--no-drop`: Restores the database without performing a `DROP OWNED BY`.
* `--no-confirm`: Restores the database without confirmation: be careful! DON'T OVERWRITE YOUR PROD DATABASE! (Ask me how I know.)

## Example Commands

`python manage.py pg_backup`

Creates a backup file in the directory `./db_backup/` (or the directory you specified with `PG_COPY_BACKUP_PATH`) called `[timestamp].sqlc` using the `default` settings from `DATABASES` using the default Django settings file resolved by `manage.py`.

`python manage.py pg_backup --directory=/tmp/pg_backup --jobs=8`

This command will create a backup directory at `/tmp/backup` using 8 parallel jobs and database connections. This is typically *much* faster.

`python manage.py pg_backup --settings=config.settings.production --database=default --filename=my_backup.sqlc`

This command will create a backup in the same directory as `manage.py` called `my_backup.sqlc` using the `default` settings from `DATABASES` using the Django settings file located at `config/settings/production.py`.

`python manage.py pg_backup -i bigtable1 -i bigtable2`

This will do the same as the previous command, but omit the tables named `bigtable1` and `bigtable2`.

`python manage.py pg_backup -e bigtable1 -e bigtable2`

This will do the same as the previous command, but include the table structure without any data for the tables named `bigtable1` and `bigtable2`.

`python manage.py pg_restore`

This command will provide a list of backup files in `PG_COPY_BACKUP_PATH` that can be restored. After selecting a backup file, it will confirm that the user wants to overwrite the destination database by showing which server and database will be overwritten from the settings. Here's what it will look like:

```bash
(venv) [django-project]$ ./manage.py pg_restore
There are 8 backup files in '/var/dev/username/django-project/db_backup'. Which would you like to restore?
1: 2020-05-27-13-33-38.sqlc
2: 2020-05-10-09-07-45.sqlc
3: 2020-05-11-13-05-49.sqlc
4: 2020-07-14-15-21-22.sqlc
5: 2020-05-15-08-31-59.sqlc
6: 2020-06-11-13-11-00.sqlc
7: 2020-06-02-13-28-09.sqlc
8: 2020-05-27-14-54-15.sqlc
Enter number of the file to restore: 4
About to restore 'django_project_db' on host 'localhost' from the file:
'/var/dev/username/django-project/db_backup/2020-07-14-15-21-22.sqlc'.
THIS WILL OVERWRITE THE DATABASE.
Type "yes" to start the restore [no]: yes
```

`python manage.py pg_restore --filename=my_file.sqlc --no-confirm`

This command will read the file `my_file.sqlc` and **skip confirmation** that the user wants to overwrite the destination database.

`python manage.py pg_restore --directory=/tmp/pg_backup --jobs=8`

This command will restore from the directory `/tmp/pg_backup` using 8 parallel jobs and database connections.

## Known Issues

#### Errors Displayed During `pg_restore`

When restoring, PostgreSQL's `pg_restore` command may output some ownership related errors. These are often safe to ignore if you are restoring to a development environment. Here is an example of what these errors may look like:

```bash
pg_restore: [archiver (db)] Error while PROCESSING TOC:
pg_restore: [archiver (db)] Error from TOC entry 1; 3079 13792 EXTENSION plpgsql
pg_restore: [archiver (db)] could not execute query: ERROR:  must be owner of extension plpgsql
    Command was: DROP EXTENSION IF EXISTS plpgsql;

pg_restore: [archiver (db)] Error from TOC entry 6; 2615 2200 SCHEMA public postgres
pg_restore: [archiver (db)] could not execute query: ERROR:  must be owner of schema public
    Command was: DROP SCHEMA IF EXISTS public;

pg_restore: [archiver (db)] could not execute query: ERROR:  schema "public" already exists
    Command was: CREATE SCHEMA public;
```

These may be errors from extensions that aren't used, or warnings about default schemata that already exist.

## Release Notes

[Release notes are available on GitHub](https://github.com/FlipperPA/django-pg-copy/releases).

## Maintainer and Contributors

* [Our Wonderful Contributors on GitHub](https://github.com/FlipperPA/django-pg-copy/graphs/contributors)
* Maintainer: [Timothy Allen](https://github.com/FlipperPA) at [The Wharton School](https://github.com/wharton)

This package is maintained by the staff of [Wharton Research Data Services](https://wrds.wharton.upenn.edu/). We are thrilled that [The Wharton School](https://www.wharton.upenn.edu/) allows us to contribute to open-source projects. We add features as they are necessary for our projects, and try to keep up with Issues and Pull Requests as best we can. Due to constraints of time (our full time jobs!), Feature Requests without a Pull Request may not be implemented, but we are always open to new ideas and grateful for both contributors and users.
