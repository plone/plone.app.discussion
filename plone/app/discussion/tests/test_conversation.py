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
        # XXX: not yet implemented
        # self.assertEquals(len(conversation.getThreads()), 1)
        self.assertEquals(conversation.total_comments, 1)
        self.assert_(conversation.last_comment_date - datetime.now() < timedelta(seconds=1))

    def test_delete_comment(self):
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

        # make sure the comment has been added
        self.assertEquals(len(conversation.getComments()), 1)
        # XXX: not yet implemented
        # self.assertEquals(len(conversation.getThreads()), 1)
        self.assertEquals(conversation.total_comments, 1)

        # delete the comment we just created
        conversation.__delitem__(new_id)

        # make sure there is no comment left in the conversation
        self.assertEquals(len(conversation.getComments()), 0)

        # XXX: not yet implemented
        # self.assertEquals(len(conversation.getThreads()), 0)
        self.assertEquals(conversation.total_comments, 0)

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

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

        # Add a four comments from three different users
        # Note: in real life, we always create
        # comments via the factory to allow different factories to be
        # swapped in
        comment1 = createObject('plone.Comment')
        comment1.title = 'Comment 1'
        comment1.text = 'Comment text'
        comment1.author_username = "Jim"
        new_comment1_id = conversation.addComment(comment1)

        comment2 = createObject('plone.Comment')
        comment2.title = 'Comment 2'
        comment2.text = 'Comment text'
        comment2.author_username = "Joe"
        new_comment2_id = conversation.addComment(comment2)

        comment3 = createObject('plone.Comment')
        comment3.title = 'Comment 3'
        comment3.text = 'Comment text'
        comment3.author_username = "Jack"
        new_comment3_id = conversation.addComment(comment3)

        comment4 = createObject('plone.Comment')
        comment4.title = 'Comment 3'
        comment4.text = 'Comment text'
        comment4.author_username = "Jack"
        new_comment4_id = conversation.addComment(comment4)

        # check if all commentators are in the commentators list
        self.assertEquals(conversation.total_comments, 4)
        self.failUnless('Jim' in conversation.commentators)
        self.failUnless('Joe' in conversation.commentators)
        self.failUnless('Jack' in conversation.commentators)

        # remove the comment from Jack
        del conversation[new_comment3_id]

        # check if Jack is still in the commentators list (since
        # he had added two comments)
        self.failUnless('Jim' in conversation.commentators)
        self.failUnless('Joe' in conversation.commentators)
        self.failUnless('Jack' in conversation.commentators)
        self.assertEquals(conversation.total_comments, 3)

        # remove the second comment from Jack
        del conversation[new_comment4_id]

        # check if Jack has been removed from the commentators list
        self.failUnless('Jim' in conversation.commentators)
        self.failUnless('Joe' in conversation.commentators)
        self.failIf('Jack' in conversation.commentators)
        self.assertEquals(conversation.total_comments, 2)

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

    def test_traversal(self):
        # make sure we can traverse to conversations and get a URL and path

        conversation = self.portal.doc1.restrictedTraverse('++conversation++default')
        self.assert_(IConversation.providedBy(conversation))

        self.assertEquals(('', 'plone', 'doc1', '++conversation++default'), conversation.getPhysicalPath())
        self.assertEquals('plone/doc1/%2B%2Bconversation%2B%2Bdefault', conversation.absolute_url())

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