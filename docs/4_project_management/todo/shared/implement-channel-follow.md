<!--
STATUS: Refined and Ready for Executor
REFINED_BY: AI (role_todo_analyzer_refiner)
REFINEMENT_DATE: 2024-05-17 
-->
# Structure Workflow Implementation TODO

**(See also: [Guild Designer Main TODO](../../../../4_project_management/todo/guild_designer.md))**

## Channel Following Feature


- [ ] **Phase 1: Database and Core Logic**
  - [ ] **1.1: Define Database Entity**
    - [ ] Create/Update `app/shared/infrastructure/models/discord/entities/channel_follow_entity.py` with `ChannelFollowEntity` class.
      - Fields: `id` (PK), `source_channel_id` (String, index), `target_channel_id` (String, index), `guild_id` (String, index), `webhook_id` (String, nullable), `webhook_token` (String, nullable), `is_active` (Boolean, default True), `created_at` (DateTime, server_default), `updated_at` (DateTime, server_default, onupdate).
      - Include `UniqueConstraint('source_channel_id', 'target_channel_id', name='uq_channel_follows_source_target')`.
    *   **Affected Files:**
        *   `app/shared/infrastructure/models/discord/entities/channel_follow_entity.py`
  - [ ] **1.2: Create Database Migration (Alembic)**
    - [ ] Generate a new Alembic migration script in `app/shared/infrastructure/database/migrations/alembic/versions/`.
    - [ ] Implement `upgrade()` function to create `channel_follows` table with columns, indexes, and unique constraint as defined for `ChannelFollowEntity` (referencing `channel_follow_implementation.md` for exact structure).
    - [ ] Implement `downgrade()` function to drop the `channel_follows` table.
    *   **Affected Files:**
        *   `app/shared/infrastructure/database/migrations/alembic/versions/` (new migration file to be created here)
  - [ ] **1.3: Implement Repository Layer**
    - [ ] Define `ChannelFollowRepository` interface in `app/shared/domain/repositories/discord/channel_follow_repository.py`.
      - Methods: `add_follow(follow_entity: ChannelFollowEntity) -> ChannelFollowEntity`
      - `get_follow(source_channel_id: str, target_channel_id: str) -> Optional[ChannelFollowEntity]`
      - `list_follows_by_source(source_channel_id: str) -> List[ChannelFollowEntity]`
      - `list_follows_by_target(target_channel_id: str) -> List[ChannelFollowEntity]`
      - `remove_follow(source_channel_id: str, target_channel_id: str) -> bool`
      - `update_webhook_details(follow_id: int, webhook_id: str, webhook_token: str) -> Optional[ChannelFollowEntity]`
    *   **Affected Files:**
        *   `app/shared/domain/repositories/discord/channel_follow_repository.py`
    - [ ] Implement `ChannelFollowRepositoryImpl` in `app/shared/infrastructure/repositories/discord/channel_follow_repository_impl.py`.
      - Implement all methods from `ChannelFollowRepository` using SQLAlchemy and database session.
    *   **Affected Files:**
        *   `app/shared/infrastructure/repositories/discord/channel_follow_repository_impl.py`
  - [ ] **1.4: Implement Service Layer**
    - [ ] Create `ChannelFollowService` in `app/bot/application/services/channel/channel_follow_service.py`.
    *   **Affected Files:**
        *   `app/bot/application/services/channel/channel_follow_service.py`
    - [ ] Constructor should accept `ChannelFollowRepository` and `DiscordQueryService` (from `app.bot.application.services.discord.discord_query_service`).
    - [ ] Implement `setup_follow(guild_id: str, source_channel_id: str, target_channel_id: str) -> ChannelFollowEntity`.
      - Validate source channel is announcement type (using Discord service).
      - Validate target channel and bot permissions (using Discord service).
      - Check if follow already exists (using repository).
      - Call Discord API (`POST /channels/{source_channel_id}/followers`) via Discord service to create the follow (Discord handles webhook creation).
      - Persist `ChannelFollowEntity` (potentially with placeholder/null webhook details if not directly returned by Discord API for this call).
    - [ ] Implement `unfollow_channel(guild_id: str, source_channel_id: str, target_channel_id: str) -> bool`.
      - Call Discord API to unfollow (e.g., might involve deleting the webhook or using a specific unfollow endpoint if available).
      - Remove `ChannelFollowEntity` from DB via repository.
    - [ ] Add helper methods as needed (e.g., for listing follows, checking status if required by UI/API).

- [ ] **Phase 2: Bot Integration**
  - [ ] **2.1: Create Discord Bot Commands**
    - [ ] Create `FollowCommands` Cog in `app/bot/interfaces/commands/channel/follow_commands.py`. (Create `channel` subdirectory if needed)
    *   **Affected Files:**
        *   `app/bot/interfaces/commands/channel/follow_commands.py`
    - [ ] Implement `/follow add source_channel target_channel` slash command.
      - Use `ChannelFollowService.setup_follow`.
      - Perform initial client-side validation (e.g., `source_channel.type == nextcord.ChannelType.news`).
      - Defer interaction and send followup messages.
    - [ ] Implement `/follow remove source_channel target_channel` slash command.
      - Use `ChannelFollowService.unfollow_channel`.
    - [ ] Implement `/follow list [source_channel_optional]` slash command to list active follows.
      - Use `ChannelFollowService` or `ChannelFollowRepository` to fetch data.
    - [ ] Ensure appropriate permission checks for commands.

- [ ] **Phase 3: Web API & UI (Guild Designer Integration)**
  - [ ] **3.1: Implement REST API Endpoints**
    - [ ] Create API router (e.g., in `app/web/interfaces/api/rest/v1/guild/channel_follows.py`).
    *   **Affected Files:**
        *   `app/web/interfaces/api/rest/v1/guild/channel_follows.py`
    - [ ] Endpoint: `POST /api/v1/guilds/{guild_id}/channel-follows`
      - Request Body: `{ "source_channel_id": "...", "target_channel_id": "..." }`
      - Uses `ChannelFollowService.setup_follow`.
    - [ ] Endpoint: `DELETE /api/v1/guilds/{guild_id}/channel-follows`
      - Request Body/Params: `{ "source_channel_id": "...", "target_channel_id": "..." }`
      - Uses `ChannelFollowService.unfollow_channel`.
    - [ ] Endpoint: `GET /api/v1/guilds/{guild_id}/channel-follows?source_channel_id=...`
      - Uses `ChannelFollowService` or `ChannelFollowRepository` to list follows for a source channel.
    - [ ] Endpoint: `GET /api/v1/guilds/{guild_id}/channel-follows?target_channel_id=...`
      - Uses `ChannelFollowService` or `ChannelFollowRepository` to list sources following a target channel.
    - [ ] Implement authentication and authorization (e.g., guild admin permissions).
  - [ ] **3.2: UI Implementation in Guild Designer**
    - [ ] **Display Follows:** In the guild designer, when a channel is selected (especially an announcement channel), display a section/tab showing:
      - Channels it's currently following (if it's a target).
      - Channels that are following it (if it's a source).
    *   **Affected Files:**
        *   `app/web/static/js/views/guild/designer/...` (relevant JS files for displaying info)
        *   `app/web/templates/views/guild/designer/...` (relevant HTML templates)
    - [ ] **Add Follow Functionality:**
      - For an announcement channel (source), provide a UI element (e.g., button "Manage Follows for this Channel") that leads to a modal or dedicated view.
      - In this view/modal, allow selecting a target channel within the same guild to follow. This should trigger the `POST` API.
    *   **Affected Files:**
        *   `app/web/static/js/views/guild/designer/...` (relevant JS files for add functionality/modal)
        *   `app/web/templates/views/guild/designer/...` (relevant HTML templates for add functionality/modal)
    - [ ] **Remove Follow Functionality:**
      - Provide UI elements (e.g., "unfollow" button next to each listed follow relationship) to trigger the `DELETE` API.
    *   **Affected Files:**
        *   `app/web/static/js/views/guild/designer/...` (relevant JS files for remove functionality)
        *   `app/web/templates/views/guild/designer/...` (relevant HTML templates for remove functionality)
    - [ ] **Data Fetching:** UI components should use the new GET API endpoints to display follow information.
    - [ ] **File locations (conceptual) - General UI files potentially touched:**
        *   `app/web/static/js/views/guild/designer/...`
        *   `app/web/templates/components/guild/designer/...`
        *   `app/web/templates/views/guild/designer/...`

- [ ] **Phase 4: Testing**
  - [ ] **4.1: Unit Tests**
    - [ ] Write unit tests for `ChannelFollowRepositoryImpl` methods (mocking DB session).
    *   **Affected Files:**
        *   `app/tests/unit/shared/infrastructure/repositories/discord/test_channel_follow_repository_impl.py`
    - [ ] Write unit tests for `ChannelFollowService` methods (mocking repository and Discord service).
    *   **Affected Files:**
        *   `app/tests/unit/bot/application/services/channel/test_channel_follow_service.py`
  - [ ] **4.2: Integration Tests**
    - [ ] Write integration tests for `ChannelFollowService` (with a test database).
    *   **Affected Files:**
        *   `app/tests/integration/bot/application/services/channel/test_channel_follow_service_integration.py`
    - [ ] Test API endpoints (e.g., using a test client like `httpx`).
    *   **Affected Files:**
        *   `app/tests/integration/web/api/v1/guild/test_channel_follows_api.py`
  - [ ] **4.3: E2E / Manual Testing**
    - [ ] Manually test Discord bot commands (`/follow add`, `/follow remove`, `/follow list`).
    - [ ] Manually test UI interactions in the guild designer for adding, listing, and removing follows.
    - [ ] Verify data persistence and consistency in the database.
    *   **Affected Files:** (N/A - Manual testing steps)

## Documentation

- [ ] **User Documentation**
  - [ ] Document channel following feature
  - [ ] Add examples and use cases

- [ ] **Developer Documentation**
  - [ ] Document API endpoints (related to channel following)
  - [ ] Create architecture documentation (for channel following feature)
  - [ ] Add code examples for extension (of channel following feature)
