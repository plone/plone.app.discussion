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
from Products.Five.testbrowser import Browser
from Products.PloneTestCase.ptc import PloneTestCase
from Products.PloneTestCase.ptc import FunctionalTestCase

from plone.app.discussion.browser.comments import CommentForm, CommentsViewlet
from plone.app.discussion.interfaces import IConversation, IComment 
from plone.app.discussion.interfaces import IReplies, IDiscussionSettings
from plone.app.discussion.tests.layer import DiscussionLayer


class TestCommentForm(PloneTestCase):

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

    def test_add_comment(self):
        form = CommentForm(self.viewlet, self.app.REQUEST)
        #self.viewlet.form.render(form)
        #self.viewlet.form.handleComment()
        #from z3c.form.testing import TestRequest
        #request = TestRequest(form={
        #                            'form.widgets.title': u'bar',
        #                            'form.widgets.text': u'foo',}
        #)
        #cf = CommentForm(self.viewlet, request)
        #cf.handleComments()
        # Zope publisher uses Python list to mark <select> values
        #self.portal.REQUEST["form.widgets.title"] = u"foo"
        #self.portal.REQUEST["form.widgets.title"] = u"Search"
        #view = self.portal.doc1.restrictedTraverse("@@view")
        # Call update() for form
        #view.process_form()
        #self.viewlet.form.handleComment()
        #print self.viewlet.form.render()
        
        # Always check form errors after update()
        #errors = view.errors
        #self.assertEqual(len(errors), 0, "Got errors:" + str(errors))


class TestCommentsViewletIntegration(FunctionalTestCase):

    layer = DiscussionLayer

    def testCommentsViewlet(self):
        browser = Browser()
        portal_url = self.portal.absolute_url()
        browser.handleErrors = False

        from Products.PloneTestCase.setup import portal_owner, default_password

        browser.open(portal_url + '/login_form')
        browser.getControl(name='__ac_name').value = portal_owner
        browser.getControl(name='__ac_password').value = default_password
        browser.getControl(name='submit').click()

        browser.open(portal_url)
        browser.getLink(id='document').click()
        browser.getControl(name='title').value = "Doc1"
        browser.getControl(name='allowDiscussion:boolean').value = True
        browser.getControl(name='form.button.save').click()        

        doc1 = self.portal['doc1']
        doc1_url = doc1.absolute_url()        
        browser.open(doc1_url)
        # Do not show the old comment viewlet
        self.failIf('discussion_reply_form' in browser.contents)
        # Show the new comment viewlet
        self.failUnless('formfield-form-widgets-in_reply_to' in browser.contents)
        self.failUnless('formfield-form-widgets-title' in browser.contents)
        self.failUnless('formfield-form-widgets-text' in browser.contents)

    
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
        # Portal owner can reply
        self.failUnless(self.viewlet.can_reply())
        self.logout()
        # Anonymous users can not reply
        self.failIf(self.viewlet.can_reply())

    def test_can_manage(self):
        # Portal owner has manage rights
        self.failUnless(self.viewlet.can_manage())
        self.logout()
        # Anonymous has no manage rights
        self.failIf(self.viewlet.can_manage())
    
    def test_is_discussion_allowed(self):
        # By default, discussion is disabled
        self.failIf(self.viewlet.is_discussion_allowed())
        # Enable discussion
        portal_discussion = getToolByName(self.portal, 'portal_discussion')
        portal_discussion.overrideDiscussionFor(self.portal.doc1, True)
        # Test if discussion has been enabled
        self.failUnless(self.viewlet.is_discussion_allowed())
    
    def test_has_replies(self):
        self.assertEquals(self.viewlet.has_replies(), False)
        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'
        conversation = IConversation(self.portal.doc1)
        conversation.addComment(comment)
        self.assertEquals(self.viewlet.has_replies(), True)

    def test_get_replies(self):
        self.failIf(self.viewlet.get_replies())
        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'
        conversation = IConversation(self.portal.doc1)
        conversation.addComment(comment)
        conversation.addComment(comment)
        replies = self.viewlet.get_replies()
        self.assertEquals(sum(1 for w in replies), 2)
        replies = self.viewlet.get_replies()
        replies.next()
        replies.next()
        self.assertRaises(StopIteration, replies.next)

    def test_get_replies_with_workflow_actions(self):
        self.failIf(self.viewlet.get_replies(workflow_actions=True))
        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'
        conversation = IConversation(self.portal.doc1)
        c1 = conversation.addComment(comment)
        self.assertEquals(sum(1 for w in self.viewlet.get_replies(workflow_actions=True)), 1)
        # Enable moderation workflow
        self.portal.portal_workflow.setChainForPortalTypes(('Discussion Item',),
                                                           ('simple_publication_workflow,'))
        # Check if workflow actions are available
        reply = self.viewlet.get_replies(workflow_actions=True).next()
        self.failUnless(reply.has_key('actions'))
        self.assertEquals(reply['actions'][0]['id'],
                          'publish')
        self.assertEquals(reply['actions'][0]['url'],
                          'http://nohost/plone/doc1/++conversation++default/%s' % int(c1) +
                          '/content_status_modify?workflow_action=publish') 
                
    def test_get_commenter_home_url(self):
        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'
        conversation = IConversation(self.portal.doc1)
        portal_membership = getToolByName(self.portal, 'portal_membership')
        m = portal_membership.getAuthenticatedMember()
        self.assertEquals(self.viewlet.get_commenter_home_url(m.getUserName()),
                          'http://nohost/plone/author/portal_owner')

    def test_get_commenter_home_url_is_none(self):
        self.failIf(self.viewlet.get_commenter_home_url())
            
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
        self.assertEquals(portrait_url, 
                          'http://nohost/plone/portal_memberdata/portraits/jim')

    def test_get_commenter_portrait_is_none(self):
        self.assertEquals(self.viewlet.get_commenter_portrait(), 
                          'defaultUser.gif')
        
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
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        registry['plone.app.discussion.interfaces.IDiscussionSettings.show_commenter_image'] = False        
        self.failIf(self.viewlet.show_commenter_image())
        
    def test_is_anonymous(self):
        self.failIf(self.viewlet.is_anonymous())
        self.logout()
        self.failUnless(self.viewlet.is_anonymous())

    def test_login_action(self):
        self.viewlet.update()
        self.assertEquals(self.viewlet.login_action(),
                          'http://nohost/plone/login_form?came_from=http%3A//nohost') 
   
    def test_format_time(self):
        python_time = datetime(2009, 02, 01, 23, 32, 03, 57)
        localized_time = self.viewlet.format_time(python_time)
        self.assertEquals(localized_time, "Feb 01, 2009 11:32 PM")

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)