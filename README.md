# Homelab Assistant Discord Bot (Python-based)
## ⚠️ Experimental Project – JUST A HOBBY ⚠️

A Docker-based Discord bot written in Python, designed to manage and monitor your homelab. It includes features for getting domain and IP, IP whitelisting, container management, system monitoring, user authentication, and security enhancements.

## Features

- **IP Whitelisting**
  - Generates unique URLs for users to register their IPs
  - Stores IP addresses with Discord user IDs and timestamps
  - Automatically updates Traefik whitelist
  - Supports both direct URL tracking and Discord OAuth methods

- **Container Management**
  - View container status and logs
  - Restart/stop containers (admin only)
  - Monitor resource usage

- **System Monitoring**
  - Real-time system status updates
  - Customizable alerts for critical events
  - Resource usage tracking

- **Security**
  - Role-based access control with hierarchical permissions
  - Two-factor authentication via Discord
  - IP validation and rate limiting
  - Secure session management with token rotation
  - Encrypted storage of sensitive data
  - Regular security audits and vulnerability scanning

## Requirements

- Docker
- Docker Compose
- Discord Bot Token
- Python 3.8+ (Ensure you have the latest version for optimal performance)

## Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/homelab-bot.git
   cd homelab-bot
   ```

2. **Set Up Environment Variables:**
   - Navigate to the compose directory and create both environment files by copying the examples:
     ```bash
     cd compose
     cp env.discordbot.example .env.discordbot
     cp .env.postgres.example .env.postgres
     ```
   - Edit the `.env.discordbot` file with your specific configuration:
     ```env
     DISCORD_TOKEN=your_discord_bot_token
     DOMAIN=your.domain.com
     AES_KEY=your_aes_key
     TYPE=Web,Game,File
     AUTH_TOKEN=your_auth_token
     DISCORD_SERVER=your_server_id
     DISCORD_HOMELAB_CHANNEL=your_channel_id
     TRACKER_URL=http://localhost:8081
     SUPER_ADMINS=NAME|ID
     ADMINS=NAME|ID
     USERS=NAME|ID,NAME|ID,NAME|ID
     ENCRYPTION_KEY=your_encryption_key
     JWT_SECRET_KEY=your_jwt_secret
     SESSION_DURATION_HOURS=24
     RATE_LIMIT_WINDOW=60
     RATE_LIMIT_MAX_ATTEMPTS=5
     PUID=1001
     PGID=987
     ```
   - Edit the `.env.postgres` file with your database configuration:
     ```env
     POSTGRES_USER=postgres
     POSTGRES_PASSWORD=secure_password
     POSTGRES_DB=homelab
     APP_DB_USER=app_user
     APP_DB_PASSWORD=app_password
     POSTGRES_HOST=postgres
     POSTGRES_PORT=5432
     ```

3. **Build and Start the Containers:**
   ```bash
   docker compose -f compose/docker-compose.yml up -d --build
   ```

## Project Structure

<details>
<summary>Click to expand</summary>

```plaintext
├── app/                    # Main application directory
│   ├── bot/               # Discord bot implementation
│   ├── postgres/          # Database related files
│   ├── tracker/           # IP tracking service
│   └── web/              # Web interface components
├── compose/               # Docker compose and environment files
│   ├── docker-compose.yml
│   ├── env.discordbot.example
│   ├── .env.postgres.example
│   └── init-db.sh
├── utils/                 # Utility scripts and tools
│   ├── python-shell.nix
│   ├── test_server.py
│   ├── test_server.sh
│   └── update_local.sh
└── SECURITY.md           # Security documentation
```
</details>

## Configuration

### Environment Variables

#### Discord Bot Configuration (.env.discordbot)

| Variable | Description | Required | Security Considerations |
|----------|-------------|----------|-------------------------|
| `DISCORD_TOKEN` | Your Discord bot token | Yes | Rotate every 90 days |
| `DOMAIN` | Your domain name | Yes | Must be valid domain |
| `SUPER_ADMINS` | Discord users with full access (NAME\|ID format) | Yes | Limit to trusted users |
| `ADMINS` | Discord users with admin access (NAME\|ID format) | Yes | Limit to minimum required |
| `USERS` | Regular users (NAME\|ID format) | No | Review regularly |
| `DISCORD_HOMELAB_CHANNEL` | Discord channel ID for system alerts | Yes | Restrict access |
| `ENCRYPTION_KEY` | Encryption key for sensitive data | Yes | 256-bit minimum |
| `JWT_SECRET_KEY` | Secret for JWT tokens | Yes | Strong random value |

#### Database Configuration (.env.postgres)

| Variable | Description | Required |
|----------|-------------|----------|
| `POSTGRES_USER` | Database admin username | Yes |
| `POSTGRES_PASSWORD` | Database admin password | Yes |
| `POSTGRES_DB` | Database name | Yes |
| `APP_DB_USER` | Application database user | Yes |
| `APP_DB_PASSWORD` | Application database password | Yes |

### Docker Compose


## Security Implementation

### Authentication & Authorization



### Data Protection



### Network Security



### Monitoring & Auditing



## Usage

## Maintenance

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

### Security Reporting


## License

MIT License

Copyright (c) 2025 fr4iser

See [LICENSE](LICENSE) for full text.
