# HomeLab Discord Bot Data-Driven Architecture

_Last Updated: [Current Date]_

## System Architecture Overview

The HomeLab Discord Bot uses a layered architecture based on Domain-Driven Design principles with a strong emphasis on data-driven design, where configurations and definitions are stored in PostgreSQL rather than hardcoded:

```
┌─────────────────────────────────────────────────────────────────┐
│ Interface Layer                                                 │
│ (Discord Commands, Dynamic Dashboards, User Interactions)       │
└───────────────────┬─────────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────────┐
│ Application Layer                                               │
│ (Application Services, Command Handlers, Builders)              │
└───────────────────┬─────────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────────┐
│ Domain Layer                                                    │
│ (Domain Models, Services, Business Logic)                       │
└───────────────────┬─────────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────────┐
│ Infrastructure Layer                                            │
│ (Discord API, Repository Implementations, External Services)    │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Shared Layer                                                    │
│ (Database Access, Common Utilities, Shared Models)              │
└─────────────────────────────────────────────────────────────────┘
```

## Data-Driven Design Approach

The bot uses a data-driven approach where system configuration and component definitions are stored in PostgreSQL:

1. **Database-Driven Configuration**: System settings, component definitions, dashboard layouts, and other configurations are stored in PostgreSQL, not hardcoded.

2. **Dynamic Component Registry**: Components are registered at runtime and instantiated based on database definitions.

3. **Builder Pattern**: The system uses builders to dynamically construct dashboards, services, and components from database definitions.

4. **Repository Pattern**: Domain objects are retrieved from PostgreSQL through repositories that map database records to domain models.

5. **Factory Pattern**: Factories create instances of domain objects and services based on configuration data from the database.

## Shared Database Architecture

The bot does not manage the database schema but consumes from a shared database:

```
┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│      Web Admin Interface        │     │      Discord Bot                │
│                                 │     │                                 │
│  ┌─────────────────────────┐    │     │  ┌─────────────────────────┐    │
│  │  Database Management    │    │     │  │  Repository Layer       │    │
│  │  (Migrations, Schema)   │    │     │  │  (Data Access Only)     │    │
│  └────────────┬────────────┘    │     │  └────────────┬────────────┘    │
│               │                 │     │               │                 │
└───────────────┼─────────────────┘     └───────────────┼─────────────────┘
                │                                       │
                ▼                                       ▼
          ┌───────────────────────────────────────────────────┐
          │                                                   │
          │                PostgreSQL Database                │
          │                                                   │
          └───────────────────────────────────────────────────┘
                                    ▲
                                    │
            ┌─────────────────────────────────────────────────┐
            │           app/shared/database                   │
            │                                                 │
            │  ├── models/        # Shared entity models      │
            │  ├── migrations/    # Database migrations       │
            │  └── core/          # Connection management     │
            └─────────────────────────────────────────────────┘
```

## Database Access in Bot Infrastructure

```python
# Example Repository Implementation
class DashboardRepositoryImpl(DashboardRepository):
    """Implementation of dashboard repository using PostgreSQL"""
    def __init__(self, db_connection):
        self.db = db_connection  # Shared connection from app/shared/database
        
    async def get_dashboard_by_id(self, dashboard_id):
        """Fetch dashboard definition from PostgreSQL"""
        query = "SELECT * FROM dashboards WHERE id = $1"
        dashboard_record = await self.db.fetchrow(query, dashboard_id)
        
        if not dashboard_record:
            return None
            
        # Load components for this dashboard
        components_query = "SELECT * FROM dashboard_components WHERE dashboard_id = $1"
        component_records = await self.db.fetch(components_query, dashboard_id)
        
        # Map DB records to domain models
        components = [self._map_component_record(r) for r in component_records]
        
        # Create and return domain model
        return DashboardDefinition(
            id=dashboard_record['id'],
            name=dashboard_record['name'],
            description=dashboard_record['description'],
            layout=json.loads(dashboard_record['layout']),
            components=components,
            refresh_rate=dashboard_record['refresh_rate']
        )
```

## Layer-to-Database Interaction

Each layer interacts with the database in specific ways:

1. **Interface Layer**: No direct database access; uses controllers to request data

2. **Application Layer**: Uses repositories to retrieve data; orchestrates domain objects

3. **Domain Layer**: Contains models that reflect database structure; no direct database access

4. **Infrastructure Layer**: Contains repository implementations that map between database and domain models 

5. **Shared Layer**: Provides database connection and access utilities used by the repository implementations

## Benefits of Shared Database Architecture

1. **Separation of Concerns**: Bot consumes data but doesn't manage the schema
2. **Centralized Database Management**: Web frontend handles database administration
3. **Consistent Data Access**: Shared models ensure consistency across applications
4. **Schema Independence**: Bot can adapt to schema changes without code changes
5. **Reduced Duplication**: Database utilities shared between bot and web frontend

## Related Documentation
- [Design Patterns](../patterns/DESIGN_PATTERN.md) - Implementation patterns
- [Data Flow Patterns](./DATA_FLOW.md) - Component interaction patterns
- [Project Structure](../../ai/context/CORE.md) - Overall project organization
- [Coding Conventions](../guidelines/CONVENTIONS.md) - Implementation standards
