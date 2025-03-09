from infrastructure.logging import logger

class CommandConfig:
    @staticmethod
    def register_commands(bot):
        """Register all command modules"""
        try:
            # Import setup functions instead of direct class references
            #from interfaces.commands.monitoring import setup as setup_monitoring
            #from interfaces.commands.auth import setup as setup_auth
            #from interfaces.commands.wireguard import setup as setup_wireguard
            from interfaces.homelab_commands import setup as setup_homelab
            # Import other setup functions here
            
            # Return setup functions that will be called by the lifecycle manager
            return [
            #    {'name': 'System Monitoring', 'setup': setup_monitoring},
            #    {'name': 'Authentication', 'setup': setup_auth},
            #    {'name': 'Wireguard', 'setup': setup_wireguard},
                {'name': 'Homelab Commands', 'setup': setup_homelab},
                # Add other command modules here
            ]
        except Exception as e:
            logger.error(f"Failed to register commands: {e}")
            return []