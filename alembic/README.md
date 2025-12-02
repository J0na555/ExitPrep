# Alembic Migrations

This directory contains database migration scripts managed by Alembic.

## Usage

### Initialize (already done)
```bash
alembic init alembic
```

### Create a new migration
```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback one migration
```bash
alembic downgrade -1
```

### View current revision
```bash
alembic current
```

### View migration history
```bash
alembic history
```

