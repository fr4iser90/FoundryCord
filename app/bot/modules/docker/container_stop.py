import docker
from nextcord.ext import commands

def setup(bot):
    @bot.command()
    async def stop_container(ctx, container_name: str):
        client = docker.from_env()
        try:
            container = client.containers.get(container_name)
            container.stop()
            await ctx.send(f'Container {container_name} gestoppt.')
        except docker.errors.NotFound:
            await ctx.send(f'Container {container_name} nicht gefunden.')
