# FoundryCord
## ⚠️ Experimental Project – JUST A HOBBY ⚠️

FoundryCord is a Discord bot combined with a web interface designed for managing Discord servers, channels, and potentially integrating custom dashboards or structure management features. Built with Python and Docker.

## Core Concepts (Examples)

- **Server Structure Management:** Tools to visualize, design, and apply server structures (categories, channels) potentially via templates (See Guild Designer Feature).
- **Web Interface:** A UI for administration, visualization, and configuration.
- **Discord Integration:** Bot commands and background tasks interacting with the Discord API.
- **Extensibility:** Designed with modularity in mind for adding features like dashboards, monitoring, etc.

## Requirements

- Docker & Docker Compose
- Discord Bot Token
- Python 3.11+ (Check `pyproject.toml`)

## Quick Setup

1.  **Prepare Docker Environment:**
    *   Navigate to the `docker/` directory.
    *   Copy the example environment file: `cp .env.example .env`
    *   Edit the `.env` file to add your `DISCORD_BOT_TOKEN` and set necessary passwords (e.g., `POSTGRES_PASSWORD`, `APP_DB_PASSWORD`). Refer to the main documentation for details on all variables.

2.  **Start Services:**
    *   From the project root directory, run:
        ```bash
        docker compose up -d --build
        ```

The web interface should become available at `http://localhost:8000` (or the configured port).

## Documentation

This project includes comprehensive documentation within the `/docs` directory. Key starting points include:

*   **Architecture Overview:** [`docs/architecture/01_overview.md`](docs/architecture/01_overview.md) - Understand the high-level system design.
*   **Backend & Frontend Design:** See respective files in [`docs/architecture/`](docs/architecture/) for details on backend/frontend structure.
*   **Database Schema:** [`docs/architecture/04_database_schema.md`](docs/architecture/04_database_schema.md) - Overview of the database structure.
*   **API Specification:** [`docs/architecture/05_api_specification.md`](docs/architecture/05_api_specification.md) - Details about the REST API.
*   **Coding Conventions:** [`docs/architecture/08_coding_conventions.md`](docs/architecture/08_coding_conventions.md) - Standards for writing code in this project.
*   **Architectural Decisions:** [`docs/architecture/09_adr_log.md`](docs/architecture/09_adr_log.md) - Log of important design choices.
*   **Feature Documentation:** Specific features are detailed in [`docs/development/features/`](docs/development/features/) (e.g., Guild Designer, State Monitor).
*   **Project Management:** Roadmap, TODOs, etc., can be found in [`docs/project_management/`](docs/project_management/).
*   **Security:** Refer to the security policy within the documentation.
*   **Configuration:** Detailed environment variable descriptions are part of the architecture documentation.

## Contributing

Contributions are welcome! Please follow these general steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bugfix.
3.  Make your changes, adhering to the [Coding Conventions](docs/architecture/08_coding_conventions.md).
4.  Ensure necessary documentation is updated.
5.  Submit a pull request.

### Security Reporting

Please report security vulnerabilities responsibly. Refer to the security policy in the documentation for details.

## License

[MIT License](LICENSE)

## Disclaimer

Please read our [disclaimer](DISCLAIMER.md) for important information about using this software.
