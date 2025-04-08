from app.web.interfaces.web import routers as web_routers
from app.web.interfaces.api import routers as api_routers

# Combine all routers for easy use
routers = web_routers + api_routers
