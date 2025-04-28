# 1. System Architecture Overview

## Components

Describe the main components of the system and their high-level responsibilities:

*   **Frontend (Web Application):** Resides in `app/web/static` (JS, CSS) and `app/web/templates` (Jinja2), served by the Backend. Provides the user interface for guild configuration, the Guild Template Designer, user management, and administrative tasks. Uses Vanilla JS (ES6+), Bootstrap, Gridstack.js, jsTree, and jQuery.
*   **Backend (REST API):** The core web application located in `app/web`. Built with FastAPI, it serves the frontend, provides RESTful API endpoints (`app/web/interfaces/api/rest/v1/`), handles business logic (`app/web/application/services/`), and manages user sessions and authentication.
*   **Discord Bot (Worker):** The Discord bot application located in `app/bot`. Built with `nextcord`, it interacts with the Discord API, handles slash commands, manages Discord-specific resources (channels, roles), applies template structures, and performs background tasks.
*   **Shared Core (`app/shared`):** A crucial library containing code shared between the Backend and the Bot. This includes:
    *   Domain logic and entities (`app/shared/domain`)
    *   Infrastructure components like database models (`app/shared/infrastructure/models`), repositories (`app/shared/infrastructure/repositories`), database session management, and shared configuration (`app/shared/infrastructure/config`).
    *   Shared application services (e.g., logging, encryption).
*   **Database:** PostgreSQL. Acts as the central persistence layer storing user data, guild information, template definitions, configurations, UI layouts, logs, and potentially bot state. Managed via SQLAlchemy ORM and Alembic migrations (defined in `app/shared`).

## Interactions

Illustrate how these components interact. A C4 Context or Container diagram would be ideal here.

*   User's Browser <-> Frontend (HTML/CSS/JS served by Backend)
*   Frontend (JavaScript) <-> Backend API (via HTTP requests)
*   Backend API -> Shared Core (Services, Repositories) -> Database
*   Backend API -> (Potentially triggers Bot actions - Method needs clarification: DB flags? Message Queue? RPC?)
*   Discord Bot -> Shared Core (Services, Repositories) -> Database
*   Discord Bot <-> Discord API (Gateway events, REST calls)
*   Discord API -> Discord Bot (Events, Interaction Hooks for commands)

## Key Responsibilities Flow

*   **Guild Onboarding:** (e.g., User invites bot, bot uses Shared Core/DB to save initial guild info, maybe triggered via Backend API call after web auth).
*   **Template Design:** (e.g., User interacts with Frontend designer, Frontend JS calls Backend API, Backend API uses Shared Core/DB to load/save templates).
*   **Template Activation/Application:** (e.g., User activates via Frontend -> Backend API -> Shared Core updates `active_template_id` in DB. Bot periodically checks or is notified -> Reads active template via Shared Core/DB -> Applies changes to Discord via Discord API). 