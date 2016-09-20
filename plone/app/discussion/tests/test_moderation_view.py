# -*- coding: utf-8 -*-
from plone.app.discussion.browser.moderation import BulkActionsView
from plone.app.discussion.browser.moderation import DeleteComment
from plone.app.discussion.browser.moderation import PublishComment
from plone.app.discussion.browser.moderation import View
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.testing import PLONE_APP_DISCUSSION_INTEGRATION_TESTING  # noqa
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import createObject
from zope.component import queryUtility

import unittest


class ModerationViewTest(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal_discussion = getToolByName(self.portal,
                                               'portal_discussion',
                                               None)
        self.membership_tool = getToolByName(self.portal,
                                             'portal_membership')
        self.memberdata = self.portal.portal_memberdata
        request = self.app.REQUEST
        context = getattr(self.portal, 'doc1')
        self.view = View(context, request)
        self.view.__of__(context)
        self.portal.portal_workflow.setChainForPortalTypes(
            ('Discussion Item',), 'comment_review_workflow')
        self.wf_tool = self.portal.portal_workflow

    def test_moderation_enabled(self):
        """Make sure that moderation_enabled returns true if the comment
           workflow implements a 'pending' state.
        """
        # If workflow is not set, enabled must return False
        self.wf_tool.setChainForPortalTypes(('Discussion Item',), ())
        self.assertEqual(self.view.moderation_enabled(), False)
        # The one_state_workflow does not have a 'pending' state
        self.wf_tool.setChainForPortalTypes(('Discussion Item',),
                                            ('one_state_workflow,'))
        self.assertEqual(self.view.moderation_enabled(), False)
        # The comment_review_workflow does have a 'pending' state
        self.wf_tool.setChainForPortalTypes(('Discussion Item',),
                                            ('comment_review_workflow,'))
        self.assertEqual(self.view.moderation_enabled(), True)


class ModerationBulkActionsViewTest(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.wf = getToolByName(self.portal,
                                'portal_workflow',
                                None)
        self.context = self.portal
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
        self.comment1 = self.portal.doc1.restrictedTraverse(
            '++conversation++default/{0}'.format(new_id_1)
        )
        comment2 = createObject('plone.Comment')
        comment2.title = 'Comment 2'
        comment2.text = 'Comment text'
        comment2.Creator = 'Joe'
        new_id_2 = conversation.addComment(comment2)
        self.comment2 = self.portal.doc1.restrictedTraverse(
            '++conversation++default/{0}'.format(new_id_2)
        )
        comment3 = createObject('plone.Comment')
        comment3.title = 'Comment 3'
        comment3.text = 'Comment text'
        comment3.Creator = 'Emma'
        new_id_3 = conversation.addComment(comment3)
        self.comment3 = self.portal.doc1.restrictedTraverse(
            '++conversation++default/{0}'.format(new_id_3)
        )
        self.conversation = conversation

    def test_default_bulkaction(self):
        # Make sure no error is raised when no bulk actions has been supplied
        self.request.set('form.select.BulkAction', '-1')
        self.request.set('paths', ['/'.join(self.comment1.getPhysicalPath())])

        view = BulkActionsView(self.portal, self.request)

        self.assertFalse(view())

    def test_retract(self):
        self.request.set('form.select.BulkAction', 'retract')
        self.request.set('paths', ['/'.join(self.comment1.getPhysicalPath())])

        view = BulkActionsView(self.portal, self.request)

        self.assertRaises(NotImplementedError,
                          view)

    def test_publish(self):
        self.request.set('form.select.BulkAction', 'publish')
        self.request.set('paths', ['/'.join(self.comment1.getPhysicalPath())])
        view = BulkActionsView(self.portal, self.request)

        view()

        # Count published comments
        published_comments = 0
        for r in self.conversation.getThreads():
            comment_obj = r['comment']
            workflow_status = self.wf.getInfoFor(comment_obj, 'review_state')
            if workflow_status == 'published':
                published_comments += 1
        # Make sure the comment has been published
        self.assertEqual(published_comments, 1)

    def test_mark_as_spam(self):
        self.request.set('form.select.BulkAction', 'mark_as_spam')
        self.request.set('paths', ['/'.join(self.comment1.getPhysicalPath())])

        view = BulkActionsView(self.portal, self.request)

        self.assertRaises(NotImplementedError,
                          view)

    def test_delete(self):
        # Initially we have three comments
        self.assertEqual(len(self.conversation.objectIds()), 3)
        # Delete two comments with bulk actions
        self.request.set('form.select.BulkAction', 'delete')
        self.request.set('paths', ['/'.join(self.comment1.getPhysicalPath()),
                                   '/'.join(self.comment3.getPhysicalPath())])
        view = BulkActionsView(self.app, self.request)

        view()

        # Make sure that the two comments have been deleted
        self.assertEqual(len(self.conversation.objectIds()), 1)
        comment = self.conversation.getComments().next()
        self.assertTrue(comment)
        self.assertEqual(comment, self.comment2)


class RedirectionTest(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        # Update settings.
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        # applyProfile(self.portal, 'plone.app.discussion:default')
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = True
        self.portal.portal_workflow.setChainForPortalTypes(
            ('Discussion Item',),
            ('comment_review_workflow',))
        # Create page plus comment.
        self.portal.invokeFactory(
            id='page',
            title='Page 1',
            type_name='Document'
        )
        self.page = self.portal.page
        self.conversation = IConversation(self.page)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        self.comment_id = self.conversation.addComment(comment)
        self.comment = list(self.conversation.getComments())[0]

    def test_regression(self):
        page_url = self.page.absolute_url()
        self.request['HTTP_REFERER'] = page_url
        for Klass in (DeleteComment, PublishComment):
            view = Klass(self.comment, self.request)
            view.__parent__ = self.comment
            self.assertEqual(page_url, view())

    def test_valid_next_url(self):
        self.request['HTTP_REFERER'] = 'http://attacker.com'
        for Klass in (DeleteComment, PublishComment):
            view = Klass(self.comment, self.request)
            view.__parent__ = self.comment
            self.assertNotEqual('http://attacker.com', view())
