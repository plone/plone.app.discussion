import unittest

from zope.component import createObject

from zope.interface import alsoProvides

from AccessControl import Unauthorized

from Products.PloneTestCase.ptc import PloneTestCase

from plone.app.discussion.tests.layer import DiscussionLayer
from plone.app.discussion.interfaces import IConversation, IDiscussionLayer

class WorkflowTest(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        self.portal.portal_types['Document'].allow_discussion = True
        self.portal_discussion = self.portal.portal_discussion

        self.folder.invokeFactory('Document', 'doc1')

        self.setRoles(('Reviewer',))
        #alsoProvides(self.portal.REQUEST, DiscussionLayer)

    def test_permission(self):
        self.setRoles(('Reviewer',))
        self.failUnless(self.portal.portal_membership.checkPermission('Review comments', self.folder), self.folder)
        self.setRoles(('Member',))
        self.failIf(self.portal.portal_membership.checkPermission('Review comments', self.folder), self.folder)

    def test_workflows_installed(self):
        self.failUnless('comment_review_workflow' in self.portal.portal_workflow.objectIds())
        self.assertEquals(('one_state_workflow',),
                self.portal.portal_workflow.getChainForPortalType('Discussion Item'))

class TestCommentOperations(PloneTestCase):

    layer = DiscussionLayer
    
    def afterSetUp(self):

        self.loginAsPortalOwner()

        # Allow discussion on the Document content type
        self.portal.portal_types['Document'].allow_discussion = True
        # Set workflow for Discussion item to review workflow
        self.portal.portal_workflow.setChainForPortalTypes(('Discussion Item',),
                                                            ('comment_review_workflow',))

        # Create a Document
        self.portal.invokeFactory('Document', 'doc1')
        self.portal_discussion = self.portal.portal_discussion

        # Create a conversation for this Document
        conversation = IConversation(self.portal.doc1)

        # Add a comment.
        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'
        comment_id = conversation.addComment(comment)
        comment = self.portal.doc1.restrictedTraverse('++conversation++default/%s' % comment_id)

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
        self.assertEquals('pending', self.portal.portal_workflow.getInfoFor(self.comment, 'review_state'))
        view = self.comment.restrictedTraverse('@@moderate-publish-comment')
        view()
        self.assertEquals('published', self.portal.portal_workflow.getInfoFor(self.comment, 'review_state'))

    def test_publish_as_anonymous(self):
        self.logout()
        self.portal.REQUEST.form['comment_id'] = self.comment_id
        self.portal.REQUEST.form['workflow_action'] = 'publish'
        self.assertEquals('pending', self.portal.portal_workflow.getInfoFor(self.comment, 'review_state'))
        self.assertRaises(Unauthorized,
                          self.comment.restrictedTraverse,
                          '@@moderate-publish-comment')
        self.assertEquals('pending', self.portal.portal_workflow.getInfoFor(self.comment, 'review_state'))

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)