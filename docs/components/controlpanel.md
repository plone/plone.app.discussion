---
myst:
  html_meta:
    "description": "Discussion control panel in plone.app.discussion"
    "property=og:description": "Discussion control panel in plone.app.discussion"
    "property=og:title": "Discussion Control Panel"
    "keywords": "Plone, Discussion, Control Panel, Settings"
---

# Discussion Control Panel

## Overview

The Discussion Control Panel provides a centralized interface for configuring the global settings of the plone.app.discussion system. It uses `plone.registry` to store and manage these settings.

## Implementation

The control panel is implemented in `plone.app.discussion.browser.controlpanel`:

```python
class DiscussionSettingsEditForm(controlpanel.RegistryEditForm):
    """Discussion settings form."""
    
    schema = IDiscussionSettings
    id = "DiscussionSettingsEditForm"
    label = _("Discussion settings")
    
    # Form implementation details
```

```python
class DiscussionSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """Discussion settings control panel."""
    
    form = DiscussionSettingsEditForm
    index = ViewPageTemplateFile("controlpanel.pt")
```

## Settings Schema

The settings schema is defined in `plone.app.discussion.interfaces.IDiscussionSettings`:

```python
class IDiscussionSettings(Interface):
    """Global discussion settings.
    
    Interface for the plone.registry configuration records.
    """
    
    globally_enabled = schema.Bool(
        title=_("Globally enable comments"),
        description=_("Enable comments globally"),
        required=True,
        default=False,
    )
    
    anonymous_comments = schema.Bool(
        title=_("Anonymous comments"),
        description=_("Enable anonymous comments"),
        required=True,
        default=False,
    )
    
    moderation_enabled = schema.Bool(
        title=_("Comment moderation"),
        description=_("Require moderation for all comments"),
        required=True,
        default=False,
    )
    
    # Additional settings for email, captcha, etc.
```

## Available Settings

The control panel provides settings for:

### Core Functionality

- `globally_enabled` - Enable/disable commenting globally
- `moderation_enabled` - Enable comment moderation for all comments
- `edit_comment_enabled` - Allow users to edit their own comments
- `delete_own_comment_enabled` - Allow users to delete their own comments
- `anonymous_comments` - Allow anonymous users to comment

### Display Options

- `show_commenter_image` - Show user portrait images
- `text_transform` - Text transformation method for comments

### CAPTCHA

- `captcha` - CAPTCHA method for anonymous comments (disabled, standard, recaptcha, norobots, hcaptcha)

### Email Notifications

- `moderator_notification_enabled` - Email notifications for moderators
- `user_notification_enabled` - Email notifications for users (on replies)

## Form Widgets

The control panel form uses custom widgets for better user experience:

```python
def updateWidgets(self):
    super().updateWidgets()
    self.widgets["globally_enabled"].label = _("Enable Comments")
    self.widgets["anonymous_comments"].label = _("Anonymous Comments")
    self.widgets["show_commenter_image"].label = _("Commenter Image")
    # etc.
```

Most boolean fields use `SingleCheckBoxFieldWidget` for a cleaner UI.

## Warning Messages

The control panel displays warning messages for common issues:

### Mail Host Warning

If email notifications are enabled but the mail server isn't configured:

```python
def mailhost_warning(self):
    """Returns true if mailhost is not configured properly."""
    registry = getUtility(IRegistry)
    mail_settings = registry.forInterface(IMailSchema, prefix="plone")
    return not mail_settings.email_from_address or not mail_settings.smtp_host
```

### Custom Workflow Warning

If a custom workflow is used for the Discussion Item type:

```python
def custom_comment_workflow_warning(self):
    """Return True if a custom comment workflow is enabled."""
    wftool = getToolByName(self.context, "portal_workflow", None)
    workflow_chain = wftool.getChainForPortalType("Discussion Item")
    one_state_workflow_enabled = "comment_one_state_workflow" in workflow_chain
    comment_review_workflow_enabled = "comment_review_workflow" in workflow_chain
    return not (one_state_workflow_enabled or comment_review_workflow_enabled)
```

## REST API Integration

The control panel also provides a REST API endpoint for Volto and other clients:

```python
@adapter(Interface, IControlpanelLayer)
class DiscussionControlPanel(RegistryConfigletPanel):
    """Volto-compatible REST API control panel for discussion settings."""
    
    schema = IDiscussionSettings
    schema_prefix = None
    configlet_id = "discussion"
    configlet_category_id = "plone-content"
    title = _("Discussion")
    group = "Content"
```

## Events

Configuration changes trigger events that subscribers can listen to:

```python
def notify_configuration_changed(event):
    """Event subscriber that is called every time the configuration changed."""
    if IRecordModifiedEvent.providedBy(event) and \
       event.record.interface == IDiscussionSettings:
        pass  # Handle configuration change
```

## Accessing Settings

The settings can be accessed from code using the registry:

```python
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from plone.app.discussion.interfaces import IDiscussionSettings

registry = queryUtility(IRegistry)
settings = registry.forInterface(IDiscussionSettings)

# Access settings
if settings.globally_enabled:
    # Comments are enabled globally
```

## Related Components

- [Behavior](./behavior.md) - Per-content type and per-item settings
- [Moderation](./moderation.md) - Comment moderation system
- [Conversation](./conversation.md) - Uses settings to determine if comments are enabled
