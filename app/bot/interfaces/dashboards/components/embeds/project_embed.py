from typing import Dict, List, Any
import nextcord
from datetime import datetime
from .base_embed import BaseEmbed

class ProjectEmbed(BaseEmbed):
    """Project specific embed implementations"""
    
    @classmethod
    def create_project_dashboard(cls, projects_by_status: Dict[str, List[Any]]) -> nextcord.Embed:
        """Creates the project dashboard overview embed"""
        embed = nextcord.Embed(
            title="📊 Project Dashboard",
            description="Übersicht aller aktuellen Projekte",
            color=cls.INFO_COLOR,
            timestamp=datetime.now()
        )
        
        status_emojis = {
            "planning": "🔵",
            "in_progress": "🟡",
            "completed": "🟢",
            "on_hold": "🟠",
            "cancelled": "🔴"
        }
        
        status_names = {
            "planning": "Planung",
            "in_progress": "In Bearbeitung",
            "completed": "Abgeschlossen",
            "on_hold": "Pausiert",
            "cancelled": "Abgebrochen"
        }
        
        for status, projects in projects_by_status.items():
            if not projects:
                continue
                
            field_value = ""
            for project in projects:
                priority_emoji = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(project.priority, '⚪')
                
                field_value += f"{priority_emoji} **{project.name}**\n"
                if project.description:
                    field_value += f"└ {project.description[:100]}...\n\n"
            
            if field_value:
                status_emoji = status_emojis.get(status, "⚪")
                status_name = status_names.get(status, status.capitalize())
                embed.add_field(
                    name=f"{status_emoji} {status_name}",
                    value=field_value,
                    inline=False
                )
        
        return embed

    @classmethod
    def create_project_details(cls, project: Any) -> nextcord.Embed:
        """Creates a detailed project embed"""
        embed = cls.create(
            title=f"📋 {project.name}",
            description=project.description,
            color=cls.INFO_COLOR
        )
        
        # Add metadata fields
        embed.add_field(name="Status", value=project.status, inline=True)
        embed.add_field(name="Priorität", value=project.priority, inline=True)
        
        if hasattr(project, 'due_date') and project.due_date:
            embed.add_field(
                name="Fällig am",
                value=project.due_date.strftime("%d.%m.%Y"),
                inline=True
            )
        
        # Add task statistics if available
        if hasattr(project, 'tasks'):
            total_tasks = len(project.tasks)
            completed_tasks = len([t for t in project.tasks if t.status == "done"])
            embed.add_field(
                name="Tasks",
                value=f"{completed_tasks}/{total_tasks} erledigt",
                inline=True
            )
            
        return embed
