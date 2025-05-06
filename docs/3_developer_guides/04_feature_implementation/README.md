# Feature Implementation Guides

This section provides detailed guides and examples for implementing new features or understanding existing complex features within [FoundryCord](docs/1_introduction/glossary.md#foundrycord). It showcases common workflows, design patterns, and best practices to follow.

## Structure

Feature implementation guides are typically organized by the specific feature or a closely related group of features. Each guide aims to provide:

*   An overview of the feature and its purpose.
*   The [Domain-Driven Design (DDD)](docs/1_introduction/glossary.md#ddd-domain-driven-design) context, including relevant [aggregates](docs/1_introduction/glossary.md#ddd-domain-driven-design), [entities](docs/1_introduction/glossary.md#ddd-domain-driven-design), and value objects.
*   Definitions of [repository interfaces](docs/1_introduction/glossary.md#ddd-domain-driven-design) for data persistence.
*   An outline of the service layer logic.
*   Sequence diagrams illustrating key interactions and workflows.
*   Conceptual examples of bot commands or API endpoints related to the feature.
*   Notes on integration with other parts of the system (e.g., dashboards, UI).

## Available Guides

*   **[[Guild Designer Features](./guild_designer/README.md)](docs/1_introduction/glossary.md#guild-designer)**: Documents related to the Guild Designer, including template structure management, channel creation workflows, and permission application logic.

Currently, the primary detailed guide in this section focuses on aspects of the **[Guild Designer](docs/1_introduction/glossary.md#guild-designer)**. As more complex features are documented, they will be added here.

### Other Complex Features (To Be Documented in Detail)

While not yet fully documented in this section, the following are examples of other complex features in FoundryCord that would benefit from similar detailed implementation guides:

*   **[[Dashboard System (Bot & Web)]](docs/1_introduction/glossary.md#dashboard)**: The complete lifecycle and interaction for creating, rendering, and managing dynamic dashboards.
*   **User Authentication Flow (End-to-End)**: The full process of user authentication and authorization across the web and bot components.
*   **System Monitoring & State Display**: The mechanisms for collecting, processing, and displaying system and service metrics.
*   **Channel Follow Feature**: The implementation of following channels from one server to another. 