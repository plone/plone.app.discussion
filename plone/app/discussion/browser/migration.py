from datetime import datetime

from Acquisition import aq_inner, aq_parent

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _

from Products.statusmessages.interfaces import IStatusMessage

from Products.CMFCore.interfaces import IContentish

from Products.CMFCore.interfaces._content import IDiscussionResponse

import transaction

from zope.component import createObject

from plone.app.discussion.comment import CommentFactory

from plone.app.discussion.interfaces import IConversation, IReplies, IComment


class View(BrowserView):
    """Migration View
    """

    def __call__(self):

        context = aq_inner(self.context)
        out = []
        self.total_comments_migrated = 0
        self.total_comments_deleted = 0
        
        dry_run = self.request.has_key("dry_run")
        
        # This is for testing only.
        # Do not use transactions during a test.
        test = self.request.has_key("test") 
        
        if not test:
            transaction.begin()
        
        catalog = getToolByName(context, 'portal_catalog')
        dtool = context.portal_discussion
        
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

                if in_reply_to == 0:
                    # Direct reply to a content object
                    new_in_reply_to = conversation.addComment(comment)
                else:
                    # Reply to another comment
                    comment_to_reply_to = conversation.get(in_reply_to)
                    replies = IReplies(comment_to_reply_to)
                    new_in_reply_to = replies.addComment(comment)

                self.total_comments_migrated += 1

                # migrate all talkbacks of the reply
                talkback = getattr( reply, 'talkback', None )
                no_replies_left = migrate_replies(context, new_in_reply_to, talkback.getReplies(), depth=depth+1)
                if no_replies_left:
                    # remove reply and talkback
                    talkback.deleteReply(reply.id)
                    obj = aq_parent(talkback)
                    obj.talkback = None
                    log("%sremove %s" % (indent, reply.id))
                    self.total_comments_deleted += 1

            # Return True when all comments on a certain level have been migrated.
            return True

        # Find content
        brains = catalog.searchResults(
                    object_provides='Products.CMFCore.interfaces._content.IContentish')
        log("Found %s content objects." % len(brains))

        count_discussion_items = len(catalog.searchResults(Type='Discussion Item'))
        count_comments_pad = len(catalog.searchResults(object_provides=IComment.__identifier__))
        count_comments_old = len(catalog.searchResults(object_provides=IDiscussionResponse.__identifier__))
        
        log("Found %s Discussion Item objects." % count_discussion_items)
        log("Found %s old discussion items." % count_comments_old)
        log("Found %s plone.app.discussion comments." % count_comments_pad)

        log("\n")
        log("Start comment migration.")
        
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
                log("\n")
                log("Migrate '%s' (%s)" % (obj.Title(), obj.absolute_url(relative=1)))
                migrate_replies(context, 0, replies)
                obj = aq_parent(talkback)
                obj.talkback = None

        if self.total_comments_deleted != self.total_comments_migrated:
            log("Something went wrong during migration. The number of migrated comments (%s)\
                 differs from the number of deleted comments (%s)."
                 % (self.total_comments_migrated, self.total_comments_deleted))
            if not test:
                transaction.abort()
            log("Abort transaction")
        
        log("\n")
        log("Comment migration finished.")
        log("\n")
        
        log("%s of %s comments migrated."
            % (self.total_comments_migrated, count_comments_old))
        
        if self.total_comments_migrated != count_comments_old:
            log("%s comments could not be migrated." % (count_comments_old - self.total_comments_migrated))
            log("Please make sure your portal catalog is up-to-date.")
        
        if dry_run and not test:
            transaction.abort()
            log("Dry run")
            log("Abort transaction")
        if not test:
            transaction.commit()        
        return '\n'.join(out)
