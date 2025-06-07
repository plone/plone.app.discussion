---
myst:
  html_meta:
    "description": "How to make plone.app.discussion work with a dexterity content type - plone.app.discussion documentation"
    "property=og:description": "How to make plone.app.discussion work with a dexterity content type - plone.app.discussion documentation"
    "property=og:title": "How to make plone.app.discussion work with a dexterity content type"
    "keywords": "Plone, Discussion, Comments, Documentation"
---

# How to make plone.app.discussion work with a dexterity content type

This document explains how to make plone.app.discussion work with a custom
dexterity content type.

XXX: TODO

configure.zcml:

```
<browser:page
    name="conversation_view"
    for=".mydexteritycontenttype.MyDexterityContentType"
    layer="plone.app.discussion.interfaces.IDiscussionLayer"
    class=".classified.ConversationView"
    permission="zope2.View"
    />
```

Define an interface IMyDexterityContentType groked schema, I added:

```
allowDiscussion  = schema.Bool(
    title=_("Allow Users to Comment"),
    description=_("Allow users to comment on you.  Comments
```

are shown at the end of each page"),

: > required=True,
  > default=True,

  )

and added this class:

from plone.app.discussion.browser.comments import CommentsViewlet
class ConversationView(object):

> """ Ability to either allow / disallow comments based on schema

option

: """
  def enabled(self):

  > return getattr(self.context, 'allowDiscussion', False)
