# Dashboard Controller Structure

## Overview

This document outlines the standardized structure for dashboard controllers in the HomeLab Discord Bot. By following these patterns, we ensure consistency across all dashboard implementations and facilitate maintenance and new feature development.

## Related Documentation
- [Dashboard Pattern](./DASHBOARD_PATTERN.md) - Overall dashboard implementation workflow
- [UI Designer Role](../../ai/roles/ui/BOT_UI_DESIGNER.md) - Role responsible for dashboard design
- [Data Flow Patterns](../architecture/DATA_FLOW.md) - Understanding data flow in dashboards

## Controller Hierarchy

BaseDashboardController
├── WelcomeDashboardController
├── MonitoringDashboardController
├── ProjectDashboardController
├── GameHubDashboardController
├── MinecraftServerDashboardController
└── [Other Specialized Controllers]


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
def init(self, bot):
super().init(bot)
# Initialize controller-specific properties
self.service = None
self.last_metrics = None
self.initialized = False
# Required methods
async def initialize(self):
"""Initialize dashboard services and configuration"""
async def create_embed(self) -> nextcord.Embed:
"""Create the dashboard embed with current data"""
def create_view(self) -> nextcord.ui.View:
"""Create the interactive view components"""
async def display_dashboard(self) -> nextcord.Message:
"""Create or update the dashboard message"""
async def refresh_data(self):
"""Fetch fresh data from app.bot.services"""
```

### 2. Error Handling

All dashboard controllers should use the standardized error handling provided by `BaseDashboardController`:

```python
In BaseDashboardController
def create_error_embed(self, error_message: str, title: str = None, error_code: str = None) -> nextcord.Embed:
"""Creates a standardized error embed for dashboards"""
dashboard_type = self.DASHBOARD_TYPE.replace('', ' ').title()
default_title = f"⚠️ {dashboard_type} Error"
embed = ErrorEmbed.create_error(
title=title or default_title,
description=f"An error occurred in the {dashboard_type} dashboard:",
error_details=error_message,
error_code=error_code or f"{self.DASHBOARD_TYPE.upper()}-ERR"
)
# Add standard footer
DashboardEmbed.add_standard_footer(embed)
return embed
```

Usage in specific controllers:

```python
In a specific dashboard controller
async def on_refresh(self, interaction: nextcord.Interaction):
"""Handler for refresh button"""
await interaction.response.defer(ephemeral=True)
try:
# Refresh logic
await self.refresh_data()
await self.display_dashboard()
await interaction.followup.send("Dashboard updated!", ephemeral=True)
except Exception as e:
logger.error(f"Error refreshing dashboard: {e}")
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
python
async def create_embed(self) -> nextcord.Embed:
"""Create the specific dashboard embed"""
embed = nextcord.Embed(
title=f"📊 {self.TITLE_IDENTIFIER}",
description="Dashboard description",
color=0x3498db
)
# Add fields with dashboard data
embed.add_field(name="Status", value="Online", inline=True)
# ... more fields
# Always add standard footer at the end
DashboardEmbed.add_standard_footer(embed)
return embed

```


## Dashboard Controller Lifecycle

### 1. Creation and Registration

Dashboard controllers are created and registered during bot initialization:

```python
In bot startup sequence
async def setup_dashboards(bot):
# Create dashboard controllers
monitoring_dashboard = MonitoringDashboardController(bot)
await monitoring_dashboard.initialize()
# Register with dashboard manager
await bot.dashboard_manager.register_dashboard(monitoring_dashboard)
```

### 2. Initialization and Channel Setup

```python
async def initialize(self):
"""Initialize the dashboard controller"""
if self.initialized:
return
# Get or create the dashboard channel
channel_config = ChannelConfig(self.bot)
channel_name = f"{self.DASHBOARD_TYPE.replace('', '-')}"
self.channel = await channel_config.get_or_create_channel(
channel_name,
f"{self.TITLE_IDENTIFIER} Dashboard",
category_name="Dashboards"
)
# Get required services
self.service = self.bot.service_factory.get_service("required_service")
# Load initial data
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
# If we already have a message, update it
if self.message:
try:
await self.message.edit(embed=embed, view=view)
return self.message
except Exception as e:
logger.warning(f"Couldn't update existing message: {e}, creating new")
# Otherwise send a new message
message = await self.channel.send(embed=embed, view=view)
self.message = message
# Track in dashboard manager
await self.bot.dashboard_manager.track_message(
dashboard_type=self.DASHBOARD_TYPE,
message_id=message.id,
channel_id=self.channel.id
)
logger.info(f"{self.TITLE_IDENTIFIER} dashboard displayed in channel {self.channel.name}")
return message
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
details_embed = await self.create_details_embed()
await interaction.followup.send(embed=details_embed, ephemeral=True)
except Exception as e:
logger.error(f"Error showing details: {e}")
error_embed = self.create_error_embed(
error_message=str(e),
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
from app.shared.logging import logger
from app.bot.infrastructure.config.channel_config import ChannelConfig
from .base_dashboard import BaseDashboardController
from app.bot.interfaces.dashboards.components.channels.example.views import ExampleView
from app.bot.domain.example.models.example_metrics import ExampleMetrics
from app.bot.interfaces.dashboards.components.common.embeds import ErrorEmbed, DashboardEmbed
class ExampleDashboardController(BaseDashboardController):
"""Controller for the Example dashboard"""
DASHBOARD_TYPE = "example"
TITLE_IDENTIFIER = "Example System"
def init(self, bot):
super().init(bot)
self.example_service = None
self.last_metrics = None
async def initialize(self):
"""Initialize the example dashboard"""
if self.initialized:
return
# Get channel
channel_config = ChannelConfig(self.bot)
self.channel = await channel_config.get_or_create_channel(
"example-dashboard",
"Example System Dashboard",
category_name="Dashboards"
)
# Get service
self.example_service = self.bot.service_factory.get_service("example")
# Load initial data
await self.refresh_data()
self.initialized = True
async def refresh_data(self):
"""Fetch fresh data from the example service"""
try:
self.last_metrics = await self.example_service.get_metrics()
except Exception as e:
logger.error(f"Error fetching example metrics: {e}")
raise
async def create_embed(self) -> nextcord.Embed:
"""Create the example dashboard embed"""
embed = nextcord.Embed(
title="📊 Example System Dashboard",
description="Current status of the example system",
color=0x3498db
)
# Add metrics data if available
if self.last_metrics:
embed.add_field(
name="Status",
value=f"{'✅ Online' if self.last_metrics.is_online else '❌ Offline'}",
inline=True
)
embed.add_field(
name="Uptime",
value=f"{self.last_metrics.uptime} hours",
inline=True
)
embed.add_field(
name="Load",
value=f"{self.last_metrics.load:.2f}%",
inline=True
)
else:
embed.add_field(
name="Status",
value="⚠️ No data available",
inline=False
)
# Always add standard footer
DashboardEmbed.add_standard_footer(embed)
return embed
def create_view(self) -> nextcord.ui.View:
"""Create the dashboard view with interactive elements"""
view = ExampleView()
# Add refresh button callback
view.refresh_button.callback = self.on_refresh
# Add details button callback if available
if hasattr(view, 'details_button'):
view.details_button.callback = self.on_details
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


By following these guidelines, all dashboard controllers will maintain a consistent structure, making the codebase more maintainable and easier to extend.

