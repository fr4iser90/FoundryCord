# Getting Started: Local Development Setup

This guide outlines the steps to set up the [FoundryCord](../../../1_introduction/glossary.md#foundrycord) project locally for development using Docker. It assumes you are comfortable with the command line and have a basic understanding of Docker.

## Prerequisites

*   **Git:** For cloning the repository.
*   **Docker:** The containerization platform. ([Installation Guide](https://docs.docker.com/engine/install/))
*   **Docker Compose:** For orchestrating multi-container applications. ([Installation Guide](https://docs.docker.com/compose/install/))
*   **Discord Bot Token & Application ID:** Create an application and a bot user in the [Discord Developer Portal](https://discord.com/developers/applications). You will need the Bot Token and the Application ID.
*   **Your Discord User ID:** Required for `OWNER` configuration. ([How to find your Discord ID](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID))
*   **`.env.example` file:** A template environment file named `.env.example` **must exist** in the `docker/` directory. This file should list all required and optional environment variables for the project. If it\'s missing, you may need to create it based on the project\'s requirements or obtain it from the project maintainers.

## Setup Steps

1.  **Clone the Repository:**
    Open your terminal and clone the project repository:
    ```bash
    git clone https://github.com/fr4iser90/FoundryCord.git
    cd FoundryCord
    ```

2.  **Navigate to Docker Directory:**
    All Docker-related files, including the environment configuration, are typically managed within the `docker/` directory.
    ```bash
    cd docker
    ```

3.  **Configure Environment Variables (using `setup.sh` - Recommended):**
    The project includes an interactive setup script (`setup.sh`) within the `docker/` directory to help you configure your environment.
    *   **Action:** Run the script:
        ```bash
        ./setup.sh
        ```
    *   **Process:** This script will:
        1.  Copy `docker/.env.example` to `docker/.env` (if `.env` doesn\'t exist or you choose to overwrite).
        2.  Prompt you to enter essential values, including:
            *   `DISCORD_BOT_TOKEN`: Your Discord bot token.
            *   `OWNER`: Your Discord username and ID in the format `USERNAME|ID` (e.g., `yourname|123456789012345678`). This grants owner-level permissions in the application.
            *   `ENVIRONMENT`: Set to `development` (default), `production`, or `testing`.
            *   `DOMAIN`: The domain or IP where the web UI will be accessible (e.g., `localhost` for local testing).
            *   Database connection details (passwords, usernames). Defaults are provided for local development.
    *   Ensure you provide all requested values accurately.

4.  **Configure Environment Variables (Manual Fallback):**
    If you prefer not to use `setup.sh` or if it\'s unavailable:
    *   **Action 1:** Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
        *(Ensure you are in the `docker/` directory. This command assumes `docker/.env.example` exists).*
    *   **Action 2:** Open `docker/.env` in a text editor.
    *   **Action 3:** Manually fill in all required variables. Key variables include:
        *   `DISCORD_BOT_TOKEN`: Your Discord bot token.
        *   `OWNER`: Your Discord username and ID (e.g., `yourname|123456789012345678`).
        *   `POSTGRES_PASSWORD`: Password for the PostgreSQL admin user.
        *   `APP_DB_PASSWORD`: Password for the application\'s database user.
        *   `ENVIRONMENT`: Set to `development`.
        *   `DOMAIN`: Set to `localhost` for local access.
        *   *(Refer to `docker/.env.example` or project documentation for a complete list of variables).*

5.  **Navigate Back to Project Root:**
    Return to the main project directory to run Docker Compose commands.
    ```bash
    cd ..
    ```

6.  **Build and Start Services:**
    Use Docker Compose to build the container images and start all services (Bot, Web, Database, Cache) in detached mode (`-d`).
    ```bash
    docker compose up -d --build
    ```
    The first build might take some time as it needs to download base images and install dependencies. Wait for this command to complete successfully.

7.  **Run Database Migrations (CRITICAL):**
    After the containers are up and the database is initialized by `docker/postgres/init-db.sh` (which creates the `alembic_version` table), you **must** run the database migrations to create the actual application tables.
    *   **Action:** Execute the following command from the project root:
        ```bash
        docker compose exec web alembic upgrade head
        ```
        *(Alternatively, if Alembic is managed by the bot service, use `docker compose exec bot alembic upgrade head`)*
    *   **Verification:** This command should output logs indicating that migrations are being applied. Look for "OK" or completion messages.

8.  **Access the Web Interface:**
    Once the containers are running and migrations are complete, the web interface should be accessible in your browser.
    *   **URL:** `http://<DOMAIN_VALUE>:<PORT>` (e.g., `http://localhost:8000` if you used `localhost` for `DOMAIN` and the default port `8000` is mapped). Check your `docker/.env` and `docker-compose.yml` for the correct host and port.

9.  **View Logs (Optional):**
    To view real-time logs from all running containers:
    ```bash
    docker compose logs -f
    ```
    To view logs for a specific service (e.g., `web` or `bot`):
    ```bash
    docker compose logs -f web
    ```
    Press `Ctrl+C` to stop following the logs.

10. **Stopping Services:**
    To stop all running containers defined in your `docker-compose.yml`:
    ```bash
    docker compose down
    ```
    To stop and remove volumes (useful for a clean restart, **will delete database data**):
    ```bash
    docker compose down -v
    ```

## Next Steps

With the local environment running, you can now start developing! Refer to other guides for:
*   [Coding Conventions](./coding_conventions.md)
*   [Contribution Guidelines](./contribution.md)
*   Understanding the [Architecture Overview](../02_architecture/overview.md)
