# app/bot/application/services/dashboard/dashboard_lifecycle_service.py
class DashboardLifecycleService:
    """Manages the lifecycle of all dashboards"""
    
    def __init__(self, bot):
        self.bot = bot
        self.registry = None
    
    async def initialize(self):
        """Initialize all dashboards"""
        from app.bot.infrastructure.dashboards.dashboard_registry import DashboardRegistry
        self.registry = DashboardRegistry(self.bot)
        await self.registry.initialize()
        
        # Activate dashboards based on channel configuration
        await self.activate_configured_dashboards()
        
        return True
    
    async def activate_configured_dashboards(self):
        """Activate dashboards based on channel configuration"""
        from app.bot.infrastructure.config.constants.dashboard_constants import DASHBOARD_MAPPINGS
        
        for channel_name, config in DASHBOARD_MAPPINGS.items():
            if config.get('auto_create', False):
                channel_id = await self.bot.channel_config.get_channel_id(channel_name)
                if channel_id:
                    await self.registry.activate_dashboard(
                        dashboard_type=config['dashboard_type'],
                        channel_id=channel_id
                    )
    
    async def deactivate_dashboard(self, dashboard_type=None, channel_id=None):
        """
        Deactivate dashboard by type or channel ID
        
        Args:
            dashboard_type (str, optional): Type of dashboard to deactivate
            channel_id (int, optional): Channel ID containing the dashboard
            
        Returns:
            bool: True if dashboard was deactivated, False otherwise
        """
        if not self.registry:
            return False
            
        return await self.registry.deactivate_dashboard(dashboard_type, channel_id)
    
    async def get_active_dashboards(self):
        """
        Get list of all active dashboards
        
        Returns:
            dict: Dictionary of active dashboards by channel_id
        """
        if not self.registry:
            return {}
            
        return self.registry.active_dashboards
    
    async def refresh_dashboard(self, channel_id):
        """
        Force refresh of a dashboard
        
        Args:
            channel_id (int): Channel ID containing the dashboard
            
        Returns:
            bool: True if dashboard was refreshed, False otherwise
        """
        if not self.registry or channel_id not in self.registry.active_dashboards:
            return False
            
        dashboard = self.registry.active_dashboards[channel_id]
        await dashboard.refresh()
        return True
    
    async def shutdown(self):
        """
        Perform clean shutdown of all dashboards
        
        Returns:
            bool: True if successful
        """
        if not self.registry:
            return True
            
        # Deactivate all dashboards
        for channel_id in list(self.registry.active_dashboards.keys()):
            await self.registry.deactivate_dashboard(channel_id=channel_id)
            
        return True