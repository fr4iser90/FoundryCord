"""Check game services running in containers"""
import logging
import socket
from .docker_utils import get_container_ip, get_all_containers
from .port_checker import check_tcp_port

logger = logging.getLogger('homelab_bot')

async def check_pufferpanel_games(services_list):
    """Check games managed by PufferPanel"""
    results = {}
    containers = get_all_containers()
    
    pufferpanel_container = containers.get("pufferpanel")
    if not pufferpanel_container or pufferpanel_container.status != "running":
        return {service["name"]: "❌ Pufferpanel offline" for service in services_list}
    
    for service in services_list:
        try:
            port_start, port_end = service["port_range"]
            active_ports = set()
            
            if pufferpanel_container.attrs.get('NetworkSettings', {}).get('Ports'):
                for container_port, host_bindings in pufferpanel_container.attrs['NetworkSettings']['Ports'].items():
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
            
    return results
