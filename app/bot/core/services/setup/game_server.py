async def setup_minecraft_channels(channel_setup, server_id: str, server_name: str):
    channel_setup.register_gameserver_channels(
        server_id,
        {
            'name': f'mc-{server_name}',
            'topic': f'Minecraft Server {server_name} Status',
            'is_private': False,
            'threads': [
                {'name': 'status', 'is_private': False},
                {'name': 'player-logs', 'is_private': True},
                {'name': 'backups', 'is_private': True}
            ]
        }
    )


    async def setup_hook(self):
    # Core Channel Setup
    self.channel_setup = ChannelSetupService(self)
    
    # Gameserver registrieren ihre Channels
    for server in self.gameservers:
        if server.type == 'minecraft':
            await setup_minecraft_channels(
                self.channel_setup, 
                server.id, 
                server.name
            )
    
    # Führe Setup aus
    await self.channel_setup.setup()