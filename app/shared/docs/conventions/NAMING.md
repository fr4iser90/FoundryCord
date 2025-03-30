# HomeLab Discord Bot - Naming Conventions

## General Principles
- Use clear, descriptive names
- Follow Python PEP 8 naming conventions
- Be consistent across the codebase

## Domain Layer

### Domain Models
- Use business terminology
- No technical suffixes
- Examples:
  - `User`
  - `Project`
  - `AuditRecord`

### Domain Interfaces
- Prefix with 'I' for clarity
- Examples:
  - `IUserRepository`
  - `IAuditService`

### Domain Services
- Suffix with 'Service'
- Examples:
  - `AuthenticationService`
  - `ProjectManagementService`

## Infrastructure Layer

### Database Entities
- Suffix with 'Entity'
- Match domain model names
- Examples:
  - `UserEntity`
  - `ProjectEntity`
  - `AuditLogEntity`

### Repository Implementations
- Suffix with 'RepositoryImpl'
- Examples:
  - `UserRepositoryImpl`
  - `AuditLogRepositoryImpl`

### Mappers
- Suffix with 'Mapper'
- Examples:
  - `UserMapper`
  - `ProjectMapper`

## Application Layer

### Use Cases/Commands
- Suffix with 'UseCase' or 'Command'
- Examples:
  - `CreateUserUseCase`
  - `UpdateProjectCommand`

### DTOs
- Suffix with 'DTO'
- Examples:
  - `UserDTO`
  - `ProjectDTO`

## Interface Layer

### Controllers
- Suffix with 'Controller'
- Examples:
  - `UserController`
  - `ProjectController`

### View Models
- Suffix with 'ViewModel'
- Examples:
  - `UserViewModel`
  - `ProjectViewModel` 