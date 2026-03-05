"""
User Ban Management System Usage Examples
========================================

This file demonstrates how to use the comprehensive user ban management system
implemented in plone.app.discussion.

## Overview

The ban system provides three types of bans:

1. **Cooldown Bans**: Temporary restrictions that automatically expire
2. **Shadow Bans**: Comments appear published to the author but are hidden from others
3. **Permanent Bans**: Complete restriction from commenting until manually lifted

## Basic Usage

### Enabling the Ban System

First, enable the ban system in the discussion control panel:

```python
from plone.registry.interfaces import IRegistry
from plone.app.discussion.interfaces import IDiscussionSettings
from zope.component import getUtility

# Get the registry
registry = getUtility(IRegistry)
settings = registry.forInterface(IDiscussionSettings, check=False)

# Enable the ban system
settings.ban_enabled = True
settings.shadow_ban_notification_enabled = False  # Optional: hide shadow bans from users
settings.default_cooldown_duration = 24  # Default duration in hours
```

### Basic Ban Operations

```python
from plone.app.discussion.ban import get_ban_manager, BAN_TYPE_COOLDOWN, BAN_TYPE_SHADOW, BAN_TYPE_PERMANENT

# Get a ban manager for your content object
ban_manager = get_ban_manager(context)

# Ban a user for 24 hours (cooldown)
cooldown_ban = ban_manager.ban_user(
    user_id="problematic_user",
    ban_type=BAN_TYPE_COOLDOWN,
    moderator_id="admin",
    reason="Repeatedly posting spam comments",
    duration_hours=24
)

# Shadow ban a user (comments hidden from others)
shadow_ban = ban_manager.ban_user(
    user_id="suspicious_user", 
    ban_type=BAN_TYPE_SHADOW,
    moderator_id="admin",
    reason="Suspected trolling behavior",
    duration_hours=72  # 3 days
)

# Permanently ban a user
permanent_ban = ban_manager.ban_user(
    user_id="banned_user",
    ban_type=BAN_TYPE_PERMANENT,
    moderator_id="admin",
    reason="Severe violation of community guidelines"
)
```

### Checking Ban Status

```python
# Check if a user is banned
is_banned = ban_manager.is_user_banned("username")

# Get ban details
ban = ban_manager.get_user_ban("username")
if ban:
    print(f"User banned: {ban.ban_type}")
    print(f"Reason: {ban.reason}")
    if ban.expires_date:
        print(f"Expires: {ban.expires_date}")

# Check if user can comment (considers all ban types)
from plone.app.discussion.ban import can_user_comment, is_comment_visible

can_comment = can_user_comment(context, "username")
comment_visible = is_comment_visible(context, "username")
```

### Managing Bans

```python
# Get all active bans
active_bans = ban_manager.get_active_bans()
for ban in active_bans:
    print(f"{ban.user_id}: {ban.ban_type} (expires: {ban.expires_date})")

# Unban a user
ban_manager.unban_user("username", "admin")

# Clean up expired bans
expired_count = ban_manager.cleanup_expired_bans()
print(f"Cleaned up {expired_count} expired bans")
```

## Web Interface Usage

### Ban Management View

Access the ban management interface at:
- `http://yoursite.com/@@ban-management`

This provides:
- Quick ban form for users
- List of active bans with details
- Bulk actions (cleanup expired bans)

### Individual User Ban Form

Ban a specific user at:
- `http://yoursite.com/@@ban-user-form?user_id=username`

Features:
- User information display
- Ban type selection with descriptions
- Duration setting for temporary bans
- Reason field

## Advanced Usage

### Custom Ban Duration

```python
from datetime import datetime, timedelta

# Custom expiration date
custom_expiry = datetime.now() + timedelta(days=7, hours=12)
ban_manager.ban_user(
    user_id="user",
    ban_type=BAN_TYPE_COOLDOWN,
    moderator_id="admin",
    expires_date=custom_expiry
)
```

### Integration with Comment Form

The ban system automatically integrates with the comment form. When a banned user
tries to comment:

```python
# This is handled automatically in CommentForm.handleComment()
from plone.app.discussion.browser.ban_integration import check_user_ban_before_comment

# Returns False if user is banned, shows appropriate message
allowed = check_user_ban_before_comment(comment_form, data)
```

### Filtering Shadow Banned Comments

```python
# Filter comments to hide shadow banned users' comments
from plone.app.discussion.browser.ban_integration import filter_shadow_banned_comments

comments = conversation.getComments()
visible_comments = filter_shadow_banned_comments(comments, context)
```

## Permissions

The ban system uses the existing "Review comments" permission:
- Users with this permission can ban/unban other users
- Regular users cannot see ban management interfaces

## Notifications

Ban notifications are shown to users via status messages:

- **Cooldown Ban**: Shows remaining time
- **Shadow Ban**: Optional notification (configurable)
- **Permanent Ban**: Clear notification of permanent status

## Storage

Bans are stored in portal annotations using the key:
`plone.app.discussion:conversation`

Data persists across restarts and is automatically cleaned up for expired bans.

## Error Handling

The system gracefully handles:
- Missing ban system (ImportError protection)
- Invalid user IDs
- Expired bans (automatic cleanup)
- Permission checks

## Migration

When upgrading from older versions:
1. Enable the ban system in the control panel
2. Existing comments remain unaffected
3. Ban data is stored separately from comment data
"""
