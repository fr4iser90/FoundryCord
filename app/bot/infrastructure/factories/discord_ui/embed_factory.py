from typing import Dict, Any, Optional
import nextcord
from ..base.base_factory import BaseFactory
from interfaces.dashboards.components.common.embeds import BaseEmbed
from interfaces.dashboards.components.channels.projects.embeds import ProjectEmbed
from interfaces.dashboards.components.channels.monitoring.embeds import MonitoringEmbed
from interfaces.dashboards.components.channels.projects.embeds import ProjectEmbed
from interfaces.dashboards.components.channels.projects.embeds import StatusEmbed
from interfaces.dashboards.components.channels.welcome.embeds import WelcomeEmbed

class EmbedFactory(BaseFactory):
    """Factory für die Erstellung von Embeds"""
    
    def __init__(self, bot):
        super().__init__(bot)
        self.embed_types = {
            'base': BaseEmbed,
            'welcome': WelcomeEmbed,
            'monitoring': MonitoringEmbed,
            'project': ProjectEmbed,
            'status': StatusEmbed
        }
    
    def create(self, name: str, **kwargs) -> Dict[str, Any]:
        """Implementation of abstract create method"""
        if name not in self.embed_types:
            return self.create_base_embed(**kwargs)
            
        embed_class = self.embed_types[name]
        embed = embed_class.create(**kwargs)
        
        return {
            'name': name,
            'embed': embed,
            'type': 'embed',
            'config': kwargs
        }

    def create_embed(
        self,
        embed_type: str,
        **kwargs
    ) -> nextcord.Embed:
        """Creates an embed of the specified type"""
        if embed_type not in self.embed_types:
            raise ValueError(f"Unknown embed type: {embed_type}")
            
        embed_class = self.embed_types[embed_type]
        
        if embed_type == 'welcome':
            return embed_class.create_welcome(**kwargs)
        elif embed_type == 'monitoring':
            return embed_class.create_system_status(**kwargs)
        elif embed_type == 'project':
            return embed_class.create_project_dashboard(**kwargs)
        else:
            return embed_class.create(**kwargs)
