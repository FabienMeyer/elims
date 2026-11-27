# elims-database

Reusable asynchronous SQLModel/SQLAlchemy infrastructure for monorepo applications.

```python
from elims_database import Database

database = Database("mysql+aiomysql://user:password@host/database")
```

## Documentation

```bash
uv sync --group docs
uv run mkdocs serve
```
