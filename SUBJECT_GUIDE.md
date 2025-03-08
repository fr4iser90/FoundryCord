# HomeLab Discord Bot Subject Guide

## System Overview
The HomeLab Discord Bot is a management and monitoring system for a home lab environment, providing dashboards, project management, and system monitoring capabilities through Discord.

## Key Components

### Dashboards
- **GeneralDashboardUI**: Displays system status in the general channel
- **ProjectDashboardUI**: Manages projects in a dedicated projects channel
- **WelcomeDashboard**: Creates welcome messages with interactive components

### System Monitoring
- **System Status Collectors**: Various modules that collect system data:
  - Hardware information
  - CPU/Memory/Disk usage
  - Network statistics
  - Docker container status
  - Security information (SSH attempts)
  - Service status

### UI Components
- **DashboardFactory**: Creates different types of dashboards
- **Views and Embeds**: Discord UI components for interactive interfaces

## Technical Architecture
- Uses nextcord for Discord integration
- Follows a service-oriented architecture with dependency injection
- Employs async/await for non-blocking operations
- Uses factories to create UI components

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
