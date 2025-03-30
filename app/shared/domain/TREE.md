app/shared/domain/
  ├── auth/                  # Authentifizierung/Autorisierung
  │   ├── models/            # User, Role, Permission
  │   ├── repositories/      # Auth-Repositories
  │   ├── services/          # Auth-Services
  │   └── policies/          # Auth-Policies
  │
  ├── discord/               # Discord-Domäne
  │   ├── models/            # Channel, Category, Message
  │   ├── repositories/      # Discord-Repositories
  │   └── services/          # Discord-Services
  │
  ├── monitoring/            # Überwachungsdomäne
  │   ├── models/            # Metric, Alert
  │   ├── repositories/      # Monitoring-Repositories 
  │   └── services/          # Monitoring-Services
  │
  ├── projects/              # Projektdomäne
  │   ├── models/            # Project, Task
  │   ├── repositories/      # Project-Repositories
  │   └── services/          # Project-Services
  │
  ├── audit/                 # Audit/Logging-Domäne
  │   ├── models/            # AuditLog, LogEntry
  │   ├── repositories/      # Audit-Repositories
  │   └── services/          # Audit-Services
  │
  └── dashboard/             # Dashboard-Domäne
      ├── models/            # Dashboard, Component
      ├── repositories/      # Dashboard-Repositories
      └── services/          # Dashboard-Services