---
myst:
  html_meta:
    "description": "Discussion tool in plone.app.discussion"
    "property=og:description": "Discussion tool in plone.app.discussion"
    "property=og:title": "Discussion Tool"
    "keywords": "Plone, Discussion, CommentingTool"
---

# Discussion Tool

## Overview

The `portal_discussion` tool provides centralized functionality for indexing and searching comments in plone.app.discussion. It's an instance of the `CommentingTool` class.

## Implementation

The tool is defined in `plone.app.discussion.tool`:

```python
@interface.implementer(ICommentingTool)
class CommentingTool(UniqueObject, SimpleItem):
    """plone.app.discussion tool.
    
    The primary purpose of this tool is indexing and searching comments.
    """
    
    meta_type = "plone.app.discussion tool"
    id = "portal_discussion"
```

## Interface

The tool implements the `ICommentingTool` interface:

```python
class ICommentingTool(Interface):
    """plone.app.discussion tool interface.
    
    This tool provides comment-specific functionality like searching for
    comments.
    """
```

## Functions

### Indexing Comments

The tool provides functions for indexing comments in the portal_catalog:

```python
def reindexObject(self, object):
    """Reindex the comment in the catalog."""
    catalog = getToolByName(self, "portal_catalog")
    catalog.reindexObject(object)

indexObject = reindexObject  # Alias for backward compatibility

def unindexObject(self, object):
    """Remove the comment from the catalog."""
    catalog = getToolByName(self, "portal_catalog")
    catalog.unindexObject(object)
```

### Searching for Comments

The tool provides a specialized search function that limits results to comments:

```python
def searchResults(self, REQUEST=None, **kw):
    """Search the catalog for comments.
    
    Calls ZCatalog.searchResults with extra arguments that limit the
    results to comments (objects providing IComment).
    """
    catalog = getToolByName(self, "portal_catalog")
    object_provides = [IComment.__identifier__]
    
    # Add any object_provides from the request or kw
    # ...
    
    kw["object_provides"] = object_provides
    return catalog.searchResults(REQUEST, **kw)
```

### Retrieving Unique Values

The tool allows retrieving unique values for specific catalog indexes:

```python
def uniqueValuesFor(self, name):
    """Return unique values for a specific metadata column of comments."""
    catalog = getToolByName(self, "portal_catalog")
    return catalog.uniqueValuesFor(name)
```

## Event Subscribers

The module also defines event subscribers for indexing and unindexing comments:

```python
def index_object(obj, event):
    """Index the object when added to the conversation"""
    # Skip if object isn't a comment
    if not IComment.providedBy(obj):
        return
    
    tool = queryUtility(ICommentingTool)
    if tool is not None:
        tool.indexObject(obj)

def unindex_object(obj, event):
    """Unindex the object when removed"""
    # Skip if object isn't a comment
    if not IComment.providedBy(obj):
        return
    
    tool = queryUtility(ICommentingTool)
    if tool is not None:
        tool.unindexObject(obj)
```

## Backward Compatibility

The tool provides backward compatibility with the old `portal_discussion` tool from Plone < 4.1:

```python
"""The portal_discussion tool, usually accessed via
queryUtility(ICommentingTool). The default implementation delegates to the
standard portal_catalog for indexing comments.

BBB support for the old portal_discussion is provided in the bbb package.
"""
```

## Installation

The tool is installed as part of the plone.app.discussion installation profile:

```xml
<object name="portal_discussion" meta_type="plone.app.discussion tool" />
```

## Usage Examples

### Finding Recent Comments

```python
from zope.component import queryUtility
from plone.app.discussion.interfaces import ICommentingTool

def get_recent_comments(context, limit=10):
    tool = queryUtility(ICommentingTool)
    if tool is None:
        return []
    
    results = tool.searchResults(
        sort_on='created',
        sort_order='reverse',
        sort_limit=limit,
    )
    
    return [r.getObject() for r in results[:limit]]
```

### Finding Comments by Author

```python
def get_comments_by_author(context, author):
    tool = queryUtility(ICommentingTool)
    if tool is None:
        return []
    
    results = tool.searchResults(
        Creator=author,
        sort_on='created',
        sort_order='reverse',
    )
    
    return [r.getObject() for r in results]
```

### Finding Comments by Content Path

```python
def get_comments_for_content(context, content_path):
    tool = queryUtility(ICommentingTool)
    if tool is None:
        return []
    
    results = tool.searchResults(
        path=content_path,
        sort_on='created',
    )
    
    return [r.getObject() for r in results]
```

## Related Components

- [Comment](./comment.md) - The objects indexed by the tool
- [Catalog](./catalog.md) - Comment indexing in the portal_catalog
