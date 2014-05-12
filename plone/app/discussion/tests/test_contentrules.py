# -*- coding: utf-8 -*-

import unittest2 as unittest
from Testing import ZopeTestCase as ztc
from zope.component import createObject, getAdapter
from zope.event import notify
from plone.app.testing import TEST_USER_ID, setRoles

from plone.contentrules.rule.interfaces import IRuleEventType
from plone.stringinterp.interfaces import IStringSubstitution

from plone.app.discussion.interfaces import IConversation, IReplies
from plone.app.discussion.interfaces import ICommentAddedEvent
from plone.app.discussion.interfaces import ICommentRemovedEvent
from plone.app.discussion.interfaces import IReplyAddedEvent
from plone.app.discussion.interfaces import IReplyRemovedEvent

from plone.app.discussion.testing import (
    PLONE_APP_DISCUSSION_INTEGRATION_TESTING,
)

class CommentContentRulesTest(unittest.TestCase):
    """ Test custom comments events
    """
    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        # Setup session manager
        ztc.utils.setupCoreSessions(self.layer['app'])

        # Setup sandbox
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        # Setup current user properties
        member = self.portal.portal_membership.getMemberById(TEST_USER_ID)
        member.setMemberProperties({
            'fullname': 'X Manager',
            'email': 'xmanager@example.com'
        })

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        name = self.portal.invokeFactory(
            id='doc1',
            title='Document 1',
            type_name='Document')

        self.document = self.portal[name]

        comment = createObject('plone.Comment')
        comment.text = "This is a comment"
        comment.author_username = "jim"
        comment.author_name = "Jim"
        comment.author_email = "jim@example.com"
        conversation = IConversation(self.document)
        conversation.addComment(comment)


    def testEventTypesMarked(self):
        self.assertTrue(IRuleEventType.providedBy(ICommentAddedEvent))
        self.assertTrue(IRuleEventType.providedBy(ICommentRemovedEvent))
        self.assertTrue(IRuleEventType.providedBy(IReplyAddedEvent))
        self.assertTrue(IRuleEventType.providedBy(IReplyRemovedEvent))

    def testCommentIdStringSubstitution(self):
        comment_id = getAdapter(self.document, IStringSubstitution,
                                name=u"comment_id")
        self.assertIsInstance(comment_id(), long)

    def testCommentTextStringSubstitution(self):
        comment_text = getAdapter(self.document, IStringSubstitution,
                                  name=u"comment_text")
        self.assertEqual(comment_text(), u"This is a comment")

    def testCommentUserIdStringSubstitution(self):
        comment_user_id = getAdapter(self.document, IStringSubstitution,
                                     name=u"comment_user_id")
        self.assertEqual(comment_user_id(), u"jim")

    def testCommentUserFullNameStringSubstitution(self):
        comment_user_fullname = getAdapter(self.document, IStringSubstitution,
                                           name=u"comment_user_fullname")
        self.assertEqual(comment_user_fullname(), u"Jim")

    def testCommentUserEmailStringSubstitution(self):
        comment_user_email = getAdapter(self.document, IStringSubstitution,
                                        name=u"comment_user_email")
        self.assertEqual(comment_user_email(), u"jim@example.com")


class ReplyContentRulesTest(unittest.TestCase):
    """ Test custom comments events
    """
    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        # Setup session manager
        ztc.utils.setupCoreSessions(self.layer['app'])

        # Setup sandbox
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        name = self.portal.invokeFactory(
            id='doc1',
            title='Document 1',
            type_name='Document')

        self.document = self.portal[name]
        conversation = IConversation(self.document)
        replies = IReplies(conversation)

        comment = createObject('plone.Comment')
        comment.text = 'This is a comment'
        new_id = replies.addComment(comment)
        comment = self.document.restrictedTraverse(
            '++conversation++default/%s' % new_id)

        re_comment = createObject('plone.Comment')
        re_comment.text = 'This is a reply'
        re_comment.author_username = "julia"
        re_comment.author_name = "Juliana"
        re_comment.author_email = "julia@example.com"

        replies = IReplies(comment)
        new_re_id = replies.addComment(re_comment)

    def testReplyIdStringSubstitution(self):
        reply_id = getAdapter(self.document, IStringSubstitution,
                              name=u"comment_id")
        self.assertIsInstance(reply_id(), long)

    def testReplyTextStringSubstitution(self):
        reply_text = getAdapter(self.document, IStringSubstitution,
                                  name=u"comment_text")
        self.assertEqual(reply_text(), u"This is a reply")

    def testReplyUserIdStringSubstitution(self):
        reply_user_id = getAdapter(self.document, IStringSubstitution,
                                   name=u"comment_user_id")
        self.assertEqual(reply_user_id(), u"julia")

    def testReplyUserFullNameStringSubstitution(self):
        reply_user_fullname = getAdapter(self.document, IStringSubstitution,
                                           name=u"comment_user_fullname")
        self.assertEqual(reply_user_fullname(), u"Juliana")

    def testReplyUserEmailStringSubstitution(self):
        reply_user_email = getAdapter(self.document, IStringSubstitution,
                                      name=u"comment_user_email")
        self.assertEqual(reply_user_email(), u"julia@example.com")
