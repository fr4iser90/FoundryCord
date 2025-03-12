# Web Interface Initial Implementation Guide (Authentication & Server Setup)

## Overview
This document outlines the initial phase of implementing the web interface, focusing specifically on setting up the server infrastructure and Discord authentication system. This foundation will serve as the base for the full dashboard implementation.

## Technology Stack

### Core Technologies
- **Backend Framework**: FastAPI
- **Template Engine**: Jinja2
- **Database**: PostgreSQL
- **Authentication**: Discord OAuth2 + JWT
- **Session Management**: Redis
- **CSS Framework**: TailwindCSS
- **Testing**: pytest

### Development Tools
- **IDE**: VSCode(Cursor) with Python and FastAPI extensions
- **API Testing**: Postman/Insomnia
- **Database Management**: DBeaver/pgAdmin
- **Version Control**: Git
- **Documentation**: MkDocs

## Initial Components

1. **Base Server Setup**
   - FastAPI application structure
   - Environment configuration
   - Middleware setup (CORS, session, etc.)
   - Error handling
   - Logging system

2. **Authentication System**
   - Discord OAuth2 flow
   - JWT token management
   - Session handling
   - User state persistence

3. **Basic Frontend**
   - Login page
   - User profile page
   - Basic navigation structure
   - Error pages (404, 500, etc.)

## Implementation Structure

```plaintext
app/
├── bot/
│   └── interfaces/
│       └── web/
│           ├── server.py
│           ├── config.py
│           ├── routes/
│           │   ├── __init__.py
│           │   ├── auth.py
│           │   └── user.py
│           ├── services/
│           │   ├── __init__.py
│           │   ├── auth_service.py
│           │   └── user_service.py
│           ├── models/
│           │   ├── __init__.py
│           │   └── user.py
│           └── templates/
│               ├── base.html
│               ├── login.html
│               └── profile.html
```

## Database Schema (Initial)

```sql
CREATE TABLE users (
    id VARCHAR(20) PRIMARY KEY,  -- Discord User ID
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    avatar_url TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    user_id VARCHAR(20) REFERENCES users(id),
    jwt_token TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL
);
```

## Implementation Steps

### Phase 1: Server Setup
1. Initialize FastAPI application
2. Configure environment variables
3. Set up database connections
4. Implement basic middleware
5. Create logging system

### Phase 2: Authentication
1. Configure Discord OAuth2
2. Implement login/logout flow
3. Create JWT service
4. Set up session management
5. Add user persistence

### Phase 3: Basic UI
1. Create base templates
2. Implement login page
3. Add user profile page
4. Style with TailwindCSS
5. Add basic error handling

## Role Definitions

### Bot Framework Developer
- Implements core server infrastructure
- Sets up FastAPI application structure
- Manages database connections
- Implements middleware and error handling
- Creates service layer abstractions

### Authentication Specialist
- Implements Discord OAuth2 flow
- Manages JWT token system
- Handles session management
- Implements user persistence
- Ensures secure authentication flow

### UI/UX Developer
- Creates responsive templates
- Implements TailwindCSS styling
- Ensures consistent UI components
- Handles frontend error states
- Creates loading states and transitions

## Security Considerations
1. Implement rate limiting
2. Set secure cookie policies
3. Configure CORS properly
4. Sanitize user inputs
5. Implement proper error handling
6. Set up SSL/TLS
7. Store secrets securely

## Testing Strategy

### Unit Tests
```python
# tests/interfaces/web/test_auth_service.py
import pytest
from app.bot.interfaces.web.services.auth_service import AuthService

class TestAuthService:
    @pytest.fixture
    def auth_service(self):
        # Setup test service
        pass

    async def test_discord_oauth_url_generation(self, auth_service):
        url = await auth_service.get_oauth_url()
        assert "discord.com/api/oauth2/authorize" in url
        assert "client_id=" in url

    async def test_token_exchange(self, auth_service):
        # Test token exchange flow
        pass

    async def test_jwt_generation(self, auth_service):
        # Test JWT token creation
        pass
```

### Integration Tests
```python
# tests/interfaces/web/test_auth_routes.py
from fastapi.testclient import TestClient

class TestAuthRoutes:
    async def test_login_redirect(self, client: TestClient):
        response = await client.get("/auth/login")
        assert response.status_code == 302
        assert "discord.com" in response.headers["location"]

    async def test_oauth_callback(self, client: TestClient):
        # Test OAuth callback handling
        pass
```

## Monitoring and Logging
- Implement structured logging
- Set up performance monitoring
- Track authentication metrics
- Monitor error rates
- Log security events

## Next Steps
1. Implement server infrastructure
2. Set up authentication system
3. Create basic UI templates
4. Add test coverage
5. Document API endpoints
6. Set up monitoring
7. Plan dashboard implementation

## Additional Notes
- Keep the initial implementation focused on authentication
- Use async/await consistently
- Follow REST best practices
- Document all security decisions
- Maintain test coverage
- Plan for scalability 