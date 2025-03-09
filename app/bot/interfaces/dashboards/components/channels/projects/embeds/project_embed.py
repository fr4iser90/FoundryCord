from typing import Dict, List, Any
import nextcord
from datetime import datetime
from interfaces.dashboards.components.common.embeds import BaseEmbed

class ProjectEmbed(BaseEmbed):
    """Project specific embed implementations with consistent formatting"""
    
    @classmethod
    def create_project_dashboard(cls, projects_by_status: Dict[str, List[Any]]) -> nextcord.Embed:
        """Creates the project dashboard overview embed with consistent formatting"""
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
        
        # Calculate statistics for header
        total_projects = sum(len(projects) for projects in projects_by_status.values())
        active_projects = len(projects_by_status.get('in_progress', []))
        
        # Add statistics bar at top
        stats = (
            f"**Gesamt:** {total_projects} Projekte | "
            f"**Aktiv:** {active_projects} | "
            f"**Planung:** {len(projects_by_status.get('planning', []))} | "
            f"**Abgeschlossen:** {len(projects_by_status.get('completed', []))}"
        )
        embed.add_field(name="📈 Statistik", value=stats, inline=False)
        
        # Add projects grouped by status
        for status, projects in projects_by_status.items():
            if not projects:
                continue
                
            field_value = ""
            for project in projects:
                # Get project attributes safely
                priority = getattr(project, 'priority', 'medium')
                deadline = getattr(project, 'deadline', None)
                progress = getattr(project, 'progress', 0)
                
                # Create progress bar for project completion
                progress_bar = cls._create_progress_bar(progress, 100)
                
                # Priority emoji based on priority level
                priority_emoji = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(priority, '⚪')
                
                # Format deadline with emoji if exists
                deadline_text = f" | ⏰ {deadline}" if deadline else ""
                
                field_value += (
                    f"{priority_emoji} **{project.name}**{deadline_text}\n"
                    f"└ {progress_bar} {progress}%"
                )
                
                if project.description:
                    field_value += f"\n└ {project.description[:80]}..." if len(project.description) > 80 else f"\n└ {project.description}"
                
                field_value += "\n\n"
            
            if field_value:
                status_emoji = status_emojis.get(status, "⚪")
                status_name = status_names.get(status, status.capitalize())
                embed.add_field(
                    name=f"{status_emoji} {status_name}",
                    value=field_value,
                    inline=False
                )
        
        embed.set_footer(text=f"Last updated • {datetime.now().strftime('%H:%M:%S')}")
        return embed
    
    @staticmethod
    def _create_progress_bar(value: float, max_value: float, length: int = 10) -> str:
        """Creates a visual progress bar with emojis"""
        filled_blocks = int((value / max_value) * length)
        
        if filled_blocks <= length * 0.33:
            filled = "🟢" * filled_blocks
        elif filled_blocks <= length * 0.66:
            filled = "🟡" * filled_blocks
        else:
            filled = "🔴" * filled_blocks
            
        empty = "⚫" * (length - filled_blocks)
        return filled + empty

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
