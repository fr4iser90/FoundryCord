# Project Structure

This document outlines the top-level directory structure of the FoundryCord project. For detailed internal structures of the main application components, please refer to the linked files below.

```tree
.
├── app/
├── docker/
├── docs/
├── .gitignore
├── .vscode/          (Editor-specific settings, optional)
├── .cursor/          (Cursor-specific settings, optional)
├── docker-compose.yml
├── DISCLAIMER.md
├── LICENSE           (Assuming LICENSE file exists or will be added)
├── README.md
└── ... (other config files if any)
```

## Top-Level Directory Descriptions

*   **`app/`**: Contains all the core Python source code for the application.
    *   See: [`bot_structure.md`](./bot_structure.md) for the Discord Bot structure.
    *   See: [`web_structure.md`](./web_structure.md) for the Web Backend/API structure.
    *   See: [`shared_structure.md`](./shared_structure.md) for the Shared Core library structure.
    *   See: [`tests_structure.md`](./tests_structure.md) for the Test suite structure.

*   **`docker/`**: Holds Dockerfiles (`Dockerfile.bot`, `Dockerfile.web`, etc.), docker-compose configurations, environment variable templates (`.env.example`), setup scripts (`setup.sh`), and other files related to containerization.

*   **`docs/`**: Contains all project documentation, including architecture details, developer guides, project management artifacts, and user guides.

*   **Configuration & Metadata**: Root directory contains project-wide configuration like `.gitignore`, `docker-compose.yml`, the main `README.md`, `DISCLAIMER.md`, and potentially environment setup files like `.project_config.sh` or `shell.nix`.

*   **Development Environment**: Folders like `.vscode` or `.cursor` contain editor-specific settings.

*   **Generated/Temporary**: Folders like `test-results` or `to_implement` appear to hold generated output or temporary files.
