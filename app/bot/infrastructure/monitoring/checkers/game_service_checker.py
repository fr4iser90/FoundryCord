"""Check game services running in containers"""
import logging
import socket
import subprocess
import asyncio
import aiohttp
from .docker_utils import get_container_ip, get_all_containers
from .port_checker import check_tcp_port
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.monitoring.collectors.game_servers.minecraft_server_collector_impl import MinecraftServerFetcher

async def get_public_ip():
    """Get the public IP address of the server"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://ipinfo.io/json', timeout=2) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"Public IP: {data['ip']}")
                    return data['ip']
    except Exception as e:
        logger.debug(f"Error getting public IP: {e}")
    return None

async def check_minecraft_server(ip, port, timeout=3.0):
    """Check if a Minecraft server is running at the given IP and port"""
    try:
        # Simple socket connection (Minecraft responds even without a full handshake)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        if result == 0:
            # Connection succeeded
            logger.debug(f"Minecraft port {port} is open at {ip}")
            sock.close()
            return True
        sock.close()
        return False
    except Exception as e:
        logger.debug(f"Minecraft check failed for {ip}:{port} - {str(e)}")
        return False

async def check_pufferpanel_games(services_list):
    """Check games managed by PufferPanel"""
    logger.debug(f"======== STARTING PUFFERPANEL GAMES CHECK ========")
    results = {}
    containers = get_all_containers()
    
    logger.debug(f"Found containers: {list(containers.keys())}")
    
    pufferpanel_container = containers.get("pufferpanel")
    if not pufferpanel_container or pufferpanel_container.status != "running":
        logger.debug("PufferPanel container not running or not found")
        return {service["name"]: "❌ Pufferpanel offline" for service in services_list}
    
    logger.debug(f"PufferPanel container status: {pufferpanel_container.status}")
    
    # Check directly if the game servers are running
    logger.debug("Checking for direct evidence of running game servers...")
    try:
        # Direct check to see what processes are running in the container
        cmd = "docker exec pufferpanel ps aux"
        ps_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        logger.debug(f"Process listing result: {ps_result.returncode}")
        logger.debug(f"Process list output: {ps_result.stdout}")
    except Exception as e:
        logger.debug(f"Error checking processes: {e}")
    
    # Get all listening ports on the system
    logger.debug("Checking all listening ports on the system...")
    try:
        listening_cmd = "ss -tulnp"
        listening_result = subprocess.run(listening_cmd, shell=True, capture_output=True, text=True)
        logger.debug(f"All listening ports: {listening_result.stdout}")
    except Exception as e:
        logger.debug(f"Error checking listening ports: {e}")
    
    # Get the container ports mapped to host
    exposed_ports = {}
    
    if pufferpanel_container.attrs.get('NetworkSettings', {}).get('Ports'):
        for container_port, host_bindings in pufferpanel_container.attrs['NetworkSettings']['Ports'].items():
            if not host_bindings:
                continue
                
            port_str, protocol = container_port.split('/') if '/' in container_port else (container_port, 'tcp')
            logger.debug(f"Processing port mapping: {port_str}/{protocol} -> {host_bindings}")
            
            # Handle port ranges (e.g. "25565-25575/tcp")
            if '-' in port_str:
                try:
                    start_port, end_port = map(int, port_str.split('-'))
                    for port in range(start_port, end_port + 1):
                        host_port = int(host_bindings[0]['HostPort']) if host_bindings[0]['HostPort'] else port
                        exposed_ports[port] = {
                            'host_port': host_port,
                            'protocol': protocol
                        }
                        logger.debug(f"Added range port mapping: {port} -> {host_port} ({protocol})")
                except (ValueError, IndexError, KeyError) as e:
                    logger.debug(f"Error processing port range {port_str}: {e}")
                    continue
            else:
                try:
                    port = int(port_str)
                    host_port = int(host_bindings[0]['HostPort']) if host_bindings[0]['HostPort'] else port
                    exposed_ports[port] = {
                        'host_port': host_port,
                        'protocol': protocol
                    }
                    logger.debug(f"Added single port mapping: {port} -> {host_port} ({protocol})")
                except (ValueError, IndexError, KeyError) as e:
                    logger.debug(f"Error processing port {port_str}: {e}")
                    continue
    
    logger.debug(f"Found {len(exposed_ports)} exposed ports in PufferPanel: {exposed_ports}")
    
    # Get established connections (players currently connected)
    try:
        logger.debug("Checking for established connections...")
        cmd = "netstat -tn | grep ESTABLISHED"
        established_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        logger.debug(f"Established connections result: {established_result.returncode}")
        logger.debug(f"Established connections output: {established_result.stdout}")
        
        established_ports = set()
        if established_result.returncode == 0:
            for line in established_result.stdout.splitlines():
                parts = line.split()
                logger.debug(f"Processing established connection line: {line}")
                if len(parts) >= 4:
                    local_addr = parts[3]  # Format: IP:PORT
                    logger.debug(f"Local address: {local_addr}")
                    if ':' in local_addr:
                        try:
                            port = int(local_addr.split(':')[-1])
                            established_ports.add(port)
                            logger.debug(f"Added established port: {port}")
                        except ValueError as e:
                            logger.debug(f"Error parsing port from {local_addr}: {e}")
                            pass
        
        logger.debug(f"Found {len(established_ports)} established connections on ports: {sorted(established_ports)}")
    except Exception as e:
        logger.debug(f"Error checking established connections: {e}")
        established_ports = set()
    
    # Get all UDP connections
    try:
        logger.debug("Checking for UDP connections...")
        udp_cmd = "netstat -un"
        udp_result = subprocess.run(udp_cmd, shell=True, capture_output=True, text=True)
        logger.debug(f"UDP connections output: {udp_result.stdout}")
    except Exception as e:
        logger.debug(f"Error checking UDP connections: {e}")
    
    # Get public IP for external checking
    public_ip = await get_public_ip()
    if not public_ip:
        logger.debug("Could not determine public IP for external checks")
    else:
        logger.debug(f"Using public IP for external checks: {public_ip}")
    
    # Check each service
    for service in services_list:
        logger.debug(f"====== Checking service: {service['name']} ======")
        try:
            port_start, port_end = service["port_range"]
            logger.debug(f"Port range: {port_start}-{port_end}")
            active_ports = set()
            
            # Get all exposed ports for this service
            exposed_service_ports = {}
            for port in range(port_start, port_end + 1):
                if port in exposed_ports:
                    exposed_service_ports[port] = exposed_ports[port]
            
            logger.debug(f"Service {service['name']} has {len(exposed_service_ports)} exposed ports: {exposed_service_ports}")
            
            # If public IP is available, prioritize external checks
            if public_ip:
                logger.debug(f"Performing external checks for {service['name']} using public IP")
                for port in exposed_service_ports.values():
                    host_port = port['host_port']
                    logger.debug(f"Checking external access for port {host_port} at {public_ip}")
                    
                    # Try TCP connection to public IP
                    try:
                        if check_tcp_port(public_ip, host_port, timeout=2.0):
                            active_ports.add(host_port)
                            logger.debug(f"TCP port {host_port} is accessible from outside at {public_ip}")
                        else:
                            logger.debug(f"TCP port {host_port} is NOT accessible from outside")
                            
                            # Special check for UDP ports that might be open
                            protocol = port['protocol']
                            if protocol == 'udp':
                                logger.debug(f"UDP port {host_port} - assuming it might be open")
                                # Try TCP on the same port as a fallback check
                                # or if we have other evidence the server is running
                                if check_tcp_port(public_ip, host_port, timeout=2.0):
                                    logger.debug(f"TCP port {host_port} is accessible, assuming UDP is available too")
                                    active_ports.add(host_port)
                                else:
                                    # For Minecraft specifically, try to check if the server responds
                                    if "Minecraft" in service["name"] and host_port == 25565:
                                        # Try a simple check for the primary Minecraft port
                                        if await check_minecraft_server(public_ip, host_port):
                                            logger.debug(f"Minecraft server detected on port {host_port}")
                                            active_ports.add(host_port)
                                            break  # One confirmed port is enough for Minecraft
                    except Exception as e:
                        logger.debug(f"Error checking port {host_port}: {str(e)}")
            
            # Final determination based on external checks
            if active_ports:
                logger.debug(f"{service['name']}: Found externally accessible ports: {active_ports}")
                results[service["name"]] = f"✅ Online auf Port(s): {', '.join(map(str, sorted(active_ports)))}"
            else:
                # Only if external check fails, try to detect if process is running
                process_detected = False
                game_name = service["name"].replace('🎮 ', '').lower()
                
                # Check for running process
                for cmd in [
                    f"docker exec pufferpanel ps aux | grep -i {game_name} | grep -v grep",
                    f"docker exec pufferpanel pgrep -f {game_name}",
                    f"docker exec pufferpanel ls -la /tmp/pufferd/servers/ | grep -i {game_name}"
                ]:
                    try:
                        logger.debug(f"Running command: {cmd}")
                        ps_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                        if ps_result.returncode == 0 and ps_result.stdout.strip():
                            logger.debug(f"Process detected for {game_name}: {ps_result.stdout}")
                            process_detected = True
                            break
                        else:
                            logger.debug(f"No process detected with command: {cmd}")
                    except Exception as e:
                        logger.debug(f"Error running {cmd}: {e}")
                
                if process_detected:
                    logger.debug(f"{service['name']}: Process detected but no accessible ports from outside")
                    results[service["name"]] = "✅ Online (standby)"
                else:
                    logger.debug(f"{service['name']}: No accessible ports or processes detected")
                    results[service["name"]] = "❌ Offline"
                
        except Exception as e:
            logger.debug(f"Fehler bei {service['name']}: {str(e)}")
            results[service["name"]] = "⚠️ Fehler"
    
    logger.debug(f"Final PufferPanel game server results: {results}")
    logger.debug(f"======== FINISHED PUFFERPANEL GAMES CHECK ========")
    return results

async def check_standalone_games(services_list):
    """Check standalone game servers"""
    results = {}
    containers = get_all_containers()
    
    for service in services_list:
        try:
            container = containers.get(service["container"])
            if not container:
                results[service["name"]] = "⚠️ Container nicht gefunden"
                continue
            
            if container.status != "running":
                results[service["name"]] = "❌ Offline"
                continue
                
            port_start, port_end = service["port_range"]
            active_ports = set()
            
            if container.attrs.get('NetworkSettings', {}).get('Ports'):
                for container_port, host_bindings in container.attrs['NetworkSettings']['Ports'].items():
                    if not host_bindings:
                        continue
                        
                    container_port_num = int(container_port.split('/')[0])
                    
                    if port_start <= container_port_num <= port_end:
                        host_ip = host_bindings[0]['HostIp'] or 'localhost'
                        host_port = int(host_bindings[0]['HostPort'])
                        
                        try:
                            check_ip = '127.0.0.1' if host_ip in ('0.0.0.0', '') else host_ip
                            
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.settimeout(2)
                            result = sock.connect_ex((check_ip, host_port))
                            sock.close()
                            
                            if result == 0:
                                active_ports.add(host_port)
                            else:
                                protocol = container_port.split('/')[1] if '/' in container_port else 'tcp'
                                if protocol == 'udp' or service["protocol"] == "udp":
                                    active_ports.add(host_port)
                        except Exception as e:
                            logger.debug(f"Socket check failed for {host_ip}:{host_port} - {str(e)}")

            if active_ports:
                results[service["name"]] = f"✅ Online auf Port(s): {', '.join(map(str, sorted(active_ports)))}"
            else:
                results[service["name"]] = "❌ Keine aktiven Ports"
                
        except Exception as e:
            logger.debug(f"Fehler bei {service['name']}: {str(e)}")
            results[service["name"]] = "⚠️ Fehler"
            
    logger.debug(f"Final standalone game server results: {results}")
    logger.debug(f"======== FINISHED STANDALONE GAMES CHECK ========")
    return results