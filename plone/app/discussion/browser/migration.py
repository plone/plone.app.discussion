from Acquisition import aq_inner, aq_parent

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _

from Products.statusmessages.interfaces import IStatusMessage

from Products.CMFCore.interfaces import IContentish

from zope.component import createObject

from plone.app.discussion.interfaces import IConversation


class View(BrowserView):
    """Migration View
    """

    def __call__(self):

        context = aq_inner(self.context)
        out = []
        def log(msg):
            context.plone_log(msg)
            out.append(msg)

        log("Comment migration started.")

        # Find content
        catalog = getToolByName(context, 'portal_catalog')
        dtool = context.portal_discussion
        brains = catalog.searchResults(
                    object_provides='Products.CMFCore.interfaces._content.IContentish')
        log("Found %s content objects to migrate." % len(brains))

        for brain in brains:
            if brain.portal_type != 'Discussion Item':
                old_comments = []
                obj = brain.getObject()
                talkback = getattr( obj, 'talkback', None )
                if talkback:
                    replies = talkback.objectValues()
                    log("%s: Found talkback with %s comments to migrate"\
                        % (obj.absolute_url(relative=1), len(replies)))
                    for reply in replies:
                        old_comments.append(reply)

                # Build up new conversation/comments structure
                conversation = IConversation(obj)

                for old_comment in old_comments:
                    comment = createObject('plone.Comment')
                    comment.title = old_comment.Title()
                    comment.text = old_comment.text
                    comment.Creator = old_comment.Creator
                    conversation.addComment(comment)

        log("Comment migration finished.")
        return out
