
Okay, das ist genau der richtige Zeitpunkt, um innezuhalten und das große Ganze zu betrachten! Du hast völlig recht, die aktuelle Situation mit den Workflows und der Datenbank ist ein Mischmasch aus alt und neu und muss dringend klar strukturiert werden, damit der Designer-Ansatz funktioniert.

Lass uns das mal entwirren:

**1. Was die Workflows AKTUELL tun (vereinfacht):** []

*   **`GuildTemplateWorkflow`:** (Neu & Gut) Liest beim "Approve" den **IST-Zustand** von Discord (Kategorien, Kanäle, Rollen/Permissions) und speichert ihn als **Snapshot/Template** in die `guild_template_*`-Tabellen. Das funktioniert.
*   **`CategoryWorkflow` & `ChannelWorkflow`:** (Alt & Problematisch) Sind darauf ausgelegt, beim Initialisieren eines Servers (`initialize_for_guild`) nach **globalen Default-Definitionen** in den Tabellen `discord_categories` und `discord_channels` zu suchen und diese dann auf dem Server zu erstellen/syncen. Sie scheitern jetzt, weil diese globalen Defaults nicht (mehr) in der DB sind (siehe die Fehlermeldungen "No categories found"). Sie wissen nichts vom neuen, server-spezifischen Template.
*   **`DashboardWorkflow`:** (Separates Thema, aber auch alt) Versucht, Dashboards basierend auf Einträgen in `dashboard_instances` zu initialisieren. Diese Tabelle ist aber aktuell auch nicht richtig mit den Servern/Kanälen verknüpft (siehe unten).


**2. Dein Ziel & Wie die Workflows Funktionieren SOLLTEN:** []

*   **Keine globalen Defaults mehr:** Die Tabellen `discord_categories` und `discord_channels` sollten keine Struktur mehr vorgeben. Die alten Seeds (`002_seed_categories.py`, `003_seed_channels.py`) sind, wie du sagst, obsolet für diesen Zweck.
*   **Template ist die Wahrheit:** Die `guild_template_*`-Tabellen (die ja schon befüllt werden) sollen die **einzige Quelle** sein, die definiert, wie ein Server strukturiert sein soll (Kategorien, Kanäle, Permissions).
*   **Web Designer:** Das Webinterface liest und **schreibt** in diese `guild_template_*`-Tabellen für den jeweiligen Server.
*   **Bot als "Anwender":** Wenn ein Server gestartet wird (oder vielleicht auf Knopfdruck "Template anwenden" im Designer), soll der Bot:
    1.  Das **aktuelle Template** für diesen Guild aus den `guild_template_*`-Tabellen laden.
    2.  Die Struktur auf Discord entsprechend **anpassen** (Kategorien/Kanäle erstellen/umbenennen/löschen, Permissions setzen).
    3.  Dashboards/Interaktive Embeds in die richtigen Kanäle posten/updaten, basierend auf Verknüpfungen im Template.

**3. Was sich an den Tabellen ändern muss (Bezug auf `001_create_tables.py`):** []

*   **`discord_categories` & `discord_channels`:** Diese Tabellen sind für die Serverstruktur **überflüssig** geworden. Die Definitionen kommen jetzt aus `guild_template_categories` und `guild_template_channels`. Wir sollten sie für diesen Zweck ignorieren oder sogar leeren/entfernen (wenn sie nicht für andere Zwecke gebraucht werden).
*   **`dashboard_instances` (oder `dashboards` im Model `DashboardEntity`):** Diese Tabelle muss **dringend** überarbeitet werden, um Guild-spezifisch zu sein!
    *   **`guild_id` hinzufügen:** Sie braucht eine Spalte `guild_id`, die auf `discord_guilds.guild_id` verweist.
    *   **Kanal-Verknüpfung:** Statt einer `channel_id`, die eine Discord-ID sein soll (was sich ändern kann), sollte sie besser eine `guild_template_channel_id` haben, die auf `guild_template_channels.id` verweist. Damit ist klar, in welchen *im Template definierten* Kanal dieses Dashboard gehört. Diese Spalte sollte `nullable=True` sein, da nicht jeder Kanal ein Dashboard hat.
    *   **`message_id`:** Diese Spalte (die die Discord-ID der geposteten Nachricht speichert) sollte `nullable=True` sein, da die Nachricht erst beim Anwenden des Templates erstellt wird.
    *   **Seed (`004_seed_dashboards.py`):** Dieser Seed ist in seiner jetzigen Form nutzlos, da er globale Dashboards erstellt, die nicht richtig verknüpft sind. Er muss entfernt oder komplett überarbeitet werden, um vielleicht *Dashboard-Typen* oder *Komponenten-Vorlagen* zu definieren, aber nicht die Instanzen selbst.
*   **`category_mappings`, `channel_mappings`:** Diese Tabellen scheinen ein älterer Ansatz zu sein, um Namen auf Discord-IDs zu mappen. Sie überschneiden sich jetzt mit den `guild_template_*`-Tabellen und sind wahrscheinlich auch überflüssig oder müssen in das neue Konzept integriert werden.

**4. Umbenennung "Dashboard" / "Interactive Embed":** []

*   Du hast recht, "Dashboard" ist vielleicht nicht der beste Name für das, was es ist (eine interaktive Nachricht, die vom Bot verwaltet wird). "Interactive Embed" oder "Managed Message" wäre präziser.
*   **Vorschlag:** Lass uns vorerst bei "Dashboard" bleiben, da es tief im Code verankert ist (Workflow, Service, Tabellen, Entities). Eine Umbenennung ist ein größeres Refactoring, das wir später angehen können, wenn die Grundfunktionen stehen. Aber behalten wir es im Hinterkopf!

**5. Shared Data:** []

*   Momentan speichern die Templates alles pro Guild.
*   Was "shared" sein könnte:
    *   **Rollen:** Die *Namen* der Rollen werden in den Template-Permissions gespeichert. Der Bot muss dann beim Anwenden die tatsächliche Discord-Rollen-ID für diesen Namen auf dem jeweiligen Server finden.
    *   **Dashboard-/Komponenten-Typen:** Wenn du verschiedene *Arten* von Dashboards (z.B. "System Monitor", "Project Overview") oder Komponenten ("CPU Chart", "Task List") hast, könnten *diese Typen* global definiert sein (vielleicht in den alten `dashboard_*`-Tabellen, aber umstrukturiert). Das Template würde dann nur sagen: "In Kanal X soll ein Dashboard vom Typ Y platziert werden."

**Zusammenfassender Plan für die Zukunft (Nach dem Frontend):** []

1.  **Datenbank Refactoring:**
    *   Passe `DashboardEntity` / `dashboard_instances` an (`guild_id`, `guild_template_channel_id`, `message_id`).
    *   Entferne/ignoriere `discord_categories`, `discord_channels`, `category_mappings`, `channel_mappings` für die Strukturdefinition.
    *   Entferne/überarbeite die alten Seeds (`002`, `003`, `004`).
2.  **Bot Workflow Refactoring:**
    *   Entferne die Struktur-Erstellungslogik aus `CategoryWorkflow.initialize_for_guild` und `ChannelWorkflow.initialize_for_guild`.
    *   Erstelle einen neuen Workflow (z.B. `GuildStructureWorkflow` oder erweitere `GuildWorkflow`), der die Methode `apply_template(guild_id)` hat.
    *   Diese Methode liest das Template aus `guild_template_*` und nutzt (ggf. angepasste) Logik aus den alten `CategoryBuilder` / `ChannelBuilder`, um die Struktur auf Discord zu erstellen/anzupassen.
    *   Der `DashboardWorkflow` muss so angepasst werden, dass er basierend auf den Infos im Template (`guild_template_channel_id` und dem verknüpften Dashboard-Typ) die Nachrichten in den richtigen Kanälen erstellt/aktualisiert.
    *   Ändere `GuildWorkflow.approve_guild`, sodass es *nur noch* `GuildTemplateWorkflow.create_template_for_guild` und danach `GuildStructureWorkflow.apply_template` aufruft (und nicht mehr `workflow_manager.initialize_guild`).

Das ist ein großer Umbau, aber absolut notwendig für dein Ziel!

**Für jetzt:** Konzentrieren wir uns darauf, die *Anzeige* der vorhandenen Template-Daten im Frontend (`index.js`) zum Laufen zu bringen. Das gibt uns eine Basis für den Designer.
