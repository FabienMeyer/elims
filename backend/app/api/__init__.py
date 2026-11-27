"""HTTP API domains.

Each domain keeps its table models in ``app/api/<domain>/models.py``, where Alembic discovers them. Importing
any domain imports this package first, so the naming convention below is set before any table is defined;
SQLAlchemy names constraints when a table is created, not afterwards.
"""

from sqlmodel import SQLModel

# Explicit names keep constraints identical on MariaDB and SQLite, so later migrations can drop them by name.
SQLModel.metadata.naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
