```plaintext
app/
├── bot/
│   ├── core/                      # Kern-Komponenten
│   │   ├── commands/              # Basis-Command-Implementierungen
│   │   ├── repositories/          # Daten-Zugriffs-Layer
│   │   │   ├── base_repository.py
│   │   │   ├── user_repository.py
│   │   │   └── settings_repository.py
│   │   ├── services/             # Basis-Services
│   │   │   ├── auth/
│   │   │   ├── logging/
│   │   │   └── encryption/
│   │   ├── factories/            # Factories für Objekt-Erstellung
│   │   └── domain/              # Domain-Modelle & Geschäftslogik
│   │       ├── models/
│   │       └── exceptions/
│   ├── infrastructure/          # Technische Implementierungen
│   │   ├── database/
│   │   │   ├── migrations/
│   │   │   └── models/
│   │   └── external/           # Externe Dienste-Integration
│   │       ├── docker_client/
│   │       └── wireguard_client/
│   ├── modules/                # Ihre Haupt-Module
│   │   ├── docker/            # Docker-Management
│   │   │   ├── commands/
│   │   │   ├── services/
│   │   │   └── repositories/
│   │   ├── wireguard/         # Wireguard-VPN
│   │   │   ├── commands/
│   │   │   ├── services/
│   │   │   └── repositories/
│   │   ├── owncloud/          # Owncloud-Integration
│   │   │   ├── commands/
│   │   │   ├── services/
│   │   │   └── repositories/
│   │   └── monitoring/        # System-Monitoring
│   │       ├── commands/
│   │       ├── services/
│   │       └── collectors/
│   ├── presentation/          # Discord-Interface
│   │   ├── cogs/             # Discord Cogs
│   │   │   ├── docker_cog.py
│   │   │   ├── wireguard_cog.py
│   │   │   └── monitoring_cog.py
│   │   └── views/            # UI-Komponenten
│   │       ├── buttons/
│   │       └── embeds/
│   └── tasks/                # Periodische Tasks
│       ├── cleanup/
│       ├── monitoring/
│       └── backup/
└── tests/                    # Tests
    ├── unit/
    ├── integration/
    └── e2e/
```