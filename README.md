# Homelab Assistant Discord Bot (Python-based)
⚠️ Experimental Project ⚠️

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
   - Create a `.env` file by copying the example:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file with your specific configuration:
     ```env
     DISCORD_TOKEN=your_discord_bot_token
     ADMINS=admin:1234567890
     GUESTS=friendlyneigbor:0987654321,friend:1234567123
     TRAEFIK_API_URL=http://traefik:8080
     SECRET_KEY=your_secure_secret_key
     ENCRYPTION_KEY=your_encryption_key
     ```

3. **Build and Start the Containers:**
   ```bash
   docker-compose up -d --build
   ```

## Configuration

### Environment Variables

| Variable | Description | Required | Security Considerations |
|----------|-------------|----------|-------------------------|
| `NEXTCORD_TOKEN` | Your Discord bot token | Yes | Rotate every 90 days |
| `TRACKER_URL` | Base URL for IP tracking | NO | Must use HTTPS |
| `ADMINS` | Comma-separated list of Discord role IDs with admin access | Yes | Limit to minimum required roles |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No | Avoid DEBUG in production |
| `DISCORD_HOMELAB_CHANNEL` | Discord channel ID for system alerts | No | Restrict access to admins |
| `SECRET_KEY` | Application secret key | NO | Must be cryptographically strong |
| `ENCRYPTION_KEY` | Encryption key for sensitive data | NO | 256-bit minimum |

### Docker Compose

The `docker-compose.yml` file defines three services:

1. **bot**: The main Discord bot service
2. **tracker**: IP tracking service

## Security Implementation

### Authentication & Authorization

- **Role-based Access Control**: Implemented through Discord roles with hierarchical permissions
- **Two-Factor Authentication**: Required for all admin operations
- **Session Management**: JWT tokens with short expiration and automatic rotation
- **Rate Limiting**: Implemented at both application and network levels

### Data Protection

- **Encryption**: AES-256 encryption for sensitive data at rest
- **Secure Storage**: Environment variables for sensitive configuration
- **Data Validation**: Strict input validation for all user-provided data

### Network Security

- **HTTPS Enforcement**: All external endpoints require HTTPS
- **IP Whitelisting**: Integrated with Traefik for network-level protection
- **Firewall Rules**: Default deny policy with explicit allow rules

### Monitoring & Auditing

- **Activity Logging**: Detailed logs of all security-relevant events
- **Intrusion Detection**: Automated monitoring for suspicious patterns
- **Vulnerability Scanning**: Regular scans of dependencies and containers

## Usage

### Basic Commands

- `!getip`: Generates a personal IP registration link for users
- `!status`: Displays the current system status
- `!containers`: Lists all running containers (admin access required)
- `!logs <container>`: Shows logs for the specified container (admin access required)
- `!restart <container>`: Restarts the specified container (admin access required)

### Security Commands

- `!audit`: Runs security audit (admin only)
- `!rotatekeys`: Rotates encryption keys (admin only)
- `!revoke <user>`: Revokes user access (admin only)

## Maintenance

### Updating

To update the bot:

```bash
docker-compose pull
docker-compose up -d --build
```

### Security Updates

1. **Dependency Updates**: Regularly update all dependencies
2. **Security Patches**: Apply security patches immediately
3. **Configuration Review**: Quarterly review of security settings

### Monitoring

The bot includes built-in monitoring:

- System resource usage
- Container health checks
- Error rate tracking
- Security event logging

### Logs

View logs for the bot service:

```bash
docker-compose logs -f bot
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

### Security Reporting

Please report any security vulnerabilities to security@example.com

## License

MIT License

Copyright (c) 2025 fr4iser

See [LICENSE](LICENSE) for full text.
