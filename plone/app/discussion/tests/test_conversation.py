import unittest
from datetime import datetime, timedelta

from plone.registry import Registry

from zope.component import createObject

from Acquisition import aq_base, aq_parent, aq_inner

from plone.app.vocabularies.types import BAD_TYPES

from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.ptc import PloneTestCase
from plone.app.discussion.tests.layer import DiscussionLayer

from plone.app.discussion.interfaces import IConversation, IComment, IReplies, IDiscussionSettings

class ConversationTest(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        # First we need to create some content.
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
        self.portal_discussion = getToolByName(self.portal, 'portal_discussion', None)

    def test_add_comment(self):
        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

        # Add a comment. Note: in real life, we always create comments via the factory
        # to allow different factories to be swapped in

        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'

        new_id = conversation.addComment(comment)

        # Check that the conversation methods return the correct data
        self.assert_(isinstance(comment.comment_id, long))
        self.assert_(IComment.providedBy(conversation[new_id]))
        self.assertEquals(aq_base(conversation[new_id].__parent__), aq_base(conversation))
        self.assertEquals(new_id, comment.comment_id)
        self.assertEquals(len(list(conversation.getComments())), 1)
        # XXX: not yet implemented
        # self.assertEquals(len(conversation.getThreads()), 1)
        self.assertEquals(conversation.total_comments, 1)
        self.assert_(conversation.last_comment_date - datetime.now() < timedelta(seconds=1))

    def test_delete_comment(self):
        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

        # Add a comment. Note: in real life, we always create comments via the factory
        # to allow different factories to be swapped in

        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'

        new_id = conversation.addComment(comment)

        # make sure the comment has been added
        self.assertEquals(len(list(conversation.getComments())), 1)
        # XXX: not yet implemented
        # self.assertEquals(len(conversation.getThreads()), 1)
        self.assertEquals(conversation.total_comments, 1)

        # delete the comment we just created
        del conversation[new_id]

        # make sure there is no comment left in the conversation
        self.assertEquals(len(list(conversation.getComments())), 0)

        # XXX: not yet implemented
        # self.assertEquals(len(conversation.getThreads()), 0)
        self.assertEquals(conversation.total_comments, 0)

    def test_delete_recursive(self):
        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

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
        comment1.title = 'Comment 1'
        comment1.text = 'Comment text'

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

        del conversation[new_id_1]

        self.assertEquals(
            [{'comment': comment2,     'depth': 0, 'id': new_id_2},
             {'comment': comment2_1,   'depth': 1, 'id': new_id_2_1},
            ], list(conversation.getThreads()))


    def test_dict_operations(self):
        # test dict operations and acquisition wrapping

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

        # Add a comment. Note: in real life, we always create comments via the factory
        # to allow different factories to be swapped in

        comment1 = createObject('plone.Comment')
        comment1.title = 'Comment 1'
        comment1.text = 'Comment text'

        new_id1 = conversation.addComment(comment1)

        comment2 = createObject('plone.Comment')
        comment2.title = 'Comment 2'
        comment2.text = 'Comment text'

        new_id2 = conversation.addComment(comment2)

        # check if get returns a comment object, and None if the key
        # can not be found
        self.failUnless(IComment.providedBy(conversation.get(new_id1)))
        self.failUnless(IComment.providedBy(conversation.get(new_id2)))
        self.assertEquals(conversation.get(123), None)

        # check if keys return the ids of all comments
        self.assertEquals(len(conversation.keys()), 2)
        self.failUnless(new_id1 in conversation.keys())
        self.failUnless(new_id2 in conversation.keys())
        self.failIf(123 in conversation.keys())

        # check if items returns (key, comment object) pairs
        self.assertEquals(len(conversation.items()), 2)
        self.failUnless((new_id1, comment1) in conversation.items())
        self.failUnless((new_id2, comment2) in conversation.items())

        # check if values returns the two comment objects
        self.assertEquals(len(conversation.values()), 2)
        self.failUnless(comment1 in conversation.values())
        self.failUnless(comment2 in conversation.values())

        # check if comment ids are in iterkeys
        self.failUnless(new_id1 in conversation.iterkeys())
        self.failUnless(new_id2 in conversation.iterkeys())
        self.failIf(123 in conversation.iterkeys())

        # check if comment objects are in itervalues
        self.failUnless(comment1 in conversation.itervalues())
        self.failUnless(comment2 in conversation.itervalues())

        # check if iteritems returns (key, comment object) pairs
        self.failUnless((new_id1, comment1) in conversation.iteritems())
        self.failUnless((new_id2, comment2) in conversation.iteritems())

        # TODO test acquisition wrapping
        #self.failUnless(aq_base(aq_parent(comment1)) is conversation)

    def test_total_comments(self):
        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

        # Add a three comments. Note: in real life, we always create
        # comments via the factory to allow different factories to be
        # swapped in

        comment1 = createObject('plone.Comment')
        comment1.title = 'Comment 1'
        comment1.text = 'Comment text'

        comment2 = createObject('plone.Comment')
        comment2.title = 'Comment 2'
        comment2.text = 'Comment text'

        comment3 = createObject('plone.Comment')
        comment3.title = 'Comment 3'
        comment3.text = 'Comment text'

        new_comment1_id = conversation.addComment(comment1)
        new_comment2_id = conversation.addComment(comment2)
        new_comment3_id = conversation.addComment(comment3)

        self.assertEquals(conversation.total_comments, 3)

    def test_commentators(self):
        # add and remove a few comments to make sure the commentators
        # property returns a true set

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

        # Add a four comments from three different users
        # Note: in real life, we always create
        # comments via the factory to allow different factories to be
        # swapped in
        comment1 = createObject('plone.Comment')
        comment1.title = 'Comment 1'
        comment1.text = 'Comment text'
        comment1.author_username = "Jim"
        new_comment1_id = conversation.addComment(comment1)

        comment2 = createObject('plone.Comment')
        comment2.title = 'Comment 2'
        comment2.text = 'Comment text'
        comment2.author_username = "Joe"
        new_comment2_id = conversation.addComment(comment2)

        comment3 = createObject('plone.Comment')
        comment3.title = 'Comment 3'
        comment3.text = 'Comment text'
        comment3.author_username = "Jack"
        new_comment3_id = conversation.addComment(comment3)

        comment4 = createObject('plone.Comment')
        comment4.title = 'Comment 3'
        comment4.text = 'Comment text'
        comment4.author_username = "Jack"
        new_comment4_id = conversation.addComment(comment4)

        # check if all commentators are in the commentators list
        self.assertEquals(conversation.total_comments, 4)
        self.failUnless('Jim' in conversation.commentators)
        self.failUnless('Joe' in conversation.commentators)
        self.failUnless('Jack' in conversation.commentators)

        # remove the comment from Jack
        del conversation[new_comment3_id]

        # check if Jack is still in the commentators list (since
        # he had added two comments)
        self.failUnless('Jim' in conversation.commentators)
        self.failUnless('Joe' in conversation.commentators)
        self.failUnless('Jack' in conversation.commentators)
        self.assertEquals(conversation.total_comments, 3)

        # remove the second comment from Jack
        del conversation[new_comment4_id]

        # check if Jack has been removed from the commentators list
        self.failUnless('Jim' in conversation.commentators)
        self.failUnless('Joe' in conversation.commentators)
        self.failIf('Jack' in conversation.commentators)
        self.assertEquals(conversation.total_comments, 2)

    def test_last_comment_date(self):
        # add and remove some comments and check if last_comment_date
        # is properly updated

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

        # Add a three comments that are at least one day old
        # Note: in real life, we always create
        # comments via the factory to allow different factories to be
        # swapped in
        comment1 = createObject('plone.Comment')
        comment1.title = 'Comment 1'
        comment1.text = 'Comment text'
        comment1.creation_date = datetime.now() - timedelta(4)
        new_comment1_id = conversation.addComment(comment1)

        comment2 = createObject('plone.Comment')
        comment2.title = 'Comment 2'
        comment2.text = 'Comment text'
        comment2.creation_date = datetime.now() - timedelta(2)
        new_comment2_id = conversation.addComment(comment2)

        comment3 = createObject('plone.Comment')
        comment3.title = 'Comment 3'
        comment3.text = 'Comment text'
        comment3.creation_date = datetime.now() - timedelta(1)
        new_comment3_id = conversation.addComment(comment3)

        # check if the latest comment is exactly one day old
        self.assert_(conversation.last_comment_date < datetime.now() - timedelta(hours=23, minutes=59, seconds=59))
        self.assert_(conversation.last_comment_date > datetime.now() - timedelta(days=1, seconds=1))

        # remove the latest comment
        del conversation[new_comment3_id]

        # check if the latest comment has been updated
        # the latest comment should be exactly two days old
        self.assert_(conversation.last_comment_date < datetime.now() - timedelta(days=1, hours=23, minutes=59, seconds=59))
        self.assert_(conversation.last_comment_date > datetime.now() - timedelta(days=2, seconds=1))

        # remove the latest comment again
        del conversation[new_comment2_id]

        # check if the latest comment has been updated
        # the latest comment should be exactly four days old
        self.assert_(conversation.last_comment_date < datetime.now() - timedelta(days=3, hours=23, minutes=59, seconds=59))
        self.assert_(conversation.last_comment_date > datetime.now() - timedelta(days=4, seconds=1))

    def test_get_comments_full(self):
        pass

    def test_get_comments_batched(self):
        pass

    def test_get_threads(self):

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

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
        comment1.title = 'Comment 1'
        comment1.text = 'Comment text'

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

        self.assertEquals(
            [{'comment': comment1,     'depth': 0, 'id': new_id_1},
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

        conversation = self.portal.doc1.restrictedTraverse('++conversation++default')
        self.assert_(IConversation.providedBy(conversation))

        self.assertEquals(('', 'plone', 'doc1', '++conversation++default'), conversation.getPhysicalPath())
        self.assertEquals('plone/doc1/%2B%2Bconversation%2B%2Bdefault', conversation.absolute_url())

    def test_discussion_item_not_in_bad_types(self):
        self.failIf('Discussion Item' in BAD_TYPES)

    def test_allow_discussion(self):
        # We currently have four layers of testing if discussion is allowed
        # on a particular content object:
        #
        # 1) Check if discussion is allowed globally
        # 2) Check if discussion is allowed on a particular content type
        # 3) If the content object is located in a folder, check if the folder
        #    has discussion allowed
        # 4) Check if discussion is allowed on this particular content object
        #
        pass

    def test_allow_discussion_globally(self):

        registry = Registry()
        registry.register_interface(IDiscussionSettings)
        globally_enabled_record = registry.records['plone.app.discussion.interfaces.IDiscussionSettings.globally_enabled']

        # Check if a record for globally_enabled is in the registry
        # with the correct default value (True).
        self.failUnless('globally_enabled' in IDiscussionSettings)
        self.assertEquals(registry['plone.app.discussion.interfaces.IDiscussionSettings.globally_enabled'], True)

        # Set the registry value for globally_enabled to False

        # Todo: Add a comment. Then set globally_enabled to false and check if
        # comments are disabled.

    def test_allow_discussion_for_content_type(self):

        portal_types = getToolByName(self.portal, 'portal_types')

        # Get the FTI for some content types
        document_fti = getattr(portal_types, 'Document')
        news_item_fti = getattr(portal_types, 'News Item')
        folder_fti = getattr(portal_types, 'Folder')

        # By default, discussion is only allowed for Document and News Item
        # XXX: allow_discussion always returns False !!!
        #self.assertEquals(document_fti.getProperty('allow_discussion'), True)
        #self.assertEquals(news_item_fti.getProperty('allow_discussion'), True)

        self.assertEquals(folder_fti.getProperty('allow_discussion'), False)

        # Disallow discussion for the News Item content types
        news_item_fti.manage_changeProperties(allow_discussion = False)

        # Allow discussion for the Folder content types
        folder_fti.manage_changeProperties(allow_discussion = True)

        # Check if discussion for News Item content types is disallowed
        self.assertEquals(news_item_fti.getProperty('allow_discussion'), False)

        # Check if discussion for Folder content types is allowed
        self.assertEquals(folder_fti.getProperty('allow_discussion'), True)

    def test_allow_discussion_for_folder(self):
        # Create a folder with two content objects. Change allow_discussion
        # and check if the content objects inside the folder are commentable.
        pass

    def test_allow_discussion_on_content_object(self):
        pass

class RepliesTest(PloneTestCase):

    # test the IReplies adapter on a conversation

    layer = DiscussionLayer

    def afterSetUp(self):
        # First we need to create some content.
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')

    def test_add_comment(self):
        # Add comments to a ConversationReplies adapter

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

        replies = IReplies(conversation)

        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'

        new_id = replies.addComment(comment)

        # check that replies provides the IReplies interface
        self.assert_(IReplies.providedBy(replies))

        # Make sure our comment was added
        self.failUnless(new_id in replies)

        # Make sure it is also reflected in the conversation
        self.failUnless(new_id in conversation)

        self.assertEquals(conversation[new_id].comment_id, new_id)

    def test_delete_comment(self):
        # Create and remove a comment and check if the replies adapter
        # has been updated accordingly

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

        replies = IReplies(conversation)

        # Add a comment.
        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'

        new_id = replies.addComment(comment)

        # make sure the comment has been added
        self.assertEquals(len(replies), 1)

        # delete the comment we just created
        del replies[new_id]

        # make sure there is no comment left in the conversation
        self.assertEquals(len(replies), 0)

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

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

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
        comment1.title = 'Comment 1'
        comment1.text = 'Comment text'

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
        new_id_1 = replies.addComment(comment1)
        replies_to_comment1 = IReplies(comment1)
        new_id_2 = replies.addComment(comment2)
        replies_to_comment2 = IReplies(comment2)

        new_id_1_1 = replies_to_comment1.addComment(comment1_1)
        replies_to_comment1_1 = IReplies(comment1_1)
        new_id_1_1_1 = replies_to_comment1_1.addComment(comment1_1_1)

        new_id_1_2 = replies_to_comment1.addComment(comment1_2)

        new_id_2_1 = replies_to_comment2.addComment(comment2_1)

        # check that replies only contain the direct comments
        # and no comments deeper than 1
        self.assertEquals(conversation.total_comments, 6)
        self.assertEquals(len(replies), 2)
        self.assertEquals(len(replies_to_comment1), 2)
        self.assertEquals(len(replies_to_comment1_1), 1)
        self.assertEquals(len(replies_to_comment2), 1)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)