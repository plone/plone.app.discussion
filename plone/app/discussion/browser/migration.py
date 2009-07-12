from datetime import datetime

from Acquisition import aq_inner, aq_parent

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _

from Products.statusmessages.interfaces import IStatusMessage

from Products.CMFCore.interfaces import IContentish

from zope.component import createObject

from plone.app.discussion.comment import CommentFactory

from plone.app.discussion.interfaces import IConversation


class View(BrowserView):
    """Migration View
    """

    def __call__(self):

        context = aq_inner(self.context)
        out = []
        self.total_comments_migrated = 0

        def log(msg):
            context.plone_log(msg)
            out.append(msg)

        def migrate_replies(context, in_reply_to, replies, depth=0):
            # recursive function to migrate all direct replies
            # of a comment

            for reply in replies:

                # log
                indent = "  "
                for i in range(depth):
                    indent += "  "
                log("%smigrate_reply: '%s'." % (indent, reply.title))

                # create a reply object
                comment = CommentFactory()
                comment.title = reply.Title()
                comment.text = reply.text
                comment.creator = reply.Creator()

                #comment.creation_date = datetime.fromtimestamp(reply.creation_date)

                comment.creation_date = datetime.fromtimestamp(reply.creation_date)
                comment.modification_date = datetime.fromtimestamp(reply.modification_date)

                comment.reply_to = in_reply_to

                new_in_reply_to = conversation.addComment(comment)
                self.total_comments_migrated += 1

                # migrate all talkbacks of the reply
                talkback = getattr( reply, 'talkback', None )
                migrate_replies(context, new_in_reply_to, talkback.getReplies(), depth=depth+1)

        log("Comment migration started.")

        # Find content
        catalog = getToolByName(context, 'portal_catalog')
        dtool = context.portal_discussion
        brains = catalog.searchResults(
                    object_provides='Products.CMFCore.interfaces._content.IContentish')
        comment_brains = catalog.searchResults(Type='Discussion Item')
        total_comment_brains = len(comment_brains)
        log("Found %s content objects." % len(brains))
        log("Found %s Discussion Item objects." % total_comment_brains)

        for brain in brains:
            if brain.portal_type != 'Discussion Item':
                obj = brain.getObject()
                talkback = getattr( obj, 'talkback', None )
                if talkback:
                    replies = talkback.getReplies()
                    if replies:
                        conversation = IConversation(obj)
                        log("Create conversation for: '%s'" % obj.Title())
                    log("%s: Found talkback" % obj.absolute_url(relative=1))
                    migrate_replies(context, 0, replies)

        log("Comment migration finished.")
        log("%s of %s comments migrated."
            % (self.total_comments_migrated, total_comment_brains))
        return '\n'.join(out)
