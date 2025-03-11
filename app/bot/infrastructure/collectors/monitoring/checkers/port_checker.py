"""Port availability checking utilities"""
import socket
import logging

logger = logging.getLogger('homelab_bot')

def check_tcp_port(ip, port, timeout=0.5):
    """Check if a TCP port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.debug(f"Error checking TCP port {port} on {ip}: {str(e)}")
        return False