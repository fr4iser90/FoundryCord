# app/bot/domain/gameservers/models/gameserver_metrics.py
from typing import Dict, Any, List, Optional
from datetime import datetime
from infrastructure.logging import logger

class GameServerStatus:
    """Status of a game server"""
    def __init__(self, 
                 name: str, 
                 status: bool = False, 
                 ports: List[int] = None,
                 players: List[str] = None,
                 version: str = None,
                 uptime: Optional[str] = None):
        self.name = name
        self.online = status
        self.ports = ports or []
        self.players = players or []
        self.player_count = len(self.players) if self.players else 0
        self.max_players = 0  # Will be filled later if available
        self.version = version
        self.uptime = uptime
        self.last_check = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for UI consumption"""
        return {
            'name': self.name,
            'online': self.online,
            'ports': self.ports,
            'players': self.players,
            'player_count': self.player_count,
            'max_players': self.max_players,
            'version': self.version,
            'uptime': self.uptime,
            'last_check': self.last_check.strftime('%H:%M:%S')
        }

class GameServersMetrics:
    """Container for all game server metrics"""
    def __init__(self):
        self.servers: Dict[str, GameServerStatus] = {}
        self.timestamp = datetime.now()
        self.public_ip = None
        self.domain = None
        self.ip_match = None
    
    @classmethod
    def from_raw_data(cls, data: Dict[str, Any]) -> 'GameServersMetrics':
        """Create GameServersMetrics from raw API data"""
        metrics = cls()
        
        # Get game server data from monitoring data
        game_servers = data.get('services', {}).get('services', {})
        
        # Extract connection information if available
        if 'system' in data:
            metrics.public_ip = data.get('system', {}).get('public_ip')
            metrics.domain = data.get('system', {}).get('domain')
            if metrics.public_ip and metrics.domain:
                domain_ip = data.get('system', {}).get('domain_ip')
                metrics.ip_match = metrics.public_ip == domain_ip
        
        # Process game servers data
        for name, status_text in game_servers.items():
            if '🎮' not in name:
                continue
                
            server_name = name.replace('🎮 ', '')
            online = 'Online' in status_text or '✅' in status_text
            ports = cls._extract_ports(status_text)
            
            server_status = GameServerStatus(
                name=server_name,
                status=online,
                ports=ports
            )
            metrics.servers[server_name] = server_status
            
        return metrics
    
    @staticmethod
    def _extract_ports(status_text):
        """Helper to extract port numbers from status text"""
        ports = []
        if 'Port' in status_text:
            try:
                port_section = status_text.split('Port')[1].split(':')[1].strip()
                ports = [int(p.strip()) for p in port_section.split(',') if p.strip().isdigit()]
            except (IndexError, ValueError):
                pass
        return ports
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all metrics to dictionary format"""
        server_dict = {}
        online_count = 0
        total_players = 0
        
        # Process each server
        for name, server in self.servers.items():
            server_dict[name] = server.to_dict()
            if server.online:
                online_count += 1
                total_players += server.player_count
        
        # Log the server_dict for debugging
        for name, data in server_dict.items():
            if "minecraft" in name.lower():
                logger.debug(f"Server {name} in to_dict(): {data}")
                logger.debug(f"  Player count: {data.get('player_count')}")
                logger.debug(f"  Players: {data.get('players')}")
        
        return {
            'servers': server_dict,
            'online_servers': online_count,
            'total_servers': len(self.servers),
            'total_players': total_players,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'public_ip': self.public_ip,
            'domain': self.domain,
            'ip_match': self.ip_match
        }

    def update_with_minecraft_data(self, minecraft_data: Dict[str, Any]) -> None:
        """Update metrics with data from Minecraft server collector"""
        logger.debug(f"�� GameServersMetrics: Starting Minecraft data update with {len(minecraft_data)} servers")
        
        for server_key, data in minecraft_data.items():
            addr, port = server_key.split(':')
            port_num = int(port)
            
            # Determine server name - use existing if found by port, or create new
            server_name = None
            for name, server in self.servers.items():
                if port_num in server.ports and "minecraft" in name.lower():
                    server_name = name
                    break
            
            if not server_name:
                server_name = "Minecraft"
            
            # Get player data
            player_list = data.get('players', [])
            player_count = data.get('player_count', 0)
            max_players = data.get('max_players', 0)
            
            logger.debug(f"🎮 GameServersMetrics: Processing server '{server_name}'")
            logger.debug(f"  - Player count: {player_count}")
            logger.debug(f"  - Max players: {max_players}")
            logger.debug(f"  - Player list: {player_list}")
            
            # Create or update the server status
            if server_name in self.servers:
                # Update existing server
                server = self.servers[server_name]
                logger.debug(f"�� GameServersMetrics: Updating existing server: {server_name}")
                server.online = data.get('online', False)
                server.players = player_list
                server.player_count = player_count
                server.max_players = max_players
                server.version = data.get('version', 'Unknown')
                server.last_check = datetime.now()
            else:
                # Create new server entry
                logger.debug(f"🎮 GameServersMetrics: Creating new server: {server_name}")
                server = GameServerStatus(
                    name=server_name,
                    status=data.get('online', False),
                    ports=[port_num],
                    players=player_list,
                    version=data.get('version', 'Unknown')
                )
                server.max_players = max_players
                server.player_count = player_count
                self.servers[server_name] = server