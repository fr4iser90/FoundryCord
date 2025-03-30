from fastapi import APIRouter
from pydantic import BaseModel
import psutil

router = APIRouter(prefix="/v1/health", tags=["System Health"])

class HealthStatus(BaseModel):
    status: str
    version: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float

class HealthController:
    """Controller für System-Gesundheitszustand"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diesen Controller"""
        self.router.get("/status")(self.get_health_status)
        self.router.get("/ping")(self.ping)
    
    async def get_health_status(self):
        """Get system health status including CPU, memory and disk usage"""
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        health_status = HealthStatus(
            status="healthy" if all(x < 90 for x in [cpu, memory, disk]) else "warning",
            version="1.0.0",  # Hier die tatsächliche Version der Anwendung einfügen
            cpu_percent=cpu,
            memory_percent=memory,
            disk_percent=disk
        )
        
        return health_status
    
    async def ping(self):
        """Simple ping endpoint for checking if the API is responsive"""
        return {"status": "ok", "message": "pong"}

# Für API-Kompatibilität
health_controller = HealthController()
get_health_status = health_controller.get_health_status
ping = health_controller.ping 