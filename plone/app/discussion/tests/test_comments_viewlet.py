import unittest
from datetime import datetime, timedelta

from plone.registry import Registry

from zope.component import createObject, queryUtility

from Acquisition import aq_base, aq_parent, aq_inner

from OFS.Image import Image

from plone.app.vocabularies.types import BAD_TYPES

from plone.registry.interfaces import IRegistry

from Products.CMFCore.FSImage import FSImage
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests import dummy
from Products.PloneTestCase.ptc import PloneTestCase

from plone.app.discussion.browser.comments import CommentsViewlet
from plone.app.discussion.interfaces import IConversation, IComment, IReplies, IDiscussionSettings
from plone.app.discussion.tests.layer import DiscussionLayer


class TestCommentsViewlet(PloneTestCase):

    layer = DiscussionLayer
        
    def afterSetUp(self):
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
        self.portal_discussion = getToolByName(self.portal, 'portal_discussion', None)
        self.membership_tool = getToolByName(self.folder, 'portal_membership')
        self.memberdata = self.portal.portal_memberdata
        request = self.app.REQUEST
        context = getattr(self.portal, 'doc1')
        self.viewlet = CommentsViewlet(context, request, None, None)
            
    def test_can_reply(self):
        self.failUnless(self.viewlet.can_reply())

    def test_can_manage(self):
        self.failUnless(self.viewlet.can_manage())
    
    def test_is_discussion_allowed(self):
        #self.failUnless(self.viewlet.is_discussion_allowed())
        pass
    
    def test_has_replies(self, workflow_actions=False):
        #self.failUnless(self.viewlet.has_replies())
        pass
    
    def test_get_replies(self, workflow_actions=False):
        #self.failUnless(self.viewlet.get_replies())
        pass
    
    def test_get_commenter_home_url(self):
        #self.failUnless(self.viewlet.get_commenter_home_url())
        pass
    
    def test_get_commenter_portrait(self):

        # Add a user with a member image
        self.membership_tool.addMember('jim', 'Jim', ['Member'], [])
        self.memberdata._setPortrait(Image(id='jim', file=dummy.File(), title=''), 'jim')
        self.assertEqual(self.memberdata._getPortrait('jim').getId(), 'jim')
        self.assertEqual(self.memberdata._getPortrait('jim').meta_type, 'Image')

        # Add a conversation with a comment
        conversation = IConversation(self.portal.doc1)
        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'
        comment.Creator = 'Jim'
        comment.author_username = 'jim'
        new_id = conversation.addComment(comment)

        # Call get_commenter_portrait method of the viewlet
        self.viewlet.update()
        portrait_url = self.viewlet.get_commenter_portrait('jim')

        # Check if the correct member image URL is returned
        self.assertEquals(portrait_url, 'http://nohost/plone/portal_memberdata/portraits/jim')

    def test_get_commenter_portrait_without_userimage(self):

        # Create a user without a user image
        self.membership_tool.addMember('jim', 'Jim', ['Member'], [])

        # Add a conversation with a comment
        conversation = IConversation(self.portal.doc1)
        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'
        comment.Creator = 'Jim'
        comment.author_username = 'jim'
        new_id = conversation.addComment(comment)

        # Call get_commenter_portrait method of the viewlet
        self.viewlet.update()
        portrait_url = self.viewlet.get_commenter_portrait('jim')

        # Check if the correct default member image URL is returned
        self.assertEquals(portrait_url, 'http://nohost/plone/defaultUser.gif')

    def test_anonymous_discussion_allowed(self):
        # Anonymous discussion is not allowed by default
        self.failIf(self.viewlet.anonymous_discussion_allowed())
        # Allow anonymous discussion
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        registry['plone.app.discussion.interfaces.IDiscussionSettings.anonymous_comments'] = True
        # Test if anonymous discussion is allowed for the viewlet
        self.failUnless(self.viewlet.anonymous_discussion_allowed())
    
    def test_show_commenter_image(self):
        self.failUnless(self.viewlet.show_commenter_image())

    def test_is_anonymous(self):
        pass

    def test_login_action(self):
        pass
        
    def test_format_time(self):
        python_time = datetime(2009, 02, 01, 23, 32, 03, 57)
        localized_time = self.viewlet.format_time(python_time)
        self.assertEquals(localized_time, "Feb 01, 2009 11:32 PM")

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)