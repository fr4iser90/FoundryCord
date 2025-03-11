import aiohttp
import asyncio
from typing import Dict, Any, List, Tuple
from datetime import datetime
import logging

logger = logging.getLogger("homelab_bot")

class MinecraftServerFetcher:
    """Fetches detailed Minecraft server information from external APIs"""
    
    API_BASE_URL = "https://api.mcstatus.io/v2/status/java/"
    TIMEOUT = 10  # seconds
    
    @staticmethod
    async def fetch_multiple_servers(servers: List[Tuple[str, int]]) -> Dict[str, Any]:
        """
        Fetch data for multiple Minecraft servers in parallel
        
        Args:
            servers: List of (address, port) tuples
            
        Returns:
            Dictionary mapping server_key to server data
        """
        logger.debug(f"🎮 MinecraftServerFetcher: Fetching data for {len(servers)} servers")
        
        tasks = []
        for address, port in servers:
            tasks.append(MinecraftServerFetcher.fetch_server_data(address, port))
        
        if not tasks:
            logger.warning("🎮 MinecraftServerFetcher: No servers to fetch")
            return {}
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        server_data = {}
        for i, (address, port) in enumerate(servers):
            result = results[i]
            server_key = f"{address}:{port}"
            
            if isinstance(result, Exception):
                logger.error(f"🎮 MinecraftServerFetcher: Error fetching {server_key}: {str(result)}")
                server_data[server_key] = {
                    "online": False,
                    "address": address,
                    "port": port,
                    "error": str(result)
                }
            else:
                server_data[server_key] = result
                
        return server_data
    
    @staticmethod
    async def fetch_server_data(server_address: str, port: int = 25565) -> Dict[str, Any]:
        """
        Fetches Minecraft server data from mcstatus.io API
        
        Args:
            server_address: Domain or IP of the Minecraft server
            port: Server port (default: 25565)
            
        Returns:
            Dictionary with processed server data
        """
        url = f"{MinecraftServerFetcher.API_BASE_URL}{server_address}:{port}"
        
        try:
            logger.debug(f"🎮 MinecraftServerFetcher: Fetching data from {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=MinecraftServerFetcher.TIMEOUT) as response:
                    if response.status != 200:
                        logger.warning(f"🎮 MinecraftServerFetcher: Failed to fetch data: HTTP {response.status}")
                        return {
                            "online": False,
                            "error": f"API returned status code {response.status}",
                            "address": server_address,
                            "port": port
                        }
                    
                    data = await response.json()
                    logger.debug(f"🎮 MinecraftServerFetcher: Raw API response: {data}")
                    
                    # Extract player information
                    player_data = data.get("players", {})
                    player_count = player_data.get("online", 0)
                    max_players = player_data.get("max", 0)
                    player_list_raw = player_data.get("list", [])
                    
                    # Extract player names
                    player_list = []
                    for player in player_list_raw:
                        name = player.get("name_clean", player.get("name_raw", "Unknown"))
                        player_list.append(name)
                    
                    logger.debug(f"🎮 MinecraftServerFetcher: Extracted {player_count} players: {player_list}")
                    
                    # Build the result
                    result = {
                        "online": data.get("online", False),
                        "address": server_address,
                        "port": port,
                        "version": data.get("version", {}).get("name_clean", "Unknown"),
                        "player_count": player_count,
                        "max_players": max_players,
                        "players": player_list,
                        "motd": data.get("motd", {}).get("clean", "A Minecraft Server"),
                        "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    return result
                    
        except Exception as e:
            logger.error(f"🎮 MinecraftServerFetcher: Error: {str(e)}")
            return {
                "online": False,
                "error": str(e),
                "address": server_address,
                "port": port
            }