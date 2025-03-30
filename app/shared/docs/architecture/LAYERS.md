# Detailed Layer Documentation

## 1. Domain Layer (`app/shared/domain/`)

### Purpose
Core business logic and rules, independent of external concerns.

### Key Components

#### 1.1 Entities
```python
# app/shared/domain/discord/entities/channel.py
class Channel:
    def __init__(self, id: str, name: str, type: ChannelType):
        self.id = id
        self.name = name
        self.type = type
        
    def rename(self, new_name: str) -> None:
        if not new_name.strip():
            raise ValueError("Channel name cannot be empty")
        self.name = new_name
```

#### 1.2 Value Objects
```python
# app/shared/domain/discord/value_objects/channel_id.py
@dataclass(frozen=True)
class ChannelId:
    value: str
    
    def __post_init__(self):
        if not self.value.isdigit():
            raise ValueError("Channel ID must be numeric")
```

#### 1.3 Domain Services
```python
# app/shared/domain/discord/services/channel_service.py
class ChannelService:
    def validate_channel_hierarchy(self, channel: Channel, parent: Category) -> bool:
        return channel.type in parent.allowed_channel_types
```

## 2. Application Layer (`app/shared/application/`)

### Purpose
Orchestrates domain objects to perform use cases.

### Key Components

#### 2.1 Use Cases
```python
# app/shared/application/use_cases/create_channel.py
class CreateChannelUseCase:
    def __init__(self, channel_repository: IChannelRepository):
        self.channel_repository = channel_repository
    
    async def execute(self, name: str, type: ChannelType) -> Channel:
        channel = Channel(generate_id(), name, type)
        await self.channel_repository.save(channel)
        return channel
```

#### 2.2 Application Services
```python
# app/shared/application/services/discord_management.py
class DiscordManagementService:
    def __init__(self, channel_use_case: CreateChannelUseCase):
        self.channel_use_case = channel_use_case
    
    async def setup_guild_channels(self, guild_config: GuildConfig):
        for channel_config in guild_config.channels:
            await self.channel_use_case.execute(
                channel_config.name,
                channel_config.type
            )
```

## 3. Infrastructure Layer (`app/shared/infrastructure/`)

### Purpose
Implements technical details and external integrations.

### Key Components

#### 3.1 Repository Implementations
```python
# app/shared/infrastructure/repositories/channel_repository_impl.py
class ChannelRepositoryImpl(IChannelRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, channel: Channel) -> None:
        channel_entity = self._to_entity(channel)
        self.session.add(channel_entity)
        await self.session.commit()
```

#### 3.2 External Service Adapters
```python
# app/shared/infrastructure/adapters/discord_api_adapter.py
class DiscordApiAdapter:
    def __init__(self, client: discord.Client):
        self.client = client
    
    async def create_channel(self, channel: Channel) -> None:
        await self.client.create_channel(
            name=channel.name,
            type=self._to_discord_type(channel.type)
        )
```

## 4. Interface Layer (`app/shared/interface/`)

### Purpose
Handles external communication and user interface.

### Key Components

#### 4.1 Controllers
```python
# app/shared/interface/controllers/channel_controller.py
class ChannelController:
    def __init__(self, create_channel_use_case: CreateChannelUseCase):
        self.create_channel_use_case = create_channel_use_case
    
    async def create_channel(self, request: CreateChannelRequest):
        channel = await self.create_channel_use_case.execute(
            request.name,
            request.type
        )
        return ChannelResponse.from_domain(channel)
```

#### 4.2 DTOs/Response Models
```python
# app/shared/interface/models/channel_response.py
@dataclass
class ChannelResponse:
    id: str
    name: str
    type: str
    
    @classmethod
    def from_domain(cls, channel: Channel) -> 'ChannelResponse':
        return cls(
            id=channel.id,
            name=channel.name,
            type=channel.type.value
        )
``` 