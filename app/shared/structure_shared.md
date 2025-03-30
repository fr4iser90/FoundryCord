# HomeLab Discord Bot - Shared Package Architektur

Die `app/shared/` Verzeichnisstruktur folgt den Prinzipien von Domain-Driven Design (DDD) und Clean Architecture mit einer klaren Schichtentrennung:

## Schichten-Übersicht

- **Domain**: Enthält Geschäftslogik, Entitäten und Interfaces
- **Infrastructure**: Enthält technische Implementierungen und Datenbankkommunikation
- **Application**: Enthält anwendungsspezifische Dienste und Prozesse
- **Interface**: Enthält öffentliche APIs für externe Komponenten

## Hauptverzeichnisse

### Domain (`app/shared/domain/`)
Geschäftliche Kernlogik des Systems, unabhängig von technischen Details:
- **auth**: Authentifizierung und Autorisierung
- **discord**: Discord-spezifische Domänenlogik
- **monitoring**: System-Monitoring-Konzepte
- **dashboard**: Dashboard-Management
- **audit**: Audit-Logging für geschäftliche Aktionen
- **projects**: Projekt- und Aufgabenverwaltung

### Infrastructure (`app/shared/infrastructure/`)
Technische Implementierungen und externe Anbindungen:
- **models**: SQLAlchemy-Datenbankmodelle
- **repositories**: Implementierungen der Domain-Repository-Interfaces
- **database**: Datenbankverbindung und -konfiguration
- **logging**: Technisches Logging
- **encryption**: Verschlüsselungsdienste
- **security**: Sicherheitsdienste

### Application (`app/shared/application/`)
Anwendungsspezifische Dienste:
- **logging**: Anwendungsspezifische Logging-Konfiguration
- **tasks**: Hintergrund- und geplante Aufgaben

### Interface (`app/shared/interface/`)
Externe Schnittstellen:
- **logging**: Öffentliche Logging-API

## Architekturprinzipien

1. **Abhängigkeitsregel**: Innere Schichten (Domain) kennen äußere Schichten (Infrastructure) nicht
2. **Dependency Inversion**: Abhängigkeiten zeigen nach innen durch Interfaces
3. **Geschäftslogik-Isolation**: Domänenlogik ist unabhängig von technischen Details
4. **Repository-Muster**: Datenzugriff über Repositories abstrahiert
