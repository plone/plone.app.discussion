---
myst:
  html_meta:
    "description": "Howto override the enable_conversation method. - plone.app.discussion documentation"
    "property=og:description": "Howto override the enable_conversation method. - plone.app.discussion documentation"
    "property=og:title": "Howto override the enable_conversation method."
    "keywords": "Plone, Discussion, Comments, Documentation"
---

# Howto override the enable_conversation method.

plone.app.discussion way to decide if commenting is enabled on a content
object can be quite complex and cumbersome due to the need to be backward
compatible with the way the old commenting system in Plone (\<4.1) worked.

The comments viewlet calls the enabled method of the ConversationView to
decide if the add comment form should show up:

```{literalinclude} ../../../plone/app/discussion/browser/conversation.py
:language: python
:pyobject: ConversationView
```

If you want to override this behavior, you just have to create your own enabled method. To do so, we first have to register our custom
ConversationView by overriding the existing one in our configure.zcml:

```
<configure
  xmlns="http://namespaces.zope.org/zope"
  xmlns:browser="http://namespaces.zope.org/browser"
  i18n_domain="mycustompackage.discussion">

  <!-- Override plone.app.discussion's conversation view -->
  <browser:page
    name="conversation_view"
    for="plone.dexterity.interfaces.IDexterityContent"
    class=".conversation.ConversationView"
    permission="zope2.View"
    />

</configure>
```

Now we implement the conversation view with a single "enable" method in
conversation.py:

```
from zope.component import queryUtility

from plone.registry.interfaces import IRegistry

from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName

from plone.app.discussion.interfaces import IDiscussionSettings


class ConversationView(object):

    def enabled(self):
        context = aq_inner(self.context)

        # Fetch discussion registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)

        # Check if discussion is allowed globally
        if not settings.globally_enabled:
            return False

        # Check if discussion is allowed on the content object
        if context.allow_discussion is not None:
            return context.allow_discussion

        # Check if discussion is allowed on the content type
        portal_types = getToolByName(self, 'portal_types')
        document_fti = getattr(portal_types, context.portal_type)
        return document_fti.getProperty('allow_discussion')
```
