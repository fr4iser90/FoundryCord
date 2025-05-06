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

Below is a C4-style Container diagram illustrating how these components interact.

```mermaid
graph LR
%% Define Actors and Systems
actor User
subgraph External_Systems ["External Systems"]
    DiscordAPI["Discord API"]
end

subgraph FoundryCord_System ["FoundryCord System"]
    direction LR
    %% Define Containers
    User -- "Interacts via Browser" --> WebBrowser["Web Browser (Client-Side UI)"]
    WebBrowser -- "HTTPS (User Actions, API Requests)" --> WebApp["FoundryCord Web App (FastAPI + Jinja2)"]
    WebApp -- "SQL (Data Read/Write via SQLAlchemy)" --> Database["PostgreSQL Database"]
    WebApp -- "HTTP (Internal API Calls via httpx)\n[e.g., Trigger Bot Action]" --> DiscordBot["FoundryCord Discord Bot (nextcord)"]
    DiscordBot -- "SQL (Data Read/Write via SQLAlchemy)" --> Database
    DiscordBot -- "HTTPS/WebSocket (Discord Gateway & API)" --> DiscordAPI
end

%% Style
classDef default fill:#ECEFF4,stroke:#333,stroke-width:2px,color:#333;
classDef actor fill:#DAE8FC,stroke:#6C8EBF,stroke-width:2px,color:#333;
classDef system fill:#FFF2CC,stroke:#D6B656,stroke-width:2px,color:#333;
classDef container fill:#D5E8D4,stroke:#82B366,stroke-width:2px,color:#333;
classDef database fill:#FFE6CC,stroke:#D79B00,stroke-width:2px,color:#333;

class User actor;
class DiscordAPI system;
class WebBrowser container;
class WebApp container;
class DiscordBot container;
class Database database;
```

The key interactions are:

*   User's Browser <-> Frontend (HTML/CSS/JS served by Backend)
*   Frontend (JavaScript) <-> Backend API (via HTTP requests)
*   Backend API -> Shared Core (Services, Repositories) -> Database
*   Backend API -> Internal Bot API (via HTTP requests using httpx - for specific, immediate bot actions triggered by the web UI)
*   Discord Bot -> Shared Core (Services, Repositories) -> Database
*   Discord Bot <-> Discord API (Gateway events, REST calls)
*   Discord API -> Discord Bot (Events, Interaction Hooks for commands)

## Key Responsibilities Flow

*   **Guild Onboarding:** (e.g., User invites bot, bot uses Shared Core/DB to save initial guild info, maybe triggered via Backend API call after web auth).
*   **Template Design:** (e.g., User interacts with Frontend designer, Frontend JS calls Backend API, Backend API uses Shared Core/DB to load/save templates).
*   **Template Activation/Application:** (e.g., User activates via Frontend -> Backend API -> Shared Core updates `active_template_id` in DB. Bot periodically checks or is notified -> Reads active template via Shared Core/DB -> Applies changes to Discord via Discord API). 