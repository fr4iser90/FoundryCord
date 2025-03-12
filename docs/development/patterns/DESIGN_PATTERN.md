# HomeLab Discord Bot: Architecture & Design Patterns Guide

## Introduction

This guide documents the architectural patterns and design principles used in the HomeLab Discord Bot. It provides both a reference for understanding the existing codebase and guidance for implementing new features.

## Core Architecture: Domain-Driven Design (DDD)

The bot is structured using Domain-Driven Design principles, which organizes code around business domains and clearly separates concerns:

### 1. Domain Layer
**Purpose**: Contains core business logic and domain models
- **Models**: `Project`, `Task`, `User`, etc.
- **Domain Services**: `PermissionService`, `MetricService`, etc.
- **Domain Policies**: Authorization rules, validation logic

**Example**:
```python
# Domain service with clear business logic focus
class PermissionService:
    def is_authorized(self, user):
        return is_authorized(user)
    
    def has_permission(self, user, permission):
        return permission in Permission.get_role_permissions(user.role)
```

### 2. Application Layer
**Purpose**: Orchestrates domain objects to fulfill user requirements
- **Application Services**: `ProjectDashboardService`, `SystemMonitoringService`
- **Command Handlers**: Process user commands by delegating to domain services

**Example**:
```python
# Application service orchestrating domain logic
class SystemMonitoringService:
    def __init__(self, bot):
        self.bot = bot
    
    async def get_full_system_status(self):
        try:
            # CPU, Memory, Disk usage
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Fetch Public IPv4 address
            try:
                public_ip = http_client.get("https://api.ipify.org?format=json").json()['ip']
            except requests.RequestException:
                public_ip = "Unable to fetch public IP"
                
            return {
                "cpu_percent": cpu_percent,
                "memory": memory,
                "disk": disk,
                "public_ip": public_ip,
                # Additional fields omitted for brevity
            }
        except Exception as e:
            logger.error(f"Error retrieving system status: {e}")
            raise
```

### 3. Infrastructure Layer
**Purpose**: Provides technical capabilities and integrations
- **Repositories**: `ProjectRepository`, `TaskRepository` 
- **Factories**: `ServiceFactory`, `TaskFactory`
- **External Integrations**: Discord API, database connections

**Example**:
```python
# Repository pattern in infrastructure layer
class ProjectRepository:
    def __init__(self, session):
        self.session = session
    
    async def get_by_id(self, project_id):
        result = await self.session.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()
```

### 4. Interface Layer
**Purpose**: Handles user interaction
- **Commands**: Discord slash commands
- **Dashboards**: Interactive Discord message UIs
- **Views & Embeds**: Visual presentation components

**Example**:
```python
# Discord command interface
class ProjectCommands(commands.Cog):
    def __init__(self, bot, project_service):
        self.bot = bot
        self.project_service = project_service
    
    @nextcord.slash_command(name="project", description="Project commands")
    async def project(self, interaction):
        pass
    
    @project.subcommand(name="list", description="List all projects")
    async def list_projects(self, interaction):
        projects = await self.project_service.get_all_projects()
        # Format and display projects
```

## Key Design Patterns

### Factory Pattern
**Purpose**: Standardizes object creation and ensures proper initialization

**Implementation**:
- `BotComponentFactory`: Main factory managing component creation
- `ServiceFactory`: Creates bot services
- `TaskFactory`: Creates background tasks
- `DashboardFactory`: Creates dashboard UI components

**Example Usage**:
```python
# Creating a service through factory
monitoring_service = bot.factory.create_service(
    "System Monitoring",
    setup_system_monitoring
)

# Creating a task through factory
task = bot.task_factory.create_task(
    "Status Update",
    status_update_task_func
)
```

### Workflow Pattern
**Purpose**: Manages initialization and cleanup sequences

**Implementation**:
- `BaseWorkflow`: Abstract base defining workflow interface
- Concrete workflows: `ServiceWorkflow`, `ChannelWorkflow`, etc.

**Example**:
```python
class ServiceWorkflow(BaseWorkflow):
    async def initialize(self):
        try:
            # Initialize critical services first
            for service_config in self.bot.critical_services:
                service = self.bot.factory.create_service(
                    service_config['name'],
                    service_config['setup']
                )
                await self.bot.lifecycle._initialize_service(service)
            
            # Then initialize module services
            for service_config in self.bot.module_services:
                service = self.bot.factory.create_service(
                    service_config['name'],
                    service_config['setup']
                )
                await self.bot.lifecycle._initialize_service(service)
            
            return True
        except Exception as e:
            logger.error(f"Service workflow initialization failed: {e}")
            raise
```

### Repository Pattern
**Purpose**: Abstracts data access from business logic

**Implementation**:
- Database-specific repositories for each domain entity
- Consistent interface for CRUD operations

**Example**:
```python
# Using repository in service
async def get_project_details(project_id):
    project = await project_repository.get_by_id(project_id)
    tasks = await task_repository.get_by_project_id(project_id)
    return {
        "project": project,
        "tasks": tasks
    }
```

### Dependency Injection
**Purpose**: Reduces coupling between components

**Example**:
```python
# Inject service into UI component
dashboard_ui = MonitoringDashboardController(bot)
dashboard_ui.set_service(monitoring_service)
```

## Implementation Requirements

### Service Implementation
- ✅ Must have a `setup` function that initializes the service
- ✅ Must work with the `ServiceFactory`
- ✅ Should implement initialization and cleanup methods
- ✅ Must handle exceptions with proper error logging

### Workflow Implementation
- ✅ Must extend `BaseWorkflow`
- ✅ Must implement `initialize()` and `cleanup()` methods
- ✅ Should handle dependencies in correct order
- ✅ Must include proper error handling

### Task Implementation
- ✅ Must be async and accept bot as first parameter
- ✅ Must handle proper cancellation
- ✅ Must be created through the TaskFactory
- ✅ Should not leak resources

## Best Practices

### Service Creation
- Always use factories instead of direct instantiation
- Register services in the appropriate configuration files
- Follow consistent error handling patterns

### Component Dependencies
- Use dependency injection to avoid tight coupling
- Initialize critical services before dependent services
- Avoid circular dependencies

### Error Handling
- Log errors with appropriate context
- Implement fallbacks for critical functionality
- Use specific exception types

### Resource Management
- Always implement cleanup methods
- Release resources in reverse order of acquisition
- Use context managers when appropriate

## Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                        Interface Layer                          │
│  ┌─────────────┐   ┌───────────────┐   ┌───────────────────┐    │
│  │  Commands   │   │  Dashboards   │   │ Views and Embeds  │    │
└──┴─────────────┴───┴───────────────┴───┴───────────────────┴────┘
               ▲                ▲                  ▲
               │                │                  │
┌──────────────┴────────────────┴──────────────────┴───────────────┐
│                       Application Layer                          │
│  ┌───────────────────────┐   ┌───────────────────────────────┐   │
│  │  Application Services │   │      Command Handlers         │   │
└──┴───────────────────────┴───┴───────────────────────────────┴───┘
               ▲                           ▲
               │                           │
┌──────────────┴───────────────────────────┴───────────────────────┐
│                         Domain Layer                             │
│  ┌─────────┐   ┌────────────────┐   ┌────────────────────────┐   │
│  │ Models  │   │ Domain Services│   │    Domain Policies     │   │
└──┴─────────┴───┴────────────────┴───┴────────────────────────┴───┘
               ▲                ▲                 ▲
               │                │                 │
┌──────────────┴────────────────┴─────────────────┴──────────────────┐
│                       Infrastructure Layer                         │
│  ┌────────────┐   ┌───────────┐   ┌───────────┐   ┌─────────────┐  │
│  │Repositories│   │ Factories │   │  Discord  │   │   Database  │  │
└──┴────────────┴───┴───────────┴───┴───────────┴───┴─────────────┴──┘
```

## How To Use This Guide

When implementing new features:
1. Identify which layer your code belongs in
2. Use the appropriate design patterns
3. Follow the implementation requirements
4. Adhere to the best practices

When modifying existing features:
1. Understand which patterns are being used
2. Maintain the existing architecture
3. Refactor according to best practices if needed

This guide provides:
1. A clear introduction explaining the purpose of the document
2. A structured overview of the Domain-Driven Design architecture
3. Detailed explanations of each key design pattern with code examples
4. Concrete implementation requirements for each component type
5. Best practices for maintaining the architecture
6. A visual architecture diagram showing relationships between layers
7. Guidance on how to use the document when developing

The document explains the "why" behind the patterns and shows how they work together to create a cohesive architecture.

## Implementation Recommendations

## Related Documentation
- [Layer Definitions](../architecture/LAYERS.md) - Layer organization details
- [Data Flow Patterns](../architecture/DATA_FLOW.md) - Component interaction patterns
- [Dashboard Pattern](./DASHBOARD_PATTERN.md) - Dashboard implementation details
- [Slash Command Pattern](./SLASHCOMMAND_PATTERN.md) - Command implementation details