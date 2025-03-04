# @/app/bot/core/startup.py
import os
import nextcord
from core.utilities.logger import logger 
from tasks.system_status import system_status_task
from tasks.cleanup_task import cleanup_task
from tasks.cleanup_dm_task import cleanup_dm_task  
from tasks.project_tracker_task import project_tracker_task

# Liste von Startup-Aufgaben
startup_tasks = []

def add_startup_task(task_func):
    """Fügt eine Aufgabe zur Startup-Liste hinzu."""
    if task_func not in startup_tasks:
        startup_tasks.append(task_func)

async def setup_tasks(bot, channel_id):
    """Legacy task setup - kann später entfernt werden"""
    logger.warning("Using deprecated setup_tasks function. Please use BotStartup instead.")

add_startup_task(system_status_task)
add_startup_task(cleanup_task)
add_startup_task(cleanup_dm_task)
add_startup_task(project_tracker_task)