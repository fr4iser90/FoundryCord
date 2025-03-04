import psutil
import logging
import time
import asyncio
import aiohttp  # Add this for speed test
from typing import Dict, Any
from .speed_test import SpeedTestManager

logger = logging.getLogger('homelab_bot')

# Create a global SpeedTestManager instance
speed_test_manager = SpeedTestManager()

async def perform_speed_test() -> Dict[str, float]:
    """Führt einen Internet Speed Test durch"""
    try:
        async with aiohttp.ClientSession() as session:
            # Using fast.com or speedtest.net API would be more accurate,
            # but for demo we'll use a simple download test
            start_time = time.time()
            async with session.get('https://speed.cloudflare.com/__down') as response:
                data = await response.read()
                duration = time.time() - start_time
                speed_mbps = (len(data) * 8 / 1_000_000) / duration  # Convert to Mbps
                return {"download": speed_mbps}
    except Exception as e:
        logger.error(f"Speed test failed: {e}")
        return {"download": 0.0}

async def get_network_info() -> Dict[str, Any]:
    """Sammelt Netzwerk-Interface Informationen mit aktueller Geschwindigkeit"""
    try:
        # Get cached or new speed test results
        speed_results = await speed_test_manager.get_speed_info()
        internet_speed = (
            f"Internet: ↓{speed_results.get('download', 0.0):.1f} Mbps, "
            f"↑{speed_results.get('upload', 0.0):.1f} Mbps"
            f" (Ping: {speed_results.get('ping', 0.0):.0f}ms)"
        )
        
        net_io_counters_start = psutil.net_io_counters(pernic=True)
        await asyncio.sleep(1)
        net_io_counters_end = psutil.net_io_counters(pernic=True)

        network_info = [internet_speed]  # Add internet speed as first line
        interface_names = {
            'eth': 'LAN',
            'wlan': 'WLAN',
            'enp': 'LAN',
            'wlp': 'WLAN',
            'ens': 'LAN',
            'wls': 'WLAN'
        }
        
        for interface, stats in psutil.net_if_stats().items():
            # Skip loopback interface
            if interface.startswith('lo'):
                continue
                
            if stats.isup:
                display_name = next(
                    (name for prefix, name in interface_names.items() 
                     if interface.startswith(prefix)), 
                    interface
                )
                
                if interface in net_io_counters_start and interface in net_io_counters_end:
                    bytes_sent = net_io_counters_end[interface].bytes_sent - net_io_counters_start[interface].bytes_sent
                    bytes_recv = net_io_counters_end[interface].bytes_recv - net_io_counters_start[interface].bytes_recv
                    
                    send_speed = bytes_sent / 1024 / 1024  # MB/s
                    recv_speed = bytes_recv / 1024 / 1024  # MB/s
                    
                    if stats.speed > 1000:
                        speed = f"{stats.speed/1000:.1f}Gb/s"
                    elif stats.speed > 0:
                        speed = f"{stats.speed}Mb/s"
                    else:
                        speed = "Unbekannt"
                    
                    network_info.append(
                        f"{display_name} (Max: {speed}, "
                        f"Aktuell: ↑{send_speed:.1f} MB/s, ↓{recv_speed:.1f} MB/s)"
                    )
                else:
                    network_info.append(f"{display_name} (Status: Aktiv)")
        
        return {
            'network_adapters': "\n".join(network_info) if network_info else "Keine aktiven Netzwerk-Adapter"
        }
    except Exception as e:
        logger.error(f"Network Info Fehler: {e}")
        return {
            'network_adapters': "Netzwerk-Informationen nicht verfügbar"
        }