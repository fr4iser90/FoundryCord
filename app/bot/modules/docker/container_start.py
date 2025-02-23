import docker
from nextcord.ext import commands

def setup(bot):
    @bot.command()
    async def start_container(ctx, container_name: str):
        client = docker.from_env()
        try:
            container = client.containers.get(container_name)
            container.start()
            await ctx.send(f'Container {container_name} gestartet.')
        except docker.errors.NotFound:
            await ctx.send(f'Container {container_name} nicht gefunden.')
