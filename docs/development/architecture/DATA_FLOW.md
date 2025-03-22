# HomeLab Bot Data Flow Architecture

## Core Data Flow

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
                       │ Discord UI      │
                       │  Rendering      │
                       └─────────────────┘
```
```
┌─────────────────────────────────────────────────────────┐
│                      Bot Core                           │
│  (Verbindungsmanagement, Event-Loop, Basis-Funktionen)  │
└───────────────────┬─────────────────────┬───────────────┘
        ┌───────────┴───────────┐ ┌───────┴───────────┐
        │   Service Registry    │ │  State Manager    │
        │ (Verwaltet Services)  │ │ (Persistenter     │
        └───────────┬───────────┘ │  Zustand)         │
                    │             └───────────────────┘
        ┌───────────┴──────────────────────────┐
        │                                      │
┌───────┴────────┐ ┌─────────────────┐ ┌───────────────┐
│ Channel Service│ │ Command Service │ │ Workflow      │
│                │ │                 │ │ Service       │
└───────┬────────┘ └────────┬────────┘ └───────┬───────┘
        │                   │                  │
        │                   │                  │
┌───────┴────────┐ ┌────────┴────────┐ ┌───────┴───────┐
│Channel Factory │ │Command Factory  │ │Workflow       │
│                │ │                 │ │Factory        │
└────────────────┘ └─────────────────┘ └───────────────┘

┌─────────────────────┐     ┌─────────────────────┐
│  Web Module         │     │  Bot Module         │
│                     │     │                     │
│  ┌───────────────┐  │     │  ┌───────────────┐  │
│  │ Admin API     │◄─┼─────┼─►│ Bot Control   │  │
│  │ Controllers   │  │     │  │ Service       │  │
│  └───────────────┘  │     │  └───────┬───────┘  │
└─────────────────────┘     │          │          │
                            │          ▼          │
                            │  ┌───────────────┐  │
                            │  │ Service       │  │
                            │  │ Registry      │  │
                            │  └───────────────┘  │
                            └─────────────────────┘
                            
```

## Database Initialization Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Web Container   │────▶│   PostgreSQL    │◀────│  Bot Container  │
│ Run Migrations  │     │   Database      │     │  Verify Data    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        ▲                       │
        │                        │                       │
        ▼                        │                       ▼
┌─────────────────┐              │             ┌─────────────────┐
│  Create Tables  │──────────────┘             │   Read Only     │
│  Seed Data      │                            │    Access       │
└─────────────────┘                            └─────────────────┘
```

## Component Access Layers

```
┌─────────────────┐
│  Presentation   │  Discord UI Components
└───────┬─────────┘
        │
┌───────▼─────────┐
│  Application    │  Commands, Events, Services
└───────┬─────────┘
        │
┌───────▼─────────┐
│    Domain       │  Business Logic, Models
└───────┬─────────┘
        │
┌───────▼─────────┐
│ Infrastructure  │  Database, External Services
└─────────────────┘
```

## Data Access Rules

1. **Web Interface**
   - CREATE/UPDATE configuration data
   - Run database migrations
  │ Manage database schema
  │ Seed initial data

2. **Bot Interface**
   - READ ONLY for configuration
   - No schema modifications
   - No data creation/updates
   - Verify data exists on startup

## Related Documentation
- [Layer Definitions](./LAYERS.md)
- [Dashboard Pattern](../patterns/DASHBOARD_PATTERN.md)
- [Project Structure](../../ai/context/CORE.md)
