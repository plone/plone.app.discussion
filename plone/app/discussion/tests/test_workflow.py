# -*- coding: utf-8 -*-
"""Test plone.app.discussion workflow and permissions.
"""
import unittest

from zope.component import createObject

from zope.interface import alsoProvides

from AccessControl import Unauthorized

from Products.CMFCore.utils import _checkPermission as checkPerm
from Products.CMFCore.permissions import View

from Products.PloneTestCase.ptc import PloneTestCase

from plone.app.discussion.tests.layer import DiscussionLayer
from plone.app.discussion.interfaces import IConversation, IDiscussionLayer


class WorkflowSetupTest(PloneTestCase):
    """Make sure the workflows are set up properly.
    """

    layer = DiscussionLayer

    def afterSetUp(self):
        """Create a document and allow discussion.
        """
        self.portal.portal_types['Document'].allow_discussion = True
        self.portal_discussion = self.portal.portal_discussion
        self.folder.invokeFactory('Document', 'doc1')
        self.doc = self.folder.doc1

    def test_workflows_installed(self):
        """Make sure both comment workflows have been installed properly.
        """
        self.failUnless('one_state_workflow' in
                        self.portal.portal_workflow.objectIds())
        self.failUnless('comment_review_workflow' in
                        self.portal.portal_workflow.objectIds())

    def test_default_workflow(self):
        """Make sure one_state_workflow is the default workflow.
        """
        self.assertEquals(('one_state_workflow',),
                          self.portal.portal_workflow.getChainForPortalType(
                              'Discussion Item'))

    def test_review_comments_permission(self):
        #'Review comments' in self.portal.permissionsOfRole('Admin')

        self.setRoles(('Reviewer',))
        self.failUnless(self.portal.portal_membership.checkPermission(
                        'Review comments', self.folder), self.folder)
        self.setRoles(('Member',))
        self.failIf(self.portal.portal_membership.checkPermission(
                    'Review comments', self.folder), self.folder)

    def test_reply_to_item_permission(self):
        pass

class PermissionsSetupTest(PloneTestCase):
    """Make sure the permissions are set up properly.
    """

    layer = DiscussionLayer

    def afterSetUp(self):
        portal = self.portal
        mtool = self.portal.portal_membership
        self.checkPermission = mtool.checkPermission

    def test_reply_to_item_permission_assigned(self):
        """Make sure the 'Reply to item' permission is properly assigned.
           By default this permission is assigned to 'Member' and 'Manager'.
           plone.app.discussion assigns this permission to 'Authenticated' as
           well to emulate the behavior of the old commenting system.
        """
        ReplyToItemPerm = "Reply to item"
        # should be allowed as Member
        self.failUnless(self.checkPermission(ReplyToItemPerm, self.portal))
        # should be allowed as Authenticated
        self.setRoles(['Authenticated'])
        self.failUnless(self.checkPermission(ReplyToItemPerm, self.portal))
        # should be allowed as Manager
        self.setRoles(['Manager'])
        self.failUnless(self.checkPermission(ReplyToItemPerm, self.portal))
        # should not be allowed as anonymous
        self.logout()
        self.failIf(self.checkPermission(ReplyToItemPerm, self.portal))


class CommentOneStateWorkflowTest(PloneTestCase):
    """Test the one_state_workflow that ships with plone.app.discussion.
    """

    layer = DiscussionLayer

    def afterSetUp(self):
        """Create a document with comments and enable the one.
        """
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.workflow.setChainForPortalTypes(['Document'],
                                             'one_state_workflow')
        self.folder.invokeFactory('Document', 'doc1')
        self.doc = self.folder.doc1

        # Add a comment
        conversation = IConversation(self.folder.doc1)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        cid = conversation.addComment(comment)

        self.comment = self.folder.doc1.restrictedTraverse(\
                            '++conversation++default/%s' % cid)

        self.portal.acl_users._doAddUser('member', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('reviewer', 'secret', ['Reviewer'], [])
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])
        self.portal.acl_users._doAddUser('editor' , ' secret', ['Editor'],[])
        self.portal.acl_users._doAddUser('reader', 'secret', ['Reader'], [])

    def test_initial_workflow_state(self):
        """Make sure the initial workflow state of a comment is 'published'.
        """
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'),
                         'published')

    def test_view_comments(self):
        """Make sure published comments can be viewed by everyone.
        """
        # Owner is allowed
        #self.login(default_user)
        #self.failUnless(checkPerm(View, self.doc))
        # Member is allowed
        self.login('member')
        self.failUnless(checkPerm(View, self.comment))
        # Reviewer is allowed
        self.login('reviewer')
        self.failUnless(checkPerm(View, self.comment))
        # Anonymous is allowed
        self.logout()
        self.failUnless(checkPerm(View, self.comment))
        # Editor is allowed
        self.login('editor')
        self.failUnless(checkPerm(View, self.comment))
        # Reader is allowed
        self.login('reader')
        self.failUnless(checkPerm(View, self.comment))


class CommentReviewWorkflowTest(PloneTestCase):
    """Test the comment_review_workflow that ships with plone.app.discussion.
    """

    layer = DiscussionLayer

    def afterSetUp(self):
        # Allow discussion and
        self.loginAsPortalOwner()

        # Allow discussion on the Document content type
        self.portal.portal_types['Document'].allow_discussion = True
        # Set workflow for Discussion item to review workflow
        self.portal.portal_workflow.setChainForPortalTypes(
            ('Discussion Item',),
            ('comment_review_workflow',))

        # Create a Document
        self.portal.invokeFactory('Document', 'doc1')
        self.portal_discussion = self.portal.portal_discussion

        # Create a conversation for this Document
        conversation = IConversation(self.portal.doc1)

        # Add a comment.
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment_id = conversation.addComment(comment)
        comment = self.portal.doc1.restrictedTraverse(
            '++conversation++default/%s' % comment_id)

        self.conversation = conversation
        self.comment_id = comment_id
        self.comment = comment

        self.setRoles(('Reviewer',))
        alsoProvides(self.portal.REQUEST, IDiscussionLayer)

    def test_delete(self):
        self.portal.REQUEST.form['comment_id'] = self.comment_id
        view = self.comment.restrictedTraverse('@@moderate-delete-comment')
        view()
        self.failIf(self.comment_id in self.conversation.objectIds())

    def test_delete_as_anonymous(self):
        # Make sure that anonymous users can not delete comments
        self.logout()
        self.portal.REQUEST.form['comment_id'] = self.comment_id
        self.assertRaises(Unauthorized,
                          self.comment.restrictedTraverse,
                          '@@moderate-delete-comment')
        self.failUnless(self.comment_id in self.conversation.objectIds())

    def test_delete_as_user(self):
        # Make sure that members can not delete comments
        self.logout()
        self.setRoles(('Member',))
        self.portal.REQUEST.form['comment_id'] = self.comment_id
        self.assertRaises(Unauthorized,
                          self.comment.restrictedTraverse,
                          '@@moderate-delete-comment')
        self.failUnless(self.comment_id in self.conversation.objectIds())

    def test_publish(self):
        self.portal.REQUEST.form['comment_id'] = self.comment_id
        self.portal.REQUEST.form['workflow_action'] = 'publish'
        self.assertEquals('pending',
                          self.portal.portal_workflow.getInfoFor(
                              self.comment, 'review_state'))
        view = self.comment.restrictedTraverse('@@moderate-publish-comment')
        view()
        self.assertEquals('published', self.portal.portal_workflow.\
                          getInfoFor(self.comment, 'review_state'))

    def test_publish_as_anonymous(self):
        self.logout()
        self.portal.REQUEST.form['comment_id'] = self.comment_id
        self.portal.REQUEST.form['workflow_action'] = 'publish'
        self.assertEquals('pending', self.portal.portal_workflow.\
                          getInfoFor(self.comment, 'review_state'))
        self.assertRaises(Unauthorized,
                          self.comment.restrictedTraverse,
                          '@@moderate-publish-comment')
        self.assertEquals('pending', self.portal.portal_workflow.\
                          getInfoFor(self.comment, 'review_state'))

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
