# Dashboard Controller Structure

## Overview

This document outlines the standardized structure for dashboard controllers in the HomeLab Discord Bot. By following these patterns, we ensure consistency across all dashboard implementations and facilitate maintenance and new feature development.

## Related Documentation
- [Dashboard Pattern](./DASHBOARD_PATTERN.md) - Overall dashboard implementation workflow
- [UI Designer Role](../../ai/roles/ui/BOT_UI_DESIGNER.md) - Role responsible for dashboard design
- [Data Flow Patterns](../architecture/DATA_FLOW.md) - Understanding data flow in dashboards

## Controller Hierarchy

```
BaseDashboardController
├── WelcomeDashboardController
├── MonitoringDashboardController
├── ProjectDashboardController
├── GameHubDashboardController
├── MinecraftServerDashboardController
└── [Other Specialized Controllers]
```

## System Architecture

```
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│  DashboardManager │────│ DynamicDashboard  │────│  ComponentRegistry│
│   (Coordinator)   │    │   Controller      │    │  (Factory)        │
└───────────────────┘    └───────────────────┘    └───────────────────┘
         │                        │                        │
         │                        │                        │
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│    Dashboard      │    │    Dashboard      │    │    Component      │
│    Repository     │────│     Builder       │────│    Instances      │
│  (Data Storage)   │    │ (Assembler)       │    │  (UI Elements)    │
└───────────────────┘    └───────────────────┘    └───────────────────┘
         │                        │                        │
         │                        │                        │
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│   Data Source     │    │    View Model     │    │    Interaction    │
│    Registry       │────│     Builder       │────│     Handlers      │
│ (Data Providers)  │    │ (Data Formatter)  │    │   (Callbacks)     │
└───────────────────┘    └───────────────────┘    └───────────────────┘
```

## Directory Structure

```
app/bot/
├── domain/
│   └── dashboards/
│       ├── models/
│       │   ├── dashboard_model.py           # Core dashboard domain models
│       │   ├── component_model.py           # Component domain models
│       │   └── data_source_model.py         # Data source domain models
│       ├── repositories/                    # Repository interfaces
│       │   └── dashboard_repository.py      # Dashboard repository interface
│       └── services/                        # Domain services
│           ├── data_processor_service.py    # Processing data for display
│           └── component_service.py         # Component business logic
│
├── application/
│   └── services/
│       └── dashboard/
│           ├── dashboard_service.py         # Dashboard orchestration
│           ├── dashboard_builder.py         # Dashboard assembly 
│           ├── data_source_service.py       # Data retrieval coordination
│           └── component_service.py         # Component service (uses domain)
│
├── infrastructure/
│   ├── repositories/
│   │   └── dashboard_repository_impl.py     # Repository implementation
│   ├── discord/
│   │   ├── message_tracker.py              # Discord message tracking
│   │   └── dashboard_channel.py            # Dashboard channel management
│   ├── factories/
│   │   ├── component_registry.py           # Component registration
│   │   └── data_source_registry.py         # Data source registration
│   ├── data_sources/                       # Data source implementations
│   │   ├── system_data_source.py           # System metrics source
│   │   └── minecraft_data_source.py        # Game server metrics source
│   └── persistence/                        # Database entities/schemas
│       └── dashboard_entity.py             # DB entity for dashboard
│
└── interfaces/
    └── dashboards/
        ├── controller/
        │   ├── base_dashboard.py           # Base controller
        │   ├── dynamic_dashboard.py        # Dynamic controller
        │   └── system_dashboard.py         # Specialized controller
        └── components/
            ├── common/
            │   ├── buttons/
            │   │   ├── refresh_button.py   # Shared refresh button
            │   │   └── navigation_button.py # Navigation buttons
            │   ├── embeds/
            │   │   ├── dashboard_embed.py  # Dashboard embed template
            │   │   └── error_embed.py      # Error embed template
            │   └── views/
            │       └── base_view.py        # Base Discord view
            └── specific/
                ├── status_indicator.py     # Status indicator component
                ├── metric_display.py       # Metric display component
                └── chart_component.py      # Chart component
```

## Standard Controller Components

### 1. Base Structure

Every dashboard controller should extend `BaseDashboardController` and include these standard elements:

```python
class SpecificDashboardController(BaseDashboardController):
    """Documentation for this dashboard controller"""
    # Dashboard type identifier used for tracking and persistence
    DASHBOARD_TYPE = "specific_type"
    # Title text displayed in embed headers
    TITLE_IDENTIFIER = "Specific Dashboard"
    
    def __init__(self, bot):
        super().__init__(bot)
        # Initialize controller-specific properties
        self.service = None
        self.last_metrics = None
        self.initialized = False
    
    # Required methods
    async def initialize(self):
        """Initialize dashboard services and configuration"""
        pass
        
    async def create_embed(self) -> nextcord.Embed:
        """Create the dashboard embed with current data"""
        pass
        
    def create_view(self) -> nextcord.ui.View:
        """Create the interactive view components"""
        pass
        
    async def display_dashboard(self) -> nextcord.Message:
        """Create or update the dashboard message"""
        pass
        
    async def refresh_data(self):
        """Fetch fresh data from app.bot.services"""
        pass
```

### 2. Error Handling

All dashboard controllers should use the standardized error handling provided by `BaseDashboardController`:

```python
# In BaseDashboardController
def create_error_embed(self, error_message: str, title: str = None, error_code: str = None) -> nextcord.Embed:
    """Creates a standardized error embed for dashboards"""
    title = title or "❌ Dashboard Error"
    
    embed = nextcord.Embed(
        title=title,
        description=error_message,
        color=0xe74c3c  # Red color for errors
    )
    
    if error_code:
        embed.add_field(name="Error Code", value=error_code)
    
    # Add timestamp
    embed.timestamp = datetime.now()
    
    # Add standard footer
    DashboardEmbed.add_standard_footer(embed)
    return embed
```

Usage in specific controllers:

```python
# In a specific dashboard controller
async def on_refresh(self, interaction: nextcord.Interaction):
    """Handler for refresh button"""
    await interaction.response.defer(ephemeral=True)
    
    try:
        await self.refresh_data()
        await self.display_dashboard()
        await interaction.followup.send("Dashboard updated successfully!", ephemeral=True)
    except Exception as e:
        logger.error(f"Error refreshing {self.DASHBOARD_TYPE} dashboard: {e}")
        error_embed = self.create_error_embed(
            error_message=str(e),
            title="❌ Refresh Error",
            error_code=f"{self.DASHBOARD_TYPE.upper()}-REFRESH-ERR"
        )
        await interaction.followup.send(embed=error_embed, ephemeral=True)
```

### 3. Standard Embeds and Footers

All dashboard embeds should include standardized footers using `DashboardEmbed.add_standard_footer()`:

```python
async def create_embed(self) -> nextcord.Embed:
    """Create the specific dashboard embed"""
    embed = nextcord.Embed(
        title=f"{self.TITLE_IDENTIFIER}",
        description="Current system status and metrics",
        color=0x3498db
    )
    
    # Add specific fields based on available data
    embed.add_field(name="CPU", value=f"{self.metrics.cpu_percent}%", inline=True)
    embed.add_field(name="Memory", value=f"{self.metrics.memory_percent}%", inline=True)
    
    # Always add standard footer at the end
    DashboardEmbed.add_standard_footer(embed)
    return embed
```

## Dashboard Controller Lifecycle

### 1. Creation and Registration

Dashboard controllers are created and registered during bot initialization:

```python
# In bot startup sequence
async def setup_dashboards(bot):
    # Create dashboard controllers
    monitoring_dashboard = MonitoringDashboardController(bot)
    welcome_dashboard = WelcomeDashboardController(bot)
    project_dashboard = ProjectDashboardController(bot)
    
    # Initialize controllers
    await monitoring_dashboard.initialize()
    await welcome_dashboard.initialize()
    await project_dashboard.initialize()
    
    # Register with dashboard manager
    await bot.dashboard_manager.register_dashboard(monitoring_dashboard)
    await bot.dashboard_manager.register_dashboard(welcome_dashboard)
    await bot.dashboard_manager.register_dashboard(project_dashboard)
```

### 2. Initialization and Channel Setup

```python
async def initialize(self):
    """Initialize the dashboard controller"""
    if self.initialized:
        return
    
    logger.info(f"Initializing {self.DASHBOARD_TYPE} dashboard...")
    
    # Get required services
    self.metrics_service = self.bot.service_factory.get_service("metrics_service")
    self.dashboard_repository = self.bot.service_factory.get_service("dashboard_repository")
    
    # Get configuration
    config = await self.dashboard_repository.get_dashboard_by_id(self.DASHBOARD_TYPE)
    self.config = config or {}
    
    # Get or create channel
    self.channel = await self._get_or_create_channel()
    
    # Initial data fetch
    await self.refresh_data()
    
    # Set initialized flag
    self.initialized = True
```

### 3. Display and Update

```python
async def display_dashboard(self) -> nextcord.Message:
    """Display or update the dashboard in the channel"""
    try:
        # Create embed and view
        embed = await self.create_embed()
        view = self.create_view()
        
        if not self.message or not self.message.id:
            # First time display - send new message
            self.message = await self.channel.send(embed=embed, view=view)
            logger.info(f"Created new {self.DASHBOARD_TYPE} dashboard message: {self.message.id}")
            
            # Track message ID for future updates
            await self.bot.dashboard_manager.track_message(
                dashboard_type=self.DASHBOARD_TYPE,
                message_id=self.message.id,
                channel_id=self.channel.id
            )
        else:
            # Update existing message
            try:
                # Get the message object
                try:
                    self.message = await self.channel.fetch_message(self.message.id)
                except (nextcord.NotFound, nextcord.HTTPException):
                    # Message not found, send new one
                    self.message = await self.channel.send(embed=embed, view=view)
                    await self.bot.dashboard_manager.track_message(
                        dashboard_type=self.DASHBOARD_TYPE,
                        message_id=self.message.id,
                        channel_id=self.channel.id
                    )
                    return self.message
                
                # Update message
                await self.message.edit(embed=embed, view=view)
                logger.debug(f"Updated {self.DASHBOARD_TYPE} dashboard message: {self.message.id}")
            except Exception as update_error:
                logger.error(f"Failed to update message for {self.DASHBOARD_TYPE}: {update_error}")
                # Create new message as fallback
                self.message = await self.channel.send(embed=embed, view=view)
        
        return self.message
    except Exception as e:
        logger.error(f"Error displaying {self.DASHBOARD_TYPE} dashboard: {e}")
        raise
```

## Common Callback Handlers

### 1. Refresh Button

```python
async def on_refresh(self, interaction: nextcord.Interaction):
    """Handle refresh button interaction"""
    await interaction.response.defer(ephemeral=True)
    
    try:
        await self.refresh_data()
        await self.display_dashboard()
        await interaction.followup.send(f"{self.TITLE_IDENTIFIER} dashboard updated!", ephemeral=True)
    except Exception as e:
        logger.error(f"Error refreshing {self.DASHBOARD_TYPE} dashboard: {e}")
        error_embed = self.create_error_embed(
            error_message=str(e),
            title="❌ Refresh Error",
            error_code=f"{self.DASHBOARD_TYPE.upper()}-REFRESH-ERR"
        )
        await interaction.followup.send(embed=error_embed, ephemeral=True)
```

### 2. Details Button
 
```python
async def on_details(self, interaction: nextcord.Interaction):
    """Handle details button interaction"""
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Create detailed embed with more information
        detailed_embed = await self.create_detailed_embed()
        await interaction.followup.send(embed=detailed_embed, ephemeral=True)
    except Exception as e:
        logger.error(f"Error showing details for {self.DASHBOARD_TYPE} dashboard: {e}")
        error_embed = self.create_error_embed(
            error_message=str(e),
            title="❌ Details Error",
            error_code=f"{self.DASHBOARD_TYPE.upper()}-DETAILS-ERR"
        )
        await interaction.followup.send(embed=error_embed, ephemeral=True) 
```

## Best Practices

### 1. Error Handling Practices

- Always use `create_error_embed()` for consistent error presentation
- Include specific error codes for easier troubleshooting
- Log errors with appropriate context before sending to user
- Handle edge cases gracefully, such as missing data or service unavailability

### 2. Design Consistency

- Use consistent color schemes across all dashboards (defined in constants)
- Apply the same button layout patterns across similar dashboards
- Maintain consistent spacing and formatting in embeds
- Use standard emoji sets for status indicators

### 3. Performance Considerations

- Cache dashboard data where appropriate
- Use deferred responses for operations that might take time
- Implement intelligent refresh strategies to minimize API calls
- Clean up resources when dashboards are no longer needed

### 4. Accessibility

- Use clear, descriptive button labels
- Ensure color choices maintain adequate contrast
- Provide text alternatives for any visual indicators
- Support keyboard navigation patterns

## Implementation Example

```python
from typing import Dict, Any, Optional
import nextcord
from datetime import datetime
import logging

from app.bot.interfaces.dashboards.controller.base_dashboard import BaseDashboardController
from app.bot.interfaces.dashboards.components.common.embeds.dashboard_embed import DashboardEmbed
from app.bot.interfaces.dashboards.components.common.buttons.refresh_button import RefreshButton

logger = logging.getLogger(__name__)

class ExampleDashboardController(BaseDashboardController):
    """Example dashboard controller implementation"""
    
    DASHBOARD_TYPE = "example_dashboard"
    TITLE_IDENTIFIER = "Example Dashboard"
    
    def __init__(self, bot):
        super().__init__(bot)
        self.metrics = None
        self.initialized = False
        self.message = None
        self.channel = None
    
    async def initialize(self):
        """Initialize the example dashboard"""
        if self.initialized:
            return
            
        logger.info(f"Initializing {self.DASHBOARD_TYPE} dashboard...")
        
        # Get services
        self.metrics_service = self.bot.service_factory.get_service("metrics_service")
        
        # Get or create channel
        self.channel = await self._get_or_create_channel()
        
        # Initial data fetch
        await self.refresh_data()
        
        self.initialized = True
        
    async def _get_or_create_channel(self):
        """Get or create the dashboard channel"""
        channel_name = "example-dashboard"
        
        for guild in self.bot.guilds:
            channel = nextcord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                return channel
                
            # Channel doesn't exist, create it
            category = nextcord.utils.get(guild.categories, name="Dashboards")
            if not category:
                # Create category if it doesn't exist
                category = await guild.create_category("Dashboards")
                
            # Create channel
            channel = await category.create_text_channel(channel_name)
            return channel
        
        return None
    
    async def refresh_data(self):
        """Refresh dashboard data"""
        self.metrics = await self.metrics_service.get_system_metrics()
    
    async def create_embed(self) -> nextcord.Embed:
        """Create the dashboard embed"""
        embed = nextcord.Embed(
            title=f"📊 {self.TITLE_IDENTIFIER}",
            description="An example dashboard with system metrics",
            color=0x3498db
        )
        
        # Add metrics fields
        if self.metrics:
            embed.add_field(name="CPU Usage", value=f"{self.metrics.cpu_percent}%", inline=True)
            embed.add_field(name="Memory Usage", value=f"{self.metrics.memory_percent}%", inline=True)
            embed.add_field(name="Disk Usage", value=f"{self.metrics.disk_percent}%", inline=True)
            embed.add_field(name="Boot Time", value=self.metrics.boot_time_formatted, inline=True)
            embed.add_field(name="Load Average", value=str(self.metrics.load_avg), inline=True)
        else:
            embed.add_field(name="Status", value="No data available", inline=False)
        
        # Add timestamp and footer
        embed.timestamp = datetime.now()
        DashboardEmbed.add_standard_footer(embed)
        
        return embed
        
    def create_view(self) -> nextcord.ui.View:
        """Create the dashboard view with buttons"""
        view = nextcord.ui.View(timeout=None)
        
        # Add refresh button
        refresh_button = RefreshButton(callback=self.on_refresh)
        view.add_item(refresh_button)
        
        return view
    
    async def on_refresh(self, interaction: nextcord.Interaction):
        """Handle refresh button interaction"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            await self.refresh_data()
            await self.display_dashboard()
            await interaction.followup.send("Example dashboard updated!", ephemeral=True)
        except Exception as e:
            logger.error(f"Error refreshing example dashboard: {e}")
            error_embed = self.create_error_embed(
                error_message=str(e),
                title="❌ Refresh Error",
                error_code="EXAMPLE-REFRESH-ERR"
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
```

## Component System

### Component Registry

```python
class ComponentRegistry:
    """Registry of available dashboard component types"""
    
    def __init__(self):
        self.components = {}
        
    def register_component(self, component_type: str, component_class):
        """Register a component type with its implementation class"""
        self.components[component_type] = component_class
        
    def get_component(self, component_type: str):
        """Get component implementation class for a type"""
        return self.components.get(component_type)
        
    def get_all_components(self):
        """Get all registered component types"""
        return self.components
```

### Dashboard Component Base Class

```python
class DashboardComponent:
    """Base class for dashboard components"""
    
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.id = config.get("id")
        
    async def render_to_embed(self, embed: nextcord.Embed, data):
        """Render component to an embed"""
        raise NotImplementedError("Component must implement render_to_embed")
        
    def create_ui_component(self, controller):
        """Create UI component for interactive view (if applicable)"""
        return None
        
    async def on_interaction(self, interaction: nextcord.Interaction, controller, action: str):
        """Handle interaction with this component"""
        pass
```

### Dashboard Repository

```python
class DashboardRepository:
    """Repository for dashboard configurations"""
    
    def __init__(self, db_service):
        self.db_service = db_service
        
    async def get_dashboard_by_id(self, dashboard_id: str):
        """Get dashboard configuration by ID"""
        # Implementation depends on database schema
        result = await self.db_service.fetch_one(
            "SELECT * FROM dashboards WHERE id = ?", 
            dashboard_id
        )
        
        if not result:
            return None
            
        # Parse JSON configuration
        config = json.loads(result["config"])
        return config
        
    async def save_dashboard(self, dashboard_id: str, config: dict):
        """Save dashboard configuration"""
        # Implementation depends on database schema
        await self.db_service.execute(
            "INSERT OR REPLACE INTO dashboards (id, config) VALUES (?, ?)",
            dashboard_id, json.dumps(config)
        )
```

## Bot Startup Sequence

```python
# In bot startup sequence
async def setup_dynamic_dashboards(bot):
    # Initialize services
    dashboard_repository = DashboardRepository(bot.db)
    component_registry = ComponentRegistry()
    data_source_registry = DataSourceRegistry()
    
    # Register with service factory
    bot.service_factory.register_service("dashboard_repository", dashboard_repository)
    bot.service_factory.register_service("component_registry", component_registry)
    bot.service_factory.register_service("data_source_registry", data_source_registry)
    
    # Register component types
    component_registry.register_component("status_indicator", StatusIndicatorComponent)
    component_registry.register_component("metric_display", MetricDisplayComponent)
    component_registry.register_component("chart", ChartComponent)
    component_registry.register_component("button_group", ButtonGroupComponent)
    
    # Register data sources
    data_source_registry.register_data_source("system_metrics", SystemMetricsDataSource)
    data_source_registry.register_data_source("minecraft_server", MinecraftServerDataSource)
    
    # Load available dashboards
    dashboard_ids = await dashboard_repository.get_all_dashboard_ids()
    
    # Create and initialize dashboard controllers
    for dashboard_id in dashboard_ids:
        dashboard_controller = DynamicDashboardController(bot, dashboard_id=dashboard_id)
        await dashboard_controller.initialize()
        await bot.dashboard_manager.register_dashboard(dashboard_controller)
```

## Example Dashboard Configuration

```json
{
  "id": "system_dashboard",
  "type": "system_monitoring",
  "title": "System Monitoring",
  "description": "Real-time system performance metrics",
  "channel_name": "system-dashboard",
  "category_name": "Dashboards",
  "embed": {
    "title": "📊 System Monitoring Dashboard",
    "description": "Current status of system resources",
    "color": "0x3498db"
  },
  "data_sources": {
    "system_metrics": {
      "type": "system_metrics",
      "refresh_interval": 60,
      "params": {}
    },
    "docker_metrics": {
      "type": "docker_metrics",
      "refresh_interval": 120,
      "params": {
        "containers": ["nextcord-bot", "postgres", "nginx"]
      }
    }
  },
  "components": [
    {
      "id": "cpu_status",
      "type": "metric_display",
      "title": "CPU Usage",
      "data_source_id": "system_metrics",
      "config": {
        "metric_path": "cpu.percent",
        "format": "{value}%",
        "thresholds": {
          "warning": 70,
          "critical": 90
        },
        "icon": "📊"
      }
    },
    {
      "id": "memory_usage",
      "type": "metric_display",
      "title": "Memory Usage",
      "data_source_id": "system_metrics",
      "config": {
        "metric_path": "memory.percent",
        "format": "{value}%",
        "thresholds": {
          "warning": 80,
          "critical": 95
        },
        "icon": "🧠"
      }
    },
    {
      "id": "disk_space",
      "type": "metric_display",
      "title": "Disk Space",
      "data_source_id": "system_metrics",
      "config": {
        "metric_path": "disk.percent",
        "format": "{value}%",
        "thresholds": {
          "warning": 85,
          "critical": 95
        },
        "icon": "💾"
      }
    },
    {
      "id": "docker_control",
      "type": "button_group",
      "title": "Docker Controls",
      "data_source_id": "docker_metrics",
      "config": {
        "buttons": [
          {
            "label": "View Containers",
            "style": "primary",
            "action": "show_containers"
          },
          {
            "label": "Restart Service",
            "style": "danger",
            "action": "restart_docker"
          }
        ]
      }
    }
  ],
  "layout": [
    { "type": "component", "component_id": "cpu_status", "row": 0, "col": 0 },
    { "type": "component", "component_id": "memory_usage", "row": 0, "col": 1 },
    { "type": "component", "component_id": "disk_space", "row": 1, "col": 0 }
  ],
  "interactive_components": [
    { "component_id": "docker_control" }
  ]
}