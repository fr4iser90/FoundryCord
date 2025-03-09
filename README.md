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

## Quick Setup

1. **Create a minimal .env.discordbot file**:
   ```bash
   cd compose
   mv .env.discordbot.example .env.discordbot
   nano .env.discordbot
   ```

2. **Create a minimal .env.postgres file**:
   ```bash
   cd compose
   mv .env.postgres.example .env.postgres
   nano .env.postgres
   ```

3. **Start the containers**:
   ```bash
   docker compose up -d --build
   ```

All other necessary configuration will be auto-generated at startup!

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

[MIT License](LICENSE)

## Disclaimer

Please read our [disclaimer](DISCLAIMER.md) for important information about using this software.
