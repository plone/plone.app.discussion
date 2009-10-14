import unittest

from datetime import datetime

from zope.component import createObject

from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from Products.PloneTestCase.ptc import PloneTestCase

from plone.app.discussion.tests.layer import DiscussionLayer

from plone.app.discussion.interfaces import IComment, IConversation, IReplies

class CatalogSetupTest(PloneTestCase):

    layer = DiscussionLayer

    def test_catalog_installed(self):
        self.failUnless('total_comments' in self.portal.portal_catalog.indexes())
        self.failUnless('commentators' in self.portal.portal_catalog.indexes())
        self.failUnless('total_comments' in self.portal.portal_catalog.schema())
        self.failUnless('in_response_to' in self.portal.portal_catalog.schema())

    def test_collection_criteria_installed(self):
        try:
            self.portal.portal_atct.getIndex('commentators')
            self.portal.portal_atct.getIndex('total_comments')
            self.portal.portal_atct.getMetadata('total_comments')
        except AttributeError:
            self.fail()

class ConversationCatalogTest(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        # First we need to create some content.
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')

        self.catalog = getToolByName(self.portal, 'portal_catalog')

        conversation = IConversation(self.portal.doc1)

        comment1 = createObject('plone.Comment')
        comment1.title = 'Comment 1'
        comment1.text = 'Comment text'
        comment1.creator = 'Jim'
        comment1.author_username = 'Jim'
        comment1.creation_date = datetime(2006, 9, 17, 14, 18, 12)
        comment1.modification_date = datetime(2006, 9, 17, 14, 18, 12)

        new_comment1_id = conversation.addComment(comment1)
        self.comment_id = new_comment1_id

        comment1 = self.portal.doc1.restrictedTraverse('++conversation++default/%s' % new_comment1_id)
        comment1.reindexObject()

        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.portal.doc1.getPhysicalPath()) },
                     portal_type = "Document"
                     )
        self.brains = brains
        self.conversation = conversation
        self.conversation_brain = brains[0]
        self.comment1 = comment1
        self.new_comment1_id = new_comment1_id

    def test_total_comments(self):
        self.failUnless(self.conversation_brain.has_key('total_comments'))
        self.assertEquals(self.conversation_brain.total_comments, 1)

        comment2 = createObject('plone.Comment')
        comment2.title = 'Comment 2'
        comment2.text = 'Comment text'
        comment2.creator = 'Emma'
        new_comment2_id = self.conversation.addComment(comment2)

        comment2 = self.portal.doc1.restrictedTraverse('++conversation++default/%s' % new_comment2_id)
        comment2.reindexObject()
        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.portal.doc1.getPhysicalPath()) },
                     portal_type = "Document"
                     )
        conversation_brain = brains[0]
        self.assertEquals(conversation_brain.total_comments, 2)

    def test_last_comment_date(self):
        self.failUnless(self.conversation_brain.has_key('last_comment_date'))
        self.assertEquals(self.conversation_brain.last_comment_date, datetime(2006, 9, 17, 14, 18, 12))

        # Add another comment and check if last comment date is updated.
        comment2 = createObject('plone.Comment')
        comment2.title = 'Comment 2'
        comment2.text = 'Comment text'
        comment2.creator = 'Emma'
        comment2.creation_date = datetime(2009, 9, 17, 14, 18, 12)
        comment2.modification_date = datetime(2009, 9, 17, 14, 18, 12)
        new_comment2_id = self.conversation.addComment(comment2)

        comment2 = self.portal.doc1.restrictedTraverse('++conversation++default/%s' % new_comment2_id)
        comment2.reindexObject()
        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.portal.doc1.getPhysicalPath()) },
                     portal_type = "Document"
                     )
        conversation_brain = brains[0]
        self.assertEquals(conversation_brain.last_comment_date, datetime(2009, 9, 17, 14, 18, 12))

        # Remove the comment again
        del self.conversation[new_comment2_id]

        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.portal.doc1.getPhysicalPath()) },
                     portal_type = "Document"
                     )
        conversation_brain = brains[0]

        self.assertEquals(conversation_brain.last_comment_date, datetime(2006, 9, 17, 14, 18, 12))

        # remove all comments
        del self.conversation[self.new_comment1_id]
        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.portal.doc1.getPhysicalPath()) },
                     portal_type = "Document"
                     )
        conversation_brain = brains[0]
        self.assertEquals(conversation_brain.last_comment_date, None)

    def test_commentators(self):
        self.failUnless(self.conversation_brain.has_key('commentators'))
        self.assertEquals(self.conversation_brain.commentators, ('Jim',))

        # add another comment with another author
        comment2 = createObject('plone.Comment')
        comment2.title = 'Comment 2'
        comment2.text = 'Comment text'
        comment2.creator = 'Emma'
        comment2.author_username = 'Emma'
        new_comment2_id = self.conversation.addComment(comment2)

        comment2 = self.portal.doc1.restrictedTraverse('++conversation++default/%s' % new_comment2_id)
        comment2.reindexObject()

        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.portal.doc1.getPhysicalPath()) },
                     portal_type = "Document"
                     )
        conversation_brain = brains[0]

        self.assertEquals(conversation_brain.commentators, ('Emma', 'Jim'))

        # remove one comments
        del self.conversation[new_comment2_id]
        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.portal.doc1.getPhysicalPath()) },
                     portal_type = "Document"
                     )
        conversation_brain = brains[0]
        self.assertEquals(conversation_brain.commentators, ('Jim',))

        # remove all comments
        del self.conversation[self.new_comment1_id]
        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.portal.doc1.getPhysicalPath()) },
                     portal_type = "Document"
                     )
        conversation_brain = brains[0]
        self.assertEquals(conversation_brain.commentators, ())

    def test_conversation_indexes_not_in_comments(self):
        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.portal.doc1.getPhysicalPath()) },
                     portal_type = "Discussion Item"
                     )
        comment1_brain = brains[0]
        self.assertEquals(comment1_brain.commentators, None)
        self.assertEquals(comment1_brain.last_comment_date, None)
        self.assertEquals(comment1_brain.total_comments, None)

class CommentCatalogTest(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        # First we need to create some content.
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')

        self.catalog = getToolByName(self.portal, 'portal_catalog')

        conversation = IConversation(self.portal.doc1)

        comment1 = createObject('plone.Comment')
        comment1.title = 'Comment 1'
        comment1.text = 'Comment text'
        comment1.creator = 'Jim'

        new_comment1_id = conversation.addComment(comment1)
        self.comment_id = new_comment1_id

        self.comment = self.portal.doc1.restrictedTraverse('++conversation++default/%s' % new_comment1_id)

        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.comment.getPhysicalPath()) })
        self.comment_brain = brains[0]

    def test_title(self):
        self.assertEquals(self.comment_brain.Title, 'Comment 1')

    def test_type(self):
        self.assertEquals(self.comment_brain.portal_type, 'Discussion Item')
        self.assertEquals(self.comment_brain.meta_type, 'Discussion Item')
        self.assertEquals(self.comment_brain.Type, 'Discussion Item')

    def test_review_state(self):
         self.assertEquals(self.comment_brain.review_state, 'published')

    def test_creator(self):
        self.assertEquals(self.comment_brain.Creator, 'Jim')

    def test_in_response_to(self):
        # make sure in_response_to returns the title or id of the content
        # object the comment was added to
        self.assertEquals(self.comment_brain.in_response_to, 'doc1')

    def test_clear_and_rebuild_catalog(self):
		# Clear and rebuild catalog
        self.catalog.clearFindAndRebuild()

        # Check if comment is still there
        brains = self.catalog.searchResults(portal_type = 'Discussion Item')
        self.failUnless(brains)
        comment_brain = brains[0]
        self.assertEquals(comment_brain.Title, 'Comment 1')

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)