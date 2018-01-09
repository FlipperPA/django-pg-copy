# Django PostgreSQL Utilities

The package `django-pg-copy` provides Django management commands for backing up and restoring PostgreSQL databases. These were developed for copying production databases to development, to allow developers to share images with one another, or bring local development databases up to date.

## Installation

`pip install django-pg-copy`

## Settings

`PG_COPY_BACKUP_PATH = 'db_backup'` By default, PostgreSQL backups will be stored in a directory called `db_backup` at the root of the project. This setting will override that location.

It is also recommended to add this path to your `.gitignore` file, if the path falls under your version control repository.

## Contributors

* Timothy Allen (https://github.com/FlipperPA)
