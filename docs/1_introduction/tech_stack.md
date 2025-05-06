# 7. Technology Stack

This document outlines the core technologies, languages, frameworks, and significant libraries used in the [FoundryCord](./glossary.md#foundrycord) project.

## Backend

*   **Language:** [Python](https://www.python.org/) (3.11+)
    *   *Rationale:* Chosen for its extensive libraries, strong community support, and suitability for both web development (with FastAPI) and bot development (with nextcord).
*   **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/)
    *   *Rationale:* A modern, high-performance web framework for building APIs with Python, based on standard Python type hints. Offers automatic data validation, serialization, and interactive API documentation.
*   **Database ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) (v2.x, async with asyncio)
    *   *Rationale:* A powerful and flexible ORM toolkit that provides full SQL capabilities and robust object-relational mapping, supporting asynchronous operations.
*   **Async Library:** `asyncio` (Built-in Python library)
    *   *Rationale:* Used for writing concurrent code using the async/await syntax, essential for I/O-bound and high-level structured network code.
*   **Database Driver:** `asyncpg` (for PostgreSQL)
    *   *Rationale:* A fast asynchronous PostgreSQL client library.
*   **Data Validation/Serialization:** [Pydantic](https://pydantic.dev/) (v2.x)
    *   *Rationale:* Provides data validation and settings management using Python type annotations, integrating seamlessly with FastAPI.
*   **Web Server:** [Uvicorn](https://www.uvicorn.org/)
    *   *Rationale:* An ASGI server, lightning-fast, for running FastAPI applications.
*   **Dependency Management:** pip with `requirements.txt` (standard Python package installer)
*   **Database Migration:** [Alembic](https://alembic.sqlalchemy.org/)
    *   *Rationale:* A lightweight database migration tool for SQLAlchemy, enabling version control for database schemas.
*   **Testing:** [pytest](https://docs.pytest.org/), `pytest-asyncio`, `pytest-cov`
    *   *Rationale:* A mature, feature-rich testing framework for Python.
*   **Security Libraries:** `Cryptography`, `PyJWT`, `python-jose`, `passlib`
    *   *Rationale:* Standard libraries for cryptographic operations, JSON Web Token handling, and password hashing.
*   **HTTP Client:** `httpx`, `requests`
    *   *Rationale:* `httpx` for asynchronous HTTP requests, `requests` for synchronous ones; both are robust and widely used.
*   **Caching:** [Redis](https://redis.io/)
    *   *Rationale:* An in-memory data structure store, used as a cache to improve performance.
*   **System Monitoring:** `psutil`, `py-cpuinfo`, `gputil`, `py3nvml`, `speedtest-cli`, `docker` SDK
    *   *Rationale:* Libraries for gathering system metrics like CPU, memory, disk, network, and Docker container information.
*   **Configuration:** `python-dotenv`
    *   *Rationale:* For managing application configuration via `.env` files.
*   **Templating Engine (used by Backend):** [Jinja2](https://jinja.palletsprojects.com/)
    *   *Rationale:* A modern and designer-friendly templating language for Python, used to render HTML pages served by FastAPI.

## Frontend

*   **Language:** JavaScript (ES6+)
    *   *Rationale:* The standard language for web browser interactivity.
*   **Templating:** [Jinja2](https://jinja.palletsprojects.com/) (Rendered by FastAPI)
    *   *Rationale:* Allows dynamic HTML generation on the server-side before sending to the client.
*   **UI Framework/Library:** [Bootstrap](https://getbootstrap.com/) (Likely 5.x)
    *   *Rationale:* A popular framework for building responsive, mobile-first sites quickly.
*   **Layout:** [Gridstack.js](https://gridstackjs.com/) (Specify version if known)
    *   *Rationale:* A JavaScript library for widget layout, enabling drag-and-drop dashboard creation.
*   **Tree View:** [jsTree](https://www.jstree.com/) (Specify version if known, requires jQuery)
    *   *Rationale:* A JavaScript library for interactive tree structures, used for hierarchical displays like channel lists.
*   **Core Lib Dependency:** [jQuery](https://jquery.com/) (Specify version if known, required by jsTree)
    *   *Rationale:* A fast, small, and feature-rich JavaScript library, primarily included as a dependency for jsTree.
*   **Styling:** CSS3
    *   *Rationale:* Standard for styling web pages.
*   **Build/Bundling:** Manual file management (No dedicated build tool like Webpack/Vite currently specified)

## Discord Bot

*   **Language:** [Python](https://www.python.org/) (Same version as backend)
*   **Library:** [nextcord](https://nextcord.readthedocs.io/) (v2.6.0)
    *   *Rationale:* A modern, easy-to-use, feature-rich, and async-ready API wrapper for Discord.
*   **Voice Support:** `PyNaCl` (for nextcord voice)
    *   *Rationale:* Required by nextcord for voice encryption.
*   **Database:** [SQLAlchemy](https://www.sqlalchemy.org/), `asyncpg` (Shared with Backend)
*   **HTTP Client:** `requests`, `aiohttp` (for async HTTP in bot context)
*   **System Monitoring:** `psutil`, `py-cpuinfo`, etc. (Shared with Backend)
*   **Configuration:** `python-dotenv` (Shared with Backend)

## Database

*   **Type:** [PostgreSQL](https://www.postgresql.org/) (Version 17, via `postgres:17-alpine` Docker image)
    *   *Rationale:* A powerful, open-source object-relational database system with a strong reputation for reliability, feature robustness, and performance.

## Infrastructure / Deployment

*   **Containerization:** [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
    *   *Rationale:* For creating consistent development and deployment environments, and for orchestrating multi-container applications.
*   **Web Server:** [Uvicorn](https://www.uvicorn.org/) (running FastAPI)
*   **CI/CD:** GitHub Actions (Assumed based on workflow files)
    *   *Rationale:* For automating build, test, and deployment pipelines.
*   **Hosting:** [Specify provider/type, e.g., VPS, Cloud Provider - Needs clarification by project owner]

## Development Tools

*   **Version Control:** [Git](https://git-scm.com/)
*   **Code Editor:** VS Code, Cursor (Based on workspace files)
*   **Linters/Formatters (Python):** flake8, black
    *   *Rationale:* `flake8` for linting (style and error checking), `black` for opinionated code formatting to ensure consistency.
*   **Linters/Formatters (JS/CSS):** [Specify if used, e.g., Prettier, ESLint - Currently not specified] 