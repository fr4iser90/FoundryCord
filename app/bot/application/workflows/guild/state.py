import logging
from app.bot.application.workflows.base_workflow import WorkflowStatus
from app.shared.interfaces.logging.api import get_bot_logger

logger = get_bot_logger()

def get_guild_status(self, guild_id: str) -> WorkflowStatus:
    """Get the current status of the workflow for a specific guild"""
    return self._guild_statuses.get(guild_id, WorkflowStatus.PENDING)
    
async def disable_for_guild(self, guild_id: str) -> None:
    """Disable workflow for a specific guild"""
    logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Disabling workflow...")
    self._guild_statuses[guild_id] = WorkflowStatus.DISABLED
    
    # Update status in DB? Maybe not needed, depends on use case.
    # async with session_context() as session:
    #     guild_repo = GuildRepositoryImpl(session)
    #     await guild_repo.update_access_status(guild_id, SOME_DISABLED_STATUS) # Need a DB status for disabled?
            
async def cleanup_guild(self, guild_id: str) -> None:
    """Cleanup resources for a specific guild"""
    logger.info(f"[GuildWorkflow] [Guild:{guild_id}] Cleaning up guild-specific state...")
    if guild_id in self._guild_statuses:
        del self._guild_statuses[guild_id]
    if guild_id in self._guild_access_statuses:
        del self._guild_access_statuses[guild_id]
        
async def cleanup(self) -> None:
    """Global cleanup"""
    logger.info("[GuildWorkflow] Cleaning up global state...")
    self._guild_statuses.clear()
    self._guild_access_statuses.clear() 