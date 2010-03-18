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

        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.portal.doc1.getPhysicalPath()) },
                     portal_type = "Document"
                     )
        self.conversation = conversation
        self.brains = brains
        self.doc1_brain = brains[0]
        self.comment1 = comment1
        self.new_comment1_id = new_comment1_id

    def test_total_comments(self):
        self.failUnless(self.doc1_brain.has_key('total_comments'))
        self.assertEquals(self.doc1_brain.total_comments, 1)

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
        doc1_brain = brains[0]
        self.assertEquals(doc1_brain.total_comments, 2)

    def test_last_comment_date(self):
        self.failUnless(self.doc1_brain.has_key('last_comment_date'))
        self.assertEquals(self.doc1_brain.last_comment_date, datetime(2006, 9, 17, 14, 18, 12))

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
        doc1_brain = brains[0]
        self.assertEquals(doc1_brain.last_comment_date, datetime(2009, 9, 17, 14, 18, 12))

        # Remove the comment again
        del self.conversation[new_comment2_id]

        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.portal.doc1.getPhysicalPath()) },
                     portal_type = "Document"
                     )
        doc1_brain = brains[0]

        self.assertEquals(doc1_brain.last_comment_date, datetime(2006, 9, 17, 14, 18, 12))

        # remove all comments
        del self.conversation[self.new_comment1_id]
        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.portal.doc1.getPhysicalPath()) },
                     portal_type = "Document"
                     )
        doc1_brain = brains[0]
        self.assertEquals(doc1_brain.last_comment_date, None)

    def test_commentators(self):
        self.failUnless(self.doc1_brain.has_key('commentators'))
        self.assertEquals(self.doc1_brain.commentators, ('Jim',))

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
        doc1_brain = brains[0]

        self.assertEquals(doc1_brain.commentators, ('Emma', 'Jim'))

        # remove one comments
        del self.conversation[new_comment2_id]
        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.portal.doc1.getPhysicalPath()) },
                     portal_type = "Document"
                     )
        doc1_brain = brains[0]
        self.assertEquals(doc1_brain.commentators, ('Jim',))

        # remove all comments
        del self.conversation[self.new_comment1_id]
        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.portal.doc1.getPhysicalPath()) },
                     portal_type = "Document"
                     )
        doc1_brain = brains[0]
        self.assertEquals(doc1_brain.commentators, ())

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
        self.typetool = typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')

        self.catalog = getToolByName(self.portal, 'portal_catalog')

        conversation = IConversation(self.portal.doc1)

        self.conversation = conversation

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
        self.assertEquals(self.comment_brain.Type, 'Comment')

    def test_review_state(self):
         self.assertEquals(self.comment_brain.review_state, 'published')

    def test_creator(self):
        self.assertEquals(self.comment_brain.Creator, 'Jim')

    def test_in_response_to(self):
        # make sure in_response_to returns the title or id of the content
        # object the comment was added to
        self.assertEquals(self.comment_brain.in_response_to, 'doc1')

    def test_add_comment(self):
        self.failUnless(self.comment_brain)
    
    def test_delete_comment(self):
        # Make sure a comment is removed from the catalog as well when it is
        # deleted.
        del self.conversation[self.comment_id]
        brains = self.catalog.searchResults(
                     path = {'query' : '/'.join(self.comment.getPhysicalPath()) })
        self.assertEquals(len(brains), 0)

    def test_remove_comments_when_content_object_is_removed(self):
        # Make sure all comments are removed from the catalog, if the content
        # object is removed.
        pass
    
    def test_clear_and_rebuild_catalog(self):
        # Clear and rebuild catalog
        self.catalog.clearFindAndRebuild()

        # Check if comment is still there
        brains = self.catalog.searchResults(portal_type = 'Discussion Item')
        self.failUnless(brains)
        comment_brain = brains[0]
        self.assertEquals(comment_brain.Title, 'Comment 1')

    def test_clear_and_rebuild_catalog_for_nested_comments(self):

        # Create a nested comment structure:
        #
        # Conversation
        # +- Comment 1
        #    +- Comment 1_1
        #    |  +- Comment 1_1_1
        #    +- Comment 1_2
        # +- Comment 2
        #    +- Comment 2_1

        comment1_1 = createObject('plone.Comment')
        comment1_1.title = 'Re: Comment 1'
        comment1_1.text = 'Comment text'

        comment1_1_1 = createObject('plone.Comment')
        comment1_1_1.title = 'Re: Re: Comment 1'
        comment1_1_1.text = 'Comment text'

        comment1_2 = createObject('plone.Comment')
        comment1_2.title = 'Re: Comment 1 (2)'
        comment1_2.text = 'Comment text'

        comment2 = createObject('plone.Comment')
        comment2.title = 'Comment 2'
        comment2.text = 'Comment text'

        comment2_1 = createObject('plone.Comment')
        comment2_1.title = 'Re: Comment 2'
        comment2_1.text = 'Comment text'

        # Create the nested comment structure
        new_id_1 = self.conversation.addComment(self.comment)
        new_id_2 = self.conversation.addComment(comment2)

        comment1_1.in_reply_to = self.comment_id
        new_id_1_1 = self.conversation.addComment(comment1_1)

        comment1_1_1.in_reply_to = new_id_1_1
        new_id_1_1_1 = self.conversation.addComment(comment1_1_1)

        comment1_2.in_reply_to = new_id_1
        new_id_1_2 = self.conversation.addComment(comment1_2)

        comment2_1.in_reply_to = new_id_2
        new_id_2_1 = self.conversation.addComment(comment2_1)

        # Clear and rebuild catalog
        self.catalog.clearFindAndRebuild()

        # Check if comments are still there
        brains = self.catalog.searchResults(portal_type = 'Discussion Item')
        self.failUnless(brains)
        self.assertEquals(len(brains), 6)

    def test_collection(self):
        self.typetool.constructContent('Topic', self.portal, 'topic')
        topic = self.portal.topic
        crit = topic.addCriterion('Type', 'ATSimpleStringCriterion')
        crit.setValue('Comment')
        query = topic.buildQuery()

        # Make sure the comment we just added is returned by the collection
        self.assertEquals(len(query), 1)
        self.assertEquals(query['Type'], 'Comment')
        self.assertEquals(len(topic.queryCatalog()), 1)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
