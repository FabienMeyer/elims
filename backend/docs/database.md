# Database and migrations

MariaDB is the production datastore. SQLModel and SQLAlchemy provide application persistence, and Alembic owns schema evolution.

Every schema change must include a reviewed migration, upgrade verification, data-loss analysis, and an operational recovery or rollback approach where practical.

## Models

Put each domain's table models in `app/api/<domain>/models.py`. Alembic imports every such module, so autogenerate sees all tables without a manual import list. A table model defined elsewhere is invisible to autogenerate.

All models share `SQLModel.metadata`, whose naming convention, set in `app/api/__init__.py`, gives indexes and constraints explicit names such as `uq_<table>_<column>` and `fk_<table>_<column>_<referred table>`. MariaDB and SQLite therefore use the same names, and later migrations can drop or alter constraints by name.

The backend test suite runs `alembic check` against a freshly migrated database and fails when the models and the migrations differ.

## Writing migrations for MariaDB

MariaDB commits each schema statement immediately, so a revision that fails partway cannot be rolled back: earlier statements stay applied and the revision is not recorded. Keep each revision to one logical change, put data changes in separate revisions from schema changes where practical, and plan recovery as a fix-forward migration or a documented manual cleanup.
