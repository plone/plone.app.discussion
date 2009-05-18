import unittest

from zope.component import createObject

from Products.PloneTestCase.ptc import PloneTestCase
from plone.app.discussion.tests.layer import DiscussionLayer

from plone.app.discussion.interfaces import IComment, IConversation
from plone.app.discussion.comment import Comment

class CommentTest(PloneTestCase):
    
    layer = DiscussionLayer
    
    def afterSetUp(self):
        # First we need to create some content.
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
    
    def test_factory(self):
        # test with createObject()
        pass
        
    def test_id(self):
        # relationship between id, getId(), __name__
        pass
        
    def test_title(self):
        pass
    
    def test_creator(self):
        pass
        
    def test_traversal(self):
        # make sure comments are traversable, have an id, absolute_url and physical path
        pass
    
    def test_workflow(self):
        # ensure that we can assign a workflow to the comment type and perform
        # workflow operations
        pass
    
    def test_fti(self):
        # test that we can look up an FTI for Discussion Item
        pass

class RepliesTest(PloneTestCase):
    
    # test the IReplies adapter on a comment
    
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