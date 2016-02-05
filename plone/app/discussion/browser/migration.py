# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import datetime
from DateTime import DateTime
from plone.app.discussion.comment import CommentFactory
from plone.app.discussion.interfaces import IComment
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IReplies
from Products.CMFCore.interfaces._content import IDiscussionResponse
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from types import TupleType

import transaction


def DT2dt(DT):
    """Convert a Zope DateTime (with timezone) into a Python datetime (GMT)."""
    DT = DT.toZone('GMT')
    return datetime(
        DT.year(),
        DT.month(),
        DT.day(),
        DT.hour(),
        DT.minute(),
        int(DT.second()))


class View(BrowserView):
    """Migration View
    """

    def __call__(self, filter_callback=None):

        context = aq_inner(self.context)
        out = []
        self.total_comments_migrated = 0
        self.total_comments_deleted = 0

        dry_run = 'dry_run' in self.request

        # This is for testing only.
        # Do not use transactions during a test.
        test = 'test' in self.request

        if not test:
            transaction.begin()  # pragma: no cover

        catalog = getToolByName(context, 'portal_catalog')

        def log(msg):
            # encode string before sending it to external world
            if isinstance(msg, unicode):
                msg = msg.encode('utf-8')  # pragma: no cover
            context.plone_log(msg)
            out.append(msg)

        def migrate_replies(context, in_reply_to, replies,
                            depth=0, just_delete=0):
            # Recursive function to migrate all direct replies
            # of a comment. Returns True if there are no replies to
            # this comment left, and therefore the comment can be removed.
            if len(replies) == 0:
                return True

            workflow = context.portal_workflow
            oldchain = workflow.getChainForPortalType('Discussion Item')
            new_workflow = workflow.comment_review_workflow
            mt = getToolByName(self.context, 'portal_membership')

            if type(oldchain) == TupleType and len(oldchain) > 0:
                oldchain = oldchain[0]

            for reply in replies:
                # log
                indent = '  '
                for i in range(depth):
                    indent += '  '
                log('{0}migrate_reply: "{1}".'.format(indent, reply.title))

                should_migrate = True
                if filter_callback and not filter_callback(reply):
                    should_migrate = False
                if just_delete:
                    should_migrate = False

                new_in_reply_to = None
                if should_migrate:
                    # create a reply object
                    comment = CommentFactory()
                    comment.title = reply.Title()
                    comment.text = reply.cooked_text
                    comment.mime_type = 'text/html'
                    comment.creator = reply.Creator()

                    try:
                        comment.author_username = reply.author_username
                    except AttributeError:
                        comment.author_username = reply.Creator()

                    member = mt.getMemberById(comment.author_username)
                    if member:
                        comment.author_name = member.fullname

                    if not comment.author_name:
                        # In migrated site member.fullname = ''
                        # while member.getProperty('fullname') has the
                        # correct value
                        if member:
                            comment.author_name = member.getProperty(
                                'fullname'
                            )
                        else:
                            comment.author_name = comment.author_username

                    try:
                        comment.author_email = reply.email
                    except AttributeError:
                        comment.author_email = None

                    comment.creation_date = DT2dt(reply.creation_date)
                    comment.modification_date = DT2dt(reply.modification_date)

                    comment.reply_to = in_reply_to

                    if in_reply_to == 0:
                        # Direct reply to a content object
                        new_in_reply_to = conversation.addComment(comment)
                    else:
                        # Reply to another comment
                        comment_to_reply_to = conversation.get(in_reply_to)
                        replies = IReplies(comment_to_reply_to)
                        new_in_reply_to = replies.addComment(comment)

                    # migrate the review state
                    old_status = workflow.getStatusOf(oldchain, reply)
                    new_status = {
                        'action': None,
                        'actor': None,
                        'comment': 'Migrated workflow state',
                        'review_state': old_status and old_status.get(
                            'review_state',
                            new_workflow.initial_state
                        ) or 'published',
                        'time': DateTime()
                    }
                    workflow.setStatusOf('comment_review_workflow',
                                         comment,
                                         new_status)

                    auto_transition = new_workflow._findAutomaticTransition(
                        comment,
                        new_workflow._getWorkflowStateOf(comment))
                    if auto_transition is not None:
                        new_workflow._changeStateOf(comment, auto_transition)
                    else:
                        new_workflow.updateRoleMappingsFor(comment)
                    comment.reindexObject(idxs=['allowedRolesAndUsers',
                                                'review_state'])

                self.total_comments_migrated += 1

                # migrate all talkbacks of the reply
                talkback = getattr(reply, 'talkback', None)
                no_replies_left = migrate_replies(
                    context,
                    new_in_reply_to,
                    talkback.getReplies(),
                    depth=depth + 1,
                    just_delete=not should_migrate)

                if no_replies_left:
                    # remove reply and talkback
                    talkback.deleteReply(reply.id)
                    obj = aq_parent(talkback)
                    obj.talkback = None
                    log('{0}remove {1}'.format(indent, reply.id))
                    self.total_comments_deleted += 1

            # Return True when all comments on a certain level have been
            # migrated.
            return True

        # Find content
        brains = catalog.searchResults(
            object_provides='Products.CMFCore.interfaces._content.IContentish')
        log('Found {0} content objects.'.format(len(brains)))

        count_discussion_items = len(
            catalog.searchResults(Type='Discussion Item')
        )
        count_comments_pad = len(
            catalog.searchResults(object_provides=IComment.__identifier__)
        )
        count_comments_old = len(
            catalog.searchResults(
                object_provides=IDiscussionResponse.__identifier__
            )
        )

        log(
            'Found {0} Discussion Item objects.'.format(
                count_discussion_items
            )
        )
        log('Found {0} old discussion items.'.format(count_comments_old))
        log(
            'Found {0} plone.app.discussion comments.'.format(
                count_comments_pad
            )
        )

        log('\n')
        log('Start comment migration.')

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
            talkback = getattr(obj, 'talkback', None)
            if talkback:
                replies = talkback.getReplies()
                if replies:
                    conversation = IConversation(obj)
                log('\n')
                log(
                    'Migrate "{0}" ({1})'.format(
                        obj.Title(),
                        obj.absolute_url(relative=1)
                    )
                )
                migrate_replies(context, 0, replies)
                obj = aq_parent(talkback)
                obj.talkback = None

        if self.total_comments_deleted != self.total_comments_migrated:
            log(
                'Something went wrong during migration. The number of '
                'migrated comments ({0}) differs from the number of deleted '
                'comments ({1}).'.format(
                    self.total_comments_migrated,
                    self.total_comments_deleted
                )
            )
            if not test:  # pragma: no cover
                transaction.abort()  # pragma: no cover
            log('Abort transaction')  # pragma: no cover

        log('\n')
        log('Comment migration finished.')
        log('\n')

        log(
            '{0} of {1} comments migrated.'.format(
                self.total_comments_migrated,
                count_comments_old
            )
        )

        if self.total_comments_migrated != count_comments_old:
            log(
                '{0} comments could not be migrated.'.format(
                    count_comments_old - self.total_comments_migrated
                )
            )  # pragma: no cover
            log('Please make sure your ' +
                'portal catalog is up-to-date.')  # pragma: no cover

        if dry_run and not test:
            transaction.abort()  # pragma: no cover
            log('Dry run')  # pragma: no cover
            log('Abort transaction')  # pragma: no cover
        if not test:
            transaction.commit()  # pragma: no cover
        return '\n'.join(out)
