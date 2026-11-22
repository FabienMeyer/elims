# Database and migrations

MariaDB is the production datastore. SQLModel and SQLAlchemy provide application persistence, and Alembic owns schema evolution.

Every schema change must include a reviewed migration, upgrade verification, data-loss analysis, and an operational recovery or rollback approach where practical.
