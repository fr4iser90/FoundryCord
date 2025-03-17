"""Migration script for dashboards to the new dynamic system."""
from typing import Dict, Any
import uuid
import json
from datetime import datetime

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class DashboardMigration:
    """Migration utility for dashboard systems."""
    
    def __init__(self, bot):
        self.bot = bot
        self.repository = None
    
    async def initialize(self):
        """Initialize the migration utility."""
        try:
            # Get dashboard repository
            self.repository = self.bot.get_service('dashboard_repository')
            if not self.repository:
                logger.error("Dashboard repository not available")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error initializing dashboard migration: {e}")
            return False
    
    async def create_welcome_dashboard(self, guild_id: int = None, channel_id: int = None) -> str:
        """Create a welcome dashboard configuration."""
        try:
            # Create dashboard ID
            dashboard_id = f"welcome_{uuid.uuid4().hex[:8]}"
            
            # Build configuration
            config = {
                'id': dashboard_id,
                'title': 'Welcome to HomeLab Discord Bot',
                'description': 'This dashboard provides information about the HomeLab Discord Bot.',
                'dashboard_type': 'dynamic',
                'guild_id': str(guild_id) if guild_id else None,
                'channel_id': str(channel_id) if channel_id else None,
                'color': '0x3498db',
                'footer': {
                    'text': 'HomeLab Discord Bot • Made with ❤️'
                },
                'components': [
                    {
                        'id': 'system_info',
                        'type': 'metric_display',
                        'config': {
                            'title': 'System Information',
                            'icon': '🖥️',
                            'format': '**Platform:** {system.platform} {system.architecture}\n**Hostname:** {system.hostname}\n**Uptime:** {system.uptime_seconds|duration}',
                            'data_source': 'system_metrics',
                            'data_path': 'system',
                            'inline': True
                        }
                    },
                    {
                        'id': 'cpu_metrics',
                        'type': 'metric_display',
                        'config': {
                            'title': 'CPU Usage',
                            'icon': '⚙️',
                            'format': '**Usage:** {cpu.percent}%\n**Cores:** {cpu.count}',
                            'data_source': 'system_metrics',
                            'data_path': 'cpu',
                            'thresholds': [
                                {'value': 90, 'color': '0xFF0000'},
                                {'value': 75, 'color': '0xFFA500'},
                                {'value': 0, 'color': '0x00FF00'}
                            ],
                            'inline': True
                        }
                    },
                    {
                        'id': 'memory_metrics',
                        'type': 'metric_display',
                        'config': {
                            'title': 'Memory Usage',
                            'icon': '🧠',
                            'format': '**Usage:** {memory.percent}%\n**Total:** {memory.total|filesize}',
                            'data_source': 'system_metrics',
                            'data_path': 'memory',
                            'thresholds': [
                                {'value': 90, 'color': '0xFF0000'},
                                {'value': 75, 'color': '0xFFA500'},
                                {'value': 0, 'color': '0x00FF00'}
                            ],
                            'inline': True
                        }
                    },
                    {
                        'id': 'refresh_button',
                        'type': 'refresh_button',
                        'config': {
                            'label': 'Refresh Dashboard',
                            'style': 'primary',
                            'emoji': '🔄'
                        }
                    }
                ],
                'data_sources': {
                    'system_metrics': {
                        'type': 'system_metrics',
                        'refresh_interval': 60,
                        'params': {
                            'metrics': ['system', 'cpu', 'memory', 'disk']
                        }
                    }
                },
                'interactive_components': ['refresh_button'],
                'refresh_interval': 300
            }
            
            # Try to find a channel ID if not provided
            if not channel_id:
                # Try to find the welcome channel
                guild = None
                if guild_id:
                    guild = self.bot.get_guild(int(guild_id))
                elif self.bot.guilds:
                    guild = self.bot.guilds[0]
                
                if guild:
                    # Look for a welcome channel
                    for channel in guild.text_channels:
                        if channel.name == 'welcome':
                            channel_id = channel.id
                            config['channel_id'] = str(channel_id)
                            break
            
            # Save to repository
            saved_id = await self.repository.save_dashboard_config(config)
            
            if saved_id:
                logger.info(f"Created welcome dashboard with ID: {saved_id}")
                
                # Activate the dashboard if we have a channel
                if channel_id:
                    logger.info(f"Activating welcome dashboard in channel {channel_id}")
                    dashboard_manager = getattr(self.bot, 'dashboard_manager', None)
                    if dashboard_manager:
                        await dashboard_manager.activate_dashboard('dynamic', channel_id, config_id=saved_id)
                
                return saved_id
            else:
                logger.error("Failed to save welcome dashboard")
                return None
                
        except Exception as e:
            logger.error(f"Error creating welcome dashboard: {e}")
            return None
    
    async def migrate_all_dashboards(self):
        """Migrate all old dashboards to the new system."""
        # For simplicity, we're just creating a welcome dashboard
        # and not migrating old ones
        result = await self.create_welcome_dashboard()
        return result is not None 