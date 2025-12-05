---
myst:
  html_meta:
    "description": "Comment moderation in plone.app.discussion"
    "property=og:description": "Comment moderation in plone.app.discussion"
    "property=og:title": "Comment Moderation"
    "keywords": "Plone, Discussion, Comment, Moderation"
---

# Comment Moderation

## Overview

The comment moderation system in plone.app.discussion provides tools for moderating comments before they are published. It includes a moderation view, bulk action capabilities, and workflow integration.

## Comment Workflows

Comments can be subject to two different workflows:

1. **comment_one_state_workflow** - Comments are immediately published
2. **comment_review_workflow** - Comments require moderation before publishing

The workflow setting is controlled at the portal_workflow level for the "Discussion Item" portal type.

## Moderation View

The moderation view is provided by the `View` class in `plone.app.discussion.browser.moderation`:

```python
class View(BrowserView):
    """Show comment moderation view."""
    
    template = ViewPageTemplateFile("moderation.pt")
```

### Features

The moderation view provides:

1. A list of all comments pending moderation
2. Search/filter capabilities
3. Bulk action capabilities (publish, delete)
4. Individual comment action buttons

### Accessing the View

The view is accessible at `@@moderate-comments` on any site or folder:

- Site level: `http://example.com/@@moderate-comments`
- Folder level: `http://example.com/folder/@@moderate-comments`

### Moderation at Different Levels

Comments can be moderated at different levels:

- Site level: All comments across the site
- Folder level: Only comments in that folder and its subfolders
- Content item level: Only comments on a specific content item

### Permissions

The moderation view requires the "Review comments" permission, which is granted to:

- Site Administrators
- Managers
- Reviewers (if the role has been given the permission)

## Bulk Actions

The bulk actions functionality allows moderators to perform actions on multiple comments at once:

```python
class BulkActionsView(BrowserView):
    """Bulk actions for comment moderation."""
    
    def __call__(self):
        """Execute bulk actions."""
        req = self.request
        context = self.context
        
        # Get all comment ids from the request
        comment_ids = req.get('comment_id', [])
        
        # Determine the action
        action = req.get('action', None)
        
        if action == 'publish':
            self.publish(comment_ids)
        elif action == 'delete':
            self.delete(comment_ids)
            
        return req.RESPONSE.redirect(context.absolute_url() + '/@@moderate-comments')
```

The available bulk actions are:

1. **Publish** - Marks the selected comments as published
2. **Delete** - Deletes the selected comments

## Auto-Approve

plone.app.discussion supports auto-approving comments from trusted users:

1. Users with "Review comments" permission have their comments auto-approved
2. This happens even when moderation is enabled globally
3. Auto-approval can be managed through permissions rather than hard-coding lists of trusted users

## Workflow Transitions

Comment workflows define several transitions:

1. **publish** - Publishes a pending comment
2. **reject** - Rejects a pending comment (doesn't delete it)
3. **retract** - Unpublishes a published comment

## Workflow State Flags

The comment moderation view shows the review state of comments:

- **pending** - Comment is waiting for moderation
- **published** - Comment is approved and visible
- **rejected** - Comment was rejected but not deleted

## Multiple State View

For workflows with multiple states, a specialized view shows comments grouped by their workflow state:

```python
class MultipleStateView(View):
    """Comment moderation view for workflows with multiple states."""
```

This view extends the standard moderation view with filters for different workflow states.

## Related Components

- [Comment](./comment.md) - The objects being moderated
- [Control Panel](./controlpanel.md) - Global moderation settings
- [Events](./events.md) - Events triggered during moderation
