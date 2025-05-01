# Structure Workflow Documentation

## Overview

The Structure Workflow is responsible for managing the Discord server structure, including categories, channels, and their relationships. This module handles operations such as:

1. Creating, updating, and deleting categories and channels
2. Managing permissions for server structure elements
3. Applying templates to create consistent server layouts
4. Tracking relationships between channels, including channel follows
5. Managing dashboards and UI panels within channels

## Key Components

### Channel Following

Discord offers a feature called "Channel Following" that allows announcement channels (news channels) to be followed by other channels. When a message is posted in the source channel, it's automatically crossposted to all follower channels.

**Technical Implementation:**
- Uses Discord's built-in webhook system to relay messages
- Only applies to announcement channels (type: news)
- Messages appear as if they were posted by the original author

### Dashboard Panels

The bot can create and manage dashboard panels in channels. These panels provide interactive UI elements for server management, statistics, and other features.

**Technical Details:**
- Dashboards are created as messages with embeds and/or components
- They can include buttons, select menus, and other interactive elements
- Data is stored in the database to enable persistence and updates

## Database Structure

The module works with these primary database entities:

1. `GuildEntity` - Represents a Discord server/guild
2. `CategoryEntity` - Represents Discord channel categories
3. `ChannelEntity` - Represents Discord channels
4. `ChannelFollowEntity` - Tracks which channels follow other channels
5. `DashboardEntity` - Represents dashboard panels in channels
6. `DashboardComponentEntity` - Individual components within dashboards

## Workflows

### Channel Creation Workflow

1. Check if a channel with the same name already exists
2. If exists, update properties as needed
3. If doesn't exist, create new channel
4. Apply appropriate permissions

### Channel Following Workflow

1. Verify source channel is an announcement channel
2. Verify target channel can receive messages
3. Create follow relationship using Discord API
4. Store relationship in database for tracking

### Dashboard Creation Workflow

1. Create dashboard configuration in database
2. Generate message content based on template
3. Send message to specified channel
4. Store message ID for future updates

## Integration Points

- Interacts with Discord API for server structure operations
- Uses database to persist configuration and state
- Interfaces with template system for standardized layouts
- Coordinates with permission system for access control 