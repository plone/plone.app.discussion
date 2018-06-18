# -*- coding: utf-8 -*-
"""Test for the plone.app.discussion indexers
"""
from datetime import datetime
from DateTime import DateTime
from plone.app.discussion import catalog
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.testing import PLONE_APP_DISCUSSION_INTEGRATION_TESTING  # noqa
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.indexer.delegate import DelegatingIndexerFactory
from zope.component import createObject

import unittest


LONG_TEXT = """Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed
diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum.
Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit
amet."""

LONG_TEXT_CUT = """Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed
diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
sed diam voluptua. At [...]"""


class ConversationIndexersTest(unittest.TestCase):
    """Conversation Indexer Tests
    """

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        workflow = self.portal.portal_workflow
        workflow.doActionFor(self.portal.doc1, 'publish')

        # Create a conversation.
        conversation = IConversation(self.portal.doc1)

        comment1 = createObject('plone.Comment')
        comment1.text = 'Comment Text'
        comment1.creator = 'jim'
        comment1.author_username = 'Jim'
        comment1.creation_date = datetime(2006, 9, 17, 14, 18, 12)
        comment1.modification_date = datetime(2006, 9, 17, 14, 18, 12)
        self.new_id1 = conversation.addComment(comment1)

        comment2 = createObject('plone.Comment')
        comment2.text = 'Comment Text'
        comment2.creator = 'emma'
        comment2.author_username = 'Emma'
        comment2.creation_date = datetime(2007, 12, 13, 4, 18, 12)
        comment2.modification_date = datetime(2007, 12, 13, 4, 18, 12)
        self.new_id2 = conversation.addComment(comment2)

        comment3 = createObject('plone.Comment')
        comment3.text = 'Comment Text'
        comment3.creator = 'lukas'
        comment3.author_username = 'Lukas'
        comment3.creation_date = datetime(2009, 4, 12, 11, 12, 12)
        comment3.modification_date = datetime(2009, 4, 12, 11, 12, 12)
        self.new_id3 = conversation.addComment(comment3)

        self.conversation = conversation

    def test_conversation_total_comments(self):
        self.assertTrue(isinstance(
            catalog.total_comments,
            DelegatingIndexerFactory,
        ))
        self.assertEqual(catalog.total_comments(self.portal.doc1)(), 3)
        del self.conversation[self.new_id1]
        self.assertEqual(catalog.total_comments(self.portal.doc1)(), 2)
        del self.conversation[self.new_id2]
        del self.conversation[self.new_id3]
        self.assertEqual(catalog.total_comments(self.portal.doc1)(), 0)

    def test_conversation_last_comment_date(self):
        self.assertTrue(isinstance(
            catalog.last_comment_date,
            DelegatingIndexerFactory,
        ))
        self.assertEqual(
            catalog.last_comment_date(self.portal.doc1)(),
            datetime(2009, 4, 12, 11, 12, 12),
        )
        del self.conversation[self.new_id3]
        self.assertEqual(
            catalog.last_comment_date(self.portal.doc1)(),
            datetime(2007, 12, 13, 4, 18, 12),
        )
        del self.conversation[self.new_id2]
        del self.conversation[self.new_id1]
        self.assertEqual(catalog.last_comment_date(self.portal.doc1)(), None)

    def test_conversation_commentators(self):
        pass
        # self.assertEqual(catalog.commentators(self.portal.doc1)(),
        #                  ('Jim', 'Emma', 'Lukas'))
        # self.assertTrue(isinstance(catalog.commentators,
        #                        DelegatingIndexerFactory))


class CommentIndexersTest(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Add a comment. Note: in real life, we always create comments via the
        # factory to allow different factories to be swapped in

        comment = createObject('plone.Comment')
        comment.text = 'Lorem ipsum dolor sit amet.'
        comment.creator = 'jim'
        comment.author_name = 'Jim'
        comment.creation_date = datetime(2006, 9, 17, 14, 18, 12)
        comment.modification_date = datetime(2008, 3, 12, 7, 32, 52)

        self.comment_id = conversation.addComment(comment)
        self.comment = comment.__of__(conversation)
        self.conversation = conversation

    def test_title(self):
        self.assertEqual(catalog.title(self.comment)(), 'Jim on Document 1')
        self.assertTrue(isinstance(catalog.title, DelegatingIndexerFactory))

    def test_description(self):
        self.assertEqual(
            catalog.description(self.comment)(),
            'Lorem ipsum dolor sit amet.',
        )
        self.assertTrue(
            isinstance(catalog.description, DelegatingIndexerFactory))

    def test_description_long(self):
        # Create a 50 word comment and make sure the description returns
        # only the first 25 words
        comment_long = createObject('plone.Comment')
        comment_long.title = 'Long Comment'
        comment_long.text = LONG_TEXT

        self.conversation.addComment(comment_long)
        self.assertEqual(
            catalog.description(comment_long)(),
            LONG_TEXT_CUT.replace('\n', ' '),
        )

    def test_dates(self):
        # Test if created, modified, effective etc. are set correctly
        self.assertEqual(
            catalog.created(self.comment)(),
            DateTime(2006, 9, 17, 14, 18, 12, 'GMT'),
        )
        self.assertEqual(
            catalog.effective(self.comment)(),
            DateTime(2006, 9, 17, 14, 18, 12, 'GMT'),
        )
        self.assertEqual(
            catalog.modified(self.comment)(),
            DateTime(2008, 3, 12, 7, 32, 52, 'GMT'),
        )

    def test_searchable_text(self):
        # Test if searchable text is a concatenation of title and comment text
        self.assertEqual(
            catalog.searchable_text(self.comment)(),
            ('Lorem ipsum dolor sit amet.'),
        )
        self.assertTrue(isinstance(
            catalog.searchable_text,
            DelegatingIndexerFactory,
        ))

    def test_creator(self):
        self.assertEqual(catalog.creator(self.comment)(), ('jim'))

    def test_in_response_to(self):
        # make sure in_response_to returns the title or id of the content
        # object the comment was added to
        self.assertEqual(catalog.in_response_to(self.comment)(), 'Document 1')
