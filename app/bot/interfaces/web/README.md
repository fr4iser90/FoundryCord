# HomeLab Discord Bot Web Interface

This is the web interface for the HomeLab Discord Bot, providing a dashboard for managing the bot and homelab resources.

## Features

- Discord OAuth2 authentication
- Dashboard management
- System monitoring visualization
- User settings and preferences
- Responsive design with TailwindCSS

## Development Setup

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis
- Discord API credentials

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Discord OAuth
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_REDIRECT_URI=http://localhost:8000/auth/callback
DISCORD_BOT_TOKEN=your_discord_bot_token

# JWT
JWT_SECRET_KEY=generate_a_secure_random_key

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/homelab

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=optional_redis_password

# Application
DEBUG=true
ENVIRONMENT=development
```

### Local Development

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```
   alembic upgrade head
   ```

4. Start the development server:
   ```
   uvicorn interfaces.web.server:app --reload
   ```

5. Access the web interface at http://localhost:8000

### Using Docker Compose

1. Start the services:
   ```
   docker-compose -f docker-compose.web.yml up -d
   ```

2. Access the web interface at http://localhost:8000

## Production Deployment

For production deployment, consider the following:

1. Set `DEBUG=false` and `ENVIRONMENT=production`
2. Use a proper web server like Nginx as a reverse proxy
3. Configure HTTPS with Let's Encrypt or other SSL provider
4. Set up proper database backup and monitoring
5. Use the GitHub Actions workflow for automated CI/CD

### Security Best Practices

- Regularly rotate the JWT secret key
- Enable rate limiting for authentication endpoints
- Store all secrets securely using environment variables
- Implement proper CORS policy
- Use HTTP Secure cookies
- Validate all user inputs

## Testing

Run the test suite with:

```
pytest app/bot/interfaces/web/tests/ --cov=app/bot/interfaces/web
```

## Continuous Integration

The project uses GitHub Actions for CI/CD. The workflow includes:

1. Running tests
2. Building a Docker image
3. Publishing the image to GitHub Container Registry
4. Deploying to the development environment

## Contributing

When contributing to this project:

1. Follow the same code style and patterns
2. Write tests for new features
3. Update documentation as needed
4. Include clear commit messages 