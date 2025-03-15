# app/bot/application/services/dashboard/gamehub_dashboard_service.py
from typing import Dict, Any, List
from nextcord.ext import commands
import asyncio
from app.shared.logging import logger
from app.bot.interfaces.dashboards.components.factories.dashboard_factory import DashboardFactory
from app.bot.domain.monitoring.factories.collector_factory import CollectorFactory
from app.bot.interfaces.dashboards.controller.gamehub_dashboard import GameHubDashboardController
from app.bot.infrastructure.monitoring.collectors.game_servers.minecraft_server_collector_impl import MinecraftServerFetcher

class GameHubDashboardService:
    """Service for the Game Hub Dashboard"""
    
    def __init__(self, bot, dashboard_factory: DashboardFactory):
        self.bot = bot
        self.dashboard_factory = dashboard_factory
        self.collector_factory = CollectorFactory()
        self.initialized = False
        self.dashboard_ui = None
        self.service_config = []  # Initialize service_config as empty list
        
    async def initialize(self) -> None:
        """Initialize the service"""
        try:
            # Get service collector through factory
            self.service_collector = self.collector_factory.create('service')
            
            # Initialize service configuration
            self.service_config = self._load_service_config()
            
            # Initialize UI component
            self.dashboard_ui = GameHubDashboardController(self.bot).set_service(self)
            await self.dashboard_ui.initialize()
            
            self.initialized = True
            logger.info("Game Hub Dashboard Service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Game Hub Dashboard Service: {e}")
            raise
    
    def _load_service_config(self) -> list:
        """Load service configuration for game servers"""
        # This is a placeholder - ideally you would load this from a config file or database
        return [
            {"name": "🎮 Minecraft", "ip": "localhost", "port": 25570},
            {"name": "🎮 Factorio", "ip": "localhost", "port": 34197},
            {"name": "🎮 CS2", "ip": "localhost", "port": 27015},
            {"name": "🎮 Valheim", "ip": "localhost", "port": 2456},
            {"name": "🎮 Palworld", "ip": "localhost", "port": 8211},
            {"name": "🎮 Satisfactory", "ip": "localhost", "port": 7777}
        ]
    
    async def get_game_servers_status_dict(self) -> Dict[str, Any]:
        """_DICT: Get the game servers status"""
        if not self.initialized:
            await self.initialize()
            
        try:
            logger.debug("Collecting game server data for game server dashboard")
            
            # Get service data through collector
            service_data = await self.service_collector.collect_game_services()
            
            # Get system information
            system_info = {}
            try:
                # If SystemMonitoringService is available, get public IP and domain info
                if hasattr(self.bot, 'system_monitoring_service'):
                    system_data = await self.bot.system_monitoring_service.get_full_system_status()
                    system_info = {
                        'public_ip': system_data.get('public_ip'),
                        'domain': system_data.get('domain'),
                        'domain_ip': system_data.get('domain_ip')
                    }
            except Exception as e:
                logger.warning(f"Could not fetch system information: {e}")
            
            # Prioritize API data for Minecraft servers
            minecraft_servers = []
            for service_name, status in service_data.items():
                if "minecraft" in service_name.lower() and "online" in status.lower():
                    # Extract server info from your config
                    if not isinstance(service_name, str):
                        logger.warning(f"service_name is not a string: {type(service_name)}")
                        continue
                    server_info = next((s for s in self.service_config if s["name"] == service_name), None)
                    if server_info:
                        minecraft_servers.append((server_info["ip"], server_info["port"]))
            
            # Fetch and update with API data
            if minecraft_servers:
                try:
                    mc_api_data = await MinecraftServerFetcher.fetch_multiple_servers(minecraft_servers)
                    # Update service_data with the API information
                    for service_name, status in service_data.items():
                        if "minecraft" in service_name.lower():
                            if not isinstance(service_name, str):
                                logger.warning(f"service_name is not a string: {type(service_name)}")
                                continue
                            server_info = next((s for s in self.service_config if s["name"] == service_name), None)
                            if server_info:
                                service_key = f"{server_info['ip']}:{server_info['port']}"
                                if service_key in mc_api_data and mc_api_data[service_key].get("online", False):
                                    api_result = mc_api_data[service_key]
                                    player_count = api_result.get("players", {}).get("online", 0)
                                    max_players = api_result.get("players", {}).get("max", 0)
                                    player_list = api_result.get("players", {}).get("list", [])
                                    
                                    if player_count > 0 and player_list:
                                        player_names = ", ".join([p.get("name_clean", "Unknown") for p in player_list])
                                        service_data[service_name] = f"✅ Online ({player_count}/{max_players}) Players: {player_names}"
                                    else:
                                        service_data[service_name] = f"✅ Online ({player_count}/{max_players})"
                except Exception as e:
                    logger.error(f"Error fetching Minecraft API data: {e}")
            
            # Return combined data
            return {
                'servers': service_data,
                'config': self.service_config,
                'system': system_info
            }
        except Exception as e:
            logger.error(f"Error collecting game server status: {e}")
            return {}
    
    async def get_server_details(self, server_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific server"""
        try:
            # This would get more detailed information about a specific server
            # For now, we'll return placeholder data
            return {
                'name': server_name,
                'ip': '127.0.0.1',
                'ports': [25565],
                'version': '1.19.2',
                'uptime': '2d 5h 30m',
                'players': [],
                'max_players': 20,
                'cpu_usage': '5%',
                'memory_usage': '2.5GB',
                'world_size': '1.2GB',
                'mods': []
            }
        except Exception as e:
            logger.error(f"Error getting server details for {server_name}: {e}")
            return {'error': str(e)}
    
    async def get_server_logs(self, server_name: str, lines: int = 10) -> List[str]:
        """Get recent logs from the server"""
        try:
            # This would fetch real logs
            # For now, return placeholder data
            return [
                f"[INFO] Server started - {server_name}",
                "[INFO] World loading complete",
                "[INFO] Listening on port 25565"
            ]
        except Exception as e:
            logger.error(f"Error getting logs for {server_name}: {e}")
            return [f"Error retrieving logs: {str(e)}"]
    
    async def display_dashboard(self) -> None:
        """Display the dashboard using the UI component"""
        if not self.dashboard_ui:
            logger.error("Dashboard UI not initialized")
            return
            
        await self.dashboard_ui.display_dashboard()

async def setup(bot):
    """Setup function for the Game Hub Dashboard service"""
    try:
        dashboard_factory = bot.dashboard_factory
        service = GameHubDashboardService(bot, dashboard_factory)
        await service.initialize()
        
        # Display the dashboard after initialization
        await service.display_dashboard()
        
        logger.info("Game Hub Dashboard service initialized successfully")
        return service
    except Exception as e:
        logger.error(f"Failed to initialize Game Hub Dashboard service: {e}")
        raise