# 7. Technology Stack

List the core technologies, languages, frameworks, and significant libraries used in the project.

## Backend

*   **Language:** Python (Specify version, e.g., 3.11+ - Check Dockerfile/runtime)
*   **Web Framework:** FastAPI
*   **Database ORM:** SQLAlchemy (v2.x, async with asyncio)
*   **Async Library:** asyncio (Built-in)
*   **Database Driver:** asyncpg (for PostgreSQL)
*   **Data Validation/Serialization:** Pydantic (v2.x)
*   **Web Server:** Uvicorn
*   **Dependency Management:** pip with `requirements.txt`
*   **Database Migration:** Alembic
*   **Testing:** pytest, pytest-asyncio, pytest-cov
*   **Security Libraries:** Cryptography, PyJWT, python-jose, passlib
*   **HTTP Client:** httpx, requests
*   **Caching:** Redis
*   **System Monitoring:** psutil, py-cpuinfo, gputil, py3nvml, speedtest-cli, docker SDK
*   **Configuration:** python-dotenv
*   **Templating Engine (used by Backend):** Jinja2
*   *(Add others like specific utility libraries if needed)*

## Frontend

*   **Language:** JavaScript (ES6+)
*   **Templating:** Jinja2 (Rendered by FastAPI)
*   **UI Framework/Library:** Bootstrap (Likely 5.x)
*   **Layout:** Gridstack.js (Specify version if known)
*   **Tree View:** jsTree (Specify version if known, mention jQuery dependency)
*   **Core Lib Dependency:** jQuery (Specify version if known, required by jsTree)
*   **Styling:** CSS3
*   **Build/Bundling:** Manual file management (No dedicated build tool like Webpack/Vite detected)
*   *(Add others like charting libraries, date pickers if used)*

## Discord Bot

*   **Language:** Python (Specify version, likely same as backend)
*   **Library:** nextcord (v2.6.0)
*   **Database:** SQLAlchemy, asyncpg (Shared with Backend)
*   **HTTP Client:** requests, aiohttp
*   **System Monitoring:** psutil, py-cpuinfo, etc. (Shared with Backend)
*   **Configuration:** python-dotenv
*   *(Add others like command handling frameworks if used)*

## Database

*   **Type:** PostgreSQL (Specify version if known)

## Infrastructure / Deployment

*   **Containerization:** Docker, Docker Compose
*   **Web Server:** Uvicorn (running FastAPI)
*   **CI/CD:** GitHub Actions (Assumed based on workflow files)
*   **Hosting:** [Specify provider/type, e.g., VPS, Cloud Provider - Needs clarification]

## Development Tools

*   **Version Control:** Git
*   **Code Editor:** VS Code, Cursor (Based on workspace files)
*   **Linters/Formatters:** flake8, black (Python), [Specify for JS/CSS if known, e.g., Prettier, ESLint] 