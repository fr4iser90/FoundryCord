# app/bot/application/services/dashboard/dynamic_minecraft_dashboard_service.py
from typing import Dict, Any, List, Optional
import nextcord
import asyncio
from datetime import datetime, timedelta

from app.bot.infrastructure.logging import logger
from app.bot.infrastructure.factories.discord_ui.dashboard_factory import DashboardFactory
from app.bot.infrastructure.config.channel_config import ChannelConfig

from app.bot.infrastructure.monitoring.collectors.service.config.game_services import get_pufferpanel_services, get_standalone_services
from app.bot.infrastructure.monitoring.collectors.service.config.web_services import get_public_services, get_private_services
from app.bot.infrastructure.monitoring.checkers.game_service_checker import check_pufferpanel_games, check_standalone_games
from app.bot.infrastructure.monitoring.checkers.web_service_checker import check_web_services
from app.bot.infrastructure.monitoring.collectors.game_servers.minecraft_server_collector_impl import MinecraftServerFetcher

from app.bot.interfaces.dashboards.components.channels.gamehub.views import GameHubView
from app.bot.interfaces.dashboards.controller.base_dashboard import BaseDashboardController
from app.bot.interfaces.dashboards.controller.minecraft_server_dashboard import MinecraftServerDashboardController

from app.bot.infrastructure.database.repositories.category_repository_impl import CategoryRepository
from app.bot.infrastructure.database.models import CategoryMapping

class DynamicMinecraftDashboardService:
    """Service for creating individual Minecraft server dashboards"""
    
    def __init__(self, bot, dashboard_factory: DashboardFactory):
        self.bot = bot
        self.dashboard_factory = dashboard_factory
        self.initialized = False
        self.minecraft_servers = {}  # port -> server data
        self.update_task = None
        
    async def initialize(self) -> None:
        """Initialize the service"""
        try:
            # Get the gameservers category ID from the database
            category_repo = CategoryRepository()
            category = await category_repo.get_by_type("gameservers")
            if not category:
                logger.warning("Gameservers category not found in database")
                self.category_id = None
            else:
                self.category_id = int(category.category_id)
            
            # Discover existing Minecraft servers
            await self.discover_minecraft_servers()
            
            # Start background update task
            self.update_task = asyncio.create_task(self.update_loop())
            
            self.initialized = True
            logger.info("Dynamic Minecraft Dashboard Service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Dynamic Minecraft Dashboard Service: {e}")
            raise
            
    async def _update_loop(self) -> None:
        """Background task to periodically update all dashboards"""
        try:
            while True:
                if not self.minecraft_servers:
                    await asyncio.sleep(self.update_interval)
                    continue
                    
                await self.update_all_dashboards()
                await asyncio.sleep(self.update_interval)
        except asyncio.CancelledError:
            logger.info("Minecraft dashboard update loop cancelled")
        except Exception as e:
            logger.error(f"Error in Minecraft dashboard update loop: {e}")
            
    async def update_all_dashboards(self) -> None:
        """Update all Minecraft server dashboards"""
        try:
            # Get system information first to populate the public IP
            system_info = {}
            if hasattr(self.bot, 'system_monitoring_service'):
                system_data = await self.bot.system_monitoring_service.get_full_system_status()
                system_info = {
                    'public_ip': system_data.get('public_ip'),
                    'domain': system_data.get('domain')
                }
                
            # Prepare server list for API fetching
            server_list = []
            public_ip = system_info.get('public_ip', 'localhost')
            
            for port, server_data in self.minecraft_servers.items():
                server_data['address'] = public_ip
                server_list.append((public_ip, port))
            
            # Fetch Minecraft server data
            minecraft_data = await MinecraftServerFetcher.fetch_multiple_servers(server_list)
            
            # Update each dashboard
            for port, server_data in self.minecraft_servers.items():
                server_key = f"{public_ip}:{port}"
                if server_key in minecraft_data:
                    await server_data['ui'].update_dashboard(minecraft_data[server_key])
                    logger.debug(f"Updated dashboard for {server_data['name']} with fresh data")
                else:
                    # Create offline status if no data available
                    offline_data = {
                        'online': False,
                        'address': public_ip,
                        'port': port,
                        'players': [],
                        'player_count': 0,
                        'max_players': 0,
                        'version': 'Unknown',
                    }
                    await server_data['ui'].update_dashboard(offline_data)
                    logger.debug(f"Updated dashboard for {server_data['name']} with offline status")
                    
        except Exception as e:
            logger.error(f"Error updating Minecraft dashboards: {e}")
    
    async def add_minecraft_server(self, server_name: str, server_port: int) -> bool:
        """Manually add a new Minecraft server dashboard"""
        try:
            if server_port in self.minecraft_servers:
                logger.warning(f"Minecraft server on port {server_port} already exists")
                return False
                
            dashboard_ui = MinecraftServerDashboardController(self.bot, server_name, server_port)
            await dashboard_ui.initialize()
            
            self.minecraft_servers[server_port] = {
                'name': server_name,
                'ui': dashboard_ui,
                'port': server_port,
                'address': 'localhost'
            }
            
            # Update the dashboard immediately
            await self.update_all_dashboards()
            
            logger.info(f"Added new Minecraft server dashboard for {server_name} on port {server_port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add Minecraft server dashboard for {server_name}: {e}")
            return False
    
    async def remove_minecraft_server(self, server_port: int) -> bool:
        """Remove a Minecraft server dashboard"""
        try:
            if server_port not in self.minecraft_servers:
                logger.warning(f"Minecraft server on port {server_port} not found")
                return False
                
            server_data = self.minecraft_servers.pop(server_port)
            
            # Delete the channel
            if server_data['ui'].channel:
                try:
                    await server_data['ui'].channel.delete()
                    logger.info(f"Deleted channel for Minecraft server {server_data['name']}")
                except Exception as e:
                    logger.error(f"Failed to delete channel for {server_data['name']}: {e}")
            
            logger.info(f"Removed Minecraft server dashboard for {server_data['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove Minecraft server dashboard: {e}")
            return False


async def setup(bot):
    """Setup function for the Dynamic Minecraft Dashboard Service"""
    dashboard_factory = bot.get_service(DashboardFactory)
    service = DynamicMinecraftDashboardService(bot, dashboard_factory)
    await service.initialize()
    bot.dynamic_minecraft_dashboard_service = service
    return service