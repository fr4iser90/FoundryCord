Ah, jetzt verstehe ich besser! Ja, lass uns die Struktur basierend auf den existierenden Verzeichnissen und der tatsächlichen Nutzung neu ausrichten:

1. **Shared Layer** (Gemeinsame Infrastruktur & Modelle):
```
shared/
├── domain/          # Gemeinsame Domain-Logik
│   ├── core/       # Kern-Domain-Konzepte
│   │   ├── entities/
│   │   ├── repositories/
│   │   └── services/
│   ├── auth/       # Auth Bounded Context
│   ├── discord/    # Discord Bounded Context
│   └── monitoring/ # Monitoring Bounded Context
│
├── application/    # Gemeinsame Anwendungslogik
│   ├── services/
│   ├── dtos/
│   └── workflows/
│
└── infrastructure/ # Gemeinsame Infrastruktur
    ├── persistence/
    ├── security/
    ├── logging/
    └── config/
```

2. **Bot Layer** (Discord Bot Funktionalität):
```
bot/
├── domain/         # Bot-spezifische Domain-Logik
│   ├── core/      # Kern-Domain-Konzepte
│   │   ├── entities/
│   │   ├── repositories/
│   │   └── services/
│   ├── commands/  # Command Bounded Context
│   ├── events/    # Event Bounded Context
│   └── workflows/ # Workflow Bounded Context
│
├── application/    # Bot-spezifische Anwendungslogik
│   ├── services/
│   ├── dtos/
│   └── workflows/
│
├── infrastructure/ # Bot-spezifische Infrastruktur
│   ├── discord/
│   ├── persistence/
│   └── logging/
│
└── interfaces/     # Bot-Schnittstellen
    ├── commands/
    ├── events/
    └── dashboards/
```

3. **Web Layer** (Web Interface):
```
web/
├── domain/         # Web-spezifische Domain-Logik
│   ├── core/      # Kern-Domain-Konzepte
│   │   ├── entities/
│   │   ├── repositories/
│   │   └── services/
│   ├── auth/      # Web Auth Bounded Context
│   ├── dashboard/ # Dashboard Bounded Context
│   └── admin/     # Admin Bounded Context
│
├── application/    # Web-spezifische Anwendungslogik
│   ├── services/
│   ├── dtos/
│   └── workflows/
│
├── infrastructure/ # Web-spezifische Infrastruktur
│   ├── fastapi/
│   ├── persistence/
│   └── security/
│
└── interfaces/     # Web-Schnittstellen
    ├── api/
    │   └── v1/
    ├── web/
    │   ├── views/
    │   ├── templates/
    │   └── static/
    └── admin/
```

Die wichtigsten Prinzipien:

1. **Shared Layer**:
- Enthält alle gemeinsamen Komponenten
- PostgreSQL-Modelle und -Migrations
- Gemeinsame Repository-Interfaces
- Basis-Infrastruktur (Logging, Security, etc.)

2. **Bot Layer**:
- Fokussiert auf Discord-Bot-Funktionalität
- Nutzt Shared-Layer für Datenzugriff
- Eigene Domain-Logik für Bot-spezifische Features
- Workflows für Bot-Prozesse

3. **Web Layer**:
- Fokussiert auf Web-Interface
- Nutzt Shared-Layer für Datenzugriff
- Eigene Domain-Logik für Web-spezifische Features
- REST API und Web-Views

Die Vorteile dieser Struktur:

1. **Klarere Trennung**:
- Bot und Web sind klar getrennt
- Shared-Komponenten sind zentralisiert
- Jeder Layer hat klare Verantwortlichkeiten

2. **Bessere Wartbarkeit**:
- Weniger Duplikation durch Shared-Layer
- Klare Abhängigkeiten
- Einfacher zu erweitern

3. **DDD-Konform**:
- Klare Domain-Grenzen
- Repository-Pattern
- Service-Layer für Business-Logik

4. **Flexibilität**:
- Bot und Web können unabhängig entwickelt werden
- Shared-Layer kann von beiden genutzt werden
- Einfach neue Features hinzuzufügen

Möchtest du, dass ich mit der Umstrukturierung eines bestimmten Bereichs beginne? Zum Beispiel könnten wir mit der Migration der Shared-Komponenten anfangen.
