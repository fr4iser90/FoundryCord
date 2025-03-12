HomeLab Discord Bot
│
├── app/
│   ├── shared/               # Gemeinsame Module
│   │   ├── auth/             # Authentifizierungslogik
│   │   ├── models/           # Gemeinsame Datenmodelle
│   │   └── utils/            # Hilfsfunktionen
│   │
│   ├── bot/                  # Discord Bot
│   │   ├── commands/         # Bot-Befehle
│   │   ├── events/           # Event-Handler
│   │   └── api/              # API für Web-Kommunikation
│   │
│   └── web/                  # Web-Interface
│       ├── api/              # Web APIs
│       ├── routes/           # Web-Routen
│       └── dashboard/        # Dashboard-Komponenten
│
└── database/                 # Gemeinsame Datenbankschicht