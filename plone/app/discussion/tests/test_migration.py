from datetime import datetime
from DateTime import DateTime

import unittest2 as unittest

from zope.annotation.interfaces import IAnnotations

from Products.CMFCore.utils import getToolByName

from plone.app.testing import TEST_USER_ID, setRoles

from plone.app.discussion.testing import  \
        PLONE_APP_DISCUSSION_INTEGRATION_TESTING

from plone.app.discussion.browser.migration import View

from plone.app.discussion.interfaces import IConversation, IComment


class MigrationTest(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.portal.invokeFactory(id='doc',
                                  title='Document 1',
                                  type_name='Document')
        # Create a document
        self.discussion = getToolByName(self.portal, 'portal_discussion', None)
        self.discussion.overrideDiscussionFor(self.portal.doc, 1)
        # Publish it
        self.workflowTool = getToolByName(self.portal, 'portal_workflow')
        self.workflowTool.setDefaultChain('simple_publication_workflow')
        self.workflowTool.doActionFor(self.portal.doc, 'publish')

        self.request.set("test", True)
        self.view = View(self.portal, self.request)
        self.workflowTool.setChainForPortalTypes(('Discussion Item',),
                                             'comment_review_workflow')

        self.doc = self.portal.doc

    def test_migrate_comment(self):

        # Create a comment
        talkback = self.discussion.getDiscussionFor(self.doc)
        self.doc.talkback.createReply('My Title', 'My Text', Creator='Jim')
        reply = talkback.getReplies()[0]
        reply.setReplyTo(self.doc)
        reply.creation_date = DateTime(2003, 3, 11, 9, 28, 6, 'GMT')
        reply.modification_date = DateTime(2009, 7, 12, 19, 38, 7, 'GMT')
        self.assertEqual(reply.Title(), 'My Title')
        self.assertEqual(reply.EditableBody(), 'My Text')
        self.assertTrue('Jim' in reply.listCreators())
        self.assertEqual(talkback.replyCount(self.doc), 1)
        self.assertEqual(reply.inReplyTo(), self.doc)

        # Call migration script
        self.view()

        # Make sure a conversation has been created
        self.assertTrue('plone.app.discussion:conversation' in
                        IAnnotations(self.doc))
        conversation = IConversation(self.doc)

        # Check migration
        self.assertEqual(conversation.total_comments, 1)
        self.assertTrue(conversation.getComments().next())
        comment1 = conversation.values()[0]
        self.assertTrue(IComment.providedBy(comment1))
        self.assertEqual(comment1.Title(), 'My Title')
        self.assertEqual(comment1.text, '<p>My Text</p>\n')
        self.assertEqual(comment1.mime_type, 'text/html')
        self.assertEqual(comment1.Creator(), 'Jim')
        self.assertEqual(comment1.creation_date,
                          datetime(2003, 3, 11, 9, 28, 6))
        self.assertEqual(comment1.modification_date,
                          datetime(2009, 7, 12, 19, 38, 7))
        self.assertEqual([
            {'comment': comment1, 'depth': 0, 'id': long(comment1.id)}
            ], list(conversation.getThreads()))
        self.assertFalse(self.doc.talkback)

    def test_migrate_nested_comments(self):
        # Create some nested comments and migrate them
        #
        # self.doc
        # +- First comment
        #    +- Re: First comment
        #       + Re: Re: First comment
        #         + Re: Re: Re: First comment
        #    +- Re: First comment (2)
        #    +- Re: First comment (3)
        #    +- Re: First comment (4)
        # +- Second comment

        talkback = self.discussion.getDiscussionFor(self.doc)

        # First comment
        talkback.createReply(title='First comment',
                             text='This is my first comment.')
        comment1 = talkback.getReplies()[0]
        talkback_comment1 = self.discussion.getDiscussionFor(comment1)

        # Re: First comment
        talkback_comment1.createReply(title='Re: First comment',
                                      text='This is my first reply.')
        comment1_1 = talkback_comment1.getReplies()[0]
        talkback_comment1_1 = self.discussion.getDiscussionFor(comment1_1)

        self.assertEqual(len(talkback.getReplies()), 1)
        self.assertEqual(len(talkback_comment1.getReplies()), 1)
        self.assertEqual(len(talkback_comment1_1.getReplies()), 0)

        #Re: Re: First comment
        talkback_comment1_1.createReply(title='Re: Re: First comment',
                                        text='This is my first re-reply.')
        comment1_1_1 = talkback_comment1_1.getReplies()[0]
        talkback_comment1_1_1 = self.discussion.getDiscussionFor(comment1_1_1)

        # Re: Re: Re: First comment
        talkback_comment1_1_1.createReply(title='Re: Re: Re: First comment',
                                          text='This is my first re-re-reply.')

        # Re: First comment (2)
        talkback_comment1.createReply(title='Re: First comment (2)',
                                      text='This is my first reply (2).')

        # Re: First comment (3)
        talkback_comment1.createReply(title='Re: First comment (3)',
                                      text='This is my first reply (3).')

        # Re: First comment (4)
        talkback_comment1.createReply(title='Re: First comment (4)',
                                      text='This is my first reply (4).')

        # Second comment
        talkback.createReply(title='Second comment',
                             text='This is my second comment.')

        # Call migration script
        self.view()

        # Check migration
        conversation = IConversation(self.doc)
        self.assertEqual(conversation.total_comments, 8)

        comment1 = conversation.values()[0]
        comment1_1 = conversation.values()[1]
        comment1_1_1 = conversation.values()[2]
        comment1_1_1_1 = conversation.values()[3]
        comment1_2 = conversation.values()[4]
        comment1_3 = conversation.values()[5]
        comment1_4 = conversation.values()[6]
        comment2 = conversation.values()[7]

        self.assertEqual(
        [{'comment': comment1,       'depth': 0, 'id': long(comment1.id)},
         {'comment': comment1_1,     'depth': 1, 'id': long(comment1_1.id)},
         {'comment': comment1_1_1,   'depth': 2, 'id': long(comment1_1_1.id)},
         {'comment': comment1_1_1_1, 'depth': 3,
          'id': long(comment1_1_1_1.id)},
         {'comment': comment1_2,     'depth': 1, 'id': long(comment1_2.id)},
         {'comment': comment1_3,     'depth': 1, 'id': long(comment1_3.id)},
         {'comment': comment1_4,     'depth': 1, 'id': long(comment1_4.id)},
         {'comment': comment2,       'depth': 0, 'id': long(comment2.id)},
        ], list(conversation.getThreads()))

        talkback = self.discussion.getDiscussionFor(self.doc)
        self.assertEqual(len(talkback.getReplies()), 0)

    def test_migrate_nested_comments_with_filter(self):
        # Create some nested comments and migrate them.
        # But use a filter that filters the top-level comment.
        # All the comments should be removed, but not migrated.
        #
        # self.doc
        # +- First comment
        #    +- Re: First comment

        talkback = self.discussion.getDiscussionFor(self.doc)

        # First comment
        talkback.createReply(title='First comment',
                             text='This is my first comment.')
        comment1 = talkback.getReplies()[0]
        talkback_comment1 = self.discussion.getDiscussionFor(comment1)

        # Re: First comment
        talkback_comment1.createReply(title='Re: First comment',
                                      text='This is my first reply.')
        comment1_1 = talkback_comment1.getReplies()[0]
        talkback_comment1_1 = self.discussion.getDiscussionFor(comment1_1)

        self.assertEqual(len(talkback.getReplies()), 1)
        self.assertEqual(len(talkback_comment1.getReplies()), 1)
        self.assertEqual(len(talkback_comment1_1.getReplies()), 0)

        def deny_comments(reply):
            return False

        # Call migration script
        self.view(filter_callback=deny_comments)

        # Check migration
        conversation = IConversation(self.doc)
        self.assertEqual(conversation.total_comments, 0)
        talkback = self.discussion.getDiscussionFor(self.doc)
        self.assertEqual(len(talkback.getReplies()), 0)

    def test_migrate_no_comment(self):

        # Call migration script
        self.view()

        # Make sure no conversation has been created
        self.assertTrue('plone.app.discussion:conversation' not in
                     IAnnotations(self.doc))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
