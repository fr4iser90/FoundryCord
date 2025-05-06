# Project Structure

Understanding the layout of the FoundryCord project is the first step for any developer looking to contribute or navigate the codebase. This document outlines the top-level directory structure and the purpose of key directories and files. For detailed internal structures of the main application components, please refer to the linked files below.

```tree
.
├── app/                  # Core application Python code (Bot, Web, Shared)
├── docker/               # Dockerfiles, docker-compose.yml, setup scripts, .env files
├── docs/                 # All project documentation
├── .cursor/              # Cursor IDE specific settings (optional)
├── .git/                 # Git version control metadata
├── .idea/                # IntelliJ IDEA specific settings (optional)
├── .vscode/              # VS Code specific settings (optional)
├── .gitignore            # Specifies intentionally untracked files that Git should ignore
├── .project_config.sh    # Project-specific shell configuration script (if used)
├── DISCLAIMER.md
├── docker-compose.yml    # Defines and configures the multi-container Docker application
├── guild_designer.md     # Specific documentation (may move to docs/)
├── LICENSE.md
├── README.md             # Main entry point for project information
└── shell.nix             # Nix environment configuration
```

## Top-Level Directory Descriptions

*   **`app/`**: Contains all the core Python source code for the application. This is where the primary business logic, interfaces, and infrastructure for the bot, web, and shared components reside.
    *   See: [`bot_structure.md`](./bot_structure.md) for the Discord Bot structure.
    *   See: [`web_structure.md`](./web_structure.md) for the Web Backend/API structure.
    *   See: [`shared_structure.md`](./shared_structure.md) for the Shared Core library structure.
    *   See: [`tests_structure.md`](./tests_structure.md) for the Test suite structure (located in the root `tests/` directory, not under `app/`).

*   **`docker/`**: Holds Dockerfiles (`Dockerfile.bot`, `Dockerfile.web`), setup scripts (`setup.sh`), environment variable files (`.env`, `.env.example` - typically managed here), and other files related to building and configuring the Docker containers. Note that `docker-compose.yml` is in the project root.

*   **`docs/`**: Contains all project documentation, including this architecture overview, developer guides (getting started, core components, feature implementation), user guides, and project management artifacts (ADRs, TODOs).

*   **`tests/`**: (Not listed in the `app/` description above, but a top-level directory) Contains all automated tests (unit, integration, etc.). Its internal structure often mirrors the `app/` directory. *(Self-correction: `tests_structure.md` link under `app/` might be misleading, as `tests/` is top-level. The link should remain, but the description clarified).* 

*   **Configuration & Metadata (Root Directory)**: The project root contains critical project-wide configuration and metadata files:
    *   `docker-compose.yml`: Defines the services, networks, and volumes for the Docker application.
    *   `.gitignore`: Specifies files and directories ignored by Git.
    *   `README.md`: The primary introduction to the project, including setup and key features.
    *   `LICENSE.md`: Contains the project's software license.
    *   `DISCLAIMER.md`: Important disclaimers regarding the use of the software.
    *   `shell.nix`, `.project_config.sh`: Files related to specific development environment setups (Nix, shell).
    *   `guild_designer.md`: Currently a root file, might be better suited inside `docs/features/` or similar.

*   **IDE & Editor Settings (Optional)**: Folders like `.vscode/`, `.idea/`, and `.cursor/` contain settings specific to particular Integrated Development Environments or editors. These are generally optional and can be gitignored if they contain user-specific paths, or committed if they enforce project-wide editor standards.

*   **Generated Output**: Directories like `app/tests/test-results/` (if tests are configured to output there) would contain generated files (e.g., test reports, coverage data). These are typically gitignored.
