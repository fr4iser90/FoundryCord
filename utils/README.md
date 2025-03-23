# Application Center

## Overview

This utility suite provides comprehensive management tools for deploying, configuring, and maintaining applications in various environments. It simplifies the operational aspects of running your applications on remote servers through an interactive command-line interface with automated setup, intelligent deployment, and robust monitoring capabilities.

## Key Features

- **Intelligent Setup**: Automatic detection and initialization of local/remote environments.
- **Remote Server Management**: Deploy and manage applications on remote servers without manual SSH commands.
- **Container Management**: Control Docker containers with simple menu options.
- **Database Operations**: Perform backups, restores, and migrations with ease.
- **Configuration Management**: Edit environment variables through guided interfaces.
- **Logging Utilities**: View and download logs from all services.
- **Testing Framework**: Run and manage automated tests.
- **Auto-start Capabilities**: Automatic service initialization after deployment.
- **Interactive Feedback**: Real-time console output with customizable verbosity levels.

## Getting Started

### Prerequisites

- SSH access to your target server.
- Docker and Docker Compose installed on the target server.
- Basic knowledge of Linux and shell operations.

### Initial Setup

1. Run the management utility:
   ```bash
   chmod +x utils/ApplicationCenter.sh
   ./utils/ApplicationCenter.sh
   ```

2. The utility will:
   - Check for existing configuration and initialize if needed.
   - Guide you through server connection setup.
   - Detect if the remote environment requires initialization.
   - Offer automated or manual deployment options.

## Main Menu Options

### Deployment Tools

- **Quick Deploy**: Preserves database, auto-starts services.
- **Partial Deploy**: Rebuilds containers only.
- **Full Reset Deploy**: WARNING: destroys all data.
- **Deploy with Monitoring**: Shows real-time console output.

### Container Management

- Start/stop/restart all containers.
- Manage individual containers.
- View container status and health metrics.
- Watch container logs in real-time.

### Testing Tools

- Run automated tests.
- Upload test files.
- Verify server environment.
- Generate test reports.

### Database Tools

- Apply migrations.
- Backup database.
- Restore database.
- View database statistics.

### Development Tools

- Generate encryption keys.
- Initialize test environment.
- Create development certificates.
- Setup local development environment.

### Configuration Management

- Edit server connection settings.
- Manage environment variables.
- Configure auto-start behavior.
- Setup notification preferences.

### Logs & Monitoring

- View various service logs.
- Download log files.
- Set up log watching.
- Configure alert thresholds.

## Directory Structure

- **`config/`**: Configuration files for the management utility.
- **`database/`**: Database management scripts.
- **`functions/`**: Core functionality modules.
- **`lib/`**: Common libraries and utilities.
- **`menus/`**: Menu interface components.
- **`testing/`**: Test execution and management.
- **`ui/`**: User interface functions.
- **`init/`**: Initialization scripts for first-time setup.

## Configuration Files

The primary configuration is stored in:
- `utils/config/config.sh`: Main configuration file.
- `utils/config/local_config.sh`: Local settings overrides.
- `utils/config/auto_start.conf`: Auto-start configuration.

## Initialization Process

When run for the first time, the utility will:
1. Check for existing configuration files.
2. Detect local Git repository and configuration files.
3. Guide you through setting up SSH connection to your server.
4. Create necessary directory structure on the remote server.
5. Initialize database and required environment variables.
6. Configure auto-start preferences.
7. Deploy and start services.

## Auto-Start and Feedback Options

The utility now includes enhanced deployment options:
```bash
# Deploy with auto-start enabled (default)
./utils/ApplicationCenter.sh --auto-start

# Deploy with real-time console feedback
./utils/ApplicationCenter.sh --watch-console

# Deploy with specific service monitoring
./utils/ApplicationCenter.sh --watch=service1,service2
```

## Advanced Usage

### Command-line Arguments

The utility supports various command-line arguments:
```bash
./utils/ApplicationCenter.sh --host=192.168.1.100 --user=admin --port=2222 --auto-start --watch-console
```

Common options:
- `--host=HOST`: Specify remote server hostname/IP.
- `--user=USER`: Specify SSH username.
- `--port=PORT`: Specify SSH port.
- `--no-restart`: Prevent automatic service restarts.
- `--rebuild`: Force container rebuilds during deployment.
- `--auto-start`: Enable automatic startup after deployment.
- `--watch-console`: Show real-time console output.
- `--watch=SERVICES`: Monitor specific services (comma-separated).
- `--init-only`: Run initialization without deployment.
- `--feedback=LEVEL`: Set feedback verbosity (minimal, normal, detailed).

### Local Mode

If you can't connect to a remote server, you can run in local mode for limited functionality:
```bash
# The utility will detect SSH connection failures and offer local mode
./utils/ApplicationCenter.sh --local
```

## Troubleshooting

### Connection Issues

If you encounter SSH connection problems:
1. Verify server address and credentials.
2. Check if SSH key authentication is set up correctly.
3. Confirm the server is online and accessible.
4. Run with `--debug` for detailed connection information.

### Deployment Failures

If deployment fails:
1. Check logs for specific errors (`Logs & Monitoring > View Deployment Logs`).
2. Verify Docker is running on the remote server.
3. Ensure required ports are not in use by other applications.
4. Try `--rebuild --force` to force a clean rebuild.

### Database Problems

For database issues:
1. Use the "Database Tools > Check Database Health" menu.
2. Consider running a database backup before attempting fixes.
3. Check logs for specific error messages.
4. Try "Database Tools > Rebuild Schema" for persistent issues.

## Best Practices

1. **Regular Backups**: Create database backups before major changes.
2. **Version Control**: Keep your local repository updated.
3. **Testing**: Run tests after configuration changes.
4. **Environment Files**: Secure your .env files as they contain sensitive information.
5. **Auto-Start Config**: Regularly review auto-start configurations for security.
6. **Feedback Logs**: Check feedback logs after unattended deployments.

## Getting Feedback

The utility now provides several ways to collect and analyze system feedback:
1. **Live Console**: Watch real-time output during deployment.
2. **Service Logs**: Monitor specific service logs for issues.
3. **Health Reports**: Generate system health reports.
4. **Deployment Summary**: View summary after deployment completes.
5. **Notification Options**: Configure email or Discord notifications.

## Support

For issues with this utility, please open an issue in the project repository or visit our support channel.

## Contribute

We welcome contributions to improve this utility! See our contributing guidelines for more information.