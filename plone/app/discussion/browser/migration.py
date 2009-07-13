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
        self.total_comments_deleted = 0

        catalog = getToolByName(context, 'portal_catalog')
        dtool = context.portal_discussion
        comment_brains = catalog.searchResults(Type='Discussion Item')

        def log(msg):
            context.plone_log(msg)
            out.append(msg)

        def migrate_replies(context, in_reply_to, replies, depth=0):
            # Recursive function to migrate all direct replies
            # of a comment. Returns True if there are no replies to
            # this comment left, and therefore the comment can be removed.
            if len(replies) == 0:
                return True

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

                comment.creation_date = datetime.fromtimestamp(reply.creation_date)
                comment.modification_date = datetime.fromtimestamp(reply.modification_date)

                comment.reply_to = in_reply_to

                new_in_reply_to = conversation.addComment(comment)
                self.total_comments_migrated += 1

                # migrate all talkbacks of the reply
                talkback = getattr( reply, 'talkback', None )
                no_replies_left = migrate_replies(context, new_in_reply_to, talkback.getReplies(), depth=depth+1)
                if no_replies_left:
                    # remove reply and talkback
                    talkback.deleteReply(reply.id)
                    obj = aq_parent(talkback)
                    obj.talkback = None
                    log("remove %s" % reply.id)
                    self.total_comments_deleted += 1

        log("Comment migration started.")

        # Find content
        brains = catalog.searchResults(
                    object_provides='Products.CMFCore.interfaces._content.IContentish')
        total_comment_brains = len(comment_brains)
        log("Found %s content objects." % len(brains))
        log("Found %s Discussion Item objects." % total_comment_brains)

        # This loop is necessary to get all contentish objects, but not
        # the Discussion Items. This wouldn't be necessary if the
        # zcatalog would support NOT expressions.
        new_brains = []
        for brain in brains:
            if brain.portal_type != 'Discussion Item':
                new_brains.append(brain)

        # Recursively run through the comment tree and migrate all comments.
        for brain in new_brains:
            obj = brain.getObject()
            talkback = getattr( obj, 'talkback', None )
            if talkback:
                replies = talkback.getReplies()
                if replies:
                    conversation = IConversation(obj)
                    log("Create conversation for: '%s'" % obj.Title())
                log("%s: Found talkback" % obj.absolute_url(relative=1))
                migrate_replies(context, 0, replies)
                obj = aq_parent(talkback)
                obj.talkback = None

        if self.total_comments_deleted != self.total_comments_migrated:
            log("Something went wrong during migration. The number of migrated comments (%s)\
                 differs from the number of deleted comments (%s)."
                 % (self.total_comments_migrated, self.total_comments_deleted))
        log("Comment migration finished.")
        log("%s of %s comments migrated."
            % (self.total_comments_migrated, total_comment_brains))
        return '\n'.join(out)
