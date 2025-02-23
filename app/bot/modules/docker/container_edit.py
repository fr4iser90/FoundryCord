import docker
from nextcord.ext import commands

def setup(bot):
    @bot.command()
    async def edit_container(ctx, container_name: str, env_variable: str, new_value: str):
        client = docker.from_env()
        try:
            container = client.containers.get(container_name)
            # Setze die neuen Umgebungsvariablen oder bearbeite die Container-Konfiguration
            container.update(environment={env_variable: new_value})
            await ctx.send(f'Container {container_name} aktualisiert mit {env_variable}={new_value}.')
        except docker.errors.NotFound:
            await ctx.send(f'Container {container_name} nicht gefunden.')
