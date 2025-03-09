from typing import Dict
from infrastructure.logging import logger

class DashboardChannelConfig:
    @staticmethod
    def register(bot) -> Dict:
        return bot.factory.create_service(
            "Project Dashboard",
            lambda bot: ProjectDashboard(bot).start()
        )