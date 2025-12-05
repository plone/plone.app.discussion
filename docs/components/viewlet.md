---
myst:
  html_meta:
    "description": "Comments viewlet in plone.app.discussion"
    "property=og:description": "Comments viewlet in plone.app.discussion"
    "property=og:title": "Comments Viewlet"
    "keywords": "Plone, Discussion, Comments Viewlet"
---

# Comments Viewlet

## Overview

The Comments Viewlet is the UI component that displays the comments list and comment form at the bottom of content pages. It's implemented as a Plone viewlet, which means it can be easily placed in different locations in the page layout.

## Implementation

The comments viewlet is defined in `plone.app.discussion.browser.comments`:

```python
class CommentsViewlet(ViewletBase):
    """Discussion Viewlet.
    
    Renders the comments viewing and posting UI.
    """
    
    index = ViewPageTemplateFile("comments.pt")
    
    def update(self):
        """Prepare the viewlet for rendering.
        """
        super(CommentsViewlet, self).update()
        self.portal_discussion = getToolByName(self.context, 'portal_discussion', None)
        self.request.set('disable_border', True)
```

## Main Features

The viewlet provides:

1. Display of existing comments
2. Threading of comments into conversations
3. Integration of the comment form
4. User interface for comment moderation

## Display of Comments

The viewlet retrieves comments from the conversation and displays them in a hierarchical structure:

```python
def getThreads(self, comment_id=0, depth=0):
    """Get threaded comments.
    
    Returns a list of dicts with comment for display in the comment viewlet.
    """
    conversation = IConversation(self.context)
    return conversation.getThreads(comment_id, depth)
```

Each comment is displayed with:
- Author name/information
- Comment date
- Comment text
- Reply link (if authenticated)
- Edit/Delete links (if user has permission)

## Comment Threading

Comments are displayed in a threaded view, showing replies indented beneath their parent comments:

```python
def getThreads(self, comment_id, depth):
    """Return all threads in a nested structure.
    """
    conversation = IConversation(self.context)
    
    threads = []
    for comment in conversation.getComments(comment_id):
        thread = {'comment': comment, 'depth': depth}
        thread['children'] = self.getThreads(comment.comment_id, depth + 1)
        threads.append(thread)
    
    return threads
```

## User Interface Conditionals

The viewlet contains logic to determine which UI elements to show:

```python
def can_reply(self):
    """Check if the user can reply to comments.
    """
    return getSecurityManager().checkPermission('Reply to item', self.context)

def can_manage(self):
    """Check if the user can manage comments.
    """
    return getSecurityManager().checkPermission('Manage portal', self.context)
    
def is_discussion_allowed(self):
    """Check if discussion is allowed for this viewlet.
    """
    return self.context.restrictedTraverse('@@conversation_view').enabled()
```

## Integration with Comment Form

The viewlet includes the comment form:

```python
def comment_form(self):
    """Return the comment form.
    """
    context = aq_inner(self.context)
    request = self.request
    
    form = getMultiAdapter((context, request), name='comment-form')
    form.update()
    
    return form
```

## Template Structure

The viewlet's template (`comments.pt`) includes:

1. Header section showing the number of comments
2. Comments listing with threading
3. Comment form for adding new comments
4. JavaScript for interactivity (showing/hiding the form, reply functionality)

## Customizing the Viewlet

The viewlet can be customized in several ways:

### CSS Classes

The viewlet includes numerous CSS hooks for styling:

- `.discussion` - Main container
- `.comment` - Individual comment
- `.commentImage` - Comment author image
- `.commentBody` - Comment text and metadata
- `.documentByLine` - Comment metadata (author, date)
- `.commentActions` - Reply, edit, delete links

### Template Override

The template can be overridden using Plone's template overrides:

1. Create a `browser/overrides/plone.app.discussion.browser.comments.pt` in your package
2. Register it with ZCML:

```xml
<configure xmlns="http://namespaces.zope.org/zope"
           xmlns:browser="http://namespaces.zope.org/browser"
           xmlns:plone="http://namespaces.plone.org/plone">
  <plone:static
    directory="browser/overrides"
    type="plone"
    />
</configure>
```

### Custom Viewlet Class

You can create a custom viewlet class that inherits from the standard one:

```python
from plone.app.discussion.browser.comments import CommentsViewlet

class MyCommentsViewlet(CommentsViewlet):
    """Enhanced comments viewlet with custom functionality."""
    
    def update(self):
        super(MyCommentsViewlet, self).update()
        # Add custom logic
```

And register it:

```xml
<browser:viewlet
    name="plone.comments"
    for="*"
    layer="my.package.interfaces.IMyLayer"
    manager="plone.app.layout.viewlets.interfaces.IBelowContentBody"
    class=".comments.MyCommentsViewlet"
    permission="zope2.View"
    />
```

## Related Components

- [Comment](./comment.md) - The objects displayed in the viewlet
- [Form](./form.md) - The comment form integrated in the viewlet
- [Conversation](./conversation.md) - Provides the comments data structure
