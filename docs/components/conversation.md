---
myst:
  html_meta:
    "description": "Conversation component in plone.app.discussion"
    "property=og:description": "Conversation component in plone.app.discussion"
    "property=og:title": "Conversation Component"
    "keywords": "Plone, Discussion, Conversation, IConversation"
---

# Conversation Component

## Overview

The Conversation component is the container for comments in the plone.app.discussion system. Each content object that allows commenting has an associated Conversation object, which is stored as an annotation on the content.

## Interfaces

### IConversation

The primary interface for conversations is `IConversation`, defined in `plone.app.discussion.interfaces`:

```python
class IConversation(IIterableMapping):
    """A conversation about a content object.

    This is a persistent object in its own right and manages all comments.

    The dict interface allows access to all comments. They are stored by
    long integer key, in the order they were added.
    """

    total_comments = schema.Int(
        title=_("Total number of public comments on this item"),
        min=0,
        readonly=True,
    )

    last_comment_date = schema.Date(
        title=_("Date of the most recent public comment"),
        readonly=True,
    )

    commentators = schema.Set(
        title=_("The set of commentators (usernames)"),
        readonly=True,
    )
```

### IReplies

The `IReplies` interface represents the set of replies to a specific comment or the top-level comments in a conversation:

```python
class IReplies(IIterableMapping):
    """A set of related comments.
    
    This is a dict-like object that can be used to access comments that are
    either direct replies to a content object (i.e. the root comments in a 
    conversation) or replies to another comment.
    """
```

## Implementation

The `Conversation` class implements the `IConversation` interface:

```python
@implementer(IConversation, IHideFromBreadcrumbs)
class Conversation(Traversable, Persistent, Explicit):
    """A conversation about a content object.
    
    This implements a dict-like API for accessing comments by id.
    """
```

Two adapter implementations provide the `IReplies` interface:

1. `ConversationReplies` - For top-level comments in a conversation
2. `CommentReplies` - For replies to a specific comment

## Storage Model

The conversation maintains three dictionary-like structures:

1. `_comments` - Maps comment IDs to actual comment objects
2. `_children` - Maps IDs (including 0 for the root) to sets of child comment IDs
3. `_depths` - Cache of comment depths for efficient retrieval

## Key Methods

### Comment Management

- `addComment(comment)` - Adds a comment to the conversation
- `__delitem__(key)` - Removes a comment from the conversation
- `getComments()` - Returns an iterator of all comments
- `getThreads()` - Returns an iterator of all comments with their depths

### Collection-like Methods

- `__getitem__(key)` - Retrieves a comment by ID
- `get(key, default=None)` - Retrieves a comment by ID with a default value
- `keys()` - Returns all comment IDs
- `values()` - Returns all comments
- `items()` - Returns (id, comment) pairs
- `__iter__()` - Iterates over comment IDs

### Enabling Comments

The conversation object has a method to check if commenting is enabled on its content:

```python
def enabled(self):
    """Return True if commenting is enabled on this conversation."""
```

This is implemented in the `ConversationView` class, which considers:

1. Global settings from `IDiscussionSettings`
2. Content-specific settings (the `allow_discussion` attribute)
3. Content type settings from `portal_types`

## Usage

### Getting a Conversation

```python
from plone.app.discussion.interfaces import IConversation

conversation = IConversation(context)
```

### Adding a Comment

```python
from zope.component import createObject

comment = createObject("plone.Comment")
comment.text = "This is a comment"

comment_id = conversation.addComment(comment)
```

### Accessing Comments

```python
# Get a specific comment
comment = conversation.get(comment_id)

# Iterate through all comments
for comment in conversation.values():
    print(comment.text)

# Get only top-level comments
from plone.app.discussion.interfaces import IReplies
for comment in IReplies(conversation).values():
    print(comment.text)

# Get replies to a specific comment
for reply in IReplies(comment).values():
    print(reply.text)
```

### Deleting Comments

```python
# Delete a comment
del conversation[comment_id]
```

## Traversal

Conversations can be traversed to via the `++conversation++default` namespace:

```
path/to/content/++conversation++default/123
```

retrieves comment 123 from the conversation of the content object.

## Related Components

- [Comment](./comment.md) - The comment objects stored in conversations
- [Behavior](./behavior.md) - Controls whether commenting is enabled
- [Viewlet](./viewlet.md) - Displays the conversation UI
