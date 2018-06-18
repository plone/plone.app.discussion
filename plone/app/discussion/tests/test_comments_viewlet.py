# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from datetime import datetime
from OFS.Image import Image
from plone.app.discussion import interfaces
from plone.app.discussion.browser.comment import EditCommentForm
from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion.browser.comments import CommentsViewlet
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.testing import PLONE_APP_DISCUSSION_INTEGRATION_TESTING  # noqa
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests import dummy
from z3c.form.interfaces import IFormLayer
from zope import interface
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import createObject
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest

import time
import unittest


class TestCommentForm(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']

        interface.alsoProvides(
            self.portal.REQUEST,
            interfaces.IDiscussionLayer,
        )

        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.doActionFor(self.portal.doc1, action='publish')
        self.portal.doc1.allow_discussion = True
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
        self.portal.doc1.allow_discussion = True
        self.viewlet = CommentsViewlet(self.context, self.request, None, None)

        def make_request(form={}):
            request = TestRequest()
            request.form.update(form)
            alsoProvides(request, IFormLayer)
            alsoProvides(request, IAttributeAnnotatable)
            return request

        provideAdapter(
            adapts=(Interface, IBrowserRequest),
            provides=Interface,
            factory=CommentForm,
            name=u'comment-form',
        )

        # The form should return an error if the comment text field is empty
        request = make_request(form={})

        commentForm = getMultiAdapter(
            (self.context, request),
            name=u'comment-form',
        )
        commentForm.update()
        data, errors = commentForm.extractData()  # pylint: disable-msg=W0612

        self.assertEqual(len(errors), 1)
        self.assertFalse(commentForm.handleComment(commentForm, 'foo'))

        # The form is submitted successfully, if the required text field is
        # filled out
        request = make_request(form={'form.widgets.text': u'bar'})

        commentForm = getMultiAdapter(
            (self.context, request),
            name=u'comment-form',
        )
        commentForm.update()
        data, errors = commentForm.extractData()  # pylint: disable-msg=W0612

        self.assertEqual(len(errors), 0)
        self.assertFalse(commentForm.handleComment(commentForm, 'foo'))

        comments = IConversation(commentForm.context).getComments()
        comments = [comment for comment in comments]  # consume iterator
        self.assertEqual(len(comments), 1)

        for comment in comments:
            self.assertEqual(comment.text, u'bar')
            self.assertEqual(comment.creator, 'test_user_1_')
            self.assertEqual(comment.getOwner().getUserName(), 'test-user')
            local_roles = comment.get_local_roles()
            self.assertEqual(len(local_roles), 1)
            userid, roles = local_roles[0]
            self.assertEqual(userid, 'test_user_1_')
            self.assertEqual(len(roles), 1)
            self.assertEqual(roles[0], 'Owner')

    def test_edit_comment(self):
        """Edit a comment as logged-in user.
        """

        # Allow discussion
        self.portal.doc1.allow_discussion = True
        self.viewlet = CommentsViewlet(self.context, self.request, None, None)

        def make_request(form={}):
            request = TestRequest()
            request.form.update(form)
            alsoProvides(request, IFormLayer)
            alsoProvides(request, IAttributeAnnotatable)
            return request

        provideAdapter(
            adapts=(Interface, IBrowserRequest),
            provides=Interface,
            factory=CommentForm,
            name=u'comment-form',
        )

        provideAdapter(
            adapts=(Interface, IBrowserRequest),
            provides=Interface,
            factory=EditCommentForm,
            name=u'edit-comment-form',
        )

        # The form is submitted successfully, if the required text field is
        # filled out
        request = make_request(form={'form.widgets.text': u'bar'})

        commentForm = getMultiAdapter(
            (self.context, request),
            name=u'comment-form',
        )
        commentForm.update()
        data, errors = commentForm.extractData()  # pylint: disable-msg=W0612

        self.assertEqual(len(errors), 0)
        self.assertFalse(commentForm.handleComment(commentForm, 'foo'))

        # Edit the last comment
        conversation = IConversation(self.context)
        comment = [x for x in conversation.getComments()][-1]
        request = make_request(form={'form.widgets.text': u'foobar'})
        editForm = getMultiAdapter(
            (comment, request),
            name=u'edit-comment-form',
        )
        editForm.update()
        data, errors = editForm.extractData()  # pylint: disable-msg=W0612

        self.assertEqual(len(errors), 0)
        self.assertFalse(editForm.handleComment(editForm, 'foo'))
        comment = [x for x in conversation.getComments()][-1]
        self.assertEqual(comment.text, u'foobar')

        comments = IConversation(commentForm.context).getComments()
        comments = [c for c in comments]  # consume iterator
        self.assertEqual(len(comments), 1)

        for comment in comments:
            self.assertEqual(comment.text, u'foobar')
            self.assertEqual(comment.creator, 'test_user_1_')

            self.assertEqual(comment.getOwner().getUserName(), 'test-user')
            local_roles = comment.get_local_roles()
            self.assertEqual(len(local_roles), 1)
            userid, roles = local_roles[0]
            self.assertEqual(userid, 'test_user_1_')
            self.assertEqual(len(roles), 1)
            self.assertEqual(roles[0], 'Owner')

    def test_delete_comment(self):
        """Delete a comment as logged-in user.
        """

        # Allow discussion
        self.portal.doc1.allow_discussion = True
        self.viewlet = CommentsViewlet(self.context, self.request, None, None)

        def make_request(form={}):
            request = TestRequest()
            request.form.update(form)
            alsoProvides(request, IFormLayer)
            alsoProvides(request, IAttributeAnnotatable)
            return request

        provideAdapter(
            adapts=(Interface, IBrowserRequest),
            provides=Interface,
            factory=CommentForm,
            name=u'comment-form',
        )

        # The form is submitted successfully, if the required text field is
        # filled out
        form_request = make_request(form={'form.widgets.text': u'bar'})

        commentForm = getMultiAdapter(
            (self.context, form_request),
            name=u'comment-form',
        )

        commentForm.update()
        data, errors = commentForm.extractData()  # pylint: disable-msg=W0612
        self.assertEqual(len(errors), 0)
        self.assertFalse(commentForm.handleComment(commentForm, 'foo'))

        # Delete the last comment
        conversation = IConversation(self.context)
        comment = [x for x in conversation.getComments()][-1]
        deleteView = getMultiAdapter(
            (comment, self.request),
            name=u'moderate-delete-comment',
        )
        # try to delete last comment without 'Delete comments' permission
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.assertRaises(
            Unauthorized,
            comment.restrictedTraverse,
            '@@moderate-delete-comment',
        )
        deleteView()
        self.assertEqual(1, len([x for x in conversation.getComments()]))
        # try to delete last comment with 'Delete comments' permission
        setRoles(self.portal, TEST_USER_ID, ['Reviewer'])
        deleteView()
        self.assertEqual(0, len([x for x in conversation.getComments()]))
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_delete_own_comment(self):
        """Delete own comment as logged-in user.
        """

        # Allow discussion
        self.portal.doc1.allow_discussion = True
        self.viewlet = CommentsViewlet(self.context, self.request, None, None)

        def make_request(form={}):
            request = TestRequest()
            request.form.update(form)
            alsoProvides(request, IFormLayer)
            alsoProvides(request, IAttributeAnnotatable)
            return request

        provideAdapter(
            adapts=(Interface, IBrowserRequest),
            provides=Interface,
            factory=CommentForm,
            name=u'comment-form',
        )

        # The form is submitted successfully, if the required text field is
        # filled out
        form_request = make_request(form={'form.widgets.text': u'bar'})

        commentForm = getMultiAdapter(
            (self.context, form_request),
            name=u'comment-form',
        )

        commentForm.update()
        data, errors = commentForm.extractData()  # pylint: disable-msg=W0612
        self.assertEqual(len(errors), 0)
        self.assertFalse(commentForm.handleComment(commentForm, 'foo'))

        # Delete the last comment
        conversation = IConversation(self.context)
        comment = [x for x in conversation.getComments()][-1]
        deleteView = getMultiAdapter(
            (comment, self.request),
            name=u'delete-own-comment',
        )
        # try to delete last comment with johndoe
        setRoles(self.portal, 'johndoe', ['Member'])
        login(self.portal, 'johndoe')
        self.assertRaises(
            Unauthorized,
            comment.restrictedTraverse,
            '@@delete-own-comment',
        )
        self.assertEqual(1, len([x for x in conversation.getComments()]))
        # try to delete last comment with the same user that created it
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        deleteView()
        self.assertEqual(0, len([x for x in conversation.getComments()]))

    def test_add_anonymous_comment(self):
        self.portal.doc1.allow_discussion = True

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
                       name=u'comment-form')

        # Post an anonymous comment and provide a name
        request = make_request(form={
            'form.widgets.name': u'john doe',
            'form.widgets.text': u'bar',
        })

        commentForm = getMultiAdapter(
            (self.context, request),
            name=u'comment-form',
        )
        commentForm.update()
        data, errors = commentForm.extractData()  # pylint: disable-msg=W0612

        self.assertEqual(len(errors), 0)
        self.assertFalse(commentForm.handleComment(commentForm, 'action'))

        comments = IConversation(commentForm.context).getComments()
        comments = [comment for comment in comments]  # consume itertor
        self.assertEqual(len(comments), 1)

        for comment in IConversation(commentForm.context).getComments():
            self.assertEqual(comment.text, u'bar')
            self.assertIsNone(comment.creator)
            roles = comment.get_local_roles()
            self.assertEqual(len(roles), 0)

    def test_can_not_add_comments_if_discussion_is_not_allowed(self):
        """Make sure that comments can't be posted if discussion is disabled.
        """

        # Disable discussion
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = False

        def make_request(form={}):
            request = TestRequest()
            request.form.update(form)
            alsoProvides(request, IFormLayer)
            alsoProvides(request, IAttributeAnnotatable)
            return request

        provideAdapter(adapts=(Interface, IBrowserRequest),
                       provides=Interface,
                       factory=CommentForm,
                       name=u'comment-form')

        request = make_request(form={'form.widgets.text': u'bar'})

        commentForm = getMultiAdapter(
            (self.context, request),
            name=u'comment-form',
        )
        commentForm.update()
        data, errors = commentForm.extractData()  # pylint: disable-msg=W0612

        # No form errors, but raise unauthorized because discussion is not
        # allowed
        self.assertEqual(len(errors), 0)

        self.assertRaises(Unauthorized,
                          commentForm.handleComment,
                          commentForm,
                          'foo')

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
                       name=u'comment-form')

        request = make_request(form={'form.widgets.text': u'bar'})

        commentForm = getMultiAdapter((self.context, request),
                                      name=u'comment-form')
        commentForm.update()
        data, errors = commentForm.extractData()  # pylint: disable-msg=W0612

        self.assertEqual(len(errors), 0)
        self.assertRaises(
            Unauthorized,
            commentForm.handleComment,
            commentForm,
            'foo',
        )


class TestCommentsViewlet(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        interface.alsoProvides(
            self.request,
            interfaces.IDiscussionLayer,
        )

        self.workflowTool = getToolByName(self.portal, 'portal_workflow')
        self.workflowTool.setDefaultChain('comment_one_state_workflow')

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
        self.portal.doc1.allow_discussion = True
        # Test if discussion has been enabled
        self.assertTrue(self.viewlet.is_discussion_allowed())

    def test_comment_transform_message(self):

        # Default transform is plain/text and comment moderation disabled
        self.assertTrue(self.viewlet.comment_transform_message())
        self.assertEqual(
            self.viewlet.comment_transform_message(),
            'You can add a comment by filling out the form below. Plain ' +
            'text formatting.')

        # Set text transform to intelligent text
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.text_transform = 'text/x-web-intelligent'

        # Make sure the comment description changes accordingly
        self.assertEqual(
            self.viewlet.comment_transform_message(),
            'You can add a comment by filling out the form below. ' +
            'Plain text formatting. Web and email addresses are transformed ' +
            'into clickable links.',
        )

        # Enable moderation workflow
        self.workflowTool.setChainForPortalTypes(
            ('Discussion Item',),
            ('comment_review_workflow,'))

        # Make sure the comment description shows that comments are moderated
        self.assertEqual(
            self.viewlet.comment_transform_message(),
            'You can add a comment by filling out the form below. ' +
            'Plain text formatting. Web and email addresses are transformed ' +
            'into clickable links. Comments are moderated.')

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
        next(replies)
        next(replies)
        self.assertRaises(StopIteration, replies.next)

    def test_get_replies_on_non_annotatable_object(self):
        context = self.portal.MailHost      # the mail host is not annotatable
        viewlet = CommentsViewlet(context, self.request, None, None)
        replies = viewlet.get_replies()
        self.assertEqual(len(tuple(replies)), 0)
        replies = viewlet.get_replies()
        self.assertRaises(StopIteration, replies.next)

    def test_get_replies_with_workflow_actions(self):
        self.assertFalse(self.viewlet.get_replies(workflow_actions=True))
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        conversation = IConversation(self.portal.doc1)
        c1 = conversation.addComment(comment)
        self.assertEqual(
            len(tuple(self.viewlet.get_replies(workflow_actions=True))),
            1,
        )
        # Enable moderation workflow
        self.workflowTool.setChainForPortalTypes(
            ('Discussion Item',),
            ('comment_review_workflow,'),
        )
        # Check if workflow actions are available
        reply = next(self.viewlet.get_replies(workflow_actions=True))
        self.assertTrue('actions' in reply)
        self.assertEqual(
            reply['actions'][0]['id'],
            'publish',
        )
        expected_url = 'http://nohost/plone/doc1/++conversation++default/{0}' \
                       '/content_status_modify?workflow_action=publish'
        self.assertEqual(
            reply['actions'][0]['url'],
            expected_url.format(int(c1)),
        )

    def test_get_commenter_home_url(self):
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        IConversation(self.portal.doc1)
        portal_membership = getToolByName(self.portal, 'portal_membership')
        m = portal_membership.getAuthenticatedMember()
        self.assertEqual(
            self.viewlet.get_commenter_home_url(m.getUserName()),
            'http://nohost/plone/author/test-user',
        )

    def test_get_commenter_home_url_is_none(self):
        self.assertFalse(self.viewlet.get_commenter_home_url())

    def test_get_commenter_portrait(self):

        # Add a user with a member image
        self.membershipTool.addMember('jim', 'Jim', ['Member'], [])
        self.memberdata._setPortrait(Image(
            id='jim',
            file=dummy.File(),
            title='',
        ), 'jim')
        self.assertEqual(
            self.memberdata._getPortrait('jim').getId(),
            'jim',
        )
        self.assertEqual(
            self.memberdata._getPortrait('jim').meta_type,
            'Image',
        )

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
        self.assertEqual(
            portrait_url,
            'http://nohost/plone/portal_memberdata/portraits/jim',
        )

    def test_get_commenter_portrait_is_none(self):

        self.assertTrue(
            self.viewlet.get_commenter_portrait() in (
                'defaultUser.png',
                'defaultUser.gif',
            ),
        )

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
        self.assertTrue(
            portrait_url in (
                'http://nohost/plone/defaultUser.png',
                'http://nohost/plone/defaultUser.gif',
            ),
        )

    def test_anonymous_discussion_allowed(self):
        # Anonymous discussion is not allowed by default
        self.assertFalse(self.viewlet.anonymous_discussion_allowed())
        # Allow anonymous discussion
        registry = queryUtility(IRegistry)
        registry[
            'plone.app.discussion.interfaces.IDiscussionSettings.' +
            'anonymous_comments'
        ] = True
        # Test if anonymous discussion is allowed for the viewlet
        self.assertTrue(self.viewlet.anonymous_discussion_allowed())

    def test_show_commenter_image(self):
        self.assertTrue(self.viewlet.show_commenter_image())
        registry = queryUtility(IRegistry)
        registry[
            'plone.app.discussion.interfaces.IDiscussionSettings.' +
            'show_commenter_image'
        ] = False
        self.assertFalse(self.viewlet.show_commenter_image())

    def test_is_anonymous(self):
        self.assertFalse(self.viewlet.is_anonymous())
        logout()
        self.assertTrue(self.viewlet.is_anonymous())

    def test_login_action(self):
        self.viewlet.update()
        self.assertEqual(
            self.viewlet.login_action(),
            'http://nohost/plone/login_form?came_from=http%3A//nohost',
        )

    def test_format_time(self):
        python_time = datetime(2009, 2, 1, 23, 32, 3, 57)
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
        self.assertTrue(
            localized_time in ['Feb 01, 2009 11:32 PM', '2009-02-01 23:32'],
        )
