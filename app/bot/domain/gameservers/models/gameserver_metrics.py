# app/bot/domain/gameservers/models/gameserver_metrics.py
from typing import Dict, Any, List, Optional
from datetime import datetime

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
    
    @classmethod
    def from_raw_data(cls, data: Dict[str, Any]) -> 'GameServersMetrics':
        """Create GameServersMetrics from raw API data"""
        metrics = cls()
        
        # Get game server data from monitoring data
        game_servers = data.get('services', {}).get('services', {})
        
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
        """Convert to dictionary format for UI consumption"""
        return {
            'servers': {name: server.to_dict() for name, server in self.servers.items()},
            'total_servers': len(self.servers),
            'online_servers': sum(1 for server in self.servers.values() if server.online),
            'total_players': sum(server.player_count for server in self.servers.values()),
            'timestamp': self.timestamp.strftime('%H:%M:%S')
        }