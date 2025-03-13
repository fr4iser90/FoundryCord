# modules/tracker/project_tracker.py
import nextcord
from datetime import datetime
from app.bot.utils.decorators.auth import admin_or_higher
from app.shared.logging import logger
from app.shared.database.models.config import get_session
from app.shared.database.repositories.project_repository_impl import ProjectRepository
from app.shared.database.repositories.task_repository import TaskRepository

def create_task_embed(tasks_data):
    """Erstellt ein Embed mit allen Projekten und Aufgaben"""
    embed = nextcord.Embed(
        title="🎯 Projekt Tracker",
        description="Aktuelle Projekte und Aufgaben",
        color=0x3498db,
        timestamp=datetime.now()
    )
    
    if not tasks_data["projects"]:
        embed.add_field(name="Keine Projekte", value="Füge ein Projekt mit `/project_add` hinzu", inline=False)
        return embed
    
    for project_name, project_data in tasks_data["projects"].items():
        tasks_text = ""
        for task in project_data["tasks"]:
            status_emoji = "✅" if task["completed"] else "⏳"
            priority_emoji = "🔴" if task["priority"] == "high" else "🟡" if task["priority"] == "medium" else "🟢"
            tasks_text += f"{status_emoji} {priority_emoji} **{task['title']}**\n"
            if task["description"]:
                tasks_text += f"└ {task['description']}\n"
        
        if not tasks_text:
            tasks_text = "Keine Aufgaben für dieses Projekt."
        
        embed.add_field(
            name=f"📋 {project_name}",
            value=tasks_text,
            inline=False
        )
    
    embed.set_footer(text="Verwende /project_* und /task_* Befehle zum Verwalten")
    return embed

async def get_projects_data():
    """Lädt die Projekte und Aufgaben aus der Datenbank"""
    async for session in get_session():
        project_repo = ProjectRepository(session)
        task_repo = TaskRepository(session)
        
        projects = await project_repo.get_all()
        
        # Format für die bestehende Logik beibehalten
        projects_data = {"projects": {}}
        
        for project in projects:
            tasks = await task_repo.get_by_project_id(project.id)
            
            tasks_list = []
            for task in tasks:
                tasks_list.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority,
                    "completed": task.status == "completed",
                    "created_at": task.created_at.isoformat(),
                    "created_by": task.created_by
                })
            
            projects_data["projects"][project.name] = {
                "created_at": project.created_at.isoformat(),
                "created_by": project.created_by,
                "tasks": tasks_list
            }
        
        return projects_data

async def setup(bot):
    """Setup function for the project tracker module"""
    try:
        # Hilfsfunktion zur Überprüfung des Threads
        async def check_tracker_thread(interaction):
            """Überprüft, ob der Befehl im Projekt-Tracker-Thread ausgeführt wird"""
            channel = interaction.channel
            
            if not isinstance(channel, nextcord.Thread) or channel.name != "Projekt Tracker":
                await interaction.response.send_message(
                    "⚠️ Dieser Befehl kann nur im 'Projekt Tracker'-Thread verwendet werden!", 
                    ephemeral=True
                )
                logger.info(f"Benutzer {interaction.user.name} versuchte, einen Projekt-Tracker-Befehl außerhalb des Threads zu verwenden.")
                return False
            return True

        # Slash-Commands für Projekte
        @bot.slash_command(name="project_add", description="Fügt ein neues Projekt hinzu")
        @admin_or_higher()
        async def add_project(interaction: nextcord.Interaction, name: str):
            # Thread-Check
            if not await check_tracker_thread(interaction):
                return
            
            async for session in get_session():
                project_repo = ProjectRepository(session)
                
                # Prüfen, ob Projekt bereits existiert
                existing_project = await project_repo.get_by_name(name)
                if existing_project:
                    await interaction.response.send_message(f"Projekt '{name}' existiert bereits!", ephemeral=True)
                    return
                
                # Projekt erstellen
                await project_repo.create(
                    name=name,
                    description="",
                    created_by=str(interaction.user.id)
                )
            
            await interaction.response.send_message(f"Projekt '{name}' erfolgreich erstellt!", ephemeral=True)
            
            # Tracker aktualisieren
            await update_tracker_thread(bot, interaction.channel_id)
        
        @bot.slash_command(name="project_delete", description="Löscht ein Projekt")
        @admin_or_higher()
        async def delete_project(interaction: nextcord.Interaction, name: str):
            # Thread-Check
            if not await check_tracker_thread(interaction):
                return
            
            async for session in get_session():
                project_repo = ProjectRepository(session)
                task_repo = TaskRepository(session)
                
                # Prüfen, ob Projekt existiert
                project = await project_repo.get_by_name(name)
                if not project:
                    await interaction.response.send_message(f"Projekt '{name}' existiert nicht!", ephemeral=True)
                    return
                
                # Alle Tasks des Projekts löschen
                tasks = await task_repo.get_by_project_id(project.id)
                for task in tasks:
                    await task_repo.delete(task)
                
                # Projekt löschen
                await project_repo.delete(project)
            
            await interaction.response.send_message(f"Projekt '{name}' erfolgreich gelöscht!", ephemeral=True)
            
            # Tracker aktualisieren
            await update_tracker_thread(bot, interaction.channel_id)
        
        @bot.slash_command(name="project_list", description="Zeigt alle Projekte an")
        @admin_or_higher()
        async def list_projects(interaction: nextcord.Interaction):
            async for session in get_session():
                project_repo = ProjectRepository(session)
                task_repo = TaskRepository(session)
                
                projects = await project_repo.get_all()
                
                if not projects:
                    await interaction.response.send_message("Keine Projekte vorhanden.", ephemeral=True)
                    return
                
                projects_list = []
                for project in projects:
                    tasks = await task_repo.get_by_project_id(project.id)
                    projects_list.append(f"📋 **{project.name}** ({len(tasks)} Aufgaben)")
                
                embed = nextcord.Embed(
                    title="Projekte",
                    description="\n".join(projects_list),
                    color=0x3498db
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Slash-Commands für Aufgaben
        @bot.slash_command(name="task_add", description="Fügt eine neue Aufgabe zu einem Projekt hinzu")
        @admin_or_higher()
        async def add_task(
            interaction: nextcord.Interaction, 
            project: str,
            title: str,
            description: str = None,
            priority: str = nextcord.SlashOption(
                description="Priorität der Aufgabe",
                choices={"Hoch": "high", "Mittel": "medium", "Niedrig": "low"},
                default="medium"
            )
        ):
            # Thread-Check
            if not await check_tracker_thread(interaction):
                return
            
            async for session in get_session():
                project_repo = ProjectRepository(session)
                task_repo = TaskRepository(session)
                
                # Prüfen, ob Projekt existiert
                project_obj = await project_repo.get_by_name(project)
                if not project_obj:
                    await interaction.response.send_message(f"Projekt '{project}' existiert nicht!", ephemeral=True)
                    return
                
                # Task erstellen
                await task_repo.create(
                    project_id=project_obj.id,
                    title=title,
                    description=description or "",
                    priority=priority,
                    created_by=str(interaction.user.id)
                )
            
            await interaction.response.send_message(f"Aufgabe '{title}' zu Projekt '{project}' hinzugefügt!", ephemeral=True)
            
            # Tracker aktualisieren
            await update_tracker_thread(bot, interaction.channel_id)
        
        @bot.slash_command(name="task_complete", description="Markiert eine Aufgabe als erledigt")
        @admin_or_higher()
        async def complete_task(
            interaction: nextcord.Interaction, 
            project: str,
            task_id: int
        ):
            # Thread-Check
            if not await check_tracker_thread(interaction):
                return
            
            async for session in get_session():
                project_repo = ProjectRepository(session)
                task_repo = TaskRepository(session)
                
                # Prüfen, ob Projekt existiert
                project_obj = await project_repo.get_by_name(project)
                if not project_obj:
                    await interaction.response.send_message(f"Projekt '{project}' existiert nicht!", ephemeral=True)
                    return
                
                # Prüfen, ob Task existiert
                task = await task_repo.get_by_id(task_id)
                if not task or task.project_id != project_obj.id:
                    await interaction.response.send_message(f"Aufgabe mit ID {task_id} nicht gefunden!", ephemeral=True)
                    return
                
                # Task-Status umschalten
                is_completed = task.status == "completed"
                await task_repo.update_status(task_id, not is_completed)
                new_status = "offen" if is_completed else "erledigt"
            
            await interaction.response.send_message(f"Aufgabe als '{new_status}' markiert!", ephemeral=True)
            
            # Tracker aktualisieren
            await update_tracker_thread(bot, interaction.channel_id)
        
        @bot.slash_command(name="task_delete", description="Löscht eine Aufgabe")
        @admin_or_higher()
        async def delete_task(
            interaction: nextcord.Interaction, 
            project: str,
            task_id: int
        ):
            # Thread-Check
            if not await check_tracker_thread(interaction):
                return
            
            async for session in get_session():
                project_repo = ProjectRepository(session)
                task_repo = TaskRepository(session)
                
                # Prüfen, ob Projekt existiert
                project_obj = await project_repo.get_by_name(project)
                if not project_obj:
                    await interaction.response.send_message(f"Projekt '{project}' existiert nicht!", ephemeral=True)
                    return
                
                # Prüfen, ob Task existiert
                task = await task_repo.get_by_id(task_id)
                if not task or task.project_id != project_obj.id:
                    await interaction.response.send_message(f"Aufgabe mit ID {task_id} nicht gefunden!", ephemeral=True)
                    return
                
                # Task speichern für Rückmeldung
                task_title = task.title
                
                # Task löschen
                await task_repo.delete(task)
            
            await interaction.response.send_message(f"Aufgabe '{task_title}' gelöscht!", ephemeral=True)
            
            # Tracker aktualisieren
            await update_tracker_thread(bot, interaction.channel_id)

        async def update_tracker_thread(bot, channel_id):
            """Aktualisiert den Tracker-Thread mit den neuesten Daten"""
            try:
                # Holen des ursprünglichen Kanals (nicht des Threads)
                channel = bot.get_channel(int(channel_id))
                if not channel:
                    logger.error(f"Kanal mit ID {channel_id} nicht gefunden.")
                    return
                
                # Prüfen, ob der Kanal selbst ein Thread ist
                if isinstance(channel, nextcord.Thread):
                    # Wenn der Kanal bereits ein Thread ist und den richtigen Namen hat
                    if channel.name == "Projekt Tracker":
                        tracker_thread = channel
                    else:
                        logger.info(f"Kanal {channel_id} ist ein Thread, aber nicht der Projekt Tracker.")
                        return None
                else:
                    # Suche nach dem Thread im Hauptkanal
                    tracker_thread = None
                    for thread in channel.threads:
                        if thread.name == "Projekt Tracker":
                            tracker_thread = thread
                            break
                
                if tracker_thread:
                    # Daten aus Datenbank laden
                    tasks_data = await get_projects_data()
                    embed = create_task_embed(tasks_data)
                    
                    try:
                        await tracker_thread.purge(limit=100)
                        await tracker_thread.send(embed=embed)
                        logger.info("Projekt Tracker aktualisiert")
                        return tracker_thread
                    except Exception as e:
                        logger.error(f"Fehler beim Aktualisieren des Trackers: {e}")
                        return None
                else:
                    logger.info(f"Kein Projekt Tracker Thread in Kanal {channel_id} gefunden.")
                    return None
            except Exception as e:
                logger.error(f"Fehler in update_tracker_thread: {e}")
                return None

        logger.info("Project tracker commands initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize project tracker: {e}")
        raise