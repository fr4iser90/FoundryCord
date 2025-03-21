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
   cd docker
   mv .env.example .env
   nano .env.discordbot
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

| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_BOT_TOKEN` | Your Discord bot token | Yes |
| `DISCORD_SERVER` | Your Discord server ID | Yes |
| `OWNER` | Discord users with full access (NAME\|ID format) | Yes |

All other variables have sensible defaults and will be auto-generated if needed.

#### Database Configuration (.env.postgres)

| Variable | Description | Required |
|----------|-------------|----------|
| `POSTGRES_PASSWORD` | Database admin password | Yes |
| `APP_DB_PASSWORD` | Application database password | Yes |

All other database variables use appropriate defaults.

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

## Documentation

This project includes comprehensive documentation to help you understand and use the bot effectively.

### Core Documentation
- [Development Protocol](docs/core/PROTOCOL.md): Our methodical development workflow
- [Architecture](docs/core/ARCHITECTURE.md): High-level system architecture
- [Coding Conventions](docs/core/CONVENTIONS.md): Code standards and practices
- [Security Policy](docs/core/SECURITY_POLICY.md): Security practices and guidelines
- [Environment Variables](docs/core/VARIABLES.md): Configuration variables reference

### Implementation Guides
- **Patterns**:
  - [Design Patterns](docs/development/patterns/DESIGN_PATTERN.md): Architecture patterns
  - [Dashboard Implementation](docs/development/patterns/DASHBOARD_PATTERN.md): Dashboard UI patterns
  - [Slash Command Pattern](docs/development/patterns/SLASHCOMMAND_PATTERN.md): Command implementation
- **Development Roles**:
  - [Bot Framework Developer](docs/development/roles/BOT_FRAMEWORK_DEVELOPER.md): Core bot development
  - [Security Specialist](docs/development/roles/SECURITY_SPECIALIST.md): Security implementation
  - [System Monitoring Developer](docs/development/roles/SYSTEM_MONITORING_DEVELOPER.py): Monitoring features
  - [Slash Command Developer](docs/development/roles/SLASH_COMMAND_DEVELOPER.py): Command implementation
  - [UI/UX Designer](docs/development/roles/UI_UX_DESIGNER.py): Dashboard and UI development

### Project Planning
- [Current Action Plan](docs/planning/ACTION_PLAN.md): Tasks in progress
- [Roadmap](docs/planning/ROADMAP.md): Future development plans
- [Milestones](docs/planning/MILESTONES.md): Project progress tracking

### Templates
- [Role Definition Template](docs/development/template/ROLE_DEFINITION.md): Template for defining roles

## License

[MIT License](LICENSE)

## Disclaimer

Please read our [disclaimer](DISCLAIMER.md) for important information about using this software.
