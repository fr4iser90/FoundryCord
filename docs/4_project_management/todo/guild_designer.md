# Guild Designer TODO

## Structure Application & Related Features (See the [Structure Workflow documentation](../../3_developer_guides/04_feature_implementation/guild_designer/structure_workflow.md) and its [detailed TODO list](../../3_developer_guides/04_feature_implementation/guild_designer/structure_workflow_todo.md))

_(This section covers applying templates to Discord, managing channel follows, dashboards, etc. Details are tracked in the separate linked files.)_

## Core Functionality

### Phase 1: Saving Edited Structure & Basic Actions

*   [x] **Implement Frontend Save Logic:**
    *   [x] **Capture Moves:** Enhanced `move_node.jstree` event handler.
    *   [x] **Track Changes:** Implemented dirty state tracking (`designerState.js`).
    *   [x] **Format Data:** Created `formatStructureForApi` in `designerUtils.js`.
    *   [x] **Add Save Button:** Added in `index.html`.
    *   [x] **Trigger Save:** Implemented `handleSaveStructureClick` in `designerEvents.js` (PUT).
    *   [x] **Save As New Modal:** Implemented (`saveAsNewModal.js`, `save_as_new_modal.html`).
    *   [x] **Handle Save As New:** Implemented listener for `saveAsNewConfirmed` in `designerEvents.js` (POST).
*   [x] **Implement Frontend Logic for Toolbar "Activate" Button:**
    *   [x] **Target File:** `designerEvents.js` (listener setup), `index.js`/`designerState.js` (state/button updates).
    *   [x] **UI:** Add/uncomment "Activate" button in `index.html` toolbar.
    *   [x] **Listener:** Add listener in `initializeDesignerEventListeners` (`designerEvents.js`) calling `handleToolbarActivateClick`.
    *   [x] **Handler:** Implement `handleToolbarActivateClick` to call `POST /api/v1/templates/guilds/{template_id}/activate`, update state, update toolbar buttons via `updateButtonStates`, dispatch `templateActivated` event.
    *   [x] **Consideration:** Add confirmation modal (`activateConfirmModal.js`, `activate_confirm_modal.html`).
*   [x] **Update Core State/Loading Logic for Activation:**
    *   [x] **Target File:** `index.js`, `designerState.js`, `designerEvents.js`.
    *   [x] **Loading:** Update `fetchGuildTemplate` (`index.js`) and `handleTemplateDataLoad` (`designerEvents.js`) to fetch/use `is_active` status and store in `state`.
    *   [x] **State:** Ensure `designerState.js` tracks `currentTemplateIsActive`.
    *   [x] **Button States:** Implement `updateToolbarButtonStates` in `designerEvents.js` to manage toolbar buttons based on `isDirty` and `currentTemplateIsActive`.
*   [x] **Ensure `templateList.js` Updates on Activation:**
    *   [x] **Target File:** `templateList.js`.
    *   [x] **Listener:** Add listener for `templateActivated` event to re-initialize the list with the correct active indicator (via `_renderTemplateList`).
    *   [x] **Refactor:** Activate button in list now dispatches `requestActivateTemplate`, handled by `designerEvents.js`.
*   [x] **Create Backend Save API Endpoints:**
    *   [x] **API Route (PUT):** Defined `PUT /api/v1/templates/guilds/{template_id}/structure`.
    *   [x] **API Route (POST):** Defined `POST /api/v1/templates/guilds/from_structure`.
    *   [x] **Payload Schemas:** Created `GuildStructureUpdatePayload` & `GuildStructureTemplateCreateFromStructure`.
    *   [x] **Service Logic (PUT):** Implemented `update_template_structure`.
    *   [x] **Service Logic (POST):** Implemented `create_template_from_structure`.
    *   [x] **Database Interaction:** Ensured services use session correctly.
*   [x] **Create Backend Activate API Endpoint:**
    *   [x] **API Route (POST):** Define `POST /api/v1/templates/guilds/{template_id}/activate` in `guild_template_controller.py`.
    *   [x] **Service Logic:** Implement `activate_template` in `template_service.py` to set `is_active` flag (ensure only one per guild).
    *   [x] **Permissions:** Ensure only owner or GUILD ADMIN can activate (Basic check implemented, comments added for future enhancement).
*   [x] **Refactor Core Bot Workflows/Services:** Implemented session-based repository handling to ensure reliable database interactions for template application and future API calls.

### Phase 2: Applying Template to Discord

*   [x] **Complete Bot `apply_template` Logic:**
    *   **Target File:** `app/bot/core/workflows/guild_workflow.py` (function `apply_template`).
    *   **Enhancements:**
        *   [x] Fetch the full template structure (categories, channels, positions, parents, permissions etc.) from the database using the shared Template Repositories. (Implemented repository calls)
        *   [x] Fetch the *current* guild structure directly from Discord using the Discord service (`app/bot/application/services/discord/discord_query_service.py` created and used).
        *   [x] Implement comparison logic (diffing) between the template and the live Discord state. (Implemented via loops/checks in apply_template)
        *   [x] Call Discord API functions (via the service) to:
            *   [x] Create missing categories/channels based on the template.
            *   [x] Delete extra categories/channels not in the template (controlled by `template_delete_unmanaged` flag in GuildConfig).
            *   [x] Update names, topics, types if they differ.
            *   [ ] **Reorder** categories and channels using Discord's bulk update endpoints if possible, or individual position updates otherwise, to match the template's `position` and parent structure. **(Deferred: To be handled by future Sync Job)**
        *   [x] Update `discord_channel_id` in DB. (Implemented via session commit)
*   [x] **Add "Apply Template" Trigger:**
    *   [x] **UI Button:** Add an "Apply to Discord" button in `app/web/templates/views/guild/designer/index.html`.
    *   [x] **UI Setting:** Add "Clean Apply" (`template_delete_unmanaged`) checkbox to control deletion behavior.
    *   [x] **Frontend Logic:** Add event listener in `app/web/static/js/views/guild/designer/designerEvents.js` for the apply button and checkbox. Added confirmation dialog for apply.
    *   [x] **Backend API (Apply):** Create a new endpoint `POST /api/v1/guilds/{guild_id}/template/apply` in `app/web/interfaces/api/rest/v1/guild/designer/guild_template_controller.py`.
    *   [x] **Backend API (Settings):** Create `PUT /guilds/{guild_id}/template/settings` endpoint to save the "Clean Apply" setting.
    *   [x] **Trigger Workflow:** The apply API endpoint calls the `guild_workflow.apply_template` function.
*   [x] **Deletion Safety:**
    *   [x] **Prevent Initial Snapshot Deletion:** In `templateList.js`, disable the delete button for templates marked as `is_initial_snapshot`.
    *   [x] **Add Delete Confirmation Modal:** 
        *   [x] Create a Bootstrap modal (`delete_confirmation_modal.html`).
        *   [x] Create associated JS (`modal/deleteModal.js`) with `initializeDeleteModal` and `openDeleteModal(id, name)` functions.
        *   [x] Modify `templateList.js` and `sharedTemplateList.js` delete handlers to use events triggering `openDeleteModal`.
        *   [x] The modal's confirm button triggers the actual DELETE API call.
    *   [x] **Refresh List after Delete:** Ensure the template list widgets correctly refresh after a successful deletion triggered via the modal.

### Phase 3: Full Designer Editing Capabilities

*   [ ] **Properties Panel - Setup & Display:**
    *   **Files:** `properties.js`, `properties.html`, `structureTree.js`, Listen-Widgets (`categoriesList.js`, `channelsList.js`).
    *   [x] **UI Grundstruktur:** HTML für Properties-Panel erstellt.
    *   [x] **Selektion:** Event (`nodeSelected`) wird bei Auswahl ausgelöst und verarbeitet.
    *   [x] **Datenfindung:** Logik (`findNodeDataInState`) korrigiert, um korrekte IDs zu verwenden.
    *   [x] **Anzeige (Basis):** `properties.js` implementiert, Panel wird mit Basisdaten gefüllt.
    *   [x] **Dynamische Felder:** Felder werden je nach selektiertem Typ (Server, Kategorie, Kanal) korrekt ein-/ausgeblendet.
    *   [x] **Initialer Zustand:** Felder werden initial deaktiviert/placeholder angezeigt und bei Auswahl aktiviert.
*   [ ] **Properties Panel - Editing aktivieren:**
    *   **Files:** `properties.js`, `designerState.js`, `designerEvents.js`.
    *   [x] **Felder aktivieren:** Input-Felder sind bei Auswahl aktiv.
    *   [x] **Änderungen verfolgen:** Listener in `properties.js` speichern Änderungen im `designerState` (`addPendingPropertyChange`).
    *   [x] **State erweitert:** `designerState.js` speichert "pending property changes".
*   [ ] **Save Button - Properties speichern:**
    *   **Files:** `designerUtils.js`, `template_service.py`, `guild_template_controller.py`.
    *   [x] **Daten formatieren (`formatStructureForApi`):** Funktion sendet geänderte Properties mit.
    *   [x] **Backend erweitert (`update_template_structure`):** PUT `/templates/guilds/{template_id}/structure` Endpunkt/Service verarbeitet Property-Updates.
    *   [x] **State aufräumen:** Nach erfolgreichem Speichern werden "pending property changes" gelöscht.
*   [ ] **Elemente löschen implementieren:**
    *   **Files:** `properties.js` / `structureTree.js`, `deleteModal.js`, `designerEvents.js`, `template_service.py`, `guild_template_controller.py`, Repos.
    *   [x] **UI Trigger:** Löschen-Button im Properties Panel hinzugefügt.
    *   [x] **Bestätigung:** Vorhandener `deleteModal` wird korrekt getriggert.
    *   [x] **Backend API (DELETE):** Neue Endpunkte (`DELETE /.../categories/{id}`, `DELETE /.../channels/{id}`) erstellt.
    *   [x] **Backend Logik:** Service/Repo-Methoden zum Löschen der DB-Entitäten implementiert.
    *   [x] **Frontend Events:** Event-Listener (`designerElementDeleted`, `requestPanelReset`) implementiert.
    *   [x] **Frontend Call:** API-Aufruf nach Modal-Bestätigung implementiert.
    *   [x] **UI Update:** Knoten wird aus Baum/Listen nach Erfolg entfernt.
*   [ ] **Elemente hinzufügen (Toolbox):**
    *   **Files:** `panel/toolbox.js`, `toolbox.html`, `structureTree.js`, `designerEvents.js`, `template_service.py`, `guild_template_controller.py`, Repos.
    *   [ ] **Toolbox UI:** Draggable Elemente für "Neue Kategorie", "Neuer Textkanal" etc. erstellen.
    *   [ ] **Tree Drag-and-Drop:** jsTree konfigurieren, um Drop aus Toolbox zu akzeptieren.
    *   [ ] **Input Modal:** Modal für Namenseingabe bei neuem Element erstellen/verwenden.
    *   [ ] **Frontend State:** Nach Eingabe: Temporären Knoten zum Baum hinzufügen, Daten in `state.pendingAdditions` speichern, `state.setDirty(true)`.
    *   [ ] **Backend API (POST):** Neue Endpunkte (`POST /templates/guilds/categories`, `POST /templates/guilds/channels` - *Prüfen ob diese oder `from_structure` gemeint war*) erstellen.
    *   [ ] **Backend Logik:** Service/Repo-Methoden zum Erstellen neuer DB-Entitäten implementieren.
    *   [ ] **Frontend Call:** Eigene POST Calls nach Modal-Bestätigung machen das Hinzufügen direkter (statt über "Save Structure").
    *   [ ] **UI Update:** Nach Erfolg: Temporären Knoten mit echter DB-ID aktualisieren, Listen neu laden.
*   [ ] **Widget-Synchronisation verbessern:**
    *   **Files:** Alle Widget-JS-Dateien, `designerEvents.js`, `designerState.js`.
    *   [ ] **Events definieren:** Klare Events für Aktionen wie `propertyUpdated`, `nodeDeleted`, `nodeAdded` definieren.
    *   [ ] **Listener implementieren:** Alle relevanten Widgets müssen auf diese Events hören und ihre Anzeige entsprechend aktualisieren (nicht nur auf `loadTemplateData`).

# --- Dashboard Instance Management (Designer) ---
*   **Revised Goal:** Implement a **Dashboard Builder** allowing users to create and configure dashboard instances using predefined components. Provide a **live preview** approximating the Discord appearance. Manage instances linked to template channels.
*   [ ] **Database & Seeds:**
    *   [x] `dashboard_instances` table exists for storing instances linked to `guild_template_channel_id` with `name`, `dashboard_type`, and `config` (JSON).
    *   [x] `dashboard_component_definitions` table exists and is seeded (via Migration 009) with component definitions (embeds, buttons, etc.) for different `dashboard_type`s.
    *   [ ] Clarify: Linking logic between `guild_template_channel_id` and potential live `channel_id`. (Defer for now).
*   [ ] **Backend - Component API:**
    *   **Files:** New controller/service/repository for dashboard components.
    *   [ ] **New Endpoint (`GET /api/v1/dashboards/components`):**
        *   [ ] Needs to query `dashboard_component_definitions` table.
        *   [ ] Return structured data of available components, potentially filterable by `dashboard_type` (e.g., 'common', 'welcome'). Include `component_type`, `component_key`, and `definition` (which describes configurable fields).
*   [ ] **Backend - Variables API (Optional/Placeholder):**
    *   **Files:** New controller/service.
    *   [ ] **New Endpoint (`GET /api/v1/dashboards/variables`):**
        *   [ ] Return a list of available template variables (e.g., `{{user_name}}`, `{{server_name}}`) with descriptions. (Initially hardcoded, later dynamic?).
*   [x] **Backend - Instance Management API:** (Existing endpoints are sufficient but handle complex `config`)
    *   [x] `GET /api/v1/templates/channels/{channel_template_id}/dashboards`: Lists instances.
    *   [x] `POST /api/v1/templates/channels/{channel_template_id}/dashboards`: Creates instance (expects complex `config` from Builder).
    *   [x] `GET /api/v1/templates/dashboards/{instance_id}`: Gets instance details (including complex `config`).
    *   [x] `PUT /api/v1/templates/dashboards/{instance_id}`: Updates instance (including complex `config`).
    *   [x] `DELETE /api/v1/templates/dashboards/{instance_id}`: Deletes instance.
    *   [x] **Files:** `template_dashboard_instances_controller.py`, `template_dashboard_instance_service.py`, `template_dashboard_instance_repository_impl.py`.

*   [ ] **Frontend - Toolbox Integration (Components):**
    *   **Files:** `panel/toolbox.js`, `toolbox.html`.
    *   [ ] **Fetch Components:** Load component definitions via the new `GET /api/v1/dashboards/components` endpoint.
    *   [ ] **Display Components:** Show components (grouped by `component_type`?) as draggable items.
    *   [ ] **Associate Data:** Link component details (`component_key`, `definition`) to draggable items.
*   [ ] **Frontend - Dashboard Editor Widget (Builder):**
    *   **Files:** New `widget/dashboardEditor.js`, `designerLayout.js`, `designerWidgets.js`.
    *   [ ] **Define Widget:** Add `dashboard-editor` widget definition to `designerLayout.js` (likely hidden initially).
    *   [ ] **Register Widget:** Add to `designerWidgets.js`.
    *   [ ] **UI Layout:**
        *   [ ] Design the builder interface (e.g., drop area/canvas, component property editor panel within the widget).
        *   [ ] Implement drag-and-drop receiving from Toolbox.
    *   [ ] **Component Handling:**
        *   [ ] When a component is dropped/added: Render its configurable fields based on its `definition`.
        *   [ ] Allow reordering/removing components within the editor.
    *   [ ] **Variable Integration:**
        *   [ ] Fetch available variables (from API or hardcoded).
        *   [ ] Provide a way for the user to insert variables into component fields (e.g., button/dropdown).
    *   [ ] **Config Generation:** On save, generate the complex `config` JSON representing the arranged and configured components.
    *   [ ] **Save/Load Logic:**
        *   [ ] Implement `loadInstance(instanceId)`: Fetch instance data (`GET .../{instance_id}`), parse `config`, and populate the editor.
        *   [ ] Implement `saveInstance()`: Generate `config`, call `PUT .../{instance_id}`.
        *   [ ] Implement `createInstance(channelTemplateId, dashboardType)`: Generate `config`, call `POST .../channels/{channel_id}/dashboards`.
    *   [ ] **Show/Hide:** Implement logic to show/hide the widget when triggered (by Properties Panel or future drag-drop).
*   [ ] **Frontend - Dashboard Preview Widget:**
    *   **Files:** New `widget/dashboardPreview.js`, `designerLayout.js`, `designerWidgets.js`.
    *   [ ] **Define Widget:** Add `dashboard-preview` widget definition.
    *   [ ] **Register Widget:** Add to `designerWidgets.js`.
    *   [ ] **Rendering Logic:**
        *   [ ] Implement `loadPreview(instanceId)`: Fetch instance data (`GET .../{instance_id}`), parse `config`.
        *   [ ] **Render:** Create HTML elements to *approximate* the Discord look based on the `config` components and their properties. Replace variables with placeholders (e.g., `[user_name]`). (This is the complex part).
    *   [ ] **Update Trigger:** Listen for events indicating an instance was selected or saved to reload the preview.
*   [ ] **Frontend - Properties Panel Integration (Revised):**
    *   **Files:** `properties.js`.
    *   [ ] **Listen:** On `designerNodeSelected`, check if selected node is a channel.
    *   [ ] **Fetch & Display Instances:** If channel selected, call `GET .../dashboards` and display the list (Name, Type).
    *   [ ] **Add "New" Button:**
        *   [ ] Button opens a selection (modal? dropdown?) for the `dashboard_type`.
        *   [ ] Triggers the **Editor Widget** in 'create' mode, passing `channel_template_id` and selected `dashboard_type`.
    *   [ ] **Add "Edit" Button:** Next to each instance, triggers the **Editor Widget** in 'edit' mode, passing `instance_id`.
    *   [ ] **Add "Delete" Button:** Next to each instance, calls `DELETE .../{instance_id}` (with confirmation).
    *   [ ] **Selection Handling:** Clicking an instance in the list should trigger the **Preview Widget** to load that instance's preview.
*   [ ] **Event Handling / Widget Interaction:**
    *   [ ] Define and implement events/callbacks for communication:
        *   Properties Panel selection -> Preview Widget load.
        *   Properties Panel "Edit" -> Editor Widget load.
        *   Properties Panel "New" (Type selected) -> Editor Widget create.
        *   Editor Widget save -> Properties Panel list refresh, Preview Widget refresh.
        *   Properties Panel delete -> Properties Panel list refresh, Preview Widget clear/reset.
        *   (Future: Toolbox drop -> Editor Widget create).
*   [ ] **Code Cleanup:**
    *   [ ] Remove OLD code parts in `properties.js` related to `is_dashboard_enabled` and `dashboard_types`.
    *   [ ] Review/Remove `DashboardType` Enum if components API makes it redundant.
*   [ ] **Sharing / Copying (Future):**
    *   [ ] Needs significant backend work for dashboard definitions separate from instances.

# --- Previous/Other Sections ---
*   [ ] **Properties Panel - Channel Follows anzeigen:**
    *   **Files:** `properties.js`, `properties.html`, `guild_template_controller.py` (API Anpassung).
    *   [ ] **API:** Backend API anpassen, um Follow-Informationen (wer folgt wem) für den ausgewählten Kanal bereitzustellen (entweder im Haupt-Template-Payload oder separater Endpunkt).

### Phase 4: Template Synchronization Job (Future)

*   [ ] **Implement Scheduled Template Sync Job:**
    *   [ ] **Scheduler Setup:** Bot-seitigen Scheduler einrichten (z.B. `apscheduler` oder integrierte `tasks.loop`).
    *   [ ] **Sync Workflow/Service:** Neuen Workflow/Service für den Sync-Job erstellen.
    *   [ ] **Core Sync Logic:**
        *   [ ] Guild-spezifische Ausführung für alle "approved" Guilds.
        *   [ ] Aktives Template für die Guild laden.
        *   [ ] Live-Discord-Struktur holen.
        *   [ ] Vergleich (Diff) durchführen.
        *   [ ] Erstellen/Löschen/Updaten von Elementen auf Discord basierend auf dem Template (Teile von `apply_template` wiederverwenden).
        *   [ ] **Neuordnung implementieren:** Verwendung von `edit_channel_positions` basierend auf Template-Reihenfolge.
    *   [ ] **Reverse Sync (Flag-Based):**
        *   [ ] Kanäle/Kategorien auf Discord erkennen, die *nicht* im Template sind.
        *   [ ] Auf spezielles Flag prüfen (z.B. `#please_add` in Name/Topic).
        *   [ ] Wenn Flag vorhanden: Entsprechenden Eintrag im DB-Template erstellen (Name, Typ, Positionierung ableiten).
        *   [ ] Flag auf Discord entfernen nach erfolgreicher Übernahme.
        *   [ ] **Konfiguration:** Job-Intervall und Flag-Marker konfigurierbar machen.

## UI/UX Enhancements (Lower Priority)

*   [x] **Improve Visual Accuracy:**
    *   **Files:** `app/web/static/js/views/guild/designer/widget/structureTree.js`, `app/web/static/js/views/guild/designer/widget/channelsList.js`.
    *   **Task:** Adjust sorting/data generation to place uncategorized channels visually at the top.
*   [ ] **Properties Panel:**
    *   **Files:** `app/web/static/js/views/guild/designer/panel/properties.js`, `app/web/static/js/views/guild/designer/widget/structureTree.js`.
    *   **Task:** Implement UI for viewing/editing selected node properties (name, topic etc.). Integrate saving changes with the "Save Structure" API call (Phase 1).
*   [ ] **Toolbox Panel:**
    *   **Files:** `app/web/static/js/views/guild/designer/panel/toolbox.js`, `app/web/static/js/views/guild/designer/widget/structureTree.js`.
    *   **Task:** Implement UI for dragging new elements. Integrate adding new elements with the "Save Structure" API call (Phase 1).
*   [ ] **Refine Share Modal:**
    *   **Files:** `app/web/templates/views/guild/designer/index.html`, `
