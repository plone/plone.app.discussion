import unittest
from datetime import datetime, timedelta
from base import TestCase

from zope.testing import doctestunit
from zope.component import testing, getMultiAdapter
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserView
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from plone.app.discussion.conversation import Conversation
from plone.app.discussion.comment import Comment

class ConversationTest(TestCase):
    def afterSetUp(self):
        # XXX If we make this a layer, it only get run once...
        # First we need to create some content.
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
            
    def test_add_comment(self):
        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = Conversation()
        
        # Add a comment. reply_to=0 means it's not a reply
        comment = Comment(conversation=conversation, reply_to=0)
        comment.title = 'Comment 1'
        comment.text = 'Comment text'
        
        conversation.addComment(comment)
        
        # Check that the conversation methods return the correct data
        self.assertEquals(comment.id, '1')
        self.assertEquals(len(conversation.getComments()), 1)
        self.assertEquals(len(conversation.getThreads()), 1)
        self.assertEquals(conversation.total_comments, 1)
        self.assert_(conversation.last_comment_date - datetime.now() < timedelta(seconds=1))
    

def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(ConversationTest),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
