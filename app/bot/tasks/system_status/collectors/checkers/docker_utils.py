"""Utilities for Docker container operations"""
import docker
import logging

logger = logging.getLogger('homelab_bot')

def get_container_ip(container_name):
    """Ermittelt die IP-Adresse eines Docker Containers mit der Docker API"""
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        # Hole die erste verfügbare IP
        networks = container.attrs['NetworkSettings']['Networks']
        for network in networks.values():
            if network.get('IPAddress'):
                return network['IPAddress']
        return None
    except Exception as e:
        logger.debug(f"Fehler beim Ermitteln der Container-IP für {container_name}: {e}")
        return None
        
def get_all_containers():
    """Returns a dictionary of all containers {name: container}"""
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        return {container.name: container for container in containers}
    except Exception as e:
        logger.debug(f"Fehler beim Abrufen der Container: {e}")
        return {}