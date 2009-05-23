import unittest
from datetime import datetime, timedelta

from zope.component import createObject

from Acquisition import aq_base

from Products.PloneTestCase.ptc import PloneTestCase
from plone.app.discussion.tests.layer import DiscussionLayer

from plone.app.discussion.interfaces import IConversation, IComment

class ConversationTest(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        # First we need to create some content.
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')

    def test_add_comment(self):
        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

        # Add a comment. Note: in real life, we always create comments via the factory
        # to allow different factories to be swapped in

        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'

        new_id = conversation.addComment(comment)

        # Check that the conversation methods return the correct data
        self.assert_(isinstance(comment.comment_id, long))
        self.assert_(IComment.providedBy(conversation[new_id]))
        self.assertEquals(aq_base(conversation[new_id].__parent__), aq_base(conversation))
        self.assertEquals(new_id, comment.comment_id)
        self.assertEquals(len(conversation.getComments()), 1)
        self.assertEquals(len(conversation.getThreads()), 1)
        self.assertEquals(conversation.total_comments, 1)
        self.assert_(conversation.last_comment_date - datetime.now() < timedelta(seconds=1))

    def test_delete(self):
        pass

    def test_dict_operations(self):
        # test dict operations and acquisition wrapping
        pass

    def test_total_comments(self):
        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

        # Add a three comments. Note: in real life, we always create
        # comments via the factory to allow different factories to be
        # swapped in

        comment1 = createObject('plone.Comment')
        comment1.title = 'Comment 1'
        comment1.text = 'Comment text'

        comment2 = createObject('plone.Comment')
        comment2.title = 'Comment 2'
        comment2.text = 'Comment text'

        comment3 = createObject('plone.Comment')
        comment3.title = 'Comment 3'
        comment3.text = 'Comment text'

        new_comment1_id = conversation.addComment(comment1)
        new_comment2_id = conversation.addComment(comment2)
        new_comment3_id = conversation.addComment(comment3)

        self.assertEquals(conversation.total_comments, 3)

    def test_commentators(self):
        # add and remove a few comments to make sure the commentators
        # property returns a true set
        pass

    def test_last_comment_date(self):
        pass

    def test_get_comments_flat(self):
        pass

    def test_get_comments_batched(self):
        pass

    def test_get_threads(self):
        pass

    def test_get_threads_batched(self):
        pass

class RepliesTest(PloneTestCase):

    # test the IReplies adapter on a conversation

    layer = DiscussionLayer

    def afterSetUp(self):
        # First we need to create some content.
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')

    def test_add_comment(self):
        pass

    def test_delete_comment(self):
        pass

    def test_dict_api(self):
        # ensure all operations use only top-level comments
        pass

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)