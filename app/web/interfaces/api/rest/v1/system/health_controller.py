from fastapi import Depends
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from pydantic import BaseModel
import psutil
from fastapi import HTTPException

class HealthStatus(BaseModel):
    status: str
    version: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float

class HealthController(BaseController):
    """Controller for system health status"""
    
    def __init__(self):
        super().__init__(prefix="/system", tags=["System Status"])
        self._register_routes()
    
    def _register_routes(self):
        """Register all health routes"""
        self.router.get("/status", response_model=HealthStatus)(self.get_system_status)
        self.router.get("/ping")(self.ping)
    
    async def get_system_status(self, current_user: AppUserEntity = Depends(get_current_user)) -> HealthStatus:
        """Get system health status including CPU, memory and disk usage"""
        try:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            health_status = HealthStatus(
                status="healthy" if all(x < 90 for x in [cpu, memory, disk]) else "warning",
                version="1.0.0",  # TODO: Get from config
                cpu_percent=cpu,
                memory_percent=memory,
                disk_percent=disk
            )
            
            return health_status
        except Exception as e:
            self.logger.error(f"Error fetching system status: {e}", exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to retrieve system status")
    
    async def ping(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Simple ping endpoint for checking if the API is responsive"""
        try:
            return {"status": "ok", "message": "pong"}
        except Exception as e:
            return self.handle_exception(e)

# Controller instance
health_controller = HealthController()

# Remove old function exports if they existed
# get_health_status = health_controller.get_health_status
# ping = health_controller.ping 