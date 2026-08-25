---
myst:
  html_meta:
    "description": "REST API integration in plone.app.discussion"
    "property=og:description": "REST API integration in plone.app.discussion"
    "property=og:title": "Discussion REST API"
    "keywords": "Plone, Discussion, REST API, Volto"
---

# REST API Integration

## Overview

plone.app.discussion provides integration with plone.restapi to enable managing comments through REST API endpoints. This is particularly useful for JavaScript frontends like Volto.

## Control Panel Integration

The discussion settings are exposed through the REST API control panel endpoint:

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

This allows Volto and other clients to:

- Retrieve the current discussion settings
- Modify the discussion settings
- Access the settings schema for generating UI forms

### Accessing Settings via REST API

```http
GET /@controlpanels/discussion HTTP/1.1
Accept: application/json
```

Response:

```json
{
  "@id": "http://localhost:8080/Plone/@controlpanels/discussion",
  "title": "Discussion",
  "group": "Content",
  "schema": {
    "fieldsets": [
      {
        "id": "default",
        "title": "Default",
        "fields": ["globally_enabled", "moderation_enabled", ...]
      }
    ],
    "properties": {
      "globally_enabled": {
        "title": "Globally enable comments",
        "description": "Enable comments globally",
        "type": "boolean",
        "default": false
      },
      "moderation_enabled": {
        "title": "Comment moderation",
        "description": "Require moderation for all comments",
        "type": "boolean",
        "default": false
      },
      // Additional properties
    }
  },
  "data": {
    "globally_enabled": true,
    "moderation_enabled": false,
    // Additional data
  }
}
```

### Updating Settings via REST API

```http
PATCH /@controlpanels/discussion HTTP/1.1
Accept: application/json
Content-Type: application/json

{
  "globally_enabled": true,
  "moderation_enabled": true
}
```

## Comments Endpoints

Comments can be accessed and manipulated through content-related endpoints:

### Getting Comments

```http
GET /plone/document/@comments HTTP/1.1
Accept: application/json
```

Response:

```json
{
  "@id": "http://localhost:8080/Plone/document/@comments",
  "items_total": 2,
  "items": [
    {
      "@id": "http://localhost:8080/Plone/document/@comments/123456789",
      "@type": "Discussion Item",
      "comment_id": "123456789",
      "author_name": "John Doe",
      "text": "This is a comment",
      "creation_date": "2023-01-15T10:00:00",
      "modification_date": "2023-01-15T10:00:00",
      "is_editable": false,
      "is_deletable": false,
      // Additional fields
    },
    // More comments
  ]
}
```

### Adding a Comment

```http
POST /plone/document/@comments HTTP/1.1
Accept: application/json
Content-Type: application/json

{
  "text": "My comment text",
  "user_notification": true
}
```

Response:

```json
{
  "@id": "http://localhost:8080/Plone/document/@comments/987654321",
  "@type": "Discussion Item",
  "comment_id": "987654321",
  "author_name": "Jane Smith",
  "text": "My comment text",
  "creation_date": "2023-01-15T11:00:00",
  "modification_date": "2023-01-15T11:00:00",
  // Additional fields
}
```

### Adding a Reply

To add a reply to a specific comment:

```http
POST /plone/document/@comments HTTP/1.1
Accept: application/json
Content-Type: application/json

{
  "text": "My reply text",
  "in_reply_to": "123456789"
}
```

### Updating a Comment

```http
PATCH /plone/document/@comments/123456789 HTTP/1.1
Accept: application/json
Content-Type: application/json

{
  "text": "Updated comment text"
}
```

### Deleting a Comment

```http
DELETE /plone/document/@comments/123456789 HTTP/1.1
Accept: application/json
```

## Comment Moderation via REST API

Comment moderation actions can also be triggered via REST API:

### Publishing a Comment

```http
POST /plone/document/@comments/123456789/publish HTTP/1.1
Accept: application/json
```

### Transition Endpoint

A general transition endpoint allows any workflow transition:

```http
POST /plone/document/@comments/123456789/@workflow/reject HTTP/1.1
Accept: application/json
```

## Implementation Details

The plone.restapi integration is conditionally registered only when plone.restapi is installed:

```python
try:
    from plone.restapi.interfaces import IControlpanelLayer
except ImportError:
    IControlpanelLayer = Interface
```

This approach ensures that the REST API components are only active when needed.

## Use with Volto

The REST API integration is particularly useful with Volto, Plone's React-based frontend:

1. Volto uses the `@comments` endpoint to display comments
2. The control panel integration allows managing discussion settings in Volto
3. Comment forms in Volto submit to the REST API endpoints

## Related Components

- [Comment](./comment.md) - The objects exposed via REST API
- [Control Panel](./controlpanel.md) - Settings accessible via REST API
