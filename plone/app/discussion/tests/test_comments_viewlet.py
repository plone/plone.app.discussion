import unittest
from datetime import datetime, timedelta

from plone.registry import Registry

from zope.component import createObject

from Acquisition import aq_base, aq_parent, aq_inner

from OFS.Image import Image

from plone.app.vocabularies.types import BAD_TYPES

from Products.CMFCore.FSImage import FSImage
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests import dummy
from Products.PloneTestCase.ptc import PloneTestCase

from plone.app.discussion.browser.comments import CommentsViewlet
from plone.app.discussion.interfaces import IConversation, IComment, IReplies, IDiscussionSettings
from plone.app.discussion.tests.layer import DiscussionLayer


class CommentsViewletTest(PloneTestCase):

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

    def test_format_time(self):
        pass

    def test_get_commenter_portrait(self):

        # Add a user with a member image
        self.membership_tool.addMember('jim', 'Jim', ['Member'], [])
        self.memberdata._setPortrait(Image(id='jim', file=dummy.File(), title=''), 'jim')
        self.assertEqual(self.memberdata._getPortrait('jim').getId(), 'jim')
        self.assertEqual(self.memberdata._getPortrait('jim').meta_type, 'Image')

        # Add a conversation with a comment
        conversation = IConversation(self.portal.doc1)
        conversation = conversation.__of__(self.portal.doc1)
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
        conversation = conversation.__of__(self.portal.doc1)
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

    def test_get_commenter_home(self):
        pass

    def test_get_commenter_home_without_username(self):
        # Create a user without setting a username
        pass

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)