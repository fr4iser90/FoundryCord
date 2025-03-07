# modules/tracker/project_tracker.py
import json
import os
import nextcord
from datetime import datetime
from utils.decorators.auth import admin_or_higher
from infrastructure.logging import logger

# Pfad zur JSON-Datei für die Aufgaben
TASKS_FILE = "data/project_tasks.json"

# Sicherstellen, dass der Ordner existiert
os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)

# Hilfsfunktionen
def load_tasks():
    """Lädt die Aufgaben aus der JSON-Datei"""
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Aufgaben: {e}")
            return {"projects": {}}
    else:
        return {"projects": {}}

def save_tasks(tasks):
    """Speichert die Aufgaben in der JSON-Datei"""
    try:
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Aufgaben: {e}")
        return False

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
            
            tasks_data = load_tasks()
            
            if name in tasks_data["projects"]:
                await interaction.response.send_message(f"Projekt '{name}' existiert bereits!", ephemeral=True)
                return
            
            tasks_data["projects"][name] = {
                "created_at": datetime.now().isoformat(),
                "created_by": str(interaction.user.id),
                "tasks": []
            }
            
            if save_tasks(tasks_data):
                await interaction.response.send_message(f"Projekt '{name}' erfolgreich erstellt!", ephemeral=True)
                
                # Tracker aktualisieren
                await update_tracker_thread(bot, interaction.channel_id)
            else:
                await interaction.response.send_message("Fehler beim Speichern des Projekts.", ephemeral=True)
        
        @bot.slash_command(name="project_delete", description="Löscht ein Projekt")
        @admin_or_higher()
        async def delete_project(interaction: nextcord.Interaction, name: str):
            # Thread-Check
            if not await check_tracker_thread(interaction):
                return
            
            tasks_data = load_tasks()
            
            if name not in tasks_data["projects"]:
                await interaction.response.send_message(f"Projekt '{name}' existiert nicht!", ephemeral=True)
                return
            
            del tasks_data["projects"][name]
            
            if save_tasks(tasks_data):
                await interaction.response.send_message(f"Projekt '{name}' erfolgreich gelöscht!", ephemeral=True)
                
                # Tracker aktualisieren
                await update_tracker_thread(bot, interaction.channel_id)
            else:
                await interaction.response.send_message("Fehler beim Löschen des Projekts.", ephemeral=True)
        
        @bot.slash_command(name="project_list", description="Zeigt alle Projekte an")
        @admin_or_higher()
        async def list_projects(interaction: nextcord.Interaction):
            tasks_data = load_tasks()
            
            if not tasks_data["projects"]:
                await interaction.response.send_message("Keine Projekte vorhanden.", ephemeral=True)
                return
            
            projects_list = "\n".join([f"📋 **{name}** ({len(project['tasks'])} Aufgaben)" 
                                      for name, project in tasks_data["projects"].items()])
            
            embed = nextcord.Embed(
                title="Projekte",
                description=projects_list,
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
            tasks_data = load_tasks()
            
            if project not in tasks_data["projects"]:
                await interaction.response.send_message(f"Projekt '{project}' existiert nicht!", ephemeral=True)
                return
            
            new_task = {
                "id": len(tasks_data["projects"][project]["tasks"]) + 1,
                "title": title,
                "description": description or "",
                "priority": priority,
                "completed": False,
                "created_at": datetime.now().isoformat(),
                "created_by": str(interaction.user.id)
            }
            
            tasks_data["projects"][project]["tasks"].append(new_task)
            
            if save_tasks(tasks_data):
                await interaction.response.send_message(f"Aufgabe '{title}' zu Projekt '{project}' hinzugefügt!", ephemeral=True)
                
                # Tracker aktualisieren
                await update_tracker_thread(bot, interaction.channel_id)
            else:
                await interaction.response.send_message("Fehler beim Speichern der Aufgabe.", ephemeral=True)
        
        @bot.slash_command(name="task_complete", description="Markiert eine Aufgabe als erledigt")
        @admin_or_higher()
        async def complete_task(
            interaction: nextcord.Interaction, 
            project: str,
            task_id: int
        ):
            tasks_data = load_tasks()
            
            if project not in tasks_data["projects"]:
                await interaction.response.send_message(f"Projekt '{project}' existiert nicht!", ephemeral=True)
                return
            
            task_found = False
            for task in tasks_data["projects"][project]["tasks"]:
                if task["id"] == task_id:
                    task["completed"] = not task["completed"]
                    status = "erledigt" if task["completed"] else "offen"
                    task_found = True
                    break
            
            if not task_found:
                await interaction.response.send_message(f"Aufgabe mit ID {task_id} nicht gefunden!", ephemeral=True)
                return
            
            if save_tasks(tasks_data):
                await interaction.response.send_message(f"Aufgabe als '{status}' markiert!", ephemeral=True)
                
                # Tracker aktualisieren
                await update_tracker_thread(bot, interaction.channel_id)
            else:
                await interaction.response.send_message("Fehler beim Aktualisieren der Aufgabe.", ephemeral=True)
        
        @bot.slash_command(name="task_delete", description="Löscht eine Aufgabe")
        @admin_or_higher()
        async def delete_task(
            interaction: nextcord.Interaction, 
            project: str,
            task_id: int
        ):
            tasks_data = load_tasks()
            
            if project not in tasks_data["projects"]:
                await interaction.response.send_message(f"Projekt '{project}' existiert nicht!", ephemeral=True)
                return
            
            tasks = tasks_data["projects"][project]["tasks"]
            task_index = next((i for i, task in enumerate(tasks) if task["id"] == task_id), None)
            
            if task_index is None:
                await interaction.response.send_message(f"Aufgabe mit ID {task_id} nicht gefunden!", ephemeral=True)
                return
            
            deleted_task = tasks.pop(task_index)
            
            if save_tasks(tasks_data):
                await interaction.response.send_message(f"Aufgabe '{deleted_task['title']}' gelöscht!", ephemeral=True)
                
                # Tracker aktualisieren
                await update_tracker_thread(bot, interaction.channel_id)
            else:
                await interaction.response.send_message("Fehler beim Löschen der Aufgabe.", ephemeral=True)

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
                    tasks_data = load_tasks()
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