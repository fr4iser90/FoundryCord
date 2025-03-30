# Common Implementation Patterns

## 1. Repository Pattern

### 1.1 Basic Repository Structure
```python
class IRepository(ABC, Generic[T]):
    """Generic repository interface"""
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        pass

class SQLAlchemyRepository(IRepository[T]):
    """Base SQLAlchemy repository implementation"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, entity: T) -> T:
        entity_model = self._to_entity(entity)
        self._session.add(entity_model)
        await self._session.commit()
        return self._to_domain(entity_model)
```

### 1.2 Entity Mapping Pattern
```python
class UserRepositoryImpl(SQLAlchemyRepository[User]):
    def _to_entity(self, domain: User) -> AppUserEntity:
        """Map domain object to database entity"""
        return AppUserEntity(
            id=domain.id,
            username=domain.username,
            email=domain.email.value
        )
    
    def _to_domain(self, entity: AppUserEntity) -> User:
        """Map database entity to domain object"""
        return User(
            id=entity.id,
            username=entity.username,
            email=EmailAddress(entity.email)
        )
```

## 2. Factory Pattern

### 2.1 Entity Factory
```python
class UserFactory:
    @staticmethod
    def create_user(username: str, email: str) -> User:
        """Create a new user with validation"""
        if not username or not email:
            raise ValueError("Username and email are required")
        
        return User(
            id=str(uuid4()),
            username=username,
            email=EmailAddress(email)
        )
```

### 2.2 Repository Factory
```python
class RepositoryFactory:
    def __init__(self, session_factory: AsyncSessionFactory):
        self._session_factory = session_factory
    
    def create_user_repository(self) -> IUserRepository:
        return UserRepositoryImpl(self._session_factory())
```

## 3. Service Pattern

### 3.1 Domain Service
```python
class AuthenticationService:
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository
    
    async def authenticate(self, credentials: Credentials) -> Optional[User]:
        user = await self._user_repository.get_by_username(credentials.username)
        if not user or not user.verify_password(credentials.password):
            return None
        return user
```

### 3.2 Application Service
```python
class UserManagementService:
    def __init__(
        self,
        user_repository: IUserRepository,
        auth_service: AuthenticationService
    ):
        self._user_repository = user_repository
        self._auth_service = auth_service
    
    async def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        user = await self._auth_service.authenticate(
            Credentials(user_id, old_password)
        )
        if not user:
            return False
        
        user.set_password(new_password)
        await self._user_repository.save(user)
        return True
```

## 4. Event Pattern

### 4.1 Domain Events
```python
@dataclass
class DomainEvent:
    occurred_on: datetime = field(default_factory=datetime.utcnow)

@dataclass
class UserCreated(DomainEvent):
    user_id: str
    username: str

class User(AggregateRoot):
    def __init__(self, id: str, username: str):
        super().__init__()
        self._id = id
        self._username = username
        self.register_event(UserCreated(id, username))
```

### 4.2 Event Handlers
```python
class UserCreatedHandler:
    def __init__(self, notification_service: NotificationService):
        self._notification_service = notification_service
    
    async def handle(self, event: UserCreated) -> None:
        await self._notification_service.send_welcome_email(
            event.user_id,
            event.username
        )
```

## 5. Unit of Work Pattern

### 5.1 Basic Implementation
```python
class UnitOfWork:
    def __init__(self, session_factory: AsyncSessionFactory):
        self._session_factory = session_factory
    
    async def __aenter__(self):
        self.session = self._session_factory()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self.session.close()
    
    async def commit(self):
        await self.session.commit()
    
    async def rollback(self):
        await self.session.rollback()
```

### 5.2 Usage Example
```python
async def create_user(username: str, email: str):
    async with UnitOfWork(session_factory) as uow:
        user = UserFactory.create_user(username, email)
        user_repo = UserRepositoryImpl(uow.session)
        await user_repo.save(user)
        await uow.commit()
        return user
``` 