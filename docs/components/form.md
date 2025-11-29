---
myst:
  html_meta:
    "description": "Comment form in plone.app.discussion"
    "property=og:description": "Comment form in plone.app.discussion"
    "property=og:title": "Comment Form"
    "keywords": "Plone, Discussion, Comment Form"
---

# Comment Form

## Overview

The Comment Form is the UI component that allows users to add and edit comments. It's implemented using z3c.form and supports extensibility through the plone.z3cform extensible form mechanism.

## Implementation

### CommentForm

The main `CommentForm` class is defined in `plone.app.discussion.browser.comments`:

```python
class CommentForm(extensible.ExtensibleForm, form.Form):
    """Comment form.
    
    Provides a form for adding and editing comments.
    """
    
    ignoreContext = True  # don't use context to get widget data
    id = None
    label = _("Add a comment")
    fields = field.Fields(IComment).omit(
        "portal_type",
        "__parent__",
        "__name__",
        "comment_id",
        "mime_type",
        "creator",
        "creation_date",
        "modification_date",
        "author_username",
        "title",
    )
```

### EditCommentForm

The `EditCommentForm` class extends `CommentForm` for editing existing comments:

```python
class EditCommentForm(CommentForm):
    """Form to edit an existing comment.
    
    Extends the CommentForm with additional functionality for editing.
    """
    
    label = _("Edit comment")
    
    @button.buttonAndHandler(_("update_comment", default="Update Comment"), name="comment")
    def handleComment(self, action):
        # Handle comment update
```

## Form Fields

The standard fields in the comment form are:

- `text` - The main comment content
- `author_name` - For anonymous users
- `author_email` - For anonymous users
- `user_notification` - Email notification option

## Form Behavior

### Adding Comments

When a user submits a comment:

1. The form validates the input data
2. Captcha is verified if enabled
3. A new Comment object is created
4. Author information is set based on the user (anonymous or authenticated)
5. The comment is added to the conversation
6. The user is redirected back to the page

### Editing Comments

When editing a comment:

1. Form is pre-populated with comment data
2. User edits the comment
3. On submit, the comment is updated
4. The user is redirected back to the page

## Extensibility

The form uses `plone.z3cform`'s extensible form pattern, which allows add-ons to extend the form with additional fields:

```python
from plone.z3cform.fieldsets import extensible

class CommentForm(extensible.ExtensibleForm, form.Form):
    """Comment form with extension points."""
```

Example of how an add-on could extend the form:

```python
from plone.app.discussion.browser.comments import CommentForm
from plone.z3cform.fieldsets.extensible import FormExtender
from z3c.form import field

class CaptchaExtender(FormExtender):
    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form
    
    def update(self):
        # Add captcha field to the form
        self.add(field.Fields(ICaptcha), group=None)
```

## CAPTCHA Integration

The form supports several CAPTCHA solutions via adapters:

- `plone.formwidget.captcha` - Simple captcha
- `plone.formwidget.recaptcha` - Google reCAPTCHA
- `collective.z3cform.norobots` - Question-based captcha
- `plone.formwidget.hcaptcha` - HCaptcha integration

## Integration with Discussion Settings

The form behavior is influenced by several settings from the Discussion Control Panel:

- `globally_enabled` - If comments are enabled globally
- `anonymous_comments` - If anonymous users can comment
- `captcha` - Type of CAPTCHA to use
- `text_transform` - Text transformation for comments
- `moderation_enabled` - If comments require moderation

## Reply Form

For replies to existing comments:

1. The JavaScript copies the comment form near the comment being replied to
2. The `in_reply_to` field is set to the parent comment ID
3. The form behavior remains the same otherwise

## Related Components

- [Comment](./comment.md) - The object created by the form
- [Viewlet](./viewlet.md) - Displays the form in the context of the page
- [Control Panel](./controlpanel.md) - Configures form behavior
