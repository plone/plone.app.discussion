import unittest

from zope.component import queryUtility, createObject

from Products.PloneTestCase.ptc import PloneTestCase
from plone.app.discussion.tests.layer import DiscussionLayer

from plone.app.discussion.interfaces import ICommentingTool, IConversation

class ToolTest(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        # First we need to create some content.
        self.loginAsPortalOwner()
        self.portal.invokeFactory(id='doc1',
                                  title='Document 1',
                                  type_name='Document')

    def test_tool_indexing(self):
        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Add a comment.
        comment = createObject('plone.Comment')
        comment.creator = 'Jim'
        comment.text = 'Comment text'

        conversation.addComment(comment)

        # Check that the comment got indexed in the tool:
        tool = queryUtility(ICommentingTool)
        comment = list(tool.searchResults())
        self.assertTrue(len(comment) == 1, "There is only one comment, but we got"
                     " %s results in the search" % len(comment))
        self.assertEqual(comment[0].Title, 'Jim on Document 1')

    def test_unindexing(self):
        pass

    def test_search(self):
        # search returns only comments
        pass

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
