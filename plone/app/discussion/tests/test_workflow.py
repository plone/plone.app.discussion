import unittest

from Products.PloneTestCase.ptc import PloneTestCase
from plone.app.discussion.tests.layer import DiscussionLayer

class WorkflowTest(PloneTestCase):

    layer = DiscussionLayer

    def test_permission(self):
        self.setRoles(('Reviewer',))
        self.failUnless(self.portal.portal_membership.checkPermission('Review comments', self.folder), self.folder)
        self.setRoles(('Member',))
        self.failIf(self.portal.portal_membership.checkPermission('Review comments', self.folder), self.folder)

    def test_workflows_installed(self):
        self.failUnless('comment_review_workflow' in self.portal.portal_workflow.objectIds())
        self.assertEquals(('one_state_workflow',),
                self.portal.portal_workflow.getChainForPortalType('Discussion Item'))

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)