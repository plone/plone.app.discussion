---
myst:
  html_meta:
    "description": "Comment cataloging in plone.app.discussion"
    "property=og:description": "Comment cataloging in plone.app.discussion"
    "property=og:title": "Comment Cataloging"
    "keywords": "Plone, Discussion, Catalog, Indexing"
---

# Comment Cataloging

## Overview

plone.app.discussion integrates with Plone's catalog system to make comments searchable and efficiently retrievable. This is accomplished through custom indexers and standard catalog integration.

## Indexers

The module `plone.app.discussion.catalog` defines custom indexers for comments:

```python
@indexer(IComment)
def SearchableText(object):
    """Indexer for the SearchableText field.
    
    Includes the comment text, author name, and other searchable fields.
    """
    return " ".join([
        safe_text(object.text) or "",
        safe_text(object.author_name) or "", 
        safe_text(object.author_email) or "",
    ])

@indexer(IComment)
def Title(object):
    """Indexer for the Title field."""
    if hasattr(object, 'title') and object.title:
        return object.title
    else:
        # Generate a title from the author's name and the content
        content_title = object.__parent__.__parent__.title
        author = object.author_name or _('Anonymous')
        return translate(
            COMMENT_TITLE, 
            context=getSite().REQUEST,
            mapping={'author_name': author, 'content': content_title}
        )

@indexer(IComment)
def Creator(object):
    """Indexer for the Creator field."""
    return object.creator

@indexer(IComment)
def in_response_to(object):
    """Indexer for the in_response_to field."""
    return object.in_reply_to

@indexer(IComment)
def effective(object):
    """Indexer for the effective date."""
    if object.publication_date is not None:
        return object.publication_date
    return object.creation_date

@indexer(IComment)
def created(object):
    """Indexer for the creation date."""
    return object.creation_date

@indexer(IComment)
def modified(object):
    """Indexer for the modification date."""
    return object.modification_date
```

## Special Indexers

Some indexers are specially defined to avoid comments inheriting properties from their container:

```python
@indexer(IComment)
def UID(object):
    """Indexer for the UID.
    
    Make sure comments don't inherit their container's UID.
    """
    return object.comment_id
```

## Conversation-related Indexers

Special indexers handle conversation-related metadata:

```python
@indexer(IComment)
def comments_total_comments(object):
    """Total comment count for a comment.
    
    Override the conversation indexers for comments.
    """
    return 0

@indexer(IComment)
def comments_last_comment_date(object):
    """Date of the most recent comment.
    
    Override the conversation indexers for comments.
    """
    return None

@indexer(IComment)
def comments_commentators(object):
    """List of commentators.
    
    Override the conversation indexers for comments.
    """
    return ()
```

## Comment Metadata

Comments are indexed with several metadata columns:

### Standard Metadata

- `Title` - The comment title
- `Creator` - The comment author
- `created` - Creation date
- `modified` - Modification date
- `effective` - Effective date (publication date)
- `SearchableText` - Full-text search index

### Custom Metadata

- `in_response_to` - Parent comment ID
- `author_name` - Display name of the author
- `author_username` - Username of the author
- `review_state` - Workflow state of the comment

## Catalog Configuration

The catalog configuration is set up in the installation profile:

```xml
<object name="portal_catalog">
  <column value="in_response_to" />
  <column value="commentators" />
  <column value="total_comments" />
</object>
```

## Indexing Events

Comments are automatically indexed when events occur:

```python
def index_object(obj, event):
    """Index the object when added to the conversation"""
    # Skip if object isn't a comment
    if not IComment.providedBy(obj):
        return
    
    tool = queryUtility(ICommentingTool)
    if tool is not None:
        tool.indexObject(obj)
```

The indexing is triggered by:

- `ObjectAddedEvent` - When a comment is added
- `ObjectModifiedEvent` - When a comment is modified
- `WorkflowTransitionEvent` - When a comment's workflow state changes

## Unindexing Events

Comments are automatically unindexed when removed:

```python
def unindex_object(obj, event):
    """Unindex the object when removed"""
    # Skip if object isn't a comment
    if not IComment.providedBy(obj):
        return
    
    tool = queryUtility(ICommentingTool)
    if tool is not None:
        tool.unindexObject(obj)
```

## Portal Catalog Integration

Comments are fully integrated with the portal_catalog, which means:

1. They can be found using standard catalog searches
2. They appear in search results alongside other content
3. They can be filtered by workflow state, creation date, etc.

## Usage Examples

### Finding Comments by Keyword

```python
def search_comments_by_text(context, searchtext):
    catalog = getToolByName(context, 'portal_catalog')
    
    results = catalog(
        object_provides=IComment.__identifier__,
        SearchableText=searchtext,
        sort_on='created',
        sort_order='reverse',
    )
    
    return [r.getObject() for r in results]
```

### Finding Recent Comments

```python
def get_recent_comments(context, count=5):
    catalog = getToolByName(context, 'portal_catalog')
    
    results = catalog(
        object_provides=IComment.__identifier__,
        sort_on='created',
        sort_order='reverse',
        sort_limit=count,
    )
    
    return [r.getObject() for r in results[:count]]
```

### Finding Comments by Review State

```python
def get_comments_by_state(context, state):
    catalog = getToolByName(context, 'portal_catalog')
    
    results = catalog(
        object_provides=IComment.__identifier__,
        review_state=state,
        sort_on='created',
        sort_order='reverse',
    )
    
    return [r.getObject() for r in results]
```

## Related Components

- [Comment](./comment.md) - The objects being indexed
- [Tool](./tool.md) - The portal_discussion tool for searching comments
