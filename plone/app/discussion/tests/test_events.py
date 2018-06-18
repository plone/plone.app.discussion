# -*- coding: utf-8 -*-
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IReplies
from plone.app.discussion.testing import PLONE_APP_DISCUSSION_INTEGRATION_TESTING  # noqa
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Zope2.App import zcml
from zope.component import createObject

import Products.Five
import unittest


#
# Fake events registry
#


class EventsRegistry(object):
    """ Fake registry to be used while testing discussion events
    """
    commentAdded = False
    commentRemoved = False
    replyAdded = False
    replyRemoved = False

#
# Fake event handlers
#


def comment_added(doc, evt):
    EventsRegistry.commentAdded = True


def comment_removed(doc, evt):
    EventsRegistry.commentRemoved = True


def reply_added(doc, evt):
    EventsRegistry.replyAdded = True


def reply_removed(doc, evt):
    EventsRegistry.replyRemoved = True


#
# Tests
#


class CommentEventsTest(unittest.TestCase):
    """ Test custom comments events
    """
    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):

        # Setup sandbox
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = EventsRegistry

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.document = self.portal['doc1']

        #
        # Subscribers
        #
        configure = """
        <configure
          xmlns="http://namespaces.zope.org/zope">

          <subscriber
            for="OFS.interfaces.ISimpleItem
                 plone.app.discussion.interfaces.ICommentAddedEvent"
            handler="plone.app.discussion.tests.test_events.comment_added"
            />

          <subscriber
            for="OFS.interfaces.ISimpleItem
                 plone.app.discussion.interfaces.ICommentRemovedEvent"
            handler="plone.app.discussion.tests.test_events.comment_removed"
            />

         </configure>
        """
        zcml.load_config('configure.zcml', Products.Five)
        zcml.load_string(configure)

    def test_addEvent(self):
        self.assertFalse(self.registry.commentAdded)
        comment = createObject('plone.Comment')
        conversation = IConversation(self.document)
        conversation.addComment(comment)
        self.assertTrue(self.registry.commentAdded)

    def test_removedEvent(self):
        self.assertFalse(self.registry.commentRemoved)
        comment = createObject('plone.Comment')
        conversation = IConversation(self.document)
        cid = conversation.addComment(comment)
        del conversation[cid]
        self.assertTrue(self.registry.commentRemoved)


class RepliesEventsTest(unittest.TestCase):
    """ Test custom replies events
    """
    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = EventsRegistry

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.document = self.portal['doc1']

        #
        # Subscribers
        #
        configure = """
        <configure
          xmlns="http://namespaces.zope.org/zope">

          <subscriber
            for="OFS.interfaces.ISimpleItem
                 plone.app.discussion.interfaces.IReplyAddedEvent"
            handler="plone.app.discussion.tests.test_events.reply_added"
            />

          <subscriber
            for="OFS.interfaces.ISimpleItem
                 plone.app.discussion.interfaces.IReplyRemovedEvent"
            handler="plone.app.discussion.tests.test_events.reply_removed"
            />

         </configure>
        """
        zcml.load_config('configure.zcml', Products.Five)
        zcml.load_string(configure)

    def test_addEvent(self):
        self.assertFalse(self.registry.replyAdded)

        conversation = IConversation(self.document)
        replies = IReplies(conversation)

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        new_id = replies.addComment(comment)
        comment = self.document.restrictedTraverse(
            '++conversation++default/{0}'.format(new_id),
        )

        re_comment = createObject('plone.Comment')
        re_comment.text = 'Comment text'

        replies = IReplies(comment)
        replies.addComment(re_comment)

        self.assertTrue(self.registry.replyAdded)

    def test_removedEvent(self):
        self.assertFalse(self.registry.replyRemoved)

        conversation = IConversation(self.portal.doc1)
        replies = IReplies(conversation)

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        new_id = replies.addComment(comment)
        comment = self.portal.doc1.restrictedTraverse(
            '++conversation++default/{0}'.format(new_id),
        )

        re_comment = createObject('plone.Comment')
        re_comment.text = 'Comment text'
        replies = IReplies(comment)
        new_re_id = replies.addComment(re_comment)

        del replies[new_re_id]
        self.assertTrue(self.registry.replyRemoved)
