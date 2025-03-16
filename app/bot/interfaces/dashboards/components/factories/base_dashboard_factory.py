from typing import Dict, Any
from app.bot.infrastructure.factories.base.base_factory import BaseFactory

class BaseDashboardFactory(BaseFactory):
    """Base factory for dashboard components"""
    
    def create(self, name: str, **kwargs) -> Dict[str, Any]:
        """Implementation required by BaseFactory"""
        # Basic implementation
        return {
            'name': name,
            'type': 'dashboard',
            'config': kwargs
        } 