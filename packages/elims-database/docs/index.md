# elims-database

`elims-database` provides reusable asynchronous SQLAlchemy and SQLModel engine and session infrastructure.

## Installation

Install the package together with the async database driver selected by the application:

```bash
pip install elims-database asyncmy
```

## Usage

```python
from elims_database import Database

database = Database("mysql+asyncmy://user:password@host/database")

async for session in database.sessions():
    ...

await database.dispose()
```
