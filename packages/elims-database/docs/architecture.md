# Architecture

The package owns only the technical lifecycle of the asynchronous engine and sessions.

- Domain packages own their SQLModel models.
- The assembling application owns Alembic configuration and migrations.
- Transaction boundaries remain the responsibility of the consuming application.
- The connection URL selects the database and async driver.

The package does not depend on FastAPI or a specific business domain.
