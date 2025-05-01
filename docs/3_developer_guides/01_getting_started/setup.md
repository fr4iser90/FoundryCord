# Getting Started: Local Setup

This guide outlines the steps to set up the FoundryCord project locally for development using Docker.

## Prerequisites

*   Git
*   Docker ([Installation Guide](https://docs.docker.com/engine/install/))
*   Docker Compose ([Installation Guide](https://docs.docker.com/compose/install/))
*   A Discord Bot Token and ID ([Discord Developer Portal](https://discord.com/developers/applications))
*   Your Discord User ID ([How to find your Discord ID](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID))

## Setup Steps

1.  **Clone the Repository:**
    Open your terminal and clone the project repository:
    ```bash
    git clone https://github.com/fr4iser90/FoundryCord.git
    cd FoundryCord
    ```

2.  **Navigate to Docker Directory:**
    Change into the `docker` directory where the setup scripts reside:
    ```bash
    cd docker
    ```

3.  **Run the Setup Script:**
    Execute the interactive setup script. This will copy the example environment file (`.env.example`) to `.env` and prompt you to enter the required configuration values.
    ```bash
    ./setup.sh
    ```
    Follow the prompts to enter your:
    *   Discord Bot Token (`DISCORD_BOT_TOKEN`)
    *   Your Discord Username and ID in the format `USERNAME|ID` (e.g., `fr4iser|151707357926129664`) for the `OWNER` variable.
    *   The domain or IP address where the web interface will be accessible (`DOMAIN`, use `localhost` for local testing).
    *   Database passwords (you can use the suggested defaults for local development or set your own secure passwords).


5.  **Navigate Back to Project Root:**
    Go back to the main project directory:
    ```bash
    cd ..
    ```

6.  **Build and Start Services:**
    Use Docker Compose to build the images and start all the services (Bot, Web, Database, Cache) in detached mode (`-d`):
    ```bash
    docker compose up -d --build
    ```
    The first build might take some time as it needs to download base images and install dependencies.

7.  **Access the Web Interface:**
    Once the containers are running, the web interface should be accessible in your browser at the address specified by the `DOMAIN` variable in your `.env` file (e.g., `http://localhost:8000` if you used `localhost` and the default port).

8.  **View Logs (Optional):**
    To view the logs from the running containers:
    ```bash
    docker compose logs -f
    ```
    Press `Ctrl+C` to stop following the logs.

9.  **Stopping Services:**
    To stop the running containers:
    ```bash
    docker compose down
    ```
