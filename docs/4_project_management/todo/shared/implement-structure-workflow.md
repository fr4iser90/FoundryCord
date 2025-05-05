# Structure Workflow Implementation TODO

**(See also: [Guild Designer Main TODO](../../../../4_project_management/todo/guild_designer.md))**

## Channel Following Feature

**(Implementation Details: [channel_follow_implementation.md](./channel_follow_implementation.md))**

- [ ] **Create Database Entities**
  - [ ] Create `ChannelFollowEntity` table for storing follow relationships
  - [ ] Define appropriate fields: source_channel_id, target_channel_id, guild_id, webhook_id, webhook_token
  - [ ] Add created_at timestamp and status fields

- [ ] **Implement Repository Layer**
  - [ ] Create `ChannelFollowRepository` interface in domain layer
  - [ ] Implement `ChannelFollowRepositoryImpl` in infrastructure layer
  - [ ] Add CRUD methods for managing follow relationships
  - [ ] Add method to get all follows for a source channel
  - [ ] Add method to get all sources following a target channel

- [ ] **Create Service Layer**
  - [ ] Implement `ChannelFollowService` for business logic
  - [ ] Add method to follow a channel (create relationship)
  - [ ] Add method to unfollow a channel (remove relationship)
  - [ ] Add validation to ensure only announcement channels can be followed
  - [ ] Add method to get follow status for a given channel

- [ ] **API Endpoints**
  - [ ] Create REST endpoint for following a channel
  - [ ] Create REST endpoint for unfollowing a channel
  - [ ] Create endpoint for retrieving follows status
  - [ ] Add proper authentication and authorization

- [ ] **Discord Bot Commands**
  - [ ] Implement `/follow` command to follow a channel
  - [ ] Implement `/unfollow` command to remove a follow
  - [ ] Implement `/follows` command to list all followed channels
  - [ ] Add appropriate permission checks

- [ ] **UI Implementation**
  - [ ] Add UI component to channel settings page for follows
  - [ ] Create modal for following new channels
  - [ ] Display list of followed channels and following channels
  - [ ] Add ability to remove follows from UI
  
- [ ] **Testing**
  - [ ] Unit tests for repository methods
  - [ ] Integration tests for service methods
  - [ ] End-to-end tests for API endpoints
  - [ ] Manual testing of Discord bot commands

## Dashboard Panels Enhancement

- [ ] **Extend Dashboard Entities**
  - [ ] Update `DashboardEntity` with fields for tracking channel follows
  - [ ] Add configuration options for auto-following channels

- [ ] **Dashboard Follow Integration**
  - [ ] Add functionality to automatically follow source channels
  - [ ] Implement auto-creation of dashboards in follower channels
  - [ ] Add synchronization of dashboard updates across followers

- [ ] **Dashboard Template System**
  - [ ] Create templates for dashboard panels
  - [ ] Add ability to apply templates across multiple channels
  - [ ] Implement template version control

- [ ] **Dashboard Component Library**
  - [ ] Create reusable components for common dashboard elements
  - [ ] Implement responsive design for different channel types
  - [ ] Add interactive elements (buttons, dropdowns)

- [ ] **Permission System**
  - [ ] Add granular permissions for dashboard management
  - [ ] Restrict dashboard access based on user roles
  - [ ] Allow configurable permission inheritance from source channels

- [ ] **Database Migration**
  - [ ] Create migration scripts for new tables and fields
  - [ ] Implement data backfill for existing installations
  - [ ] Add database indexes for performance

## Documentation

- [ ] **User Documentation**
  - [ ] Document channel following feature
  - [ ] Create dashboard management guide
  - [ ] Add examples and use cases

- [ ] **Developer Documentation**
  - [ ] Document API endpoints
  - [ ] Create architecture documentation
  - [ ] Add code examples for extension
