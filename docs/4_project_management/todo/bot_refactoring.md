# Bot Refactoring Plan: Phase 1 - Dynamische Struktur & Konstantenentfernung

**Ziel:** Umstellung von hardcodierten Konstanten auf eine dynamische, datenbankgesteuerte Konfiguration für Kernkomponenten (Kanäle, Kategorien, Dashboards), basierend auf Guild Templates und Dashboard Templates.

## 1. Kanal- & Kategorie-Management (Fokus: Guild Templates)

*   **Entfernen:** Alle Logik, die `CHANNELS`, `CATEGORIES`, `CATEGORY_CHANNEL_MAPPINGS` aus alten Konstantendateien verwendet, muss entfernt oder ersetzt werden. (Status: `CATEGORIES`-Nutzung in `CategorySetupService` markiert, `ChannelWorkflow` & `CategoryWorkflow` bereinigt, `ChannelBuilder` überprüft - OK, `ChannelConfig` & `GameServerChannelService` offen)
*   **Quelle:** Die Struktur einer Guild (Kanäle, Kategorien, Berechtigungen) wird ausschließlich durch das `active_template_id` in der `guild_configs`-Tabelle und die verknüpften Einträge in `guild_templates`, `guild_template_categories`, `guild_template_channels`, `guild_template_category_permissions`, `guild_template_channel_permissions` definiert.
*   **Refactoring Ziele:**
    *   `ChannelWorkflow` / `CategoryWorkflow` / `GuildWorkflow` (oder ein neuer `GuildSyncWorkflow`?): Müssen Logik enthalten, um beim Bot-Start oder auf Anforderung die Discord-Struktur einer Guild mit dem aktiven Template aus der Datenbank abzugleichen (Kanäle/Kategorien erstellen, löschen, umbenennen, verschieben, Berechtigungen setzen). (Status: `ChannelWorkflow`/`CategoryWorkflow` bereinigt, `GuildWorkflow` enthält `apply_template`-Logik für Sync - OK, benötigt ggf. Feinschliff und Triggerung).
    *   `ChannelSetupService` / `CategorySetupService` / `ChannelBuilder` / `CategoryBuilder`: Müssen überarbeitet werden, um Template-Daten statt statischer Konfigurationen zu verarbeiten. Sie benötigen wahrscheinlich Zugriff auf die entsprechenden Template-Repositories. (Status: `ChannelSetupService` existiert nicht, `CategorySetupService` als veraltet markiert, `ChannelBuilder`/`CategoryBuilder` scheinen OK/datenbankbasiert).
    *   Funktionen wie `get_channel_factory_config`, `repair_channel_mapping`, `validate_channels` in `ChannelConfig` müssen entweder entfernt oder grundlegend überarbeitet werden, um mit Template-Daten zu arbeiten. (Status: Offen - Nächster Schritt)
    *   `GameServerChannelService`: Muss überarbeitet werden, um Kanäle basierend auf dynamischen Konfigurationen (evtl. spezielle Templates?) statt `GameServerChannelConfig` zu erstellen. (Status: Offen)

## 2. Dashboard-Management (Fokus: Entkopplung)

*   **Entfernen:** Alle Logik, die `DASHBOARD_MAPPINGS` und `DASHBOARD_SERVICES` aus alten Konstantendateien verwendet, muss entfernt oder ersetzt werden. (**Erledigt:** Logik auskommentiert/entfernt, `dashboard_config.py` gelöscht, keine Code-Nutzung von `DASHBOARD_SERVICES` gefunden).
*   **Quelle:**
    *   Verfügbare Dashboard-*Typen* und ihre *Komponenten* werden durch `dashboard_component_definitions` (geseeded in `009`) definiert.
    *   Vordefinierte Dashboard-*Layouts* werden in `dashboard_templates` (geseeded in `011`) gespeichert.
    *   Die *aktive Instanz* eines Dashboards in einem Kanal muss neu definiert werden (z.B. über eine neue Tabelle `live_dashboards` oder ähnliches, die `channel_id`, `message_id` und `dashboard_template_id` oder eine benutzerdefinierte `config` speichert).
*   **Rolle von `DashboardCategory`:** Das `DashboardCategory`-Enum dient ausschließlich zur Kategorisierung und Filterung von Dashboard-Templates/-Komponenten (z.B. in der UI oder API). Es wird **nicht** zur dynamischen Auswahl von spezifischer Service-Logik verwendet. Die Logik ergibt sich aus dem gewählten `dashboard_template` und dessen `config`.
*   **Refactoring Ziele:**
    *   `DashboardFactory` / **Controller-Erstellung:** Benötigt einen neuen Mechanismus, um eine Dashboard-Instanz (Ziel: ein generischer `DashboardController`, der `dashboard_templates`/`dashboard_component_definitions` nutzt) für eine bestimmte Konfiguration zu erstellen, anstatt Service-Klassen basierend auf `DASHBOARD_SERVICES` zu laden. (Status: Alter Service-Lade-Mechanismus in `DashboardFactory` ist defekt/markiert. Controller-Instanziierung erfolgt nun vermutlich über `DashboardLifecycleService` / `DashboardRegistry` basierend auf DB-Entitäten).
    *   **Konsolidierung der Controller-Logik:** Logik aus spezifischen Controllern (`dynamic_dashboard.py`, `template_dashboard.py`, etc.) in den `DashboardController` überführen oder veraltete Controller entfernen. `BaseDashboardController` ggf. als Basis beibehalten. (**Erledigt:** `DashboardController` (ehem. Universal) ist der einzige Controller, erbt von `BaseDashboardController`).
    *   **Überprüfung der Service-Verantwortlichkeiten:** Klären, ob `DashboardBuilderService` benötigt wird oder ob dessen Logik (UI-Erstellung aus Config) Teil des `DashboardController` sein soll. (**Erledigt:** UI-Logik in `DashboardController` verschoben. Service zu `DashboardDataService` umbenannt, fokussiert auf Datenbeschaffung).
    *   **Daten-/Konfigurationsgesteuerte Services:** Sicherstellen, dass `DashboardService` und andere Daten-Services daten-/konfigurationsgesteuert sind und keine feste Logik basierend auf `DashboardCategory` enthalten. (Status: `DashboardService` überprüft, scheint OK. `DashboardDataService` ist konfigurationsgesteuert).
    *   `DashboardLifecycleService` / `DashboardSetupService`: Die automatische Erstellung/Aktivierung muss auf der neuen Instanzlogik basieren (z.B. Laden von `live_dashboards`/`DashboardEntity`), nicht auf `DASHBOARD_MAPPINGS`. (Status: `DashboardSetupService` gelöscht. `DashboardLifecycleService` überprüft, TODO für DB-basierte Aktivierung hinzugefügt).
    *   `DashboardWorkflow`: Muss die neue Logik zur Verwaltung von Live-Dashboard-Instanzen implementieren (Erstellen, Aktualisieren, Löschen basierend auf Konfigurationen/Templates). (Status: Überprüft und vereinfacht, verwaltet nur Status. LifecycleService/Registry/Controller übernehmen Logik).
    *   API (`dashboard_controller.py`): Listet bereits `DashboardCategory`-Werte, aber die Logik zur tatsächlichen *Auswahl* und *Konfiguration* eines Dashboards im Frontend muss mit den neuen Tabellen (`dashboard_templates`) interagieren. (Status: API-Controller (`app/web/...`) nicht Teil dieser Phase, aber Backend-Logik im Bot ist vorbereitet).

## 3. Konkrete Überprüfungsliste (Nach Entfernung der OLD-Konstanten)

*   **Code-Logik korrigieren:**
    *   `app/bot/infrastructure/discord/category_setup_service.py`: Verwendet `CATEGORIES`. (Status: Service als veraltet markiert, Logik auskommentiert/als TODO markiert).
    *   ~~`app/bot/infrastructure/discord/dashboard_setup_service.py`: Verwendet `DASHBOARD_MAPPINGS`.~~ (File deleted)
    *   ~~`app/bot/infrastructure/config/services/dashboard_config.py`: Verwendet `dashboard_services`. Prüfen, ob Datei/Logik veraltet ist.~~ (File deleted)
*   **Kommentare entfernen/aktualisieren:** (Alle Erledigt)
    *   ~~`app/bot/infrastructure/config/channel_config.py`: Kommentare bzgl. `CATEGORY_CHANNEL_MAPPINGS`.~~
    *   ~~`app/web/interfaces/api/rest/v1/dashboards/dashboard_controller.py`: Kommentare bzgl. `DASHBOARD_MAPPINGS`.~~
    *   ~~`app/bot/application/services/channel/game_server_channel_service.py`: Kommentare bzgl. `GameServerChannelConfig`.~~
    *   ~~`app/bot/application/services/bot_control_service.py`: Kommentare bzgl. `BotConnector`.~~
    *   ~~`app/web/interfaces/web/views/owner/control_view.py`: Kommentare bzgl. `BotConnector`.~~
    *   ~~`app/web/interfaces/web/views/owner/bot_control_view.py`: Kommentare bzgl. `BotConnector`.~~
