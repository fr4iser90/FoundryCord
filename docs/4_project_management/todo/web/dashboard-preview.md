# Discord-Style Dashboard Preview TODO

**Goal:** Das Web-Dashboard-Preview soll **dynamisch** das HTML für eine Vorschau generieren, die das **jeweilige aktive Dashboard** so darstellt, wie es im Bot erscheinen würde. Die Darstellung soll sich an dem Stil orientieren, den dein "System Status"-Screenshot zeigt (dunkles Thema, Layout von Embeds und Buttons), aber der Inhalt muss sich natürlich an das geladene Dashboard anpassen. **Es wird nichts hardcodiert für ein spezifisches Dashboard.**

**Related Documentation (Optional):**
*   [Link to relevant ADRs, design docs, etc.]

<!--
STATUS: New / Needs Refinement -> In Progress
-->

## Phase 1: Analyse und Design-Konzept

*   [x] **Task 1.1:** Bestehende Dashboard-Preview-Komponenten analysieren und Discord-UI-Elemente als Stilvorlage sowie Datenstrukturen für das dynamische Rendering recherchieren.
    *   **Depends on (Optional):**
    *   **Affected Files (Optional):**
        *   `app/web/static/js/views/guild/designer/panel/toolbox.js`
        *   `app/web/templates/components/guild/designer/panel/toolbox.html`
        *   `app/web/static/js/views/guild/designer/widget/structureTree.js`
        *   `app/web/static/js/views/guild/designer/designerEvents.js`
        *   `app/web/static/js/views/guild/designer/designerWidgets.js`
        *   `app/web/static/js/views/guild/designer/widget/dashboardConfiguration.js`
        *   `app/web/static/js/views/guild/designer/widget/dashboardPreview.js`
        *   `app/shared/infrastructure/database/migrations/alembic/versions/011_seed_default_dashboards.py` (für `config` Struktur)
        *   `app/shared/infrastructure/database/migrations/alembic/versions/009_seed_dashboard_component_definitions.py` (und zugehörige Seed-Dateien für Komponentendefinitionen)
    *   **Definition of Done (DoD) (Optional):**
        *   Aktuelle Implementierung des Dashboard-Previews ist dokumentiert (zeigt Titel, TBD-Text, rohes JSON).
        *   Stilvorlage (System Status Screenshot) und relevante Datenstrukturen (Dashboard `config`, Komponentendefinitionen) sind analysiert.
        *   Konzept für dynamische, generische HTML-Generierung in `dashboardPreview.js` ist erstellt.

## Phase 2: Implementierung - Frontend

*   [ ] **Task 2.1:** `dashboardPreview.js` überarbeiten, um Komponenten dynamisch zu rendern.
    *   **Sub-Task 2.1.1: Zugriff auf Komponentendefinitionen sicherstellen/implementieren.**
        *   Klären/Implementieren, wie `dashboardPreview.js` die von `/api/v1/dashboards/components` geladenen Definitionen abrufen kann (z.B. über globales Objekt, State Management, oder direkten API-Call falls nötig).
        *   Erstellen einer Hilfsfunktion/eines Mechanismus (z.B. `componentDefinitionStore.getDefinition(dashboardType, componentKey)`), um eine spezifische Definition zu erhalten.
    *   **Sub-Task 2.1.2: Rendering-Logik im `dashboardConfigLoaded`-Event-Listener implementieren.**
        *   Daten aus `receivedConfigData` extrahieren (Name, ID, Typ, Komponentenliste).
        *   HTML-Grundgerüst für die Vorschau erstellen (Wrapper, dynamischer Titel).
        *   Durch die `componentsToRender`-Liste (`receivedConfigData.config.components`) iterieren.
        *   Für jede Komponente: Definition laden, Typ prüfen (Embed, Button, etc.).
        *   Entsprechende Render-Funktion aufrufen (`renderEmbedPreview`, `renderButtonPreview`).
        *   Generiertes HTML sammeln.
    *   **Sub-Task 2.1.3: Hilfsfunktionen `renderEmbedPreview(definition, instanceSettings)` und `renderButtonPreview(definition, instanceSettings)` implementieren.**
        *   `renderEmbedPreview`: Erzeugt HTML für Embeds (Titel, Beschreibung, Farbe, Felder mit Platzhaltern für dynamische Werte wie `{{hostname}}`).
        *   `renderButtonPreview`: Erzeugt HTML für Buttons (Emoji, Label, Style). Berücksichtigt die `row`-Eigenschaft aus der Definition für spätere Gruppierung.
    *   **Sub-Task 2.1.4: Button-Gruppierung implementieren.**
        *   HTML-Strings für Buttons nach ihrer `row`-Eigenschaft in Zeilen (`<div class="preview-button-row">`) gruppieren.
    *   **Sub-Task 2.1.5: Finale HTML-Ausgabe im `contentElement` aktualisieren.**
    *   **Affected Files (Potenziell):** `app/web/static/js/views/guild/designer/widget/dashboardPreview.js`, ggf. `app/web/static/js/views/guild/designer/index.js` oder `toolbox.js` (falls Definitionen von dort bereitgestellt/verwaltet werden).
    *   **DoD:** Das Preview rendert dynamisch Embeds und Buttons basierend auf der geladenen Dashboard-Konfiguration und den Komponentendefinitionen. Die Struktur entspricht dem gewünschten Layout (Embeds oben, Buttons in Zeilen darunter). Platzhalter für dynamische Bot-Daten werden als Text angezeigt.

*   [ ] **Task 2.2: CSS-Styling für das Dashboard-Preview erstellen.**
    *   **Sub-Task 2.2.1: CSS-Klassen für Preview-Wrapper, Embeds, Felder, Buttons und Button-Reihen definieren.**
        *   z.B. `.discord-preview-wrapper`, `.discord-embed-preview`, `.embed-title`, `.embed-description`, `.embed-fields`, `.embed-field`, `.embed-field.inline`, `.preview-button-row`, `.discord-button-preview`, `.discord-button-style-primary`, `.discord-button-style-secondary`.
    *   **Sub-Task 2.2.2: Farben, Abstände, Schriftarten und Layout (Flexbox/Grid für Felder und Button-Reihen) gemäß der "System Status"-Screenshot-Stilvorlage implementieren.**
    *   **Affected Files (Potenziell):** Neue CSS-Datei (z.B. `app/web/static/css/views/guild/designer-preview.css`) oder Erweiterung einer bestehenden (z.B. `app/web/static/css/views/guild/designer.css`). Einbindung in `app/web/templates/views/guild/designer/index.html` sicherstellen.
    *   **DoD:** Das dynamisch generierte Preview ist visuell ansprechend und ähnelt dem Stil des "System Status"-Screenshots (dunkles Thema, korrekte Darstellung von Embeds, Buttons und deren Anordnung).

## General Notes / Future Considerations

*   Die genaue Abbildung von Discord-Interaktivität im Preview muss evaluiert werden (Was ist machbar/sinnvoll?).
*   Performance-Aspekte für komplexe Dashboard-Previews im Auge behalten.
*   Zugriffsmethode für Komponentendefinitionen in `dashboardPreview.js` muss noch final geklärt und implementiert werden (siehe Task 2.1.1).
