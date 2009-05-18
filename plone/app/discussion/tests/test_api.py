import unittest
from datetime import datetime, timedelta

from Products.PloneTestCase.ptc import PloneTestCase
from plone.app.discussion.tests.layer import DiscussionLayer

from plone.app.discussion.conversation import Conversation
from plone.app.discussion.comment import Comment
from plone.app.discussion.interfaces import ICommentingTool, IConversation

class ConversationTest(PloneTestCase):
    
    layer = DiscussionLayer
    
    def afterSetUp(self):
        # XXX If we make this a layer, it only get run once...
        # First we need to create some content.
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
            
    def test_add_comment(self):
        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)
        # Pretend that we have traversed to the comment by aq wrapping it.
        # XXX implement traversal to commenting and change this:
        conversation = conversation.__of__(self.portal.doc1)

        # Add a comment. reply_to=0 means it's not a reply
        comment = Comment(conversation=conversation, reply_to=0)
        comment.title = 'Comment 1'
        comment.text = 'Comment text'
        
        conversation.addComment(comment)
        
        # Check that the conversation methods return the correct data
        self.assert_(isinstance(comment.comment_id, long))
        self.assertEquals(len(conversation.getComments()), 1)
        self.assertEquals(len(conversation.getThreads()), 1)
        self.assertEquals(conversation.total_comments, 1)
        self.assert_(conversation.last_comment_date - datetime.now() < timedelta(seconds=1))
    
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)