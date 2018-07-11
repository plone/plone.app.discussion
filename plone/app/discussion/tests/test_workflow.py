# -*- coding: utf-8 -*-
"""Test plone.app.discussion workflow and permissions.
"""
from AccessControl import Unauthorized
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionLayer
from plone.app.discussion.testing import PLONE_APP_DISCUSSION_INTEGRATION_TESTING  # noqa
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import _checkPermission as checkPerm
from zope.component import createObject
from zope.interface import alsoProvides

import unittest


class WorkflowSetupTest(unittest.TestCase):
    """Make sure the workflows are set up properly.
    """

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.portal.portal_types['Document'].allow_discussion = True
        self.folder.invokeFactory('Document', 'doc1')
        self.doc = self.folder.doc1

    def test_workflows_installed(self):
        """Make sure both comment workflows have been installed properly.
        """
        self.assertTrue('comment_one_state_workflow' in
                        self.portal.portal_workflow.objectIds())
        self.assertTrue('comment_review_workflow' in
                        self.portal.portal_workflow.objectIds())

    def test_default_workflow(self):
        """Make sure one_state_workflow is the default workflow.
        """
        self.assertEqual(
            ('comment_one_state_workflow',),
            self.portal.portal_workflow.getChainForPortalType(
                'Discussion Item',
            ),
        )

    def test_review_comments_permission(self):
        # 'Review comments' in self.portal.permissionsOfRole('Admin')

        setRoles(self.portal, TEST_USER_ID, ['Reviewer'])
        self.assertTrue(self.portal.portal_membership.checkPermission(
                        'Review comments', self.folder), self.folder)
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.assertFalse(
            self.portal.portal_membership.checkPermission(
                'Review comments',
                self.folder,
            ),
            self.folder,
        )

    def test_reply_to_item_permission(self):
        pass


class PermissionsSetupTest(unittest.TestCase):
    """Make sure the permissions are set up properly.
    """

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        mtool = self.portal.portal_membership
        self.checkPermission = mtool.checkPermission

    def test_reply_to_item_permission_assigned(self):
        """Make sure the 'Reply to item' permission is properly assigned.
           By default this permission is assigned to 'Member' and 'Manager'.
           plone.app.discussion assigns this permission to 'Authenticated' as
           well to emulate the behavior of the old commenting system.
        """
        ReplyToItemPerm = 'Reply to item'
        # should be allowed as Member
        self.assertTrue(self.checkPermission(ReplyToItemPerm, self.portal))
        # should be allowed as Authenticated
        setRoles(self.portal, TEST_USER_ID, ['Authenticated'])
        self.assertTrue(self.checkPermission(ReplyToItemPerm, self.portal))
        # should be allowed as Manager
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.assertTrue(self.checkPermission(ReplyToItemPerm, self.portal))
        # should not be allowed as anonymous
        logout()
        self.assertFalse(self.checkPermission(ReplyToItemPerm, self.portal))


class CommentOneStateWorkflowTest(unittest.TestCase):
    """Test the comment_one_state_workflow that ships with plone.app.discussion.
    """

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.folder.invokeFactory('Document', 'doc1')
        self.doc = self.folder.doc1

        # Add a comment
        conversation = IConversation(self.folder.doc1)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        cid = conversation.addComment(comment)

        self.comment = self.folder.doc1.restrictedTraverse(
            '++conversation++default/{0}'.format(cid),
        )

        self.portal.acl_users._doAddUser('member', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser(
            'reviewer', 'secret', ['Reviewer'], [])
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])
        self.portal.acl_users._doAddUser('editor', ' secret', ['Editor'], [])
        self.portal.acl_users._doAddUser('reader', 'secret', ['Reader'], [])

    def test_initial_workflow_state(self):
        """Make sure the initial workflow state of a comment is 'private'.
        """
        self.assertEqual(
            self.workflow.getInfoFor(self.doc, 'review_state'),
            'private',
        )

    def test_view_comments(self):
        """Make sure published comments can be viewed by everyone.
        """
        # Owner is allowed
        # self.login(default_user)
        # self.assertTrue(checkPerm(View, self.doc))
        # Member is allowed
        login(self.portal, TEST_USER_NAME)
        workflow = self.portal.portal_workflow
        workflow.doActionFor(self.doc, 'publish')

        login(self.portal, 'member')
        self.assertTrue(checkPerm(View, self.comment))
        # Reviewer is allowed
        login(self.portal, 'reviewer')
        self.assertTrue(checkPerm(View, self.comment))
        # Anonymous is allowed
        logout()
        self.assertTrue(checkPerm(View, self.comment))
        # Editor is allowed
        login(self.portal, 'editor')
        self.assertTrue(checkPerm(View, self.comment))
        # Reader is allowed
        login(self.portal, 'reader')
        self.assertTrue(checkPerm(View, self.comment))

    def test_comment_on_private_content_not_visible_to_world(self):
        logout()
        self.assertFalse(checkPerm(View, self.comment))

    def test_migration(self):
        from plone.app.discussion.upgrades import upgrade_comment_workflows
        # Fake permission according to earlier one_comment_workflow.
        self.comment._View_Permission = ('Anonymous',)
        # Anonymous can see the comment.
        logout()
        self.assertTrue(checkPerm(View, self.comment))
        # Run the upgrade.
        login(self.portal, TEST_USER_NAME)
        upgrade_comment_workflows(self.portal.portal_setup)
        # The workflow chain is still what we want.
        self.assertEqual(
            self.portal.portal_workflow.getChainFor('Discussion Item'),
            ('comment_one_state_workflow',),
        )
        # A Manager can still see the comment.
        self.assertTrue(checkPerm(View, self.comment))
        # Anonymous cannot see the comment.
        logout()
        self.assertFalse(checkPerm(View, self.comment))


class CommentReviewWorkflowTest(unittest.TestCase):
    """Test the comment_review_workflow that ships with plone.app.discussion.
    """

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']

        # Allow discussion on the Document content type
        self.portal.portal_types['Document'].allow_discussion = True
        # Set workflow for Discussion item to review workflow
        self.portal.portal_workflow.setChainForPortalTypes(
            ('Discussion Item',),
            ('comment_review_workflow',),
        )

        # Create a conversation for this Document
        conversation = IConversation(self.portal.doc1)

        # Add a comment.
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment_id = conversation.addComment(comment)
        comment = self.portal.doc1.restrictedTraverse(
            '++conversation++default/{0}'.format(comment_id),
        )

        self.conversation = conversation
        self.comment_id = comment_id
        self.comment = comment

        setRoles(self.portal, TEST_USER_ID, ['Reviewer'])
        alsoProvides(self.portal.REQUEST, IDiscussionLayer)

    def test_delete(self):
        self.portal.REQUEST.form['comment_id'] = self.comment_id
        view = self.comment.restrictedTraverse('@@moderate-delete-comment')
        view()
        self.assertFalse(self.comment_id in self.conversation.objectIds())

    def test_delete_as_anonymous(self):
        # Make sure that anonymous users can not delete comments
        logout()
        self.portal.REQUEST.form['comment_id'] = self.comment_id
        self.assertRaises(
            Unauthorized,
            self.comment.restrictedTraverse,
            '@@moderate-delete-comment',
        )
        self.assertTrue(self.comment_id in self.conversation.objectIds())

    def test_delete_as_user(self):
        # Make sure that members can not delete comments
        logout()
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.portal.REQUEST.form['comment_id'] = self.comment_id
        self.assertRaises(
            Unauthorized,
            self.comment.restrictedTraverse,
            '@@moderate-delete-comment',
        )
        self.assertTrue(self.comment_id in self.conversation.objectIds())

    def test_publish(self):
        self.portal.REQUEST.form['comment_id'] = self.comment_id
        self.portal.REQUEST.form['workflow_action'] = 'publish'
        self.assertEqual(
            'pending',
            self.portal.portal_workflow.getInfoFor(
                self.comment,
                'review_state',
            ),
        )
        view = self.comment.restrictedTraverse('@@moderate-publish-comment')
        view()
        self.assertEqual(
            'published',
            self.portal.portal_workflow.getInfoFor(
                self.comment,
                'review_state',
            ),
        )

    def test_publish_as_anonymous(self):
        logout()
        self.portal.REQUEST.form['comment_id'] = self.comment_id
        self.portal.REQUEST.form['workflow_action'] = 'publish'
        self.assertEqual(
            'pending', self.portal.portal_workflow.getInfoFor(
                self.comment,
                'review_state',
            ),
        )
        self.assertRaises(
            Unauthorized,
            self.comment.restrictedTraverse,
            '@@moderate-publish-comment',
        )
        self.assertEqual(
            'pending',
            self.portal.portal_workflow.getInfoFor(
                self.comment,
                'review_state',
            ),
        )

    def test_publish_comment_on_private_content_not_visible_to_world(self):
        logout()
        self.assertFalse(checkPerm(View, self.comment))

        # publish comment and check again
        login(self.portal, TEST_USER_NAME)
        workflow = self.portal.portal_workflow
        workflow.doActionFor(self.comment, 'publish')

        logout()
        self.assertFalse(checkPerm(View, self.comment))

    def test_migration(self):
        from plone.app.discussion.upgrades import upgrade_comment_workflows
        # Fake permission according to earlier comment_review_workflow.
        self.comment._View_Permission = ('Anonymous',)
        # Anonymous can see the comment.
        logout()
        self.assertTrue(checkPerm(View, self.comment))
        # Run the upgrade.
        login(self.portal, TEST_USER_NAME)
        upgrade_comment_workflows(self.portal.portal_setup)
        # The workflow chain is still what we want.
        self.assertEqual(
            self.portal.portal_workflow.getChainFor('Discussion Item'),
            ('comment_review_workflow',))
        # A Manager can still see the comment.
        self.assertTrue(checkPerm(View, self.comment))
        # Anonymous cannot see the comment.
        logout()
        self.assertFalse(checkPerm(View, self.comment))
