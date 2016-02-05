# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Acquisition import aq_parent
from datetime import datetime
from datetime import timedelta
from plone.app.discussion import interfaces
from plone.app.discussion.interfaces import IComment
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import IReplies
from plone.app.discussion.testing import PLONE_APP_DISCUSSION_INTEGRATION_TESTING  # noqa
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.vocabularies.types import BAD_TYPES
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope import interface
from zope.annotation.interfaces import IAnnotations
from zope.component import createObject
from zope.component import queryUtility

import unittest2 as unittest


try:
    from plone.dexterity.interfaces import IDexterityContent
    DEXTERITY = True
except ImportError:
    DEXTERITY = False


class ConversationTest(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        interface.alsoProvides(
            self.portal.REQUEST, interfaces.IDiscussionLayer)

        self.typetool = self.portal.portal_types
        self.portal_discussion = getToolByName(
            self.portal,
            'portal_discussion',
            None,
        )
        # Allow discussion
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = True

    def test_add_comment(self):
        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Add a comment. Note: in real life, we always create comments via the
        # factory to allow different factories to be swapped in

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'

        new_id = conversation.addComment(comment)

        # Check that the conversation methods return the correct data
        self.assertTrue(isinstance(comment.comment_id, long))
        self.assertTrue(IComment.providedBy(conversation[new_id]))
        self.assertEqual(
            aq_base(conversation[new_id].__parent__),
            aq_base(conversation)
        )
        self.assertEqual(new_id, comment.comment_id)
        self.assertEqual(len(list(conversation.getComments())), 1)
        self.assertEqual(len(tuple(conversation.getThreads())), 1)
        self.assertEqual(conversation.total_comments(), 1)
        self.assertTrue(
            conversation.last_comment_date - datetime.utcnow() <
            timedelta(seconds=1)
        )

    def test_private_comment(self):
        conversation = IConversation(self.portal.doc1)

        comment = createObject('plone.Comment')
        comment.author_username = 'nobody'
        conversation.addComment(comment)
        comment.manage_permission('View', roles=tuple())
        self.assertEqual(0, conversation.total_comments())
        self.assertEqual(None, conversation.last_comment_date)
        self.assertEqual(['nobody'], list(conversation.commentators))
        self.assertEqual([], list(conversation.public_commentators))

    def test_delete_comment(self):
        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Add a comment. Note: in real life, we always create comments via the
        # factory to allow different factories to be swapped in

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'

        new_id = conversation.addComment(comment)

        # make sure the comment has been added
        self.assertEqual(len(list(conversation.getComments())), 1)
        self.assertEqual(len(tuple(conversation.getThreads())), 1)
        self.assertEqual(conversation.total_comments(), 1)

        # delete the comment we just created
        del conversation[new_id]

        # make sure there is no comment left in the conversation
        self.assertEqual(len(list(conversation.getComments())), 0)
        self.assertEqual(len(tuple(conversation.getThreads())), 0)
        self.assertEqual(conversation.total_comments(), 0)

    def test_delete_recursive(self):
        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        IReplies(conversation)

        # Create a nested comment structure:
        #
        # Conversation
        # +- Comment 1
        #    +- Comment 1_1
        #    |  +- Comment 1_1_1
        #    +- Comment 1_2
        # +- Comment 2
        #    +- Comment 2_1

        # Create all comments
        comment1 = createObject('plone.Comment')
        comment1.text = 'Comment text'

        comment1_1 = createObject('plone.Comment')
        comment1_1.text = 'Comment text'

        comment1_1_1 = createObject('plone.Comment')
        comment1_1_1.text = 'Comment text'

        comment1_2 = createObject('plone.Comment')
        comment1_2.text = 'Comment text'

        comment2 = createObject('plone.Comment')
        comment2.text = 'Comment text'

        comment2_1 = createObject('plone.Comment')
        comment2_1.text = 'Comment text'

        # Create the nested comment structure
        new_id_1 = conversation.addComment(comment1)
        new_id_2 = conversation.addComment(comment2)

        comment1_1.in_reply_to = new_id_1
        new_id_1_1 = conversation.addComment(comment1_1)

        comment1_1_1.in_reply_to = new_id_1_1
        conversation.addComment(comment1_1_1)

        comment1_2.in_reply_to = new_id_1
        conversation.addComment(comment1_2)

        comment2_1.in_reply_to = new_id_2
        new_id_2_1 = conversation.addComment(comment2_1)

        del conversation[new_id_1]

        self.assertEqual([
            {'comment': comment2,     'depth': 0, 'id': new_id_2},
            {'comment': comment2_1,   'depth': 1, 'id': new_id_2_1},
        ], list(conversation.getThreads()))

    def test_delete_comment_when_content_object_is_deleted(self):
        # Make sure all comments of a content object are deleted when the
        # object itself is deleted.
        conversation = IConversation(self.portal.doc1)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        conversation.addComment(comment)

        # Delete the content object
        self.portal.manage_delObjects(['doc1'])

        # Make sure the comment has been deleted as well
        self.assertEqual(len(list(conversation.getComments())), 0)
        self.assertEqual(len(tuple(conversation.getThreads())), 0)
        self.assertEqual(conversation.total_comments(), 0)

    def test_comments_enabled_on_doc_in_subfolder(self):
        typetool = self.portal.portal_types
        typetool.constructContent('Folder', self.portal, 'folder1')
        typetool.constructContent('Document', self.portal.folder1, 'doc2')

        folder = self.portal.folder1

        folder.allow_discussion = True
        self.assertTrue(aq_base(folder).allow_discussion)
        folder.allow_discussion = False
        self.assertFalse(aq_base(folder).allow_discussion)

        doc = self.portal.folder1.doc2
        conversation = doc.restrictedTraverse('@@conversation_view')
        self.assertEqual(conversation.enabled(), False)

        # We have to allow discussion on Document content type, since
        # otherwise allow_discussion will always return False
        portal_types = getToolByName(self.portal, 'portal_types')
        document_fti = getattr(portal_types, 'Document')
        document_fti.manage_changeProperties(allow_discussion=True)

        self.assertEqual(conversation.enabled(), True)

    def test_disable_commenting_globally(self):

        # Create a conversation.
        conversation = self.portal.doc1.restrictedTraverse(
            '@@conversation_view')

        # We have to allow discussion on Document content type, since
        # otherwise allow_discussion will always return False
        portal_types = getToolByName(self.portal, 'portal_types')
        document_fti = getattr(portal_types, 'Document')
        document_fti.manage_changeProperties(allow_discussion=True)

        # Check if conversation is enabled now
        self.assertEqual(conversation.enabled(), True)

        # Disable commenting in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = False

        # Check if commenting is disabled on the conversation
        self.assertEqual(conversation.enabled(), False)

        # Enable discussion again
        settings.globally_enabled = True
        self.assertEqual(conversation.enabled(), True)

    def test_allow_discussion_for_news_items(self):

        self.typetool.constructContent('News Item', self.portal, 'newsitem')
        newsitem = self.portal.newsitem
        conversation = newsitem.restrictedTraverse('@@conversation_view')

        # We have to allow discussion on Document content type, since
        # otherwise allow_discussion will always return False
        portal_types = getToolByName(self.portal, 'portal_types')
        document_fti = getattr(portal_types, 'News Item')
        document_fti.manage_changeProperties(allow_discussion=True)

        # Check if conversation is enabled now
        self.assertEqual(conversation.enabled(), True)

        # Disable commenting in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = False

        # Check if commenting is disabled on the conversation
        self.assertEqual(conversation.enabled(), False)

        # Enable discussion again
        settings.globally_enabled = True
        self.assertEqual(conversation.enabled(), True)

    def test_disable_commenting_for_content_type(self):

        # Create a conversation.
        conversation = self.portal.doc1.restrictedTraverse(
            '@@conversation_view'
        )

        # The Document content type is disabled by default
        self.assertEqual(conversation.enabled(), False)

        # Allow discussion on Document content type
        portal_types = getToolByName(self.portal, 'portal_types')
        document_fti = getattr(portal_types, 'Document')
        document_fti.manage_changeProperties(allow_discussion=True)

        # Check if conversation is enabled now
        self.assertEqual(conversation.enabled(), True)

        # Disallow discussion on Document content type
        portal_types = getToolByName(self.portal, 'portal_types')
        document_fti = getattr(portal_types, 'Document')
        document_fti.manage_changeProperties(allow_discussion=False)

        # Check if conversation is enabled now
        self.assertEqual(conversation.enabled(), False)

    def test_allow_discussion_on_folder(self):
        # The ATContentTypes based allow_discussion method did not allow to
        # allow discussion on a folder. The dexerity behavior shipped with
        # plone.app.contenttypes does not have this restriction any longer.

        # Create a folder
        self.typetool.constructContent('Folder', self.portal, 'f1')

        # Usually we don't create a conversation on a folder
        conversation = self.portal.f1.restrictedTraverse('@@conversation_view')

        # Allow discussion for the folder
        self.portal.f1.allow_discussion = True

        # Allow discussion on Folder content type
        portal_types = getToolByName(self.portal, 'portal_types')
        document_fti = getattr(portal_types, 'Folder')
        document_fti.manage_changeProperties(allow_discussion=True)

        self.assertTrue(conversation.enabled())

    def test_is_discussion_allowed_on_content_object(self):
        # Allow discussion on a single content object

        # Create a conversation.
        conversation = self.portal.doc1.restrictedTraverse(
            '@@conversation_view'
        )

        # Discussion is disallowed by default
        self.assertEqual(conversation.enabled(), False)

        # Allow discussion on content object
        self.portal.doc1.allow_discussion = True

        # Check if discussion is now allowed on the content object
        self.assertEqual(conversation.enabled(), True)

        self.portal.doc1.allow_discussion = False
        self.assertEqual(conversation.enabled(), False)

    def test_dict_operations(self):
        # test dict operations and acquisition wrapping

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Add a comment. Note: in real life, we always create comments via the
        # factory to allow different factories to be swapped in

        comment1 = createObject('plone.Comment')
        comment1.text = 'Comment text'

        new_id1 = conversation.addComment(comment1)

        comment2 = createObject('plone.Comment')
        comment2.text = 'Comment text'

        new_id2 = conversation.addComment(comment2)

        # check if get returns a comment object, and None if the key
        # can not be found
        self.assertTrue(IComment.providedBy(conversation.get(new_id1)))
        self.assertTrue(IComment.providedBy(conversation.get(new_id2)))
        self.assertEqual(conversation.get(123), None)

        # check if keys return the ids of all comments
        self.assertEqual(len(conversation.keys()), 2)
        self.assertTrue(new_id1 in conversation.keys())
        self.assertTrue(new_id2 in conversation.keys())
        self.assertFalse(123 in conversation.keys())

        # check if items returns (key, comment object) pairs
        self.assertEqual(len(conversation.items()), 2)
        self.assertTrue((new_id1, comment1) in conversation.items())
        self.assertTrue((new_id2, comment2) in conversation.items())

        # check if values returns the two comment objects
        self.assertEqual(len(conversation.values()), 2)
        self.assertTrue(comment1 in conversation.values())
        self.assertTrue(comment2 in conversation.values())

        # check if comment ids are in iterkeys
        self.assertTrue(new_id1 in conversation.iterkeys())
        self.assertTrue(new_id2 in conversation.iterkeys())
        self.assertFalse(123 in conversation.iterkeys())

        # check if comment objects are in itervalues
        self.assertTrue(comment1 in conversation.itervalues())
        self.assertTrue(comment2 in conversation.itervalues())

        # check if iteritems returns (key, comment object) pairs
        self.assertTrue((new_id1, comment1) in conversation.iteritems())
        self.assertTrue((new_id2, comment2) in conversation.iteritems())

        # TODO test acquisition wrapping
        # self.assertTrue(aq_base(aq_parent(comment1)) is conversation)

    def test_total_comments(self):
        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Add a three comments. Note: in real life, we always create
        # comments via the factory to allow different factories to be
        # swapped in

        comment1 = createObject('plone.Comment')
        comment1.text = 'Comment text'

        comment2 = createObject('plone.Comment')
        comment2.text = 'Comment text'

        comment3 = createObject('plone.Comment')
        comment3.text = 'Comment text'

        conversation.addComment(comment1)
        conversation.addComment(comment2)
        conversation.addComment(comment3)

        self.assertEqual(conversation.total_comments(), 3)

    def test_commentators(self):
        # add and remove a few comments to make sure the commentators
        # property returns a true set

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        self.assertEqual(conversation.total_comments(), 0)

        # Add a four comments from three different users
        # Note: in real life, we always create
        # comments via the factory to allow different factories to be
        # swapped in
        comment1 = createObject('plone.Comment')
        comment1.text = 'Comment text'
        comment1.author_username = 'Jim'
        conversation.addComment(comment1)

        comment2 = createObject('plone.Comment')
        comment2.text = 'Comment text'
        comment2.author_username = 'Joe'
        conversation.addComment(comment2)

        comment3 = createObject('plone.Comment')
        comment3.text = 'Comment text'
        comment3.author_username = 'Jack'
        new_comment3_id = conversation.addComment(comment3)

        comment4 = createObject('plone.Comment')
        comment4.text = 'Comment text'
        comment4.author_username = 'Jack'
        new_comment4_id = conversation.addComment(comment4)

        # check if all commentators are in the commentators list
        self.assertEqual(conversation.total_comments(), 4)
        self.assertTrue('Jim' in conversation.commentators)
        self.assertTrue('Joe' in conversation.commentators)
        self.assertTrue('Jack' in conversation.commentators)

        # remove the comment from Jack
        del conversation[new_comment3_id]

        # check if Jack is still in the commentators list (since
        # he had added two comments)
        self.assertTrue('Jim' in conversation.commentators)
        self.assertTrue('Joe' in conversation.commentators)
        self.assertTrue('Jack' in conversation.commentators)
        self.assertEqual(conversation.total_comments(), 3)

        # remove the second comment from Jack
        del conversation[new_comment4_id]

        # check if Jack has been removed from the commentators list
        self.assertTrue('Jim' in conversation.commentators)
        self.assertTrue('Joe' in conversation.commentators)
        self.assertFalse('Jack' in conversation.commentators)
        self.assertEqual(conversation.total_comments(), 2)

    def test_last_comment_date(self):
        # add and remove some comments and check if last_comment_date
        # is properly updated

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Add a three comments that are at least one day old
        # Note: in real life, we always create
        # comments via the factory to allow different factories to be
        # swapped in
        comment1 = createObject('plone.Comment')
        comment1.text = 'Comment text'
        comment1.creation_date = datetime.utcnow() - timedelta(4)
        conversation.addComment(comment1)

        comment2 = createObject('plone.Comment')
        comment2.text = 'Comment text'
        comment2.creation_date = datetime.utcnow() - timedelta(2)
        new_comment2_id = conversation.addComment(comment2)

        comment3 = createObject('plone.Comment')
        comment3.text = 'Comment text'
        comment3.creation_date = datetime.utcnow() - timedelta(1)
        new_comment3_id = conversation.addComment(comment3)

        # check if the latest comment is exactly one day old
        self.assertTrue(
            conversation.last_comment_date < datetime.utcnow() -
            timedelta(hours=23, minutes=59, seconds=59)
        )
        self.assertTrue(
            conversation.last_comment_date >
            datetime.utcnow() - timedelta(days=1, seconds=1)
        )

        # remove the latest comment
        del conversation[new_comment3_id]

        # check if the latest comment has been updated
        # the latest comment should be exactly two days old
        self.assertTrue(
            conversation.last_comment_date < datetime.utcnow() -
            timedelta(days=1, hours=23, minutes=59, seconds=59)
        )
        self.assertTrue(
            conversation.last_comment_date > datetime.utcnow() -
            timedelta(days=2, seconds=1)
        )

        # remove the latest comment again
        del conversation[new_comment2_id]

        # check if the latest comment has been updated
        # the latest comment should be exactly four days old
        self.assertTrue(
            conversation.last_comment_date < datetime.utcnow() -
            timedelta(days=3, hours=23, minutes=59, seconds=59)
        )
        self.assertTrue(
            conversation.last_comment_date > datetime.utcnow() -
            timedelta(days=4, seconds=2)
        )

    def test_get_comments_full(self):
        pass

    def test_get_comments_batched(self):
        pass

    def test_get_threads(self):

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        IReplies(conversation)

        # Create a nested comment structure:
        #
        # Conversation
        # +- Comment 1
        #    +- Comment 1_1
        #    |  +- Comment 1_1_1
        #    +- Comment 1_2
        # +- Comment 2
        #    +- Comment 2_1

        # Create all comments
        comment1 = createObject('plone.Comment')
        comment1.text = 'Comment text'

        comment1_1 = createObject('plone.Comment')
        comment1_1.text = 'Comment text'

        comment1_1_1 = createObject('plone.Comment')
        comment1_1_1.text = 'Comment text'

        comment1_2 = createObject('plone.Comment')
        comment1_2.text = 'Comment text'

        comment2 = createObject('plone.Comment')
        comment2.text = 'Comment text'

        comment2_1 = createObject('plone.Comment')
        comment2_1.text = 'Comment text'

        # Create the nested comment structure
        new_id_1 = conversation.addComment(comment1)
        new_id_2 = conversation.addComment(comment2)

        comment1_1.in_reply_to = new_id_1
        new_id_1_1 = conversation.addComment(comment1_1)

        comment1_1_1.in_reply_to = new_id_1_1
        new_id_1_1_1 = conversation.addComment(comment1_1_1)

        comment1_2.in_reply_to = new_id_1
        new_id_1_2 = conversation.addComment(comment1_2)

        comment2_1.in_reply_to = new_id_2
        new_id_2_1 = conversation.addComment(comment2_1)

        # Get threads

        self.assertEqual([
            {'comment': comment1,     'depth': 0, 'id': new_id_1},
            {'comment': comment1_1,   'depth': 1, 'id': new_id_1_1},
            {'comment': comment1_1_1, 'depth': 2, 'id': new_id_1_1_1},
            {'comment': comment1_2,   'depth': 1, 'id': new_id_1_2},
            {'comment': comment2,     'depth': 0, 'id': new_id_2},
            {'comment': comment2_1,   'depth': 1, 'id': new_id_2_1},
        ], list(conversation.getThreads()))

    def test_get_threads_batched(self):
        # TODO: test start, size, root and depth arguments to getThreads()
        #   - may want to split this into multiple tests
        pass

    def test_traversal(self):
        # make sure we can traverse to conversations and get a URL and path

        conversation = self.portal.doc1.restrictedTraverse(
            '++conversation++default'
        )
        self.assertTrue(IConversation.providedBy(conversation))

        self.assertEqual(
            ('', 'plone', 'doc1', '++conversation++default'),
            conversation.getPhysicalPath()
        )
        self.assertEqual(
            'http://nohost/plone/doc1/++conversation++default',
            conversation.absolute_url()
        )

    def test_unconvertible_id(self):
        # make sure the conversation view doesn't break when given comment id
        # can't be converted to long

        conversation = self.portal.doc1.restrictedTraverse(
            '++conversation++default/ThisCantBeRight'
        )
        self.assertEqual(conversation, None)

    def test_parent(self):
        # Check that conversation has a content object as parent

        # Create a conversation.
        conversation = IConversation(self.portal.doc1)

        # Check the parent
        self.assertTrue(conversation.__parent__)
        self.assertTrue(aq_parent(conversation))

        self.assertEqual(conversation.__parent__.getId(), 'doc1')

    def test_discussion_item_not_in_bad_types(self):
        self.assertFalse('Discussion Item' in BAD_TYPES)

    def test_no_comment(self):
        IConversation(self.portal.doc1)
        # Make sure no conversation has been created
        self.assertTrue(
            'plone.app.discussion:conversation' not in
            IAnnotations(self.portal.doc1)
        )


class ConversationEnabledForDexterityTypesTest(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        interface.alsoProvides(
            self.portal.REQUEST,
            interfaces.IDiscussionLayer
        )

        if DEXTERITY:
            interface.alsoProvides(
                self.portal.doc1,
                IDexterityContent
            )

    def _makeOne(self, *args, **kw):
        return self.portal.doc1.restrictedTraverse('@@conversation_view')

    def _globally_enable_discussion(self, value):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = value

    def _enable_discussion_on_portal_type(self, portal_type, allow_discussion):
        portal_types = getToolByName(self.portal, 'portal_types')
        document_fti = getattr(portal_types, portal_type)
        document_fti.manage_changeProperties(allow_discussion=allow_discussion)

    def test_conversation_is_not_enabled_by_default(self):
        if DEXTERITY:
            conversation = self._makeOne(self.portal.doc1)
            self.assertFalse(conversation.enabled())

    def test_conversation_is_not_enabled_by_default_on_portal_type(self):
        if DEXTERITY:
            self._globally_enable_discussion(True)
            conversation = self._makeOne(self.portal.doc1)
            self.assertFalse(conversation.enabled())

    def test_conversation_needs_to_be_enabled_globally_and_for_type(self):
        if DEXTERITY:
            self._globally_enable_discussion(True)
            self._enable_discussion_on_portal_type('Document', True)
            conversation = self._makeOne(self.portal.doc1)
            self.assertTrue(conversation.enabled())

    def test_disable_discussion(self):
        if DEXTERITY:
            self._globally_enable_discussion(True)
            self._enable_discussion_on_portal_type('Document', True)
            self.portal.doc1.allow_discussion = False
            conversation = self._makeOne(self.portal.doc1)
            self.assertFalse(conversation.enabled())

    def test_enable_discussion(self):
        if DEXTERITY:
            self._globally_enable_discussion(True)
            self._enable_discussion_on_portal_type('Document', True)
            self.portal.doc1.allow_discussion = True
            conversation = self._makeOne(self.portal.doc1)
            self.assertTrue(conversation.enabled())


class RepliesTest(unittest.TestCase):

    # test the IReplies adapter on a conversation

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_add_comment(self):
        # Add comments to a ConversationReplies adapter

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        replies = IReplies(conversation)

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'

        new_id = replies.addComment(comment)

        # check that replies provides the IReplies interface
        self.assertTrue(IReplies.providedBy(replies))

        # Make sure our comment was added
        self.assertTrue(new_id in replies)

        # Make sure it is also reflected in the conversation
        self.assertTrue(new_id in conversation)

        self.assertEqual(conversation[new_id].comment_id, new_id)

    def test_delete_comment(self):
        # Create and remove a comment and check if the replies adapter
        # has been updated accordingly

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        replies = IReplies(conversation)

        # Add a comment.
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'

        new_id = replies.addComment(comment)

        # make sure the comment has been added
        self.assertEqual(len(replies), 1)

        # delete the comment we just created
        del replies[new_id]

        # make sure there is no comment left in the conversation
        self.assertEqual(len(replies), 0)

    def test_dict_api(self):
        # This test is for the ConversationReplies as well as the
        # CommentReplies adapter.
        #
        # Ensure all operations use only top-level comments. Add some
        # deeper children and ensure that these are not exposed through the
        # IReplies dict.

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        replies = IReplies(conversation)

        # Create a nested comment structure:
        #
        # Conversation
        # +- Comment 1
        #    +- Comment 1_1
        #    |  +- Comment 1_1_1
        #    +- Comment 1_2
        # +- Comment 2
        #    +- Comment 2_1

        # Create all comments
        comment1 = createObject('plone.Comment')
        comment1.text = 'Comment text'

        comment1_1 = createObject('plone.Comment')
        comment1_1.text = 'Comment text'

        comment1_1_1 = createObject('plone.Comment')
        comment1_1_1.text = 'Comment text'

        comment1_2 = createObject('plone.Comment')
        comment1_2.text = 'Comment text'

        comment2 = createObject('plone.Comment')
        comment2.text = 'Comment text'

        comment2_1 = createObject('plone.Comment')
        comment2_1.text = 'Comment text'

        # Create the nested comment structure
        new_id_1 = replies.addComment(comment1)
        comment1 = self.portal.doc1.restrictedTraverse(
            '++conversation++default/{0}'.format(new_id_1)
        )
        replies_to_comment1 = IReplies(comment1)
        new_id_2 = replies.addComment(comment2)
        comment2 = self.portal.doc1.restrictedTraverse(
            '++conversation++default/{0}'.format(new_id_2)
        )
        replies_to_comment2 = IReplies(comment2)

        new_id_1_1 = replies_to_comment1.addComment(comment1_1)
        comment1_1 = self.portal.doc1.restrictedTraverse(
            '++conversation++default/{0}'.format(new_id_1_1)
        )
        replies_to_comment1_1 = IReplies(comment1_1)
        replies_to_comment1_1.addComment(comment1_1_1)

        replies_to_comment1.addComment(comment1_2)

        replies_to_comment2.addComment(comment2_1)

        # check that replies only contain the direct comments
        # and no comments deeper than 1
        self.assertEqual(conversation.total_comments(), 6)
        self.assertEqual(len(replies), 2)
        self.assertEqual(len(replies_to_comment1), 2)
        self.assertEqual(len(replies_to_comment1_1), 1)
        self.assertEqual(len(replies_to_comment2), 1)
