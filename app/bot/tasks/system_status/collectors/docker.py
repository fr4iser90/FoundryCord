import docker
import subprocess
import logging

logger = logging.getLogger('homelab_bot')

async def get_docker_status():
    """Holt Docker-Container Status mit tatsächlichen Daten oder Fallback."""
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        
        running = 0
        errors = 0
        details = ""
        
        for container in containers:
            name = container.name
            status = container.status
            
            if status == "running":
                running += 1
                details += f"{name}: ✅ Running\n"
            elif status in ["exited", "dead", "created"]:
                errors += 1
                details += f"{name}: ❌ {status.capitalize()}\n"
            else:
                details += f"{name}: ⚠️ {status.capitalize()}\n"
        
        return running, errors, details
    except Exception as docker_api_error:
        logger.warning(f"Docker API nicht verfügbar: {docker_api_error}")
        
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.Names}}: {{.Status}}"],
                capture_output=True, text=True, check=True
            )
            
            lines = result.stdout.strip().split('\n')
            running = sum(1 for line in lines if "Up " in line)
            errors = sum(1 for line in lines if "Exited" in line)
            
            return running, errors, result.stdout
        except Exception as cmd_error:
            logger.error(f"Docker Kommandozeile nicht verfügbar: {cmd_error}")
            return "N/A", "N/A", "Docker nicht verfügbar"