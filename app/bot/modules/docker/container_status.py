import docker
import os
from nextcord.ext import commands

bot = commands.Bot(command_prefix='!')

def setup(bot):
    @bot.command()
    async def container_status(ctx, container_name: str = None):
        import requests
        try:
            response = requests.get('http://127.0.0.1:5000/containers', headers={'Authorization': os.getenv('AUTH_TOKEN')})
            response.raise_for_status()
            containers = response.json()
            if container_name:
                filtered_containers = [container for container in containers if container['name'] == container_name]
                if filtered_containers:
                    container_list = '\n'.join([f"{container['name']}: Status unknown, but details: {container}" for container in filtered_containers])
                    await ctx.send(f'Container Details for {container_name}:\n{container_list}')
                else:
                    await ctx.send(f'No container found with name: {container_name}')
            else:
                container_list = '\n'.join([f"{container['name']}: Status unknown, but details: {container}" for container in containers])
                await ctx.send(f'Container Details:\n{container_list}')
        except requests.RequestException as e:
            await ctx.send(f'Error retrieving container information: {str(e)}')

    @bot.command()
    async def container_list(ctx):
        import requests
        try:
            response = requests.get('http://127.0.0.1:5000/containers', headers={'Authorization': os.getenv('AUTH_TOKEN')})
            response.raise_for_status()
            containers = response.json()
            container_names = [container['name'] for container in containers]
            await ctx.send(f'Container List:\n{", ".join(container_names)}')
        except requests.RequestException as e:
            await ctx.send(f'Error retrieving container list: {str(e)}')
