# HomeLab Discord Bot Utilities

This directory contains utility scripts for managing, deploying, testing, and maintaining the HomeLab Discord Bot.

## Directory Structure

- **`config/`**: Configuration files and environment settings
- **`database/`**: Database migration and maintenance scripts
- **`deployment/`**: Deployment and server management scripts
- **`development/`**: Development tools and utilities
- **`lib/`**: Common libraries and shared functions
- **`testing/`**: Testing frameworks and test runners

## 🚀 Quick Start Guide

```bash
chmod +x utils/HomeLabCenter.sh
./utils/HomeLabCenter.sh
```

### Initial Setup on a Remote Server

To set up a new instance on a remote server:

```bash
# 1. Configure your environment settings first
cp utils/config/env_dev.sh utils/config/local_config.sh
nano utils/config/local_config.sh  # Edit with your server details

# 2. Deploy to a fresh server
bash utils/deployment/deploy.sh --rebuild

# 3. Check if services started correctly
bash utils/deployment/check_services.sh
```

### Common Operations

```bash
# Update configuration on remote server
utils/deployment/deploy.sh --env=dev

# Update only Docker configuration
utils/deployment/update_docker.sh

# Run tests on remote server
utils/testing/run_tests.sh

# Apply database migrations
utils/database/update_alembic_migration.sh
```

## 🔄 Complete Rebuild (with data removal)

To completely rebuild from scratch (WARNING: destroys all data):

```bash
# SSH into your server
ssh docker@your-server-hostname

# Stop all containers
cd /home/docker/docker/companion-management/homelab-discord-bot/compose
docker-compose down

# Remove all volumes (WARNING: DESTROYS ALL DATA)
docker volume rm $(docker volume ls -q | grep homelab)

# Return to your local machine and redeploy
utils/deployment/deploy.sh --rebuild
```

## 🔨 Development Workflow

1. Make changes to your code locally
2. Run `utils/testing/run_tests.sh` to execute tests on the remote server
3. If tests pass, deploy with `utils/deployment/deploy.sh`
4. Verify deployment with `utils/deployment/check_services.sh`

## 🔍 Troubleshooting

### Services Not Starting

If services don't start after deployment:

```bash
# Check service status
utils/deployment/check_services.sh

# Check logs on remote server
ssh docker@your-server-hostname "docker logs homelab-discord-bot"

# Restart services
utils/deployment/update_docker.sh --rebuild
```

### Database Issues

If encountering database problems:

```bash
# Run Alembic migrations
utils/database/update_alembic_migration.sh

# For serious issues requiring schema changes
utils/database/update_remote_database.sh
```

## 📝 Configuration Management

The configuration system is based on environment-specific settings files:

- `config/config.sh`: Main configuration loaded by all scripts
- `config/env_dev.sh`: Development environment settings
- `config/env_prod.sh`: Production environment settings
- `config/local_config.sh`: Local overrides (not committed to git)

Override settings by creating `local_config.sh` or using command arguments:

```bash
# Override server host for a single command
utils/deployment/deploy.sh --host=192.168.1.100

# Use production environment settings
utils/deployment/deploy.sh --env=prod
```

## 🔒 Security Notes

- Never commit `local_config.sh` or any file containing credentials
- Use SSH key authentication instead of passwords
- Keep your server's Docker and system packages updated
- Review logs regularly for security issues

## 📊 Monitoring

For basic system monitoring:

```bash
# Check server status and running services
utils/testing/test_server.sh

# Check server resource usage
ssh docker@your-server-hostname "docker stats --no-stream"
``` 