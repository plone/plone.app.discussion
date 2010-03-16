import unittest
from datetime import datetime, timedelta

from zope.component import createObject, queryUtility

from Acquisition import aq_base, aq_parent, aq_inner

from plone.app.vocabularies.types import BAD_TYPES

from plone.registry.interfaces import IRegistry

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
        self.typetool = typetool
        self.portal_discussion = getToolByName(self.portal, 'portal_discussion', None)

    def test_add_comment(self):
        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

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
        self.assertEquals(sum(1 for w in conversation.getThreads()), 1)
        self.assertEquals(conversation.total_comments, 1)
        self.assert_(conversation.last_comment_date - datetime.now() < timedelta(seconds=1))

    def test_delete_comment(self):
        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Add a comment. Note: in real life, we always create comments via the factory
        # to allow different factories to be swapped in

        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'

        new_id = conversation.addComment(comment)

        # make sure the comment has been added
        self.assertEquals(len(list(conversation.getComments())), 1)
        self.assertEquals(sum(1 for w in conversation.getThreads()), 1)
        self.assertEquals(conversation.total_comments, 1)

        # delete the comment we just created
        del conversation[new_id]

        # make sure there is no comment left in the conversation
        self.assertEquals(len(list(conversation.getComments())), 0)
        self.assertEquals(sum(1 for w in conversation.getThreads()), 0)
        self.assertEquals(conversation.total_comments, 0)

    def test_delete_recursive(self):
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

    def test_delete_comment_when_content_object_is_deleted(self):
        # Make sure all comments of a content object are deleted when the object
        # itself is deleted.
        conversation = IConversation(self.portal.doc1)
        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment text'
        new_id = conversation.addComment(comment)

        # Delete the content object
        self.portal.manage_delObjects(['doc1'])
        
        # Make sure the comment has been deleted as well
        self.assertEquals(len(list(conversation.getComments())), 0)
        self.assertEquals(sum(1 for w in conversation.getThreads()), 0)
        self.assertEquals(conversation.total_comments, 0) 

    def test_allow_discussion(self):
        # This is not a real test! It's only there to understand the
        # allow discussion attribute. Maybe we should remove this at
        # some point.

        # 1) allow_discussion attribute: Every content object in Plone
        # has a allow_discussion attribute. By default it is set to None.


        # Create a conversation.
        conversation = IConversation(self.portal.doc1)

        # By default, discussion is disabled for all content types
        portal_types = getToolByName(self.portal, 'portal_types')
        from plone.app.vocabularies.types import BAD_TYPES
        for type in list(portal_types):
            type_fti = getattr(portal_types, type)
            if type not in BAD_TYPES:
                if type != 'Discussion Item':
                    self.failIf(type_fti.allowDiscussion())

        # By default, allow_discussion on newly created content objects is
        # set to False
        portal_discussion = getToolByName(self.portal, 'portal_discussion')
        self.assertEquals(portal_discussion.isDiscussionAllowedFor(self.portal.doc1), False)
        self.assertEquals(self.portal.doc1.getTypeInfo().allowDiscussion(), False)

        # The allow discussion flag is None by default
        self.failIf(getattr(self.portal.doc1, 'allow_discussion', None))

        # But isDiscussionAllowedFor, also checks if discussion is allowed on the
        # content type. So we allow discussion on the Document content type and
        # check if the Document object allows discussion now.
        document_fti = getattr(portal_types, 'Document')
        document_fti.manage_changeProperties(allow_discussion = True)
        self.assertEquals(portal_discussion.isDiscussionAllowedFor(self.portal.doc1), True)
        self.assertEquals(self.portal.doc1.getTypeInfo().allowDiscussion(), True)

        # We can also override the allow_discussion locally
        self.portal_discussion.overrideDiscussionFor(self.portal.doc1, False)
        # Check if the Document discussion is disabled
        self.assertEquals(portal_discussion.isDiscussionAllowedFor(self.portal.doc1), False)
        # Check that the local allow_discussion flag is now explicitly set to False
        self.assertEquals(getattr(self.portal.doc1, 'allow_discussion', None), False)

        # Disallow discussion on the Document content type again
        document_fti.manage_changeProperties(allow_discussion = False)
        self.assertEquals(portal_discussion.isDiscussionAllowedFor(self.portal.doc1), False)
        self.assertEquals(self.portal.doc1.getTypeInfo().allowDiscussion(), False)

        # Now we override allow_discussion again (True) for the Document
        # content object
        self.portal_discussion.overrideDiscussionFor(self.portal.doc1, True)
        self.assertEquals(portal_discussion.isDiscussionAllowedFor(self.portal.doc1), True)
        self.assertEquals(getattr(self.portal.doc1, 'allow_discussion', None), True)

    def test_disable_commenting_globally(self):

        # Create a conversation.
        conversation = IConversation(self.portal.doc1)

        # We have to allow discussion on Document content type, since
        # otherwise allow_discussion will always return False
        portal_types = getToolByName(self.portal, 'portal_types')
        document_fti = getattr(portal_types, 'Document')
        document_fti.manage_changeProperties(allow_discussion = True)

        # Check if conversation is enabled now
        self.assertEquals(conversation.enabled(), True)

        # Disable commenting in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = False

        # Check if commenting is disabled on the conversation
        self.assertEquals(conversation.enabled(), False)

        # Enable discussion again
        settings.globally_enabled = True
        self.assertEquals(conversation.enabled(), True)


    def test_allow_discussion_for_news_items(self):

        self.typetool.constructContent('News Item', self.portal, 'newsitem')
        newsitem = self.portal.newsitem
        conversation = IConversation(newsitem)

        # We have to allow discussion on Document content type, since
        # otherwise allow_discussion will always return False
        portal_types = getToolByName(self.portal, 'portal_types')
        document_fti = getattr(portal_types, 'News Item')
        document_fti.manage_changeProperties(allow_discussion = True)

        # Check if conversation is enabled now
        self.assertEquals(conversation.enabled(), True)

        # Disable commenting in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = False

        # Check if commenting is disabled on the conversation
        self.assertEquals(conversation.enabled(), False)

        # Enable discussion again
        settings.globally_enabled = True
        self.assertEquals(conversation.enabled(), True)

    def test_disable_commenting_for_content_type(self):

        # Create a conversation.
        conversation = IConversation(self.portal.doc1)

        # The Document content type is disabled by default
        self.assertEquals(conversation.enabled(), False)

        # Allow discussion on Document content type
        portal_types = getToolByName(self.portal, 'portal_types')
        document_fti = getattr(portal_types, 'Document')
        document_fti.manage_changeProperties(allow_discussion = True)

        # Check if conversation is enabled now
        self.assertEquals(conversation.enabled(), True)

        # Disallow discussion on Document content type
        portal_types = getToolByName(self.portal, 'portal_types')
        document_fti = getattr(portal_types, 'Document')
        document_fti.manage_changeProperties(allow_discussion = False)

        # Check if conversation is enabled now
        self.assertEquals(conversation.enabled(), False)

    def test_allow_discussion_on_folder(self):
        # The enabled method should always return False for the folder
        # itself.

        # Create a folder
        self.typetool.constructContent('Folder', self.portal, 'f1')
        f1 = self.portal.f1
        # Usually we don't create a conversation on a folder
        conversation = IConversation(self.portal.f1)

        # Allow discussion for the folder
        self.portal_discussion.overrideDiscussionFor(f1, True)

        # Allow discussion on Folder content type
        portal_types = getToolByName(self.portal, 'portal_types')
        document_fti = getattr(portal_types, 'Folder')
        document_fti.manage_changeProperties(allow_discussion = True)

        # Always return False
        self.failIf(conversation.enabled())

    def test_is_discussion_allowed_for_folder(self):
        # When a content item provides IFolderish from CMF and
        # does not provide INonStructuralFolder from Plone,
        # allow_discussion acts as an on/off flag for all items
        # in that folder, overriding settings for any parent folders,
        # and the for the FTI, but is overridden by child items and
        # folders further down.

        # Create a folder
        self.typetool.constructContent('Folder', self.portal, 'f1')
        f1 = self.portal.f1

        # Create a document inside the folder
        self.typetool.constructContent('Document', f1, 'doc1')
        doc1 = self.portal.f1.doc1
        doc1_conversation = IConversation(doc1)

        self.assertEquals(doc1_conversation.enabled(), False)

        # Allow commenting for the folder
        self.portal_discussion.overrideDiscussionFor(f1, True)

        # Check if the content objects allows discussion
        self.assertEquals(doc1_conversation.enabled(), True)

        # Turn commenting for the folder off
        self.portal_discussion.overrideDiscussionFor(f1, False)

        # Check if content objects do not allow discussion anymore
        self.assertEquals(doc1_conversation.enabled(), False)

    def test_is_discussion_allowed_on_content_object(self):
        # Allow discussion on a single content object

        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)

        # Create a conversation.
        conversation = IConversation(self.portal.doc1)

        # Discussion is disallowed by default
        self.assertEquals(conversation.enabled(), False)

        # Allow discussion on content object
        self.portal_discussion.overrideDiscussionFor(self.portal.doc1, True)

        # Check if discussion is now allowed on the content object
        self.assertEquals(conversation.enabled(), True)

        self.portal_discussion.overrideDiscussionFor(self.portal.doc1, False)
        self.assertEquals(conversation.enabled(), False)

    def test_dict_operations(self):
        # test dict operations and acquisition wrapping

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

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

        self.assertEquals(conversation.total_comments, 0)

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
        self.assert_(conversation.last_comment_date > datetime.now() - timedelta(days=4, seconds=2))

    def test_get_comments_full(self):
        pass

    def test_get_comments_batched(self):
        pass

    def test_get_threads(self):

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
        # XXX: conversation.absolute_url() returns different values dependent on
        # the Plone version used.
        # Plone 3.3:
        #self.assertEquals('plone/doc1/%2B%2Bconversation%2B%2Bdefault', conversation.absolute_url())
        # Plone 4:
        #self.assertEquals('http://nohost/plone/doc1/++conversation++default', conversation.absolute_url())

    def test_parent(self):
        # Check that conversation has a content object as parent

        # Create a conversation.
        conversation = IConversation(self.portal.doc1)

        # Check the parent
        self.failUnless(conversation.__parent__)
        self.failUnless(aq_parent(conversation))

        self.assertEquals(conversation.__parent__.getId(), 'doc1')


    def test_discussion_item_not_in_bad_types(self):
        self.failIf('Discussion Item' in BAD_TYPES)


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
        comment1 = self.portal.doc1.restrictedTraverse('++conversation++default/%s' % new_id_1)
        replies_to_comment1 = IReplies(comment1)
        new_id_2 = replies.addComment(comment2)
        comment2 = self.portal.doc1.restrictedTraverse('++conversation++default/%s' % new_id_2)
        replies_to_comment2 = IReplies(comment2)

        new_id_1_1 = replies_to_comment1.addComment(comment1_1)
        comment1_1 = self.portal.doc1.restrictedTraverse('++conversation++default/%s' % new_id_1_1)
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