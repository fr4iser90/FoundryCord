app/
├── bot/                                    # Bot-Anwendung
│   ├── domain/                             # Domain-Schicht (Domänenlogik)
│   │   ├── categories/                     # Kategorie-Domain
│   │   │   ├── services/                   # Domain-Services
│   │   │   │   └── category_validator.py   # Validierungsregeln
│   │   │   ├── exceptions/                 # Domain-spezifische Exceptions
│   │   │   │   └── category_exceptions.py  # Fehlerklassen
│   │   │   └── events/                     # Domain-Events
│   │   │       └── category_events.py      # Event-Klassen
│   │   │
│   │   ├── channels/                       # Kanal-Domain
│   │   │   ├── services/                   # Domain-Services
│   │   │   │   └── channel_validator.py    # Validierungsregeln
│   │   │   ├── exceptions/                 # Domain-spezifische Exceptions
│   │   │   │   └── channel_exceptions.py   # Fehlerklassen
│   │   │   └── events/                     # Domain-Events
│   │   │       └── channel_events.py       # Event-Klassen
│   │   │
│   │   ├── guilds/                         # Guild-Domain
│   │   │   ├── services/                   # Domain-Services
│   │   │   │   └── guild_validator.py      # Validierungsregeln
│   │   │   ├── exceptions/                 # Domain-spezifische Exceptions
│   │   │   │   └── guild_exceptions.py     # Fehlerklassen
│   │   │   └── events/                     # Domain-Events
│   │   │       └── guild_events.py         # Event-Klassen
│   │   │
│   │   ├── dashboards/                     # Dashboard-Domain
│   │   │   ├── services/                   # Domain-Services
│   │   │   │   └── component_resolver.py   # Komponentenauflösung
│   │   │   ├── exceptions/                 # Domain-spezifische Exceptions
│   │   │   │   └── dashboard_exceptions.py # Fehlerklassen
│   │   │   └── events/                     # Domain-Events
│   │   │       └── dashboard_events.py     # Event-Klassen
│   │   │
│   │   ├── monitoring/                     # Monitoring-Domain
│   │   │   ├── services/                   # Domain-Services
│   │   │   │   └── threshold_analyzer.py   # Schwellenwertanalyse
│   │   │   └── events/                     # Domain-Events
│   │   │       └── monitoring_events.py    # Event-Klassen
│   │   │
│   │   ├── projects/                       # Projekt-Domain
│   │   │   ├── services/                   # Domain-Services
│   │   │   │   └── task_scheduler.py       # Aufgabenplanung
│   │   │   └── events/                     # Domain-Events
│   │   │       └── project_events.py       # Event-Klassen
│   │   │
│   │   ├── wireguard/                      # VPN-Domain
│   │   │   └── services/                   # Domain-Services
│   │   │       └── config_generator.py     # Konfigurationsgenerator
│   │   │
│   │   └── common/                         # Gemeinsame Domain-Komponenten
│   │       ├── events/                     # Event-System
│   │       │   ├── event.py                # Basis-Event
│   │       │   └── event_dispatcher.py     # Event-Dispatcher
│   │       └── exceptions/                 # Allgemeine Exceptions
│   │           └── domain_exceptions.py    # Basis-Exceptions
│   │
│   ├── application/                        # Anwendungsschicht (Use Cases)
│   │   ├── services/                       # Anwendungsservices
│   │   │   ├── core/                       # Kern-Services
│   │   │   │   ├── database_service.py     # Datenbankdienst
│   │   │   │   ├── config_service.py       # Konfigurationsdienst
│   │   │   │   └── auth_service.py         # Authentifizierungsdienst
│   │   │   │
│   │   │   ├── discord/                    # Discord-Services
│   │   │   │   ├── guild_service.py        # Guild-Management
│   │   │   │   ├── category_service.py     # Kategorie-Management
│   │   │   │   ├── channel_service.py      # Kanal-Management
│   │   │   │   └── message_service.py      # Nachrichtendienst
│   │   │   │
│   │   │   ├── dashboard/                  # Dashboard-Services
│   │   │   │   ├── dashboard_service.py    # Dashboard-Hauptdienst
│   │   │   │   ├── component_service.py    # Komponentendienst
│   │   │   │   └── data_source_service.py  # Datenquellendienst
│   │   │   │
│   │   │   ├── monitoring/                 # Monitoring-Services
│   │   │   │   ├── metrics_service.py      # Metrikendienst
│   │   │   │   └── alert_service.py        # Alarmdienst
│   │   │   │
│   │   │   ├── projects/                   # Projekt-Services
│   │   │   │   ├── project_service.py      # Projektdienst
│   │   │   │   └── task_service.py         # Aufgabendienst
│   │   │   │
│   │   │   └── wireguard/                  # VPN-Services
│   │   │       └── wireguard_service.py    # VPN-Konfigurationsdienst
│   │   │
│   │   ├── commands/                       # Command-Handler (CQRS)
│   │   │   ├── guild/                      # Guild-Commands
│   │   │   │   ├── create_guild.py         # Guild erstellen
│   │   │   │   └── update_guild.py         # Guild aktualisieren
│   │   │   ├── category/                   # Kategorie-Commands
│   │   │   │   ├── create_category.py      # Kategorie erstellen
│   │   │   │   └── update_category.py      # Kategorie aktualisieren
│   │   │   ├── channel/                    # Kanal-Commands
│   │   │   │   ├── create_channel.py       # Kanal erstellen
│   │   │   │   └── update_channel.py       # Kanal aktualisieren
│   │   │   └── dashboard/                  # Dashboard-Commands
│   │   │       ├── create_dashboard.py     # Dashboard erstellen
│   │   │       └── update_dashboard.py     # Dashboard aktualisieren
│   │   │
│   │   ├── queries/                        # Query-Handler (CQRS)
│   │   │   ├── guild/                      # Guild-Queries
│   │   │   │   ├── get_guild.py            # Guild abrufen
│   │   │   │   └── list_guilds.py          # Guilds auflisten
│   │   │   ├── category/                   # Kategorie-Queries
│   │   │   │   ├── get_category.py         # Kategorie abrufen
│   │   │   │   └── list_categories.py      # Kategorien auflisten
│   │   │   ├── channel/                    # Kanal-Queries
│   │   │   │   ├── get_channel.py          # Kanal abrufen
│   │   │   │   └── list_channels.py        # Kanäle auflisten
│   │   │   └── dashboard/                  # Dashboard-Queries
│   │   │       ├── get_dashboard.py        # Dashboard abrufen
│   │   │       └── list_dashboards.py      # Dashboards auflisten
│   │   │
│   │   └── processes/                      # Hintergrundaufgaben
│   │       ├── cleanup_tasks.py            # Aufräumaufgaben
│   │       ├── monitoring_tasks.py         # Überwachungsaufgaben
│   │       └── schedule_tasks.py           # Zeitgesteuerte Aufgaben
│   │
│   ├── infrastructure/                     # Infrastrukturschicht
│   │   ├── registry/                       # Service-Registry
│   │   │   ├── service_registry.py         # Hauptservice-Registry
│   │   │   └── factory.py                  # Service-Factory
│   │   │
│   │   ├── discord/                        # Discord-API-Infrastruktur
│   │   │   ├── client/                     # Discord-Client-Wrapper
│   │   │   │   └── discord_client.py       # Discord-Client
│   │   │   ├── guild/                      # Guild-Infrastruktur
│   │   │   │   └── guild_manager.py        # Guild-Manager
│   │   │   ├── category/                   # Kategorie-Infrastruktur
│   │   │   │   └── category_manager.py     # Kategorie-Manager
│   │   │   └── channel/                    # Kanal-Infrastruktur
│   │   │       └── channel_manager.py      # Kanal-Manager
│   │   │
│   │   ├── factories/                      # Factories für komplexe Objekte
│   │   │   ├── component/                  # Komponentenfactories
│   │   │   │   ├── component_factory.py    # Komponentenfactory
│   │   │   │   └── component_registry.py   # Komponentenregistry
│   │   │   ├── data_source/                # Datenquellenfactories
│   │   │   │   ├── data_source_factory.py  # Datenquellenfactory
│   │   │   │   └── data_source_registry.py # Datenquellenregistry
│   │   │   └── service/                    # Servicefactories
│   │   │       └── service_factory.py      # Servicefactory
│   │   │
│   │   ├── config/                         # Konfigurationsinfrastruktur
│   │   │   ├── config_provider.py          # Konfigurationsanbieter
│   │   │   └── config_loader.py            # Konfigurationslader
│   │   │
│   │   ├── logging/                        # Logging-Infrastruktur
│   │   │   ├── logger.py                   # Logger-Konfiguration
│   │   │   └── log_formatter.py            # Log-Formatter
│   │   │
│   │   ├── security/                       # Sicherheitsinfrastruktur
│   │   │   ├── auth/                       # Authentifizierung
│   │   │   │   ├── authenticator.py        # Authentifikator
│   │   │   │   └── token_service.py        # Token-Service
│   │   │   └── permissions/                # Berechtigungen
│   │   │       └── permission_checker.py   # Berechtigungsprüfer
│   │   │
│   │   ├── api/                            # API-Client für Bot
│   │   │   ├── client/                     # HTTP-Client
│   │   │   │   └── api_client.py           # API-Client-Implementierung
│   │   │   └── models/                     # API-Modelle
│   │   │       └── response_models.py      # Antwortmodelle
│   │   │
│   │   └── messaging/                      # Messaging-Infrastruktur
│   │       ├── event_bus.py                # Event-Bus
│   │       └── message_broker.py           # Message-Broker
│   │
│   ├── interfaces/                         # Schnittstellenschicht
│   │   └── discord/                        # Discord-Schnittstellen
│   │       ├── commands/                   # Discord-Bot-Befehle
│   │       │   ├── guild_commands.py       # Guild-Befehle
│   │       │   ├── category_commands.py    # Kategorie-Befehle
│   │       │   ├── channel_commands.py     # Kanal-Befehle
│   │       │   └── dashboard_commands.py   # Dashboard-Befehle
│   │       ├── cogs/                       # Discord-Cogs
│   │       │   ├── admin_cog.py            # Admin-Cog
│   │       │   ├── category_cog.py         # Kategorie-Cog
│   │       │   ├── channel_cog.py          # Kanal-Cog
│   │       │   └── dashboard_cog.py        # Dashboard-Cog
│   │       ├── events/                     # Discord-Event-Handler
│   │       │   ├── guild_events.py         # Guild-Events
│   │       │   ├── message_events.py       # Nachrichtenereignisse
│   │       │   └── reaction_events.py      # Reaktionsereignisse
│   │       └── views/                      # Discord-UI-Views
│   │           ├── dashboard_view.py       # Dashboard-View
│   │           ├── button_view.py          # Button-View
│   │           └── modal_view.py           # Modal-View
│   │
│   ├── core/                               # Kernanwendungslogik
        ├── bot.py                          # Hauptbot-Klasse
│   │   ├── service_registry.py             # Service-Registry
│   │   ├── lifecycle_manager.py            # Lebenszyklus-Manager
│   │   ├── main.py                         # Anwendungseinstiegspunkt
        └── extension_loader.py             # Erweiterungslader