# app/bot/application/services/dashboard/gamehub_dashboard_service.py
from typing import Dict, Any, List
from nextcord.ext import commands
import asyncio
from infrastructure.logging import logger
from infrastructure.factories.discord_ui.dashboard_factory import DashboardFactory
from domain.monitoring.collectors import service_collector
from domain.gameservers.models.gameserver_metrics import GameServersMetrics
from interfaces.dashboards.ui.gamehub_dashboard import GameHubDashboardUI
from infrastructure.collectors.game_servers.minecraft_server_collector_impl import MinecraftServerFetcher


class GameHubDashboardService:
    """Service for the Game Hub Dashboard"""
    
    def __init__(self, bot, dashboard_factory: DashboardFactory):
        self.bot = bot
        self.dashboard_factory = dashboard_factory
        self.initialized = False
        self.dashboard_ui = None
        
    async def initialize(self) -> None:
        """Initialize the service"""
        try:
            # Use the service collector from monitoring
            self.service_collector = service_collector
            
            # Initialize UI component
            self.dashboard_ui = GameHubDashboardUI(self.bot).set_service(self)
            await self.dashboard_ui.initialize()
            
            self.initialized = True
            logger.info("Game Hub Dashboard Service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Game Hub Dashboard Service: {e}")
            raise
    
    async def get_game_servers_status(self) -> Dict[str, Any]:
        """Get the game servers status"""
        if not self.initialized:
            await self.initialize()
            
        try:
            logger.debug("Collecting game server data for game server dashboard")
            
            # Get service data
            service_data = await service_collector.collect_service_data()
            
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
                    server_info = next((s for s in service_config if s["name"] == service_name), None)
                    if server_info:
                        minecraft_servers.append((server_info["ip"], server_info["port"]))
            
            # Fetch and update with API data
            if minecraft_servers:
                try:
                    mc_api_data = await MinecraftServerFetcher.fetch_multiple_servers(minecraft_servers)
                    # Update service_data with the API information
                    for service_name, status in service_data.items():
                        if "minecraft" in service_name.lower():
                            server_info = next((s for s in service_config if s["name"] == service_name), None)
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
                'services': service_data,
                'system': system_info
            }
        except Exception as e:
            logger.error(f"Error collecting game server status: {e}")
            raise
    
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