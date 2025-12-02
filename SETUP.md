# PostgreSQL + Docker Setup Guide

This guide covers the complete PostgreSQL + Docker setup for the FastAPI backend with async SQLAlchemy 2.0.

## Files Created/Updated

### 1. Docker Configuration

- **docker-compose.yml**: PostgreSQL 15 service with healthcheck and FastAPI backend service
- **Dockerfile**: Python 3.11-slim based image with all dependencies

### 2. Environment Configuration

- **.env**: Database and JWT configuration (you need to create this manually - see below)

### 3. Database & Config Files

- **app/utils/database.py**: Async SQLAlchemy 2.0 setup with async_engine and AsyncSessionLocal
- **app/utils/config.py**: Pydantic Settings with JWT_SECRET_KEY and JWT_ALGORITHM
- **app/utils/dependencies.py**: Async get_db() and get_current_user() dependencies

### 4. Alembic Migrations

- **alembic.ini**: Alembic configuration
- **alembic/env.py**: Async-compatible migration environment
- **alembic/script.py.mako**: Migration template

## Setup Instructions

### Step 1: Create .env File

Create a `.env` file in the project root with the following content:

```env
DATABASE_URL=postgresql+asyncpg://exitprep_user:exitprep_pass@db:5432/exitprep
JWT_SECRET_KEY=your_generated_secure_key_change_this_in_production_use_openssl_rand_hex_32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Important**: Generate a secure JWT_SECRET_KEY for production:
```bash
openssl rand -hex 32
```

### Step 2: Build and Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

The backend will wait for PostgreSQL to be healthy before starting.

### Step 3: Initialize Alembic Migrations

#### Inside Docker Container

```bash
# Enter the backend container
docker-compose exec backend bash

# Initialize Alembic (if not already done)
# This is already set up, but if you need to reinitialize:
# alembic init alembic

# Create your first migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

#### From Host Machine

```bash
# Create migration
docker-compose exec backend alembic revision --autogenerate -m "Initial migration"

# Apply migrations
docker-compose exec backend alembic upgrade head
```

### Step 4: Verify Setup

```bash
# Check if services are running
docker-compose ps

# Check backend logs
docker-compose logs backend

# Check database logs
docker-compose logs db

# Test API health endpoint
curl http://localhost:8000/health
```

## Alembic Migration Workflow

### Creating Migrations

When you add or modify models:

1. **Autogenerate migration**:
   ```bash
   docker-compose exec backend alembic revision --autogenerate -m "description of changes"
   ```

2. **Review the generated migration** in `alembic/versions/`:
   - Check that it correctly reflects your model changes
   - Modify if needed (e.g., for data migrations)

3. **Apply migration**:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

### Common Alembic Commands

```bash
# View current database revision
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# Rollback to specific revision
docker-compose exec backend alembic downgrade <revision_id>

# Upgrade to specific revision
docker-compose exec backend alembic upgrade <revision_id>

# Show SQL for a migration (without applying)
docker-compose exec backend alembic upgrade head --sql
```

## Development Workflow

### Running Migrations During Development

1. Make changes to your models in `app/models/`
2. Generate migration: `docker-compose exec backend alembic revision --autogenerate -m "your message"`
3. Review the migration file
4. Apply: `docker-compose exec backend alembic upgrade head`

### Adding New Models

When you add a new model:

1. Create the model file in `app/models/`
2. Import it in `app/models/__init__.py`
3. Import it in `app/utils/database.py` (already done automatically via `from app.models import *`)
4. Import it in `alembic/env.py` (already set up to import all models)
5. Generate and apply migration

Example:
```python
# app/models/new_model.py
from app.models import Base
from sqlalchemy.orm import Mapped, mapped_column

class NewModel(Base):
    __tablename__ = "new_models"
    id: Mapped[int] = mapped_column(primary_key=True)
    # ... other fields
```

Then:
```bash
docker-compose exec backend alembic revision --autogenerate -m "Add NewModel"
docker-compose exec backend alembic upgrade head
```

## Database Connection

- **Host**: `db` (inside Docker) or `localhost` (from host)
- **Port**: `5432`
- **Database**: `exitprep`
- **User**: `exitprep_user`
- **Password**: `exitprep_pass`

### Connecting from Host Machine

```bash
# Using psql
psql -h localhost -p 5432 -U exitprep_user -d exitprep

# Or using docker
docker-compose exec db psql -U exitprep_user -d exitprep
```

## Troubleshooting

### Database Connection Issues

If you see connection errors:

1. Check if PostgreSQL is healthy:
   ```bash
   docker-compose ps db
   ```

2. Check database logs:
   ```bash
   docker-compose logs db
   ```

3. Verify .env file has correct DATABASE_URL

### Migration Issues

If migrations fail:

1. Check current revision:
   ```bash
   docker-compose exec backend alembic current
   ```

2. View migration history:
   ```bash
   docker-compose exec backend alembic history
   ```

3. If stuck, you can manually fix the alembic_version table:
   ```sql
   -- Connect to database
   docker-compose exec db psql -U exitprep_user -d exitprep
   
   -- Check current version
   SELECT * FROM alembic_version;
   
   -- Update if needed (be careful!)
   UPDATE alembic_version SET version_num = '<revision_id>';
   ```

### Async Session Issues

If you see errors about async/await:

- Make sure all route handlers are `async def`
- Use `await db.execute(select(...))` instead of `db.query(...)`
- Use `await db.commit()` instead of `db.commit()`
- Use `await db.refresh()` instead of `db.refresh()`

## Production Considerations

1. **Change JWT_SECRET_KEY**: Use a strong, randomly generated key
2. **Update CORS origins**: Modify `main.py` to allow only your frontend domain
3. **Use environment-specific .env files**: Don't commit `.env` to version control
4. **Database backups**: Set up regular backups of the PostgreSQL volume
5. **SSL/TLS**: Configure SSL for database connections in production
6. **Resource limits**: Add resource limits to docker-compose.yml for production

## Notes

- The setup uses **async SQLAlchemy 2.0** with `asyncpg` for database connections
- Alembic migrations use **sync psycopg2** connections (Alembic requirement)
- All models are automatically imported in both `database.py` and `alembic/env.py`
- The database URL format: `postgresql+asyncpg://` for app, converted to `postgresql+psycopg2://` for migrations

