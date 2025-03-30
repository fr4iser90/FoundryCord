# Configuration Documentation

## 1. Configuration Structure

### 1.1 Base Configuration
```python
@dataclass
class BaseConfig:
    """Base configuration class"""
    environment: str
    debug: bool
    log_level: str
    
    @classmethod
    def from_env(cls) -> 'BaseConfig':
        return cls(
            environment=os.getenv('ENVIRONMENT', 'development'),
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )
```

### 1.2 Feature Configuration
```python
@dataclass
class FeatureFlags:
    """Feature flag configuration"""
    enable_dashboard: bool = True
    enable_monitoring: bool = True
    enable_auto_moderation: bool = False
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FeatureFlags':
        return cls(**{
            k: v for k, v in data.items()
            if k in inspect.signature(cls).parameters
        })
```

## 2. Configuration Sources

### 2.1 Environment Variables
```python
class EnvironmentConfig:
    """Load configuration from environment variables"""
    
    @staticmethod
    def load() -> Dict[str, Any]:
        return {
            'database_url': os.getenv('DATABASE_URL'),
            'redis_url': os.getenv('REDIS_URL'),
            'discord_token': os.getenv('DISCORD_TOKEN'),
            'secret_key': os.getenv('SECRET_KEY')
        }
```

### 2.2 Configuration Files
```yaml
# config/development.yaml
database:
  pool_size: 20
  max_overflow: 10
  pool_timeout: 30

redis:
  max_connections: 10
  socket_timeout: 5

discord:
  command_prefix: "!"
  description: "Development Bot"
```

## 3. Configuration Management

### 3.1 Configuration Service
```python
class ConfigurationService:
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._watchers: List[Callable] = []
    
    async def load(self):
        """Load configuration from all sources"""
        env_config = EnvironmentConfig.load()
        file_config = await self._load_config_files()
        self._config = self._merge_configs(env_config, file_config)
        await self._notify_watchers()
    
    def watch(self, callback: Callable):
        """Register configuration change callback"""
        self._watchers.append(callback)
```

### 3.2 Dynamic Configuration
```python
class DynamicConfig:
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def get(self, key: str) -> Any:
        """Get configuration value with TTL cache"""
        cached = await self.redis.get(f"config:{key}")
        if cached:
            return json.loads(cached)
        
        value = await self._fetch_from_db(key)
        await self.redis.setex(f"config:{key}", 300, json.dumps(value))
        return value
```

## 4. Environment-Specific Configuration

### 4.1 Development
```python
class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""
    
    def __init__(self):
        super().__init__(
            environment='development',
            debug=True,
            log_level='DEBUG'
        )
        self.enable_hot_reload = True
        self.mock_external_services = True
```

### 4.2 Production
```python
class ProductionConfig(BaseConfig):
    """Production environment configuration"""
    
    def __init__(self):
        super().__init__(
            environment='production',
            debug=False,
            log_level='INFO'
        )
        self.enable_hot_reload = False
        self.mock_external_services = False
```

## 5. Validation

### 5.1 Configuration Validation
```python
class ConfigurationValidator:
    @staticmethod
    def validate(config: Dict[str, Any]) -> List[str]:
        """Validate configuration values"""
        errors = []
        
        required_keys = ['database_url', 'discord_token', 'secret_key']
        for key in required_keys:
            if not config.get(key):
                errors.append(f"Missing required config: {key}")
        
        return errors
```

### 5.2 Type Validation
```python
@dataclass
class DatabaseConfig:
    url: str
    pool_size: int
    max_overflow: int
    
    @validator('pool_size')
    def validate_pool_size(cls, v):
        if not 5 <= v <= 100:
            raise ValueError('Pool size must be between 5 and 100')
        return v
``` 