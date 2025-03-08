# HomeLab Discord Bot Subject Guide

## System Overview
The HomeLab Discord Bot is a management and monitoring system for a home lab environment, providing dashboards, project management, and system monitoring capabilities through Discord.

## Architecture

### Domain-Driven Design (DDD)
The project follows Domain-Driven Design principles with a clear separation of:

- **Domain Layer**: Core business logic and entities
- **Application Layer**: Orchestration of domain objects to perform tasks
- **Infrastructure Layer**: Technical capabilities that support the application
- **Interface Layer**: User interaction points (commands, dashboards)

### Project Structure
```
app/
├── bot/
│ ├── application/ # Application services
│ ├── core/ # Core bot functionality
│ ├── domain/ # Domain models and business logic
│ │ ├── auth/ # Authentication domain
│ │ ├── channels/ # Channel management domain
│ │ ├── gameservers/ # Game server domain
│ │ ├── monitoring/ # System monitoring domain
│ │ └── tracker/ # Project tracking domain
│ ├── infrastructure/ # Technical infrastructure
│ │ ├── config/ # Configuration management
│ │ ├── database/ # Database access
│ │ ├── discord/ # Discord-specific infrastructure
│ │ ├── factories/ # Object factories
│ │ ├── logging/ # Logging infrastructure
│ │ └── security/ # Security infrastructure
│ ├── interfaces/ # User interfaces
│ │ ├── commands/ # Discord commands
│ │ ├── dashboards/ # Dashboard interfaces
│ └── utils/ # Utility functions
```

### Design Patterns

1. **Factory Pattern**: Used extensively to create complex objects
   - `BotComponentFactory`: Creates bot components
   - `DashboardFactory`: Creates dashboard UI components
   - `ChannelFactory`: Creates Discord channels

2. **Repository Pattern**: Abstracts data access
   - `UserRepository`: Manages user data
   - `ProjectRepository`: Manages project data
   - `MonitoringRepository`: Manages monitoring data

3. **Service Pattern**: Encapsulates business logic
   - `AuthenticationService`: Handles authentication
   - `ProjectService`: Manages projects
   - `MonitoringService`: Processes monitoring data

4. **Dependency Injection**: Used for loose coupling
   - Services are injected into UI components
   - Repositories are injected into services

5. **Command Pattern**: Used for Discord commands
   - Each command is encapsulated in its own class
   - Commands are registered with the bot

## Key Components

### Dashboards

- **WelcomeDashboardUI**: Creates welcome messages with interactive components
- **ProjectDashboardUI**: Manages projects in a dedicated projects channel
- **SystemMonitoringDashboardUI**: Displays system status in the general channel


### System Monitoring
- **System Status Collectors**: Various modules that collect system data:
  - Hardware information (CPU, GPU, Memory)
  - Storage usage
  - Network statistics
  - Docker container status
  - Security information (SSH attempts)
  - Service status (web services, game servers)

### UI Components
- **DashboardFactory**: Creates different types of dashboards
- **Views and Embeds**: Discord UI components for interactive interfaces
- **Buttons and Menus**: Interactive elements for user input

## Technical Architecture
- Uses nextcord for Discord integration
- Follows a service-oriented architecture with dependency injection
- Employs async/await for non-blocking operations
- Uses factories to create UI components
- Implements repository pattern for data access

## Data Flow
1. System collectors gather data from the host system
2. Services process and format this data
3. UI components display the data in Discord channels
4. User interactions trigger callbacks that update or display additional information

## Key Concepts
- **Dashboards**: Interactive Discord messages with embeds and buttons
- **Services**: Backend components that gather and process data
- **Factories**: Create UI components and other objects
- **Collectors**: Gather system information from various sources
- **Repositories**: Abstract data access and persistence
- **Commands**: User interaction points for specific actions