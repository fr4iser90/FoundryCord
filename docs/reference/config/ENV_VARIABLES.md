
#### Discord Bot Configuration (.env)

| Variable | Description | Required | Security Considerations |
|----------|-------------|----------|-------------------------|
| `DISCORD_BOT_TOKEN` | Your Discord bot token | Yes | Rotate every 90 days |
| `DISCORD_SERVER` | Your Discord server ID | Yes | - |
| `HOMELAB_CATEGORY_ID` | Discord category ID for bot channels | Yes | Can set to "auto" for automatic creation | 
| `OWNER` | Discord users with full access (NAME\|ID format) | Yes | Limit to trusted users |
| `ENVIRONMENT` | Runtime environment (development/production/testing) | No | Default: development |
| `DOMAIN` | Your domain name | No | Default: localhost |
| `OFFLINE_MODE` | Disable internet-dependent features | No | Default: false |
| `ENABLED_SERVICES` | Services to enable (comma-separated) | No | Default: Web,Game,File |
| `ADMINS` | Discord users with admin access (NAME\|ID format) | No | Limit to minimum required |
| `USERS` | Regular users (NAME\|ID format) | No | Review regularly |
| `AES_KEY` | Key for AES encryption | No | Auto-generated if missing |
| `ENCRYPTION_KEY` | Key for Fernet encryption | No | Auto-generated if missing |
| `JWT_SECRET_KEY` | Secret for JWT tokens | No | Auto-generated if missing |
| `SESSION_DURATION_HOURS` | Session duration in hours | No | Default: 24 |
| `RATE_LIMIT_WINDOW` | Rate limit time window in seconds | No | Default: 60 |
| `RATE_LIMIT_MAX_ATTEMPTS` | Max attempts per rate limit window | No | Default: 5 |
| `PUID` | Process User ID for Docker | No | Default: 1001 |
| `PGID` | Process Group ID for Docker | No | Default: 987 |

#### Database Configuration (.env)

| Variable | Description | Required | Security Considerations |
|----------|-------------|----------|-------------------------|
| `POSTGRES_PASSWORD` | Database admin password | Yes | Use strong password, min 12 chars |
| `APP_DB_PASSWORD` | Application database password | Yes | Different from admin password |
| `POSTGRES_HOST` | Database hostname | No | Default: homelab-postgres |
| `POSTGRES_PORT` | Database port | No | Default: 5432 |
| `POSTGRES_USER` | Database admin username | No | Default: postgres |
| `POSTGRES_DB` | Database name | No | Default: homelab |
| `APP_DB_USER` | Application database user | No | Default: homelab_discord_bot |
