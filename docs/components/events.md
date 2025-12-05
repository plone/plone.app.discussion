---
myst:
  html_meta:
    "description": "Events in plone.app.discussion"
    "property=og:description": "Events in plone.app.discussion"
    "property=og:title": "Discussion Events"
    "keywords": "Plone, Discussion, Events, Notifications"
---

# Discussion Events

## Overview

plone.app.discussion provides a rich set of events that are triggered during various comment operations. These events allow for extending the functionality of the discussion system through event subscribers.

## Event Types

### Base Events

All discussion events inherit from the base `IDiscussionEvent` interface:

```python
class IDiscussionEvent(Interface):
    """Base interface for discussion events."""
    
    object = Attribute("The comment that is subject of the event")
    comment = Attribute("Alias for 'object'")
```

### Comment Addition

```python
class ICommentAddedEvent(IDiscussionEvent):
    """Event fired when a comment is added."""

class IReplyAddedEvent(ICommentAddedEvent):
    """Event fired when a reply is added."""
```

### Comment Modification

```python
class ICommentModifiedEvent(IDiscussionEvent):
    """Event fired when a comment is modified."""

class IReplyModifiedEvent(ICommentModifiedEvent):
    """Event fired when a reply is modified."""
```

### Comment Removal

```python
class ICommentRemovedEvent(IDiscussionEvent):
    """Event fired when a comment is removed."""

class IReplyRemovedEvent(ICommentRemovedEvent):
    """Event fired when a reply is removed."""
```

### Comment Workflow

```python
class ICommentTransitionEvent(IDiscussionEvent):
    """Event fired when a workflow transition is performed on a comment."""
    
    old_state = Attribute("Old workflow state")
    new_state = Attribute("New workflow state")
    transition = Attribute("Transition performed")

class ICommentPublishedEvent(ICommentTransitionEvent):
    """Event fired when a comment is published."""
```

## Event Implementation

Events are implemented in `plone.app.discussion.events`:

```python
@implementer(IDiscussionEvent)
class DiscussionEvent:
    """Custom event"""
    
    def __init__(self, object):
        self.object = object
        self.comment = object

@implementer(ICommentAddedEvent)
class CommentAddedEvent(DiscussionEvent):
    """Event to be triggered when a Comment is added"""

@implementer(ICommentModifiedEvent)
class CommentModifiedEvent(DiscussionEvent):
    """Event to be triggered when a Comment is modified"""

# etc.
```

## Email Notifications

One of the primary uses of discussion events is triggering email notifications.

### Moderator Notifications

When a comment is added and moderation is enabled, an email is sent to moderators:

```python
def notify_comment_added(event):
    """Event handler for sending emails when comments are added."""
    
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IDiscussionSettings, check=False)
    
    if settings.moderator_notification_enabled:
        # Send email to moderators
```

### User Notifications

When a reply is added to a user's comment, the user can receive a notification:

```python
def notify_user_reply_added(event):
    """Event handler for sending emails to users on replies."""
    
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IDiscussionSettings, check=False)
    
    if settings.user_notification_enabled and IReplyAddedEvent.providedBy(event):
        # Send email to the author of the parent comment
```

## Subscribing to Events

To subscribe to discussion events, use the standard Zope event system:

```python
from plone.app.discussion.interfaces import ICommentAddedEvent
from zope.component import adapter

@adapter(ICommentAddedEvent)
def my_comment_added_handler(event):
    """Handle comment added event."""
    comment = event.object
    # Do something with the comment
```

Register the subscriber in ZCML:

```xml
<subscriber
    for="plone.app.discussion.interfaces.ICommentAddedEvent"
    handler=".events.my_comment_added_handler"
    />
```

## Content Rules Integration

Discussion events can be leveraged in Plone's content rules system:

1. Events are exposed as content rule triggers
2. This allows site administrators to create custom rules for comment events
3. Rules can send notifications, move comments, tag content, etc.

## Content Rule Conditions

The `contentrules.py` module defines several conditions for content rules:

```python
class CommentAuthorCondition(SimpleCondition):
    """Content rule condition: comment author is a specific user."""
    
    author_name = schema.TextLine(title=_(u"Username"),
                                   description=_(u"The username to check for"),
                                   required=True)
    
    def evaluate(self):
        comment = self.event.object
        if IComment.providedBy(comment):
            return comment.author_username == self.data.author_name
        return False
```

Available conditions include:

- `ICommentAuthorCondition` - Comment was authored by a specific user
- `ICommentTextCondition` - Comment text matches a pattern
- `ICommentInReplyToCondition` - Comment is a reply to a specific comment

## Custom Event Subscribers

You can implement your own custom event subscribers, for example:

```python
from plone.app.discussion.interfaces import ICommentAddedEvent

@adapter(ICommentAddedEvent)
def log_comment_activity(event):
    """Log comment activity to a custom log file."""
    comment = event.object
    logger = logging.getLogger('comment_activity')
    logger.info(f"Comment added by {comment.author_name} on {comment.creation_date}")
```

## Related Components

- [Comment](./comment.md) - The objects that generate events
- [Moderation](./moderation.md) - Workflow transitions that generate events
