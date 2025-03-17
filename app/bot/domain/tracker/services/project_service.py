from app.shared.infrastructure.database.management.connection import get_session

from app.shared.infrastructure.database.repositories.project_repository_impl import ProjectRepository
from app.shared.infrastructure.database.repositories.task_repository import TaskRepository
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

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
