# -*- coding: utf-8 -*-
import unittest
import time
from datetime import datetime

from AccessControl import Unauthorized
        
from zope.component import createObject, queryUtility

from OFS.Image import Image

from zope.interface import alsoProvides
from zope.publisher.browser import TestRequest
from zope.annotation.interfaces import IAttributeAnnotatable
from z3c.form.interfaces import IFormLayer

from zope.component import provideAdapter
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.interface import Interface
from zope.component import getMultiAdapter

from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.tests import dummy

from Products.PloneTestCase.ptc import PloneTestCase

from plone.app.discussion.browser.comments import CommentsViewlet
from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion.interfaces import IConversation 
from plone.app.discussion.tests.layer import DiscussionLayer


class TestCommentForm(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
        self.dtool = getToolByName(self.portal, 
                                   'portal_discussion', 
                                    None)
        self.dtool.overrideDiscussionFor(self.portal.doc1, False)
        self.mtool = getToolByName(self.folder, 'portal_membership', None)
        self.memberdata = self.portal.portal_memberdata
        self.request = self.app.REQUEST
        self.context = getattr(self.portal, 'doc1')
        
    def test_add_comment(self):
        # Allow discussion
        self.dtool.overrideDiscussionFor(self.portal.doc1, True)
        self.viewlet = CommentsViewlet(self.context, self.request, None, None)

        def make_request(form={}):
            request = TestRequest()
            request.form.update(form)
            alsoProvides(request, IFormLayer)
            alsoProvides(request, IAttributeAnnotatable)
            return request
        
        provideAdapter(adapts=(Interface, IBrowserRequest),
                       provides=Interface,
                       factory=CommentForm,
                       name=u"comment-form")
        
        # The form should return an error if the comment text field is empty
        request = make_request(form={})

        commentForm = getMultiAdapter((self.context, request), 
                                      name=u"comment-form")
        commentForm.update()
        data, errors = commentForm.extractData() # pylint: disable-msgs=W0612
        
        self.assertEquals(len(errors), 1)
        self.failIf(commentForm.handleComment(commentForm, "foo"))
        
        # The form is submitted successfully, if the required text field is 
        # filled out
        request = make_request(form={'form.widgets.text': u'bar'})

        commentForm = getMultiAdapter((self.context, request), 
                                      name=u"comment-form")
        commentForm.update()
        data, errors = commentForm.extractData() # pylint: disable-msgs=W0612

        self.assertEquals(len(errors), 0)
        self.failIf(commentForm.handleComment(commentForm, "foo"))
        

    def test_can_not_add_comments_if_discussion_is_not_allowed(self):
        """Make sure that comments can't be posted if discussion is disabled.
        """
        
        # Discussion is disabled by default
        
        def make_request(form={}):
            request = TestRequest()
            request.form.update(form)
            alsoProvides(request, IFormLayer)
            alsoProvides(request, IAttributeAnnotatable)
            return request
        
        provideAdapter(adapts=(Interface, IBrowserRequest),
                       provides=Interface,
                       factory=CommentForm,
                       name=u"comment-form")
        
        request = make_request(form={'form.widgets.text': u'bar'})

        commentForm = getMultiAdapter((self.context, request), 
                                      name=u"comment-form")
        commentForm.update()
        data, errors = commentForm.extractData() # pylint: disable-msgs=W0612
        
        # No form errors, but raise unauthorized because discussion is not
        # allowed
        self.assertEquals(len(errors), 0)
        self.assertRaises(Unauthorized,
                          commentForm.handleComment,
                          commentForm,
                          "foo")
                                
    def test_add_comment_as_anonymous(self):
        """Make sure that anonymous users can't post comments if anonymous
           comments are disabled.
        """
        
        # Anonymous comments are disabled by default
        
        self.logout()
        
        def make_request(form={}):
            request = TestRequest()
            request.form.update(form)
            alsoProvides(request, IFormLayer)
            alsoProvides(request, IAttributeAnnotatable)
            return request
        
        provideAdapter(adapts=(Interface, IBrowserRequest),
                       provides=Interface,
                       factory=CommentForm,
                       name=u"comment-form")
        
        request = make_request(form={'form.widgets.text': u'bar'})

        commentForm = getMultiAdapter((self.context, request), 
                                      name=u"comment-form")
        commentForm.update()
        data, errors = commentForm.extractData() # pylint: disable-msgs=W0612
        
        self.assertEquals(len(errors), 0)
        self.assertRaises(Unauthorized,
                          commentForm.handleComment,
                          commentForm,
                          "foo")

   
class TestCommentsViewlet(PloneTestCase):

    layer = DiscussionLayer
        
    def afterSetUp(self):
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
        self.portal_discussion = getToolByName(self.portal, 
                                               'portal_discussion', 
                                               None)
        self.mtool = getToolByName(self.folder, 'portal_membership')
        self.memberdata = self.portal.portal_memberdata
        request = self.app.REQUEST
        context = getattr(self.portal, 'doc1')
        self.viewlet = CommentsViewlet(context, request, None, None)

    def test_cook(self):
        text = """First paragraph
        
        Second paragraph"""
        self.assertEquals(self.viewlet.cook(text),
        "<p>First paragraph<br />        <br />        Second paragraph</p>")

    def test_cook_no_html(self):
        text = """<b>Got HTML?</b>"""
        self.assertEquals(self.viewlet.cook(text),
                          "<p>&lt;b&gt;Got HTML?&lt;/b&gt;</p>")
    
    def test_cook_with_no_ascii_characters(self):
        text = """Umlaute sind ä, ö und ü."""
        self.assertEquals(self.viewlet.cook(text), 
            "<p>Umlaute sind \xc3\xa4, \xc3\xb6 und \xc3\xbc.</p>")
    
    def test_cook_links(self):
        text = "Go to http://www.plone.org"
        self.assertEquals(self.viewlet.cook(text), 
                          "<p>Go to http://www.plone.org</p>")
        
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
        comment.text = 'Comment text'
        conversation = IConversation(self.portal.doc1)
        conversation.addComment(comment)
        self.assertEquals(self.viewlet.has_replies(), True)

    def test_get_replies(self):
        self.failIf(self.viewlet.get_replies())
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        conversation = IConversation(self.portal.doc1)
        conversation.addComment(comment)
        conversation.addComment(comment)
        replies = self.viewlet.get_replies()
        self.assertEquals(sum(1 for w in replies), # pylint: disable-msgs=W0612
                          2) 
        replies = self.viewlet.get_replies()
        replies.next()
        replies.next()
        self.assertRaises(StopIteration, replies.next)

    def test_get_replies_with_workflow_actions(self):
        self.failIf(self.viewlet.get_replies(workflow_actions=True))
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        conversation = IConversation(self.portal.doc1)
        c1 = conversation.addComment(comment)
        self.assertEquals(sum(1 for w in # pylint: disable-msgs=W0612
                              self.viewlet.get_replies(workflow_actions=True)), 
                              1) 
        # Enable moderation workflow
        self.portal.portal_workflow.setChainForPortalTypes(
            ('Discussion Item',),
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
        comment.text = 'Comment text'
        IConversation(self.portal.doc1)
        portal_membership = getToolByName(self.portal, 'portal_membership')
        m = portal_membership.getAuthenticatedMember()
        self.assertEquals(self.viewlet.get_commenter_home_url(m.getUserName()),
                          'http://nohost/plone/author/portal_owner')

    def test_get_commenter_home_url_is_none(self):
        self.failIf(self.viewlet.get_commenter_home_url())
            
    def test_get_commenter_portrait(self):

        # Add a user with a member image
        self.mtool.addMember('jim', 'Jim', ['Member'], [])
        self.memberdata._setPortrait(Image(id='jim', 
                                           file=dummy.File(),
                                           title=''), 'jim')
        self.assertEqual(self.memberdata._getPortrait('jim').getId(), 
                         'jim')
        self.assertEqual(self.memberdata._getPortrait('jim').meta_type, 
                         'Image')

        # Add a conversation with a comment
        conversation = IConversation(self.portal.doc1)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment.Creator = 'Jim'
        comment.author_username = 'jim'
        conversation.addComment(comment)

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
        self.mtool.addMember('jim', 'Jim', ['Member'], [])

        # Add a conversation with a comment
        conversation = IConversation(self.portal.doc1)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment.Creator = 'Jim'
        comment.author_username = 'jim'
        conversation.addComment(comment)

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
        registry['plone.app.discussion.interfaces.IDiscussionSettings.' +
                  'anonymous_comments'] = True
        # Test if anonymous discussion is allowed for the viewlet
        self.failUnless(self.viewlet.anonymous_discussion_allowed())
    
    def test_show_commenter_image(self):
        self.failUnless(self.viewlet.show_commenter_image())
        registry = queryUtility(IRegistry)
        registry['plone.app.discussion.interfaces.IDiscussionSettings.' +
                 'show_commenter_image'] = False        
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
        # Python Time must be utc time. There seems to be no too simple way
        # to tell datetime to be of utc time.
        # therefor, we convert the time to seconds since epoch, which seems
        # to assume, that the datetime was given in local time, and does the
        # correction to the seconds since epoch. Then time.gmtime returns
        # a correct utc time that can be used to make datetime set the utc
        # time of the local time given above. That way, the time for the
        # example below is correct within each time zone, independent of DST
        python_time = datetime(*time.gmtime(time.mktime(python_time.timetuple()))[:7])
        localized_time = self.viewlet.format_time(python_time)
        self.assertEquals(localized_time, "Feb 01, 2009 11:32 PM")

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
