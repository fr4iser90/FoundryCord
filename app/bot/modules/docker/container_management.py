import nextcord
from nextcord.ext import commands
from modules.docker.container_start import setup as setup_container_start
from modules.docker.container_stop import setup as setup_container_stop
from modules.docker.container_status import setup as setup_container_status
from modules.docker.container_edit import setup as setup_container_edit
import threading
from modules.docker.container_management_api import run_flask

def setup(bot):
    # Registrieren der Setup-Funktionen
    setup_container_start(bot)
    setup_container_stop(bot)
    setup_container_status(bot)
    setup_container_edit(bot)

    # Flask-Server in einem eigenen Thread starten
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()