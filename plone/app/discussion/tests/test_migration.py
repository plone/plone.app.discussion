import unittest

from zope.annotation.interfaces import IAnnotations

from Products.CMFCore.utils import getToolByName

from Products.PloneTestCase.ptc import PloneTestCase

from plone.app.discussion.tests.layer import DiscussionLayer

from plone.app.discussion.browser.migration import View

from plone.app.discussion.interfaces import IConversation, IComment

class MigrationTest(PloneTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc')
        # Create a document
        self.discussion = getToolByName(self.portal, 'portal_discussion', None)
        self.discussion.overrideDiscussionFor(self.portal.doc, 1)
        # Publish it
        self.workflow = self.portal.portal_workflow
        self.workflow.doActionFor(self.portal.doc, 'publish')

        request = self.app.REQUEST
        context = getattr(self.portal, 'doc')
        self.view = View(context, request)
        self.workflow.setChainForPortalTypes(('Discussion Item',), 'comment_review_workflow')

    def test_migrate_comment(self):

        # Create one comment
        self.discussion.getDiscussionFor(self.portal.doc)
        self.portal.doc.talkback.createReply('My Title', 'My Text')
        reply = self.portal.doc.talkback.objectValues()[0]
        self.assertEqual(reply.Title(), 'My Title')
        self.assertEqual(reply.EditableBody(), 'My Text')

        # Call migration script
        self.view()

        # Make sure a conversation has been created
        self.failUnless('plone.app.discussion:conversation' in IAnnotations(self.portal.doc))

        conversation = IConversation(self.portal.doc)

        # Check migration
        self.assertEquals(conversation.total_comments, 1)
        self.failUnless(conversation.getComments().next())
        self.assert_(IComment.providedBy(conversation.getComments().next()))
        self.assertEquals(conversation.getComments().next().Title(), 'My Title')
        self.assertEquals(conversation.getComments().next().text, 'My Text')

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)