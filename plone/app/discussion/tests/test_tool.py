import unittest

from zope.component import getUtility

from Products.PloneTestCase.ptc import PloneTestCase
from plone.app.discussion.tests.layer import DiscussionLayer

from plone.app.discussion.comment import Comment
from plone.app.discussion.interfaces import ICommentingTool, IConversation

class ToolTest(PloneTestCase):
    
    layer = DiscussionLayer
    
    def afterSetUp(self):
        # XXX If we make this a layer, it only get run once...
        # First we need to create some content.
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
            
    def test_tool_indexing(self):
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
        
        # Check that the comment got indexed in the tool:
        tool = getUtility(ICommentingTool)
        comment = list(tool.searchResults())
        self.assert_(len(comment) == 1, "There is only one comment, but we got"
                     " %s results in the search" % len(comment))
        self.assertEquals(comment[0].Title, 'Comment 1')
    
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)