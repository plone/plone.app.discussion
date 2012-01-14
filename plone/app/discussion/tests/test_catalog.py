"""Test the plone.app.discussion catalog indexes
"""
import unittest2 as unittest

import transaction

from datetime import datetime

from zope.component import createObject
from zope.annotation.interfaces import IAnnotations

from Products.CMFCore.utils import getToolByName

from plone.app.testing import TEST_USER_ID, setRoles

from plone.app.discussion.testing import \
  PLONE_APP_DISCUSSION_INTEGRATION_TESTING

from plone.app.discussion.interfaces import IConversation


class CatalogSetupTest(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_catalog_installed(self):
        self.assertTrue('total_comments' in
                        self.portal.portal_catalog.indexes())
        self.assertTrue('commentators' in
                        self.portal.portal_catalog.indexes())
        self.assertTrue('total_comments' in
                        self.portal.portal_catalog.schema())
        self.assertTrue('in_response_to' in
                        self.portal.portal_catalog.schema())

    def test_collection_criteria_installed(self):
        try:
            self.portal.portal_atct.getIndex('commentators')
            self.portal.portal_atct.getIndex('total_comments')
            self.portal.portal_atct.getMetadata('total_comments')
        except AttributeError:
            self.fail()


class ConversationCatalogTest(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory(id='doc1',
                                  Title='Document 1',
                                  type_name='Document')

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

        brains = self.catalog.searchResults(dict(
             path={'query':
                   '/'.join(self.portal.doc1.getPhysicalPath())},
             portal_type="Document"
             ))
        self.conversation = conversation
        self.brains = brains
        self.doc1_brain = brains[0]
        self.comment1 = comment1
        self.new_comment1_id = new_comment1_id

    def test_total_comments(self):
        self.assertTrue('total_comments' in self.doc1_brain)
        self.assertEqual(self.doc1_brain.total_comments, 1)

        comment2 = createObject('plone.Comment')
        comment2.title = 'Comment 2'
        comment2.text = 'Comment text'
        comment2.creator = 'Emma'
        new_comment2_id = self.conversation.addComment(comment2)

        comment2 = self.portal.doc1.restrictedTraverse(
            '++conversation++default/%s' % new_comment2_id)
        comment2.reindexObject()
        brains = self.catalog.searchResults(dict(
                     path={'query':
                           '/'.join(self.portal.doc1.getPhysicalPath())},
                     portal_type="Document"
                     ))
        doc1_brain = brains[0]
        self.assertEqual(doc1_brain.total_comments, 2)

    def test_last_comment_date(self):
        self.assertTrue('last_comment_date' in self.doc1_brain)
        self.assertEqual(self.doc1_brain.last_comment_date,
                          datetime(2006, 9, 17, 14, 18, 12))

        # Add another comment and check if last comment date is updated.
        comment2 = createObject('plone.Comment')
        comment2.title = 'Comment 2'
        comment2.text = 'Comment text'
        comment2.creator = 'Emma'
        comment2.creation_date = datetime(2009, 9, 17, 14, 18, 12)
        comment2.modification_date = datetime(2009, 9, 17, 14, 18, 12)
        new_comment2_id = self.conversation.addComment(comment2)

        comment2 = self.portal.doc1.restrictedTraverse(
            '++conversation++default/%s' % new_comment2_id)
        comment2.reindexObject()
        brains = self.catalog.searchResults(dict(
                     path={'query':
                           '/'.join(self.portal.doc1.getPhysicalPath())},
                     portal_type="Document"
                     ))
        doc1_brain = brains[0]
        self.assertEqual(doc1_brain.last_comment_date,
                          datetime(2009, 9, 17, 14, 18, 12))

        # Remove the comment again
        del self.conversation[new_comment2_id]

        brains = self.catalog.searchResults(dict(
                     path={'query':
                           '/'.join(self.portal.doc1.getPhysicalPath())},
                     portal_type="Document"
                     ))
        doc1_brain = brains[0]
        self.assertEqual(doc1_brain.last_comment_date,
                          datetime(2006, 9, 17, 14, 18, 12))

        # remove all comments
        del self.conversation[self.new_comment1_id]
        brains = self.catalog.searchResults(dict(
                     path={'query':
                           '/'.join(self.portal.doc1.getPhysicalPath())},
                     portal_type="Document"
                     ))
        doc1_brain = brains[0]
        self.assertEqual(doc1_brain.last_comment_date, None)

    def test_commentators(self):
        self.assertTrue('commentators' in self.doc1_brain)
        self.assertEqual(self.doc1_brain.commentators, ('Jim',))

        # add another comment with another author
        comment2 = createObject('plone.Comment')
        comment2.title = 'Comment 2'
        comment2.text = 'Comment text'
        comment2.creator = 'Emma'
        comment2.author_username = 'Emma'
        new_comment2_id = self.conversation.addComment(comment2)

        comment2 = self.portal.doc1.restrictedTraverse(
            '++conversation++default/%s' % new_comment2_id)
        comment2.reindexObject()

        brains = self.catalog.searchResults(dict(
                     path={'query':
                           '/'.join(self.portal.doc1.getPhysicalPath())},
                     portal_type="Document"
                     ))
        doc1_brain = brains[0]

        self.assertEqual(doc1_brain.commentators, ('Emma', 'Jim'))

        # remove one comments
        del self.conversation[new_comment2_id]
        brains = self.catalog.searchResults(dict(
                     path={'query':
                          '/'.join(self.portal.doc1.getPhysicalPath())},
                     portal_type="Document"
                     ))
        doc1_brain = brains[0]
        self.assertEqual(doc1_brain.commentators, ('Jim',))

        # remove all comments
        del self.conversation[self.new_comment1_id]
        brains = self.catalog.searchResults(dict(
                     path={'query':
                           '/'.join(self.portal.doc1.getPhysicalPath())},
                     portal_type="Document"
                     ))
        doc1_brain = brains[0]
        self.assertEqual(doc1_brain.commentators, ())

    def test_conversation_indexes_not_in_comments(self):
        brains = self.catalog.searchResults(dict(
                     path={'query':
                           '/'.join(self.portal.doc1.getPhysicalPath())},
                     portal_type="Discussion Item"
                     ))
        comment1_brain = brains[0]
        self.assertEqual(comment1_brain.commentators, None)
        self.assertEqual(comment1_brain.last_comment_date, None)
        self.assertEqual(comment1_brain.total_comments, None)


class CommentCatalogTest(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory(id='doc1',
                                  title='Document 1',
                                  type_name='Document')
        self.catalog = getToolByName(self.portal, 'portal_catalog')

        conversation = IConversation(self.portal.doc1)
        self.conversation = conversation

        comment1 = createObject('plone.Comment')
        comment1.text = 'Comment text'
        comment1.creator = 'Jim'
        new_comment1_id = conversation.addComment(comment1)
        self.comment_id = new_comment1_id

        # Comment brain
        self.comment = self.portal.doc1.restrictedTraverse(
            '++conversation++default/%s' % new_comment1_id)
        brains = self.catalog.searchResults(dict(
                     path={'query':
                             '/'.join(self.comment.getPhysicalPath())}))
        self.comment_brain = brains[0]

    def test_title(self):
        self.assertEqual(self.comment_brain.Title, 'Jim on Document 1')

    def test_no_name_title(self):
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        cid = self.conversation.addComment(comment)

        # Comment brain
        comment = self.portal.doc1.restrictedTraverse(
            '++conversation++default/%s' % cid)
        brains = self.catalog.searchResults(dict(
                     path={'query':
                             '/'.join(comment.getPhysicalPath())}))
        comment_brain = brains[0]
        self.assertEqual(comment_brain.Title, "Anonymous on Document 1")

    def test_type(self):
        self.assertEqual(self.comment_brain.portal_type, 'Discussion Item')
        self.assertEqual(self.comment_brain.meta_type, 'Discussion Item')
        self.assertEqual(self.comment_brain.Type, 'Comment')

    def test_review_state(self):
        self.assertEqual(self.comment_brain.review_state, 'published')

    def test_creator(self):
        self.assertEqual(self.comment_brain.Creator, 'Jim')

    def test_in_response_to(self):
        """Make sure in_response_to returns the title or id of the content
           object the comment was added to.
        """
        self.assertEqual(self.comment_brain.in_response_to, 'Document 1')

    def test_add_comment(self):
        self.assertTrue(self.comment_brain)

    def test_delete_comment(self):
        # Make sure a comment is removed from the catalog as well when it is
        # deleted.
        del self.conversation[self.comment_id]
        brains = self.catalog.searchResults(dict(
                     path={'query':
                             '/'.join(self.comment.getPhysicalPath())}))
        self.assertEqual(len(brains), 0)

    def test_remove_comments_when_content_object_is_removed(self):
        """Make sure all comments are removed from the catalog, if the content
           object is removed.
        """
        brains = self.catalog.searchResults({'portal_type': 'Discussion Item'})
        self.assertEqual(len(brains), 1)
        self.portal.manage_delObjects(["doc1"])
        brains = self.catalog.searchResults({'portal_type': 'Discussion Item'})
        self.assertEqual(len(brains), 0)

    def test_move_comments_when_content_object_is_moved(self):
        # Create two folders and a content object with a comment
        self.portal.invokeFactory(id='folder1',
                                  title='Folder 1',
                                  type_name='Folder')
        self.portal.invokeFactory(id='folder2',
                                  title='Folder 2',
                                  type_name='Folder')
        self.portal.folder1.invokeFactory(id='moveme',
                                  title='Move Me',
                                  type_name='Document')
        conversation = IConversation(self.portal.folder1.moveme)
        comment = createObject('plone.Comment')
        comment_id = conversation.addComment(comment)
        # We need to commit here so that _p_jar isn't None and move will work
        transaction.savepoint(optimistic=True)

        # Move moveme from folder1 to folder2
        cp = self.portal.folder1.manage_cutObjects(ids=('moveme',))
        self.portal.folder2.manage_pasteObjects(cp)

        # Make sure no old comment brains are
        brains = self.catalog.searchResults(dict(
             portal_type="Discussion Item",
             path={'query': '/'.join(self.portal.folder1.getPhysicalPath())}
             ))
        self.assertEquals(len(brains), 0)

        brains = self.catalog.searchResults(dict(
                 portal_type="Discussion Item",
                 path={
                     'query': '/'.join(self.portal.folder2.getPhysicalPath())
                     }
                 ))
        self.assertEquals(len(brains), 1)
        self.assertEquals(brains[0].getPath(),
                          '/plone/folder2/moveme/++conversation++default/' +
                          str(comment_id))

    def test_update_comments_when_content_object_is_renamed(self):
        # We need to commit here so that _p_jar isn't None and move will work
        transaction.savepoint(optimistic=True)

        self.portal.manage_renameObject("doc1", "doc2")

        brains = self.catalog.searchResults(
            portal_type='Discussion Item')
        self.assertEquals(len(brains), 1)
        self.assertEquals(brains[0].getPath(),
                          '/plone/doc2/++conversation++default/' +
                          str(self.comment_id))

    def test_clear_and_rebuild_catalog(self):
        # Clear and rebuild catalog
        self.catalog.clearFindAndRebuild()

        # Check if comment is still there
        brains = self.catalog.searchResults({'portal_type': 'Discussion Item'})
        self.assertTrue(brains)
        comment_brain = brains[0]
        self.assertEqual(comment_brain.Title, u'Jim on Document 1')
        self.assertEqual(comment_brain.getPath(),
            '/plone/doc1/++conversation++default/' +
            str(self.comment_id))

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
        self.conversation.addComment(comment1_1_1)

        comment1_2.in_reply_to = new_id_1
        self.conversation.addComment(comment1_2)

        comment2_1.in_reply_to = new_id_2
        self.conversation.addComment(comment2_1)

        # Clear and rebuild catalog
        self.catalog.clearFindAndRebuild()

        # Check if comments are still there
        brains = self.catalog.searchResults({'portal_type': 'Discussion Item'})
        self.assertTrue(brains)
        self.assertEqual(len(brains), 6)

    def test_collection(self):
        self.portal.invokeFactory(id='topic', type_name='Topic')
        topic = self.portal.topic
        crit = topic.addCriterion('Type', 'ATSimpleStringCriterion')
        crit.setValue('Comment')
        query = topic.buildQuery()

        # Make sure the comment we just added is returned by the collection
        self.assertEqual(len(query), 1)
        self.assertEqual(query['Type'], 'Comment')
        self.assertEqual(len(topic.queryCatalog()), 1)


class NoConversationCatalogTest(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory(id='doc1',
                                  Title='Document 1',
                                  type_name='Document')

        self.catalog = getToolByName(self.portal, 'portal_catalog')

        conversation = IConversation(self.portal.doc1)

        brains = self.catalog.searchResults(dict(
                     path={'query':
                             '/'.join(self.portal.doc1.getPhysicalPath())},
                     portal_type="Document"
                     ))
        self.conversation = conversation
        self.brains = brains
        self.doc1_brain = brains[0]

    def test_total_comments(self):
        self.assertTrue('total_comments' in self.doc1_brain)
        self.assertEqual(self.doc1_brain.total_comments, 0)

        # Make sure no conversation has been created
        self.assertTrue('plone.app.discussion:conversation' not in
                     IAnnotations(self.portal.doc1))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
