# HomeLab Bot Data Flow Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Web Interface   │────▶│  Data Storage   │◀────│   Bot Data      │
│ (Data Creation) │     │   (PostgreSQL)  │     │ Consumption     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │                       │
                                │                       ▼
                                │             ┌─────────────────┐
                                │             │  Repository     │
                                │             │     Layer       │
                                │             └─────────────────┘
                                │                      │
                                ▼                      ▼
┌─────────────────┐     ┌───────────────┐     ┌─────────────────┐
│   Shared DB     │────▶│ Domain Models │◀────│ Application     │
│  Access Layer   │     │               │     │ Services        │
└─────────────────┘     └───────────────┘     └─────────────────┘
                                │                      │
                                ▼                      │
                       ┌─────────────────┐             │
                       │   View Models   │◀────────────┘
                       │                 │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Rendering Layer │
                       │                 │
                       └─────────────────┘
```

## Web Interface to Bot Data Flow

1. **Web UI Data Creation**: Administrators create/modify configuration data through web interface
   │
   ▼
2. **Database Storage**: Configuration data is stored in PostgreSQL
   │
   ▼
3. **Bot Data Consumption**: Bot reads configuration from shared database

## Data-Driven Dashboard Flow in Bot

1. **Repository Layer**: Dashboard Repository loads dashboard definition from PostgreSQL
   │
   ▼
2. **Domain Models**: Data is mapped to domain models (DashboardDefinition, ComponentDefinition)
   │
   ▼
3. **Application Services**: DashboardBuilder assembles dashboard from definition
   │
   ▼
4. **Component Registry**: Components are instantiated based on their type from registry
   │
   ▼
5. **Data Sources**: Each component connects to its configured data source for live data
   │
   ▼
6. **View Assembly**: Complete dashboard view is assembled with data-populated components
   │
   ▼
7. **Rendering**: Final dashboard is rendered to Discord UI

## Data Access in Bot Applications

1. **Shared Database Access Layer**: Located in `app/shared/database/core/`
   │
   ▼
2. **Repository Implementations**: Use shared database layer but live in bot infrastructure
   │
   ▼
3. **Domain Access**: Application services use repositories through domain interfaces
   │
   ▼
4. **Command/Event Handling**: Commands and events trigger application layer operations
   │
   ▼
5. **UI Rendering**: Results are formatted for Discord display

## Related Documentation
- [Layer Definitions](./LAYERS.md) - Component layer organization
- [Dashboard Pattern](../patterns/DASHBOARD_PATTERN.md) - Dashboard implementation
- [Project Structure](../../ai/context/CORE.md) - Overall project organization
