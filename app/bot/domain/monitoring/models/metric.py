from datetime import datetime
from typing import Dict, Any, List, Optional, Union

class Metric:
    """Base class for system metrics"""
    def __init__(self, name, value, unit=None, timestamp=None, metadata=None):
        self.name = name
        self.value = value
        self.unit = unit
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
    
    def is_critical(self, threshold):
        """Check if metric exceeds critical threshold"""
        # Implementation depends on the metric type
        return False


class SystemMetrics:
    """Container for all system metrics"""
    def __init__(self):
        self.cpu = CPUMetrics()
        self.memory = MemoryMetrics()
        self.disk = DiskMetrics()
        self.network = NetworkMetrics()
        self.services = ServiceMetrics()
        self.game_servers = {}
        self.timestamp = datetime.now()
    
    @classmethod
    def from_raw_data(cls, data: Dict[str, Any]) -> 'SystemMetrics':
        """Create SystemMetrics from raw API data"""
        metrics = cls()
        
        system_data = data.get('system', {})
        service_data = data.get('services', {})
        
        # Fill CPU metrics
        metrics.cpu = CPUMetrics.from_raw_data(system_data)
        
        # Fill Memory metrics
        metrics.memory = MemoryMetrics.from_raw_data(system_data)
        
        # Fill Disk metrics
        metrics.disk = DiskMetrics.from_raw_data(system_data)
        
        # Fill Network metrics
        metrics.network = NetworkMetrics.from_raw_data(system_data)
        
        # Fill Service metrics
        metrics.services = ServiceMetrics.from_raw_data(service_data)
        
        # Process game servers
        if 'services' in service_data:
            game_services = {
                name.replace('🎮 ', ''): {
                    'online': 'Online' in status or '✅' in status,
                    'ports': cls._extract_ports(status)
                }
                for name, status in service_data.get('services', {}).items() 
                if '🎮' in name
            }
            metrics.game_servers = game_services
        
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
            # CPU metrics
            'cpu_usage': self.cpu.usage,
            'cpu_model': self.cpu.model,
            'cpu_cores': self.cpu.cores,
            'cpu_threads': self.cpu.threads,
            'cpu_temp': self.cpu.temperature,
            
            # Memory metrics
            'memory_used': self.memory.percent_used,
            'memory_total': self.memory.total_gb,
            
            # Disk metrics
            'disk_free': self.disk.free_gb,
            'disk_total': self.disk.total_gb,
            
            # Network metrics
            'net_download': self.network.download_speed,
            'net_upload': self.network.upload_speed,
            'net_ping': self.network.ping,
            'lan_max': self.network.max_speed,
            'lan_up': self.network.lan_upload,
            'lan_down': self.network.lan_download,
            
            # Docker/container metrics
            'containers_running': self.services.containers_running,
            'containers_total': self.services.containers_total,
            'containers_errors': self.services.containers_errors,
            
            # Game servers
            'game_servers': self.game_servers,
            
            # Add hardware info for detailed views
            'hardware_info': self.cpu.hardware_info
        }


class CPUMetrics:
    """CPU specific metrics"""
    def __init__(self):
        self.usage = 0
        self.model = "Unknown"
        self.cores = 0
        self.threads = 0
        self.temperature = 0
        self.freq_current = "Unknown"
        self.freq_min = "Unknown"
        self.freq_max = "Unknown"
        self.hardware_info = {}
    
    @classmethod
    def from_raw_data(cls, system_data: Dict[str, Any]) -> 'CPUMetrics':
        """Create CPU metrics from raw system data"""
        cpu = cls()
        cpu.usage = system_data.get('cpu', 0)
        
        hardware_info = system_data.get('hardware_info', {})
        cpu.model = hardware_info.get('cpu_model', 'Unknown')
        cpu.cores = hardware_info.get('cpu_cores', 0)
        cpu.threads = hardware_info.get('cpu_threads', 0)
        cpu.temperature = system_data.get('cpu_temp', 0)
        cpu.freq_current = hardware_info.get('cpu_freq_current', 'Unknown')
        cpu.freq_min = hardware_info.get('cpu_freq_min', 'Unknown')
        cpu.freq_max = hardware_info.get('cpu_freq_max', 'Unknown')
        cpu.hardware_info = hardware_info
        
        return cpu
    
    def is_critical(self, threshold=90):
        """Check if CPU usage is critical"""
        return self.usage > threshold or self.temperature > 85


class MemoryMetrics:
    """Memory specific metrics"""
    def __init__(self):
        self.percent_used = 0
        self.total_gb = 0
    
    @classmethod
    def from_raw_data(cls, system_data: Dict[str, Any]) -> 'MemoryMetrics':
        """Create Memory metrics from raw system data"""
        memory = cls()
        memory_data = system_data.get('memory', {})
        
        memory.percent_used = memory_data.percent if hasattr(memory_data, 'percent') else 0
        memory.total_gb = round(memory_data.total / (1024**3), 1) if hasattr(memory_data, 'total') else 0
        
        return memory
    
    def is_critical(self, threshold=90):
        """Check if memory usage is critical"""
        return self.percent_used > threshold


class DiskMetrics:
    """Disk specific metrics"""
    def __init__(self):
        self.free_gb = 0
        self.total_gb = 0
    
    @property
    def used_percent(self):
        """Calculate used percentage"""
        if self.total_gb > 0:
            return 100 - (self.free_gb / self.total_gb * 100)
        return 0
    
    @classmethod
    def from_raw_data(cls, system_data: Dict[str, Any]) -> 'DiskMetrics':
        """Create Disk metrics from raw system data"""
        disk = cls()
        disk_data = system_data.get('disk', {})
        
        disk.free_gb = round(disk_data.free / (1024**3), 2) if hasattr(disk_data, 'free') else 0
        disk.total_gb = round(disk_data.total / (1024**3), 2) if hasattr(disk_data, 'total') else 0
        
        return disk
    
    def is_critical(self, threshold=5):
        """Check if free disk space is critically low (in GB)"""
        return self.free_gb < threshold


class NetworkMetrics:
    """Network specific metrics"""
    def __init__(self):
        self.download_speed = 0
        self.upload_speed = 0
        self.ping = 0
        self.max_speed = "?"
        self.lan_upload = "?"
        self.lan_download = "?"
    
    @classmethod
    def from_raw_data(cls, system_data: Dict[str, Any]) -> 'NetworkMetrics':
        """Create Network metrics from raw system data"""
        network = cls()
        network_data = system_data.get('network', {})
        
        network.download_speed = getattr(network_data, 'download_speed', 0)
        network.upload_speed = getattr(network_data, 'upload_speed', 0)
        network.ping = getattr(network_data, 'ping', 0)
        network.max_speed = getattr(network_data, 'max_speed', '?')
        network.lan_upload = getattr(network_data, 'lan_upload', '?')
        network.lan_download = getattr(network_data, 'lan_download', '?')
        
        return network


class ServiceMetrics:
    """Service specific metrics"""
    def __init__(self):
        self.containers_running = 0
        self.containers_total = 0
        self.containers_errors = 0
        self.containers = []
    
    @classmethod
    def from_raw_data(cls, service_data: Dict[str, Any]) -> 'ServiceMetrics':
        """Create Service metrics from raw service data"""
        services = cls()
        
        services.containers_running = service_data.get('docker_running', 0)
        services.containers_total = service_data.get('docker_total', 0)
        services.containers_errors = service_data.get('docker_errors', 0)
        services.containers = service_data.get('containers', [])
        
        return services