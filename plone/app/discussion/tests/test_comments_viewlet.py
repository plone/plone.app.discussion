# -*- coding: utf-8 -*-
import unittest2 as unittest
import time
from datetime import datetime

from AccessControl import Unauthorized

from OFS.Image import Image

from zope import interface
from zope.interface import alsoProvides
from zope.publisher.browser import TestRequest
from zope.annotation.interfaces import IAttributeAnnotatable
from z3c.form.interfaces import IFormLayer

from zope.component import provideAdapter
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.component import createObject, queryUtility

from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.tests import dummy

from plone.app.testing import TEST_USER_ID, setRoles
from plone.app.testing import logout
from plone.app.testing import login


from plone.app.discussion.browser.comments import CommentsViewlet
from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion import interfaces
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.testing import \
    PLONE_APP_DISCUSSION_INTEGRATION_TESTING
from plone.app.discussion.interfaces import IDiscussionSettings


class TestCommentForm(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']

        interface.alsoProvides(
            self.portal.REQUEST, interfaces.IDiscussionLayer)

        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
        self.discussionTool = getToolByName(self.portal,
                                   'portal_discussion',
                                    None)
        self.discussionTool.overrideDiscussionFor(self.portal.doc1, False)
        self.membershipTool = getToolByName(self.folder, 'portal_membership')
        self.memberdata = self.portal.portal_memberdata
        self.context = getattr(self.portal, 'doc1')

        # Allow discussion
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = True

    def test_add_comment(self):
        """Post a comment as logged-in user.
        """

        # Allow discussion
        self.discussionTool.overrideDiscussionFor(self.portal.doc1, True)
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
        data, errors = commentForm.extractData()  # pylint: disable-msg=W0612

        self.assertEqual(len(errors), 1)
        self.assertFalse(commentForm.handleComment(commentForm, "foo"))

        # The form is submitted successfully, if the required text field is
        # filled out
        request = make_request(form={'form.widgets.text': u'bar'})

        commentForm = getMultiAdapter((self.context, request),
                                      name=u"comment-form")
        commentForm.update()
        data, errors = commentForm.extractData()  # pylint: disable-msg=W0612

        self.assertEqual(len(errors), 0)
        self.assertFalse(commentForm.handleComment(commentForm, "foo"))

    def test_add_anonymous_comment(self):
        self.discussionTool.overrideDiscussionFor(self.portal.doc1, True)

        self.viewlet = CommentsViewlet(self.context, self.request, None, None)

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.anonymous_comments = True

        # Logout
        logout()

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

        # Post an anonymous comment and provide a name
        request = make_request(form={'form.widgets.name': u'john doe',
                                     'form.widgets.text': u'bar'})

        commentForm = getMultiAdapter((self.context, request),
                                      name=u"comment-form")
        commentForm.update()
        data, errors = commentForm.extractData()  # pylint: disable-msg=W0612

        self.assertEqual(len(errors), 0)
        self.assertFalse(commentForm.handleComment(commentForm, "action"))

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
        data, errors = commentForm.extractData()  # pylint: disable-msg=W0612

        # No form errors, but raise unauthorized because discussion is not
        # allowed
        self.assertEqual(len(errors), 0)
        self.assertRaises(Unauthorized,
                          commentForm.handleComment,
                          commentForm,
                          "foo")

    def test_anonymous_can_not_add_comments_if_discussion_is_not_allowed(self):
        """Make sure that anonymous users can't post comments if anonymous
           comments are disabled.
        """

        # Anonymous comments are disabled by default

        logout()

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
        data, errors = commentForm.extractData()  # pylint: disable-msg=W0612

        self.assertEqual(len(errors), 0)
        self.assertRaises(Unauthorized,
                          commentForm.handleComment,
                          commentForm,
                          "foo")


class TestCommentsViewlet(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        interface.alsoProvides(
            self.request, interfaces.IDiscussionLayer)

        self.workflowTool = getToolByName(self.portal, 'portal_workflow')
        self.workflowTool.setDefaultChain('one_state_workflow')

        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
        self.portal_discussion = getToolByName(self.portal,
                                               'portal_discussion',
                                               None)
        self.membershipTool = getToolByName(self.folder, 'portal_membership')
        self.memberdata = self.portal.portal_memberdata
        context = getattr(self.portal, 'doc1')
        self.viewlet = CommentsViewlet(context, self.request, None, None)

        # Allow discussion
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = True

    def test_can_reply(self):
        # Portal owner can reply
        self.assertTrue(self.viewlet.can_reply())
        logout()
        # Anonymous users can not reply
        self.assertFalse(self.viewlet.can_reply())

    def test_can_review(self):
        # Portal owner has 'can review' permission
        self.assertTrue(self.viewlet.can_review())
        logout()
        # Anonymous has no 'can review' permission
        self.assertFalse(self.viewlet.can_review())
        # The reviewer role has the 'Review comments' permission
        self.portal.acl_users._doAddUser(
            'reviewer', 'secret', ['Reviewer'], [])
        login(self.portal, 'reviewer')
        self.assertTrue(self.viewlet.can_review())

    def test_can_manage(self):
        """We keep this method for backward compatibility. This method has been
           removed in version 1.0b9 and added again in 1.0b11 because we don't
           do API changes in beta releases.
        """
        # Portal owner has 'can review' permission
        self.assertTrue(self.viewlet.can_manage())
        logout()
        # Anonymous has no 'can review' permission
        self.assertFalse(self.viewlet.can_manage())
        # The reviewer role has the 'Review comments' permission
        self.portal.acl_users._doAddUser(
            'reviewer', 'secret', ['Reviewer'], [])
        login(self.portal, 'reviewer')
        self.assertTrue(self.viewlet.can_manage())

    def test_is_discussion_allowed(self):
        # By default, discussion is disabled
        self.assertFalse(self.viewlet.is_discussion_allowed())
        # Enable discussion
        portal_discussion = getToolByName(self.portal, 'portal_discussion')
        portal_discussion.overrideDiscussionFor(self.portal.doc1, True)
        # Test if discussion has been enabled
        self.assertTrue(self.viewlet.is_discussion_allowed())

    def test_comment_transform_message(self):

        # Default transform is plain/text and comment moderation disabled
        self.assertTrue(self.viewlet.comment_transform_message())
        self.assertEqual(
            self.viewlet.comment_transform_message(),
            "You can add a comment by filling out the form below. Plain " +
            "text formatting.")

        # Set text transform to intelligent text
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.text_transform = "text/x-web-intelligent"

        # Make sure the comment description changes accordingly
        self.assertEqual(
            self.viewlet.comment_transform_message(),
            "You can add a comment by filling out the form below. " +
            "Plain text formatting. Web and email addresses are transformed " +
             "into clickable links.")

        # Enable moderation workflow
        self.workflowTool.setChainForPortalTypes(
            ('Discussion Item',),
            ('comment_review_workflow,'))

        # Make sure the comment description shows that comments are moderated
        self.assertEqual(
            self.viewlet.comment_transform_message(),
            "You can add a comment by filling out the form below. " +
            "Plain text formatting. Web and email addresses are transformed " +
            "into clickable links. Comments are moderated.")

    def test_has_replies(self):
        self.assertEqual(self.viewlet.has_replies(), False)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        conversation = IConversation(self.portal.doc1)
        conversation.addComment(comment)
        self.assertEqual(self.viewlet.has_replies(), True)

    def test_get_replies(self):
        self.assertFalse(self.viewlet.get_replies())
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        conversation = IConversation(self.portal.doc1)
        conversation.addComment(comment)
        conversation.addComment(comment)
        replies = self.viewlet.get_replies()
        self.assertEqual(len(tuple(replies)), 2)
        replies = self.viewlet.get_replies()
        replies.next()
        replies.next()
        self.assertRaises(StopIteration, replies.next)

    def test_get_replies_with_workflow_actions(self):
        self.assertFalse(self.viewlet.get_replies(workflow_actions=True))
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        conversation = IConversation(self.portal.doc1)
        c1 = conversation.addComment(comment)
        self.assertEqual(
            len(tuple(self.viewlet.get_replies(workflow_actions=True))), 1)
        # Enable moderation workflow
        self.workflowTool.setChainForPortalTypes(
            ('Discussion Item',),
            ('comment_review_workflow,'))
        # Check if workflow actions are available
        reply = self.viewlet.get_replies(workflow_actions=True).next()
        self.assertTrue('actions' in reply)
        self.assertEqual(reply['actions'][0]['id'],
                          'publish')
        self.assertEqual(reply['actions'][0]['url'],
            'http://nohost/plone/doc1/++conversation++default/%s' % int(c1) +
            '/content_status_modify?workflow_action=publish')

    def test_get_commenter_home_url(self):
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        IConversation(self.portal.doc1)
        portal_membership = getToolByName(self.portal, 'portal_membership')
        m = portal_membership.getAuthenticatedMember()
        self.assertEqual(self.viewlet.get_commenter_home_url(m.getUserName()),
                          'http://nohost/plone/author/test-user')

    def test_get_commenter_home_url_is_none(self):
        self.assertFalse(self.viewlet.get_commenter_home_url())

    def test_get_commenter_portrait(self):

        # Add a user with a member image
        self.membershipTool.addMember('jim', 'Jim', ['Member'], [])
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
        self.assertEqual(portrait_url,
            'http://nohost/plone/portal_memberdata/portraits/jim')

    def test_get_commenter_portrait_is_none(self):
        self.assertEqual(self.viewlet.get_commenter_portrait(),
                          'defaultUser.gif')

    def test_get_commenter_portrait_without_userimage(self):

        # Create a user without a user image
        self.membershipTool.addMember('jim', 'Jim', ['Member'], [])

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

        # Check if the correct default member image URL is returned.
        # Note that Products.PlonePAS 4.0.5 and later have .png and
        # earlier versions have .gif.
        self.assertTrue(portrait_url in
                        ('http://nohost/plone/defaultUser.png',
                         'http://nohost/plone/defaultUser.gif'))

    def test_anonymous_discussion_allowed(self):
        # Anonymous discussion is not allowed by default
        self.assertFalse(self.viewlet.anonymous_discussion_allowed())
        # Allow anonymous discussion
        registry = queryUtility(IRegistry)
        registry['plone.app.discussion.interfaces.IDiscussionSettings.' +
                  'anonymous_comments'] = True
        # Test if anonymous discussion is allowed for the viewlet
        self.assertTrue(self.viewlet.anonymous_discussion_allowed())

    def test_show_commenter_image(self):
        self.assertTrue(self.viewlet.show_commenter_image())
        registry = queryUtility(IRegistry)
        registry['plone.app.discussion.interfaces.IDiscussionSettings.' +
                 'show_commenter_image'] = False
        self.assertFalse(self.viewlet.show_commenter_image())

    def test_is_anonymous(self):
        self.assertFalse(self.viewlet.is_anonymous())
        logout()
        self.assertTrue(self.viewlet.is_anonymous())

    def test_login_action(self):
        self.viewlet.update()
        self.assertEqual(self.viewlet.login_action(),
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
        python_time = datetime(
            *time.gmtime(time.mktime(python_time.timetuple()))[:7])
        localized_time = self.viewlet.format_time(python_time)
        self.assertEqual(localized_time, "Feb 01, 2009 11:32 PM")


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
