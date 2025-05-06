# Deployment

This document outlines the deployment strategy for the [FoundryCord](../../../1_introduction/glossary.md#foundrycord) application suite (Frontend/Backend API, and Discord Bot). It covers infrastructure, containerization, CI/CD workflow, and considerations for different environments.

## Overview

Describe how the application (Frontend/Backend/Bot) is deployed.

The application is designed to be deployed using Docker containers, orchestrated potentially via Docker Compose or a similar system.

## Infrastructure

*   **Hosting:** The specific production hosting environment is **yet to be finalized**. Options under consideration include Virtual Private Servers (VPS), cloud providers (e.g., AWS, GCP, Azure), or dedicated servers. The final choice will depend on factors like scalability requirements, cost, and operational management preferences.
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
*   **CI/CD Platform:** GitHub Actions (assumed, based on typical project structure; workflows would reside in `.github/workflows/`).
*   **Workflow Steps (Conceptual - actual implementation may vary):**
    *   Trigger: Push/Pull Request to specific branches (e.g., `main` for production, `develop` for staging/testing).
    *   Linting/Static Analysis: Run tools like `flake8`, `black`.
    *   Testing: Execute `pytest` using the test environment (e.g., via `docker-compose -f docker-compose.test.yml run test_runner` or similar).
    *   Building Docker images: Build `web` and `bot` images using their respective `Dockerfiles`.
    *   Pushing images to registry: Built images will be pushed to a **chosen container registry** (e.g., Docker Hub, GitHub Container Registry (GHCR), or a private registry).
    *   Deploying to server/cloud: The method for deploying updates (pulling new images and restarting containers) to the chosen hosting environment will be defined based on that environment. Common approaches include SSH scripts (e.g., `git pull && docker-compose pull && docker-compose up -d`), Kubernetes deployment updates, or Platform-as-a-Service (PaaS) specific deployment commands.

*   **Environment Configuration & Secrets Management:**
    *   Environment variables are managed using `.env` files for local development (e.g., `docker/.env`, sourced from `docker/.env.example`). A validation script (`docker/validate-env.sh`) can be used to check for required variables.
    *   For **staging and production environments, `.env` files must not be committed to the repository.** Secrets (like `DISCORD_BOT_TOKEN`, database passwords, API keys) must be securely managed via:
        *   CI/CD platform secret management (e.g., GitHub Actions secrets).
        *   Host environment variables on the deployment server(s).
        *   Dedicated secret management tools (e.g., HashiCorp Vault, cloud provider KMS).
    *   These secrets are then injected into the Docker containers at runtime.

## Monitoring & Logging

*   **Monitoring:**
    *   Basic health checks are defined in `docker-compose.yml` for services like `web` and `postgres`.
    *   A formal Application Performance Monitoring (APM) solution (e.g., Sentry, Datadog, Prometheus/Grafana) and comprehensive external uptime monitoring are **future considerations** for production environments.
*   **Logging:**
    *   Base logging is handled via Docker container logs (`stdout`/`stderr`), accessible via `docker logs <container_name>` or `docker-compose logs -f <service_name>`.
    *   The Python applications (Bot/Web) have internal logging configurations (see `app/shared/application/logging/`) which direct logs to `stdout` by default, aligning with Docker\'s logging practices. These may include handlers for file or database logging if specifically configured.
    *   A centralized log aggregation system (e.g., ELK stack, Grafana Loki, cloud provider logging services) is a **future consideration** for production environments to facilitate easier troubleshooting, searching, and analysis across services.

## Troubleshooting Common Deployment Issues (Local Docker Focus)

*   **Service Fails to Start:**
    *   Check container logs: `docker-compose logs -f <service_name>` (e.g., `web`, `bot`, `postgres`). Look for error messages or stack traces.
    *   Ensure all required environment variables in `docker/.env` are correctly set and sourced by Docker Compose.
    *   Verify port conflicts: Ensure ports defined in `docker-compose.yml` (e.g., `8000` for the web app) are not already in use on your host machine.
*   **Database Connection Issues:**
    *   Confirm the `postgres` container is running and healthy: `docker ps`, `docker-compose logs -f postgres`.
    *   Verify database credentials in `docker/.env` match those used by the application services (web, bot).
    *   Ensure the application is waiting for the database to be ready before attempting to connect (e.g., `depends_on` with `condition: service_healthy` in `docker-compose.yml`).
*   **Migrations Not Applied:**
    *   After initial `docker-compose up -d --build`, run database migrations: `docker-compose exec web alembic upgrade head` (or `bot` if Alembic is run from there).
    *   Check current migration status: `docker-compose exec web alembic current`.
*   **Incorrect File Permissions or Volume Mounts:**
    *   Ensure Docker has correct permissions to access mounted volumes, especially if developing on Linux where user IDs might differ between host and container. 