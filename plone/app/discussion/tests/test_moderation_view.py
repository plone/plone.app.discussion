import unittest

from DateTime import DateTime
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

from plone.app.discussion.browser.moderation import View
from plone.app.discussion.interfaces import IConversation, IComment
from plone.app.discussion.interfaces import IReplies, IDiscussionSettings
from plone.app.discussion.tests.layer import DiscussionLayer


class ModerationViewTest(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
        
        self.portal_discussion = getToolByName(self.portal,
                                               'portal_discussion',
                                               None)
        self.membership_tool = getToolByName(self.folder,
                                             'portal_membership')
        self.memberdata = self.portal.portal_memberdata
        request = self.app.REQUEST
        context = getattr(self.portal, 'doc1')
        self.view = View(context, request)
        self.view.__of__(context)
        self.portal.portal_workflow.setChainForPortalTypes(
            ('Discussion Item',), 'comment_review_workflow')
        self.wf_tool = self.portal.portal_workflow

        # Add a conversation with three comments

        conversation = IConversation(self.portal.doc1)

        comment1 = createObject('plone.Comment')
        comment1.title = 'Comment 1'
        comment1.text = 'Comment text'
        comment1.Creator = 'Jim'
        new_id_1 = conversation.addComment(comment1)
        self.comment1 = self.portal.doc1.restrictedTraverse(\
                            '++conversation++default/%s' % new_id_1)

        comment2 = createObject('plone.Comment')
        comment2.title = 'Comment 2'
        comment2.text = 'Comment text'
        comment2.Creator = 'Joe'
        new_id_2 = conversation.addComment(comment2)
        self.comment2 = self.portal.doc1.restrictedTraverse(\
                            '++conversation++default/%s' % new_id_2)

        comment3 = createObject('plone.Comment')
        comment3.title = 'Comment 3'
        comment3.text = 'Comment text'
        comment3.Creator = 'Emma'
        new_id_3 = conversation.addComment(comment3)
        self.comment3 = self.portal.doc1.restrictedTraverse(\
                            '++conversation++default/%s' % new_id_3)

    def test_moderation_enabled(self):
        self.assertEquals(self.view.moderation_enabled(), True)
        self.wf_tool.setChainForPortalTypes(('Discussion Item',),
                                            ('simple_publication_workflow,'))
        self.assertEquals(self.view.moderation_enabled(), False)

    def test_old_comments_not_shown_in_moderation_view(self):
        # Create an old comment and make sure it is not shown
        # in the moderation view.
        
        # Create old comment
        discussion = getToolByName(self.portal, 'portal_discussion', None)
        discussion.overrideDiscussionFor(self.portal.doc1, 1)        
        talkback = discussion.getDiscussionFor(self.portal.doc1)
        self.portal.doc1.talkback.createReply('My Title', 'My Text', Creator='Jim')
        reply = talkback.getReplies()[0]
        reply.setReplyTo(self.portal.doc1)
        reply.creation_date = DateTime(2003, 3, 11, 9, 28, 6)
        reply.modification_date = DateTime(2009, 7, 12, 19, 38, 7)
        self.assertEquals(reply.Title(), 'My Title')
        self.assertEquals(reply.EditableBody(), 'My Text')
        self.failUnless('Jim' in reply.listCreators())
        self.assertEquals(talkback.replyCount(self.portal.doc1), 1)
        self.assertEquals(reply.inReplyTo(), self.portal.doc1)
        
        # Make sure only the two new comments are shown
        self.view()
        self.assertEquals(len(self.view.comments), 3)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)