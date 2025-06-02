---
myst:
  html_meta:
    "description": "Comment component in plone.app.discussion"
    "property=og:description": "Comment component in plone.app.discussion"
    "property=og:title": "Comment Component"
    "keywords": "Plone, Discussion, Comment, IComment"
---

# Comment Component

## Overview

The Comment component is the core object that represents a user comment in the plone.app.discussion system. Comments are lightweight content objects that store the actual comment text and metadata.

## Interfaces

The primary interface for comments is `IComment`, defined in `plone.app.discussion.interfaces`:

```python
class IComment(Interface):
    """A comment.
    
    Comments are stored in IConversation objects and contained in them.
    """
    
    portal_type = schema.ASCIILine(
        title=_("Portal type"),
        default="Discussion Item",
        readonly=True,
    )
    
    __parent__ = schema.Object(
        title=_("Conversation"), 
        schema=Interface,
    )
    
    __name__ = schema.TextLine(title=_("Name"), default=None)
    
    comment_id = schema.Int(
        title=_("Comment id"), 
        default=None,
    )
    
    in_reply_to = schema.Int(
        title=_("In reply to"), 
        default=0,
    )
    
    # plus additional fields for content, author info, etc.
```

## Implementation

The `Comment` class implements the `IComment` interface and is defined in `plone.app.discussion.comment`. It inherits from several base classes to provide its functionality:

```python
@implementer(IComment)
class Comment(
    CatalogAware,
    WorkflowAware,
    DynamicType,
    Traversable,
    RoleManager,
    Owned,
    Implicit,
    Persistent,
):
    """A comment.
    
    Comments are stored in Conversation objects and contained in them.
    """
```

The base classes provide the following capabilities:

- `CatalogAware` - For indexing in the portal_catalog
- `WorkflowAware` - For workflow integration
- `DynamicType` - For dynamic type information
- `Traversable` - For traversal support (URLs)
- `RoleManager` - For permissions and role management
- `Owned` - For ownership tracking
- `Implicit` - For implicit acquisition
- `Persistent` - For ZODB persistence

## Key Attributes

A comment has several important attributes:

- `text`: The actual comment text
- `creator`: The user who created the comment
- `creation_date`: When the comment was created
- `modification_date`: When the comment was last modified  
- `author_name`: Display name of the author
- `author_email`: Email of the author
- `title`: Auto-generated title based on author and content
- `mime_type`: MIME type of the comment text (plain text, HTML, etc.)
- `comment_id`: Unique identifier for the comment
- `in_reply_to`: ID of the parent comment (0 for top-level comments)

## Usage

### Creating a Comment

Comments are created using the `createObject` factory:

```python
from zope.component import createObject

comment = createObject("plone.Comment")
comment.text = "This is a comment"
comment.author_name = "John Doe"
comment.author_email = "john@example.com"
```

### Adding a Comment to a Conversation

```python
from plone.app.discussion.interfaces import IConversation

conversation = IConversation(context)
comment_id = conversation.addComment(comment)
```

### Retrieving a Comment

```python
# By traversal
comment = context.restrictedTraverse("++conversation++default/123")

# Or from the conversation
conversation = IConversation(context)
comment = conversation.get(comment_id)
```

## Workflow Integration

Comments can be subject to workflow. The default workflows provided are:

1. `comment_one_state_workflow` - Comments are immediately published
2. `comment_review_workflow` - Comments require moderation before publishing

Workflows are applied to the "Discussion Item" portal type.

## Events

When comments are added, modified, or removed, corresponding events are fired:

- `ICommentAddedEvent` - When a comment is added to a conversation
- `ICommentModifiedEvent` - When a comment is modified
- `ICommentRemovedEvent` - When a comment is removed

## Related Components

- [Conversation](./conversation.md) - Container for comments
- [Events](./events.md) - Event system for comments
- [Form](./form.md) - UI for adding and editing comments
