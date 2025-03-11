app/
├── bot/
    ├── application/
    │   ├── services/                    # Application services orchestrating domain objects
    │   │   ├── admin/                   # Admin-related services
    │   │   ├── analytics/               # Analytics and reporting services
    │   │   ├── channel/                 # Channel management services
    │   │   ├── dashboard/               # Dashboard services
    │   │   ├── events/                  # Event coordination services
    │   │   ├── integration/             # Integration services with external systems
    │   │   ├── monitoring/              # Monitoring orchestration services
    │   │   ├── notification/            # Notification delivery services
    │   │   └── wireguard/               # Wireguard VPN services
    │   │
    │   ├── handlers/                    # Application event handlers
    │   │   ├── command_handlers/        # Command processing handlers
    │   │   ├── event_handlers/          # Discord event handlers
    │   │   └── error_handlers/          # Error handling strategies
    │   │
    │   ├── orchestrators/               # Process orchestrators
    │   │   ├── setup_orchestrator.py
    │   │   └── integration_orchestrator.py
    │   │
    │   └── tasks/                       # Background and scheduled tasks
    │       ├── cleanup_tasks/           # Cleanup operation tasks
    │       ├── maintenance_tasks/       # System maintenance tasks
    │       ├── notification_tasks/      # Scheduled notifications
    │       └── security_tasks/          # Security-related tasks
    │
    ├── core/                            # Core application components
    │   ├── bootstrap/                   # Application bootstrapping
    │   │   ├── initializers/            # Component initializers
    │   │   └── startup.py               # Startup sequence
    │   │
    │   ├── context/                     # Application context
    │   │   └── application_context.py
    │   │
    │   ├── extensions/                  # System extensions
    │   │   ├── extension_loader.py
    │   │   └── extension_registry.py
    │   │
    │   ├── lifecycle/                   # Application lifecycle
    │   │   ├── lifecycle_events.py
    │   │   └── lifecycle_manager.py
    │   │
    │   ├── settings/                    # Application settings
    │   │   └── settings_manager.py
    │   │
    │   └── workflows/                   # Process orchestration
    │       ├── base_workflow.py
    │       ├── category_workflow.py
    │       ├── channel_workflow.py
    │       ├── dashboard_workflow.py
    │       ├── database_workflow.py
    │       ├── service_workflow.py
    │       ├── slash_commands_workflow.py
    │       └── task_workflow.py
    │
    ├── domain/                          # Business domains
    │   ├── analytics/                   # Analytics domain
    │   │   ├── models/                  # Analytics entities
    │   │   ├── repositories/            # Analytics repository interfaces
    │   │   └── services/                # Analytics domain services
    │   │
    │   ├── auth/                        # Authentication domain
    │   │   ├── events/                  # Auth-related domain events
    │   │   ├── exceptions/              # Auth-specific exceptions
    │   │   ├── models/                  # Domain entities (User, Role, etc.)
    │   │   ├── repositories/            # Repository interfaces only
    │   │   ├── policies/                # Business rules
    │   │   ├── services/                # Domain services (business logic)
    │   │   └── value_objects/           # Auth-related value objects
    │   │
    │   ├── gameservers/                 # Game server domain
    │   │   ├── collectors/              # Game server data collectors (interfaces)
    │   │   ├── events/                  # Game server domain events
    │   │   ├── exceptions/              # Game server domain exceptions
    │   │   ├── models/                  # Game server domain models
    │   │   ├── repositories/            # Game server repository interfaces
    │   │   ├── services/                # Game server domain services
    │   │   └── value_objects/           # Game server value objects
    │   │
    │   ├── monitoring/                  # Monitoring domain
    │   │   ├── collectors/              # Monitoring data collection interfaces
    │   │   ├── events/                  # Monitoring domain events
    │   │   ├── exceptions/              # Monitoring-specific exceptions
    │   │   ├── models/                  # Domain models for metrics, alerts
    │   │   ├── repositories/            # Repository interfaces
    │   │   ├── policies/                # Alert policies, thresholds
    │   │   ├── services/                # Domain services for monitoring logic
    │   │   └── value_objects/           # Monitoring value objects
    │   │
    │   ├── notification/                # Notification domain
    │   │   ├── models/                  # Notification message models
    │   │   ├── repositories/            # Notification repository interfaces
    │   │   ├── services/                # Notification domain services
    │   │   └── strategies/              # Notification delivery strategies
    │   │
    │   ├── security/                    # Security domain (consolidated)
    │   │   ├── events/                  # Security-related domain events
    │   │   ├── exceptions/              # Security-specific exceptions
    │   │   ├── models/                  # Security models
    │   │   ├── policies/                # Security rules
    │   │   ├── repositories/            # Security repository interfaces
    │   │   ├── services/                # Security domain services
    │   │   └── value_objects/           # Security-related value objects
    │   │
    │   ├── tracker/                     # Project tracker domain
    │   │   ├── models/                  # Project models
    │   │   ├── repositories/            # Tracker repository interfaces
    │   │   └── services/                # Tracker domain services
    │   │
    │   └── wireguard/                   # Wireguard domain
    │       ├── models/                  # Wireguard configuration models
    │       ├── repositories/            # Wireguard repository interfaces
    │       └── services/                # Wireguard domain services
    │
    ├── infrastructure/                  # Technical infrastructure
    │   ├── adapters/                    # External system adapters
    │   │   ├── discord_adapter.py       # Discord API integration
    │   │   ├── prometheus_adapter.py    # Prometheus metrics integration
    │   │   └── ssh_adapter.py           # SSH connection adapter
    │   │
    │   ├── caching/                     # Caching mechanisms
    │   │   ├── cache_manager.py
    │   │   └── providers/               # Different cache implementations
    │   │
    │   ├── config/                      # Configuration
    │   │   ├── constants/               # System constants
    │   │   ├── providers/               # Config providers (env, file, etc.)
    │   │   └── validators/              # Config validation
    │   │
    │   ├── converters/                  # Data converters
    │   │   ├── discord_converters.py
    │   │   └── model_converters.py
    │   │
    │   ├── database/                    # Database infrastructure
    │   │   ├── connection/              # Database connection management
    │   │   │   └── connection_pool.py
    │   │   ├── management/              # Database management
    │   │   │   └── credential_manager.py
    │   │   ├── migrations/              # Database schema migrations
    │   │   ├── models/                  # ORM models
    │   │   └── repositories/            # Repository implementations
    │   │       ├── auth/                # Auth repository implementations
    │   │       ├── gameservers/         # Game server repository implementations
    │   │       ├── monitoring/          # Monitoring repository implementations
    │   │       └── security/            # Security repository implementations
    │   │
    │   ├── discord/                     # Discord integration
    │   │   ├── api/                     # Discord API clients
    │   │   ├── events/                  # Discord event handlers
    │   │   └── rate_limiting/           # Discord rate limit handling
    │   │
    │   ├── encryption/                  # Encryption services
    │   │   ├── providers/               # Encryption implementations
    │   │   └── encryption_service.py    # Encryption service implementation
    │   │
    │   ├── event_bus/                   # Internal event messaging
    │   │   ├── event_dispatcher.py
    │   │   └── event_subscribers.py
    │   │
    │   ├── factories/                   # Object factories
    │   │   ├── command_factory.py       # Command object creation
    │   │   ├── embed_factory.py         # Discord embed creation
    │   │   └── service_factory.py       # Service instance creation
    │   │
    │   ├── logging/                     # Logging infrastructure
    │   │   ├── formatters/              # Log message formatters
    │   │   ├── handlers/                # Log output handlers
    │   │   └── logger.py                # Logger implementation
    │   │
    │   ├── managers/                    # Technical lifecycle managers
    │   │   ├── connection_manager.py    # Connection lifecycle management
    │   │   ├── dashboard_manager.py     # Dashboard lifecycle management
    │   │   └── key_manager.py           # Encryption key lifecycle management
    │   │
    │   ├── messaging/                   # Messaging infrastructure
    │   │   ├── formatters/              # Message formatters
    │   │   └── providers/               # Message delivery providers
    │   │
    │   ├── observability/               # System observability
    │   │   ├── metrics/                 # System metrics collection
    │   │   └── tracing/                 # Distributed tracing
    │   │
    │   ├── rate_limiting/               # Rate limit infrastructure
    │   │   └── rate_limiter.py
    │   │
    │   ├── resolvers/                   # Resource resolvers
    │   │   └── dependency_resolver.py   # Dependency injection implementation
    │   │
    │   ├── security/                    # Security implementation
    │   │   ├── authentication/          # Authentication implementation
    │   │   ├── authorization/           # Authorization implementation
    │   │   └── key_management/          # Key management implementation
    │   │
    │   ├── storage/                     # Storage mechanisms
    │   │   ├── file_storage.py          # File storage implementation
    │   │   └── object_storage.py        # Object storage implementation
    │   │
    │   └── collectors/                  # Implementation of collectors
    │       ├── gameserver_collector/    # Game server collectors implementation
    │       │   └── minecraft_collector.py
    │       ├── system_collector/        # System metrics collectors
    │       │   ├── cpu_collector.py
    │       │   ├── memory_collector.py
    │       │   └── network_collector.py
    │       └── service_collector/       # Service status collectors
    │           ├── docker_collector.py
    │           └── web_service_collector.py
    │
    ├── interfaces/                      # User interfaces
    │   ├── api/                         # API endpoints (if applicable)
    │   │   └── routes/
    │   │
    │   ├── commands/                    # Discord commands
    │   │   ├── admin/                   # Admin commands
    │   │   ├── auth/                    # Authentication commands
    │   │   ├── gameserver/              # Game server management commands
    │   │   ├── monitoring/              # System monitoring commands
    │   │   ├── tracker/                 # Project tracker commands
    │   │   ├── wireguard/               # VPN management commands
    │   │   └── utils/                   # Utility commands
    │   │
    │   ├── dashboards/                  # Dashboard UI
    │   │   ├── components/              # UI components
    │   │   │   ├── admin/               # Admin dashboard components
    │   │   │   ├── buttons/             # Button components
    │   │   │   ├── common/              # Common UI components
    │   │   │   ├── embeds/              # Embed templates
    │   │   │   ├── modals/              # Modal dialogs
    │   │   │   ├── selectors/           # Selection components
    │   │   │   └── views/               # View components
    │   │   │
    │   │   ├── factories/               # UI component factories
    │   │   └── ui/                      # Complete dashboard UIs
    │   │       ├── gameserver_dashboard.py
    │   │       ├── monitoring_dashboard.py
    │   │       └── welcome_dashboard.py
    │   │
    │   ├── events/                      # Discord event handlers
    │   │   ├── member_events.py
    │   │   └── message_events.py
    │   │
    │   ├── webhooks/                    # Webhook handlers
    │   │   └── github_webhook.py
    │   │
    │   └── homelab_commands.py          # Main command group
    │
    ├── logs/                            # Application logs directory
    │   └── homelab_bot.log
    │
    ├── presentation/                    # Presentation logic
    │   ├── formatters/                  # Output formatting
    │   │   ├── embed_formatter.py
    │   │   └── message_formatter.py
    │   │
    │   ├── viewmodels/                  # View models
    │   │   ├── dashboard_viewmodel.py
    │   │   └── monitoring_viewmodel.py
    │   │
    │   └── views/                       # View templates
    │       └── templates/
    │
    └── utils/                           # General utilities
        ├── constants/                   # Global constants
        │   └── error_messages.py
        │
        ├── decorators/                  # Function decorators
        │   ├── auth.py                  # Authentication decorators
        │   ├── caching.py               # Cache decorators
        │   ├── logging.py               # Logging decorators
        │   └── respond.py               # Response decorators
        │
        ├── formatters/                  # Text/data formatters
        │   ├── chunk_manager.py
        │   └── response_mode.py
        │
        ├── helpers/                     # Helper functions
        │   ├── date_helpers.py
        │   ├── string_helpers.py
        │   └── validation_helpers.py
        │
        ├── http_client.py               # HTTP utility
        ├── message_sender.py            # Message sending utility
        └── vars.py                      # Global variables