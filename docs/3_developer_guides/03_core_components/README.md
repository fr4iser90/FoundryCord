# Core Components Internals

This section delves into the specific internal workings of key components within the Bot, Web, and Shared parts of the [FoundryCord](../../../1_introduction/glossary.md#foundrycord) application. It aims to provide developers with a deeper understanding of critical services, domain logic, and significant algorithms.

## Documents

*   **[Bot Internals (`bot_internals.md`)]**: Explores the core application services of the Bot, such as [Dashboard](../../../1_introduction/glossary.md#dashboard) Lifecycle Management, System Monitoring, and Configuration Services. It also details complex workflows like the [Guild Template Application process](../../../1_introduction/glossary.md#guild-designer) and discusses any critical algorithms specific to the bot's functionality.

*   **[Web App Internals (`web_internals.md`)]**: Focuses on the key services within the Web application, including API handlers, view rendering logic, and user session management. It details workflows such as [saving a Guild Template](../../../1_introduction/glossary.md#guild-designer) through the web interface and explains frontend-backend interaction patterns. Placeholder for critical web-specific algorithms.

*   **[Shared Components Internals (`shared_components.md`)]**: Describes crucial shared domain services like Authentication, Authorization, and Auditing. It details important domain [aggregates](../../../1_introduction/glossary.md#ddd-domain-driven-design) (e.g., User, GuildTemplate), outlines the [repository](../../../1_introduction/glossary.md#ddd-domain-driven-design) interfaces for data access, and explains the workings of shared infrastructure pieces like database session management, encryption services, and the centralized logging framework. Placeholder for critical algorithms residing in the shared core. 