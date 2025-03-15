# Database Migrations

This directory contains database migration scripts using Alembic.

## Commands

### Create a new migration

Automatically generate migration based on model changes

```bash
alembic revision --autogenerate -m "description of changes"
```

Create an empty migration

```bash
alembic revision -m "description of changes"
```
### Apply migrations
bash
Apply all pending migrations

```bash
alembic upgrade head
```

Apply next migration

```bash
alembic upgrade +1
```

Apply specific migration

```bash
alembic upgrade <revision>
```
### Rollback migrations

Rollback the last migration

```bash
alembic downgrade -1
```

Rollback to specific migration

```bash
alembic downgrade <revision>
```

Rollback all migrations

```bash
alembic downgrade base
```
### Migration information

Show current revision

```bash
alembic current
```

Show migration history

```bash
alembic history
```

Show pending migrations

```bash

EXAMPLE:

Generate a migration for CategoryMapping:

```bash
Navigate to your project root
cd /path/to/your/project
Run alembic to generate a migration
alembic revision --autogenerate -m "Add CategoryMapping table"
```

This will create a new file in `app/bot/infrastructure/database/migrations/versions/` with SQL commands to create the CategoryMapping table.

### 3. Apply the migration:

```bash
Run the migration
alembic upgrade head
```

### 4. Update DatabaseWorkflow to use Alembic:

```python
from .base_workflow import BaseWorkflow
from app.shared.logging import logger
from alembic.config import Config
from alembic import command
class DatabaseWorkflow(BaseWorkflow):
async def initialize(self):
try:
logger.debug("Starting database workflow initialization")
# Run database migrations using Alembic
await self.run_migrations()
# Migrate existing users if needed (keep this as a separate step)
from app.shared.infrastructure.database.migrations.init_db import migrate_existing_users
await migrate_existing_users()
# Verify database integrity
await self.verify_database_integrity()
logger.info("Database workflow initialized successfully")
return True
except Exception as e:
logger.error(f"Database workflow initialization failed: {e}")
raise
async def run_migrations(self):
"""Run database migrations using Alembic"""
try:
import os
from concurrent.futures import ThreadPoolExecutor
# Create Alembic configuration
alembic_cfg = Config("app/bot/infrastructure/database/migrations/alembic.ini")
# Run migrations in a thread pool to avoid blocking the event loop
with ThreadPoolExecutor() as pool:
await self.bot.loop.run_in_executor(
pool, command.upgrade, alembic_cfg, "head"
)
logger.info("Database migrations completed successfully")
except Exception as e:
logger.error(f"Database migrations failed: {e}")
raise
```

This ensures that database migrations are run asynchronously and do not block the event loop.

## Decision based on Your Needs

1. If you're in early development and frequently changing your schema, stick with approach #1 for now.

2. If you need more control, data preservation, and versioning, invest time in setting up Alembic (approach #2).

Would you like me to help with implementing either approach further?