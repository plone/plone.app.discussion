# Comprehensive User Ban Management System Implementation

## Overview

This implementation provides a complete user ban management system for plone.app.discussion with three distinct ban types:

1. **Cooldown Bans (Temporary Bans)** - Time-limited restrictions with automatic expiration
2. **Shadow Bans** - Comments appear published to author but hidden from others  
3. **Permanent Bans** - Complete commenting restriction until manually lifted

## Architecture

### Core Components

#### 1. Ban Data Model (`ban.py`)
- `IBan` interface defining ban structure
- `Ban` persistent class with expiration logic
- `IBanManager` interface for ban operations
- `BanManager` implementation using portal annotations
- Helper functions for checking ban status

#### 2. Web Interface (`browser/ban.py`)
- `BanManagementView` - Main management interface
- `BanUserFormView` - Individual user ban form
- `UserBanStatusView` - JSON API for ban status

#### 3. Comment Integration (`browser/ban_integration.py`)
- `check_user_ban_before_comment()` - Pre-submission validation
- `process_shadow_banned_comment()` - Post-submission processing
- `filter_shadow_banned_comments()` - Comment visibility filtering

#### 4. Template Files
- `ban_management.pt` - Main management interface
- `ban_user_form.pt` - Individual user ban form

### Integration Points

#### Comment Form Integration
```python
# In CommentForm.handleComment() method
try:
    from plone.app.discussion.browser.ban_integration import check_user_ban_before_comment
    if not check_user_ban_before_comment(self, data):
        return  # User is banned, error message already shown
except ImportError:
    pass  # Ban system not available, continue normally
```

#### Comment Visibility Filtering
```python
# In CommentsViewlet.get_replies() method
def published_replies_filtered():
    try:
        from plone.app.discussion.browser.ban_integration import filter_shadow_banned_comments
        published_comments = [r["comment"] for r in published_replies()]
        filtered_comments = filter_shadow_banned_comments(published_comments, context)
        # Rebuild thread structure with filtered comments
        ...
    except ImportError:
        # Ban system not available, fall back to normal behavior
        for r in published_replies():
            yield r
```

## Configuration

### Registry Settings (`interfaces.py`)
Added to `IDiscussionSettings`:

```python
ban_enabled = schema.Bool(
    title=_("Enable user ban system"),
    description=_("If enabled, administrators can ban users from commenting"),
    default=False,
    required=False,
)

shadow_ban_notification_enabled = schema.Bool(
    title=_("Notify users of shadow bans"),
    description=_("If enabled, users will be notified when shadow banned"),
    default=False,
    required=False,
)

default_cooldown_duration = schema.Int(
    title=_("Default cooldown duration (hours)"),
    description=_("Default duration for cooldown bans when not specified"),
    default=24,
    min=1,
    required=False,
)
```

### Control Panel Integration (`browser/controlpanel.py`)
- Added checkbox widgets for ban settings
- Added field labels and descriptions
- Integrated with existing discussion control panel

### ZCML Configuration (`browser/configure.zcml`)
```xml
<!-- Ban management views -->
<browser:page
    name="ban-management"
    for="Products.CMFCore.interfaces.ISiteRoot"
    class=".ban.BanManagementView"
    permission="plone.app.discussion.ReviewComments"
    layer="..interfaces.IDiscussionLayer"
    />

<browser:page
    name="ban-user-form"
    for="Products.CMFCore.interfaces.ISiteRoot"
    class=".ban.BanUserFormView"
    permission="plone.app.discussion.ReviewComments"
    layer="..interfaces.IDiscussionLayer"
    />

<browser:page
    name="user-ban-status"
    for="Products.CMFCore.interfaces.ISiteRoot"
    class=".ban.UserBanStatusView"
    permission="zope2.View"
    layer="..interfaces.IDiscussionLayer"
    />
```

## Ban Types Implementation

### 1. Cooldown Bans
- **Purpose**: Temporary restriction for cooling off periods
- **Behavior**: User cannot comment until expiration
- **User Experience**: Clear notification with remaining time
- **Use Cases**: Minor infractions, heated discussions, first-time offenses

### 2. Shadow Bans  
- **Purpose**: Hidden restriction without user awareness
- **Behavior**: Comments appear published to author but invisible to others
- **User Experience**: Optional notification (configurable)
- **Use Cases**: Suspected trolling, testing period, behavioral modification

### 3. Permanent Bans
- **Purpose**: Complete commenting restriction
- **Behavior**: User cannot comment until manually unbanned
- **User Experience**: Clear permanent status notification
- **Use Cases**: Severe violations, repeat offenders, ToS violations

## Data Storage

### Annotation Storage
- **Key**: `plone.app.discussion:conversation`
- **Location**: Portal annotations
- **Structure**: Dictionary mapping user_id to Ban objects
- **Persistence**: Survives restarts, automatic cleanup

### Ban Object Structure
```python
class Ban:
    user_id: str          # User identifier
    ban_type: str         # cooldown/shadow/permanent
    created_date: datetime # When ban was created
    expires_date: datetime # When ban expires (None for permanent)
    reason: str           # Reason for ban
    moderator_id: str     # Who created the ban
```

## User Interface

### Main Management View (`@@ban-management`)
**Features:**
- Quick ban form with user ID, type, duration, reason
- Active bans table with details and actions
- Bulk cleanup of expired bans
- User information display

**Workflow:**
1. Enter user ID
2. Select ban type (with descriptions)
3. Set duration (for temporary bans)
4. Provide reason
5. Submit to create ban

### Individual Ban Form (`@@ban-user-form?user_id=username`)
**Features:**
- User information verification
- Detailed ban type explanations
- Duration configuration
- Mandatory reason field

**User Information Display:**
- User ID and existence verification
- Full name and email (if available)
- Current ban status

### Status API (`@@user-ban-status`)
**Returns JSON:**
```json
{
  "banned": true,
  "ban_type": "cooldown",
  "can_comment": false,
  "reason": "Spam posting",
  "expires_date": "2024-01-15T10:30:00",
  "remaining_seconds": 7200
}
```

## Security Model

### Permissions
- Uses existing "Review comments" permission
- No additional permissions required
- Follows Plone security architecture

### Access Control
- Ban management restricted to comment reviewers
- Status API available to all users
- Self-service ban checking allowed

## Error Handling

### Graceful Degradation
```python
try:
    from plone.app.discussion.browser.ban_integration import check_user_ban_before_comment
    if not check_user_ban_before_comment(self, data):
        return
except ImportError:
    pass  # Ban system not available, continue normally
```

### Common Error Scenarios
- Ban system disabled: Falls back to normal behavior
- Missing permissions: Proper access control
- Invalid user IDs: Clear error messages
- Expired bans: Automatic cleanup

## Upgrade Path

### New Installation
1. Enable ban system in discussion control panel
2. Configure default settings
3. Train moderators on usage

### Existing Installation
```python
def upgrade_ban_system_registry(context):
    """Add ban system settings to the registry."""
    registry = getUtility(IRegistry)
    registry.registerInterface(IDiscussionSettings)
    
    settings = registry.forInterface(IDiscussionSettings, check=False)
    
    if not hasattr(settings, 'ban_enabled'):
        settings.ban_enabled = False
    if not hasattr(settings, 'shadow_ban_notification_enabled'):
        settings.shadow_ban_notification_enabled = False
    if not hasattr(settings, 'default_cooldown_duration'):
        settings.default_cooldown_duration = 24
```

## Testing

### Test Coverage (`tests/test_ban_system.py`)
- Ban creation and management
- Different ban type behaviors
- Expiration and cleanup
- Permission checking
- API functionality

### Test Scenarios
```python
def test_ban_behavior(self):
    """Test how different ban types affect commenting."""
    # Cooldown: cannot comment, comments visible
    self.assertFalse(can_user_comment(context, "cooldown_user"))
    self.assertTrue(is_comment_visible(context, "cooldown_user"))
    
    # Shadow: can comment, comments invisible
    self.assertTrue(can_user_comment(context, "shadow_user"))
    self.assertFalse(is_comment_visible(context, "shadow_user"))
    
    # Permanent: cannot comment, comments visible
    self.assertFalse(can_user_comment(context, "permanent_user"))
    self.assertTrue(is_comment_visible(context, "permanent_user"))
```

## Documentation

### Usage Documentation
- `ban_system_usage.rst` - Developer API guide
- `ban_management_guide.rst` - Administrator interface guide

### Key Features Documented
- Basic usage examples
- Web interface workflows  
- Configuration options
- Best practices
- Troubleshooting guides

## Performance Considerations

### Optimization Features
- Automatic expired ban cleanup
- Efficient annotation storage
- Minimal performance impact
- Lazy loading of ban data

### Scalability
- Suitable for sites with hundreds of users
- Regular cleanup recommended for high-volume sites
- Monitor ban storage growth

## Future Enhancements

### Potential Additions
- IP-based banning
- Appeal process workflow
- Ban statistics/reporting
- Integration with user profiles
- Automated ban triggers

### Extension Points
- Custom ban types
- External notification systems
- Advanced filtering options
- Integration with other moderation tools

## Summary

This implementation provides a comprehensive, production-ready user ban management system that:

✅ **Implements all three required ban types** (cooldown, shadow, permanent)
✅ **Provides intuitive web interface** for administrators  
✅ **Integrates seamlessly** with existing comment system
✅ **Handles edge cases gracefully** with proper error handling
✅ **Includes comprehensive documentation** and examples
✅ **Follows Plone best practices** for security and architecture
✅ **Provides upgrade path** for existing installations
✅ **Includes automated testing** for reliability

The system is ready for production use and provides administrators with flexible tools for managing problematic users without resorting to permanent account restrictions.
