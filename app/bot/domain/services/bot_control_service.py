# app/bot/domain/services/bot_control_service.py
import asyncio
from typing import List, Optional, Dict
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class BotControlService:
    """Service for controlling bot operations and workflows"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_workflows = {}  # Track active workflows
        
    async def start_bot(self):
        """Start the bot and connect to Discord"""
        logger.info("Starting bot")
        # Start core bot functionality only
        await self.bot.login(self.bot.token)
        await self.bot.connect()
        
    async def stop_bot(self):
        """Stop the bot and disconnect from Discord"""
        logger.info("Stopping bot")
        await self.bot.close()
        
    async def restart_bot(self):
        """Restart the bot"""
        logger.info("Restarting bot")
        await self.stop_bot()
        await asyncio.sleep(2)  # Brief pause
        await self.start_bot()
        
    async def enable_workflow(self, workflow_name: str):
        """Enable a specific workflow"""
        logger.info(f"Enabling workflow: {workflow_name}")
        if not self.bot.workflow_manager:
            logger.error("Workflow manager not available")
            return False
            
        workflow = self.bot.workflow_manager.get_workflow(workflow_name)
        if not workflow:
            logger.error(f"Workflow not found: {workflow_name}")
            return False
            
        if workflow_name in self.active_workflows:
            logger.warning(f"Workflow already active: {workflow_name}")
            return True
            
        try:
            success = await workflow.initialize()
            if success:
                self.active_workflows[workflow_name] = workflow
                logger.info(f"Workflow enabled: {workflow_name}")
                return True
            logger.error(f"Failed to initialize workflow: {workflow_name}")
            return False
        except Exception as e:
            logger.error(f"Error enabling workflow {workflow_name}: {e}")
            return False
            
    async def disable_workflow(self, workflow_name: str):
        """Disable a specific workflow"""
        logger.info(f"Disabling workflow: {workflow_name}")
        if not self.bot.workflow_manager:
            logger.error("Workflow manager not available")
            return False
            
        if workflow_name not in self.active_workflows:
            logger.warning(f"Workflow not active: {workflow_name}")
            return True
            
        workflow = self.active_workflows[workflow_name]
        try:
            await workflow.cleanup()
            del self.active_workflows[workflow_name]
            logger.info(f"Workflow disabled: {workflow_name}")
            return True
        except Exception as e:
            logger.error(f"Error disabling workflow {workflow_name}: {e}")
            return False
            
    def get_status(self) -> Dict:
        """Get current bot status"""
        status = {
            "connected": self.bot.is_ready(),
            "active_workflows": list(self.active_workflows.keys()),
            "available_workflows": [w.name for w in self.bot.workflow_manager.workflows],
            "uptime": self.bot.uptime if hasattr(self.bot, "uptime") else None,
        }
        return status