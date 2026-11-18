---
myst:
  html_meta:
    "description": "Discussion behavior in plone.app.discussion"
    "property=og:description": "Discussion behavior in plone.app.discussion"
    "property=og:title": "Discussion Behavior"
    "keywords": "Plone, Discussion, Behavior, IAllowDiscussion"
---

# Allow Discussion Behavior

## Overview

The `IAllowDiscussion` behavior provides a UI control for enabling or disabling comments on individual content objects. This behavior can be applied to any content type, allowing fine-grained control over which content items can have comments.

## Interface

The behavior is defined in `plone.app.discussion.behavior`:

```python
@provider(IFormFieldProvider)
class IAllowDiscussion(model.Schema):
    """Allow discussion behavior.
    
    Provides a field to enable or disable comments on a content item.
    """
    
    model.fieldset(
        "settings",
        label=_("Settings"),
        fields=["allow_discussion"],
    )

    allow_discussion = schema.Choice(
        title=_("Allow discussion"),
        description=_("Allow discussion for this content object."),
        vocabulary=options,
        required=False,
        default=None,
    )
```

The vocabulary options are simple Yes/No values:

```python
options = SimpleVocabulary(
    [
        SimpleTerm(value=True, title=_("Yes")),
        SimpleTerm(value=False, title=_("No")),
    ]
)
```

## Usage

### Enabling the Behavior

To enable the behavior on a content type, add it to the type's FTI:

```xml
<property name="behaviors">
    <element value="plone.allowdiscussion" />
</property>
```

Or in Python:

```python
fti = getUtility(IDexterityFTI, name='my_content_type')
behaviors = list(fti.behaviors)
behaviors.append('plone.allowdiscussion')
fti.behaviors = tuple(behaviors)
```

### Using the Behavior

Once the behavior is enabled for a content type:

1. The "Allow discussion" field appears in the "Settings" fieldset of the edit form.
2. Users can select "Yes" or "No" to enable or disable comments.
3. If left unselected (None), the content type's default setting is used.

## Checking If Discussion is Enabled

The conversation component uses this behavior to determine if discussion is enabled:

```python
def enabled(self):
    """Return True if commenting is enabled on this conversation."""
    
    # Global setting
    if not registry_settings.globally_enabled:
        return False
        
    # Content-specific setting
    if context.allow_discussion is not None:
        return context.allow_discussion
        
    # Content type setting
    return portal_types.getTypeInfo(context).getProperty('allow_discussion')
```

## Default Settings

The behavior defaults to `None`, which means the content type's setting is used. 
Content types have an `allow_discussion` property that can be set in their FTI:

```xml
<property name="allow_discussion">False</property>
```

## Interoperability

This behavior works with both Dexterity and Archetypes content types:

- For Dexterity, the `plone.allowdiscussion` behavior is used.
- For Archetypes, the `allowDiscussion` method is used.

## Related Components

- [Conversation](./conversation.md) - Uses the behavior to determine if comments are enabled
- [Control Panel](./controlpanel.md) - Global settings for discussions
