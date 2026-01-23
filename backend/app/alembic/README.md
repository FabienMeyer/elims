# Alembic Database Migrations

This directory contains Alembic database migration scripts for ELIMS backend.

## Setup

Alembic is configured to work with SQLModel and async SQLAlchemy. The configuration automatically uses the database URL from your application settings.

## Common Commands

### Create a new migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration
alembic revision -m "description of changes"
```

### Apply migrations

```bash
# Upgrade to the latest version
alembic upgrade head

# Upgrade by one version
alembic upgrade +1

# Upgrade to specific revision
alembic upgrade <revision_id>
```

### Downgrade migrations

```bash
# Downgrade by one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>

# Downgrade to base (remove all migrations)
alembic downgrade base
```

### View migration history

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show migration history with details
alembic history --verbose
```

## Migration Best Practices

1. **Always review auto-generated migrations** - Alembic's autogenerate is smart but not perfect
1. **Test migrations in development first** - Always test upgrade and downgrade
1. **Keep migrations small and focused** - One logical change per migration
1. **Never edit applied migrations** - Create new migrations to fix issues
1. **Write descriptive migration messages** - Future you will thank you

## Environment Configuration

The database URL is automatically loaded from `app.config.settings`. Make sure your `.env` file has:

```env
MARIADB_HOST=localhost
MARIADB_PORT=3306
MARIADB_USER=your_user
MARIADB_PASSWORD=your_password
MARIADB_DATABASE=elims
```

## Docker Usage

When running in Docker, execute migrations:

```bash
# From project root
docker exec -it elims-backend alembic upgrade head

# Or when building/starting services
docker compose exec backend alembic upgrade head
```

## Troubleshooting

### "Target database is not up to date"

```bash
alembic stamp head
```

### "Can't locate revision identified by 'xyz'"

Check that all migration files are present in `alembic/versions/`

### Migration conflicts

If multiple developers create migrations simultaneously, you may need to merge them:

```bash
alembic merge heads
```
