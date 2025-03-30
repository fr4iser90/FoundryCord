# Coding Style Guidelines

## 1. General Python Guidelines

### 1.1 Imports
```python
# Standard library imports
from typing import Optional, List
from datetime import datetime

# Third-party imports
import discord
from sqlalchemy import Column, Integer

# Local imports
from app.shared.domain.models import User
from app.shared.infrastructure.database import Base
```

### 1.2 Type Hints
Always use type hints for function arguments and return values:
```python
def get_user(user_id: str) -> Optional[User]:
    """
    Retrieve a user by their ID.
    
    Args:
        user_id: The unique identifier of the user
        
    Returns:
        User object if found, None otherwise
    """
    return User.get(user_id)
```

## 2. Domain Layer Guidelines

### 2.1 Entity Design
```python
class User:
    def __init__(self, id: str, username: str):
        self._id = id  # Use underscore for "private" attributes
        self._username = username
        self._roles: List[Role] = []
    
    @property
    def username(self) -> str:
        return self._username
    
    def add_role(self, role: Role) -> None:
        if role in self._roles:
            raise DomainError("Role already assigned")
        self._roles.append(role)
```

### 2.2 Value Objects
```python
@dataclass(frozen=True)
class EmailAddress:
    value: str
    
    def __post_init__(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.value):
            raise ValueError("Invalid email format")
```

## 3. Infrastructure Layer Guidelines

### 3.1 Entity Models
```python
class UserEntity(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    
    def __repr__(self) -> str:
        return f"<UserEntity(id={self.id}, username='{self.username}')>"
```

### 3.2 Repository Implementation
```python
class UserRepositoryImpl(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session  # Use underscore for internal attributes
    
    async def get_by_id(self, id: str) -> Optional[User]:
        result = await self._session.get(UserEntity, id)
        return self._to_domain(result) if result else None
    
    def _to_domain(self, entity: UserEntity) -> User:  # Internal helper methods with underscore
        return User(
            id=str(entity.id),
            username=entity.username
        )
```

## 4. Error Handling

### 4.1 Custom Exceptions
```python
class DomainError(Exception):
    """Base exception for domain errors"""
    pass

class UserNotFoundError(DomainError):
    """Raised when a user cannot be found"""
    pass
```

### 4.2 Error Handling Pattern
```python
async def get_user(user_id: str) -> User:
    try:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user
    except DatabaseError as e:
        raise InfrastructureError(f"Database error: {str(e)}")
```

## 5. Testing Guidelines

### 5.1 Test Structure
```python
class TestUser(unittest.TestCase):
    def setUp(self):
        self.user = User("1", "test_user")
    
    def test_add_role(self):
        # Arrange
        role = Role("admin")
        
        # Act
        self.user.add_role(role)
        
        # Assert
        self.assertIn(role, self.user.roles)
```

### 5.2 Mock Usage
```python
@patch('app.shared.infrastructure.repositories.user_repository.AsyncSession')
async def test_get_user(self, mock_session):
    # Arrange
    mock_session.get.return_value = UserEntity(id=1, username="test")
    repository = UserRepositoryImpl(mock_session)
    
    # Act
    user = await repository.get_by_id("1")
    
    # Assert
    self.assertEqual(user.username, "test")
``` 