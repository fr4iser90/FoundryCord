# 6. Deployment Strategy

## Overview

Describe how the application (Frontend/Backend/Bot) is deployed.

The application is designed to be deployed using Docker containers, orchestrated potentially via Docker Compose or a similar system.

## Infrastructure

*   **Hosting:** [Needs Specification - Where is the production environment hosted? e.g., VPS, Cloud Provider (AWS, GCP, Azure), Dedicated Server?]
*   **Database:** PostgreSQL, running as a dedicated Docker container (defined in `docker-compose.yml`).
*   **Other Services:** Redis, used for caching/session management, running as a dedicated Docker container (defined in `docker-compose.yml`).

## Build Process

*   **Frontend:** No explicit build step. Static assets (JS, CSS, images) located in `app/web/static/` are served directly by the FastAPI backend container.
*   **Backend:** No explicit build step beyond installing Python dependencies via `pip install -r requirements.txt` during the Docker image build (`docker/Dockerfile.web`).
*   **Bot:** No explicit build step beyond installing Python dependencies via `pip install -r requirements.txt` during the Docker image build (`docker/Dockerfile.bot`).

## Containerization (if used)

*   **Docker:** Yes, Docker is fundamental to the deployment strategy.
*   **Dockerfile(s):** Located in the `docker/` directory:
    *   `Dockerfile.web`: Defines the image for the FastAPI web application (Backend + Frontend serving).
    *   `Dockerfile.bot`: Defines the image for the `nextcord` Discord bot worker.
    *   `Dockerfile.test`: Defines an image used for running tests (likely in CI).
*   **Docker Compose:** `docker-compose.yml` in the project root defines the services (`web`, `bot`, `postgres`, `redis`) and their connections, primarily used for local development and potentially as a base for deployment orchestration. A separate `docker/test/docker-compose.yml` exists for the testing environment.

## Deployment Workflow (CI/CD)

*   **Source Control:** Git (Repository hosting likely GitHub based on assumed CI/CD).
*   **CI/CD Platform:** GitHub Actions (Assumed based on `.github/workflows/` or `to_implement/workflows/` like `test.yml`).
*   **Workflow Steps (Based on `test.yml`, deployment steps need confirmation):**
    *   Trigger: Push/Pull Request to specific branches (e.g., `main`, `develop`).
    *   Linting/Static Analysis: Run tools like `flake8`, `black`.
    *   Testing: Execute `pytest` using the test container (`docker/test/docker-compose.yml` or `Dockerfile.test`).
    *   Building Docker images: Build `web` and `bot` images.
    *   Pushing images to registry: [Needs Specification - e.g., Docker Hub, GitHub Container Registry (GHCR)].
    *   Deploying to server/cloud: [Needs Specification - How are images pulled and containers updated? e.g., SSH + `docker-compose pull && docker-compose up -d`, Kubernetes update, PaaS deployment command].
*   **Environment Configuration:** Environment variables are managed using `.env` files (e.g., `docker/.env`). A validation script (`docker/validate-env.sh`) likely exists. These variables are passed into the containers via Docker Compose (`env_file` directive) or potentially environment variables set on the host/CI/CD platform.

## Monitoring & Logging

*   **Monitoring:** [Needs Specification - How is application health and performance monitored? e.g., Health checks, external uptime monitoring, APM tools like Sentry/Datadog?]
*   **Logging:** Base logging is handled via Docker container logs (`stdout`/`stderr`), accessible via `docker logs` or `docker-compose logs`. Python applications (Bot/Web) have internal logging configuration (`app/shared/application/logging/`) which might include handlers for file or database logging, but a centralized log aggregation system (e.g., ELK, Loki) is not explicitly defined. 