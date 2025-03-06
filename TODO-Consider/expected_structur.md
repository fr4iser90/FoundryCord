```plaintext
app/bot/
├── core/
│   ├── __init__.py
│   ├── main.py
│   ├── extensions.py
│   └── lifecycle/
│       └── lifecycle_manager.py
├── domain/
│   ├── auth/
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── role.py
│   │   │   └── permission.py
│   │   └── repositories/
│   │       └── user_repository.py
│   ├── channels/
│   │   ├── models/
│   │   │   ├── channel.py
│   │   │   └── thread.py
│   │   ├── factories/
│   │   │   ├── channel_factory.py
│   │   │   └── thread_factory.py
│   │   └── repositories/
│   │       └── channel_repository.py
│   ├── gameservers/
│   │   ├── models/
│   │   │   ├── server.py
│   │   │   └── player.py
│   │   ├── services/
│   │   │   ├── minecraft_service.py
│   │   │   └── status_service.py
│   │   └── repositories/
│   └── monitoring/
│       ├── models/
│       │   ├── metric.py
│       │   └── alert.py
│       └── collectors/
│           ├── system_collector.py
│           └── service_collector.py
├── infrastructure/
│   ├── database/
│   │   ├── migrations/
│   │   ├── models/
│   │   └── repositories/
│   ├── security/
│   │   ├── encryption/
│   │   │   └── encryption_service.py
│   │   └── key_management/
│   │       └── key_manager.py
│   └── logging/
│       ├── formatters/
│       ├── handlers/
│       └── logging_service.py
├── interfaces/
│   ├── commands/
│   │   ├── admin/
│   │   ├── gameserver/
│   │   └── monitoring/
│   ├── dashboards/
│   │   ├── components/
│   │   │   ├── buttons/
│   │   │   ├── menus/
│   │   │   └── views/
│   │   └── templates/
│   │       ├── monitoring_dashboard.py
│   │       └── gameserver_dashboard.py
│   └── middleware/
│       ├── auth_middleware.py
│       └── rate_limit_middleware.py
├── services/
│   ├── channels/
│   │   ├── channel_setup_service.py
│   │   └── thread_management_service.py
│   ├── monitoring/
│   │   ├── alert_service.py
│   │   └── metric_service.py
│   └── auth/
│       ├── authentication_service.py
│       └── authorization_service.py
├── utils/
│   ├── decorators/
│   ├── formatters/
│   └── validators/
└── tests/
    ├── domain/
    ├── infrastructure/
    ├── interfaces/
    └── services/
```