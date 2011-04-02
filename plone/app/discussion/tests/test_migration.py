from datetime import datetime
from DateTime import DateTime

import unittest

from zope.annotation.interfaces import IAnnotations

from Products.CMFCore.utils import getToolByName

from Products.PloneTestCase.ptc import PloneTestCase

from plone.app.discussion.tests.layer import DiscussionLayer

from plone.app.discussion.browser.migration import View

from plone.app.discussion.interfaces import IConversation, IComment

class MigrationTest(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory(id='doc',
                                  title='Document 1',
                                  type_name='Document')
        # Create a document
        self.discussion = getToolByName(self.portal, 'portal_discussion', None)
        self.discussion.overrideDiscussionFor(self.portal.doc, 1)
        # Publish it
        self.workflow = self.portal.portal_workflow
        self.workflow.doActionFor(self.portal.doc, 'publish')

        request = self.app.REQUEST
        request.set("test", True)
        context = getattr(self.portal, 'doc')
        self.view = View(context, request)
        self.workflow.setChainForPortalTypes(('Discussion Item',),
                                             'comment_review_workflow')

        self.doc = self.portal.doc

    def test_migrate_comment(self):

        # Create a comment
        talkback = self.discussion.getDiscussionFor(self.doc)
        self.doc.talkback.createReply('My Title', 'My Text', Creator='Jim')
        reply = talkback.getReplies()[0]
        reply.setReplyTo(self.doc)
        reply.creation_date = DateTime(2003, 3, 11, 9, 28, 6)
        reply.modification_date = DateTime(2009, 7, 12, 19, 38, 7)
        self.assertEquals(reply.Title(), 'My Title')
        self.assertEquals(reply.EditableBody(), 'My Text')
        self.failUnless('Jim' in reply.listCreators())
        self.assertEquals(talkback.replyCount(self.doc), 1)
        self.assertEquals(reply.inReplyTo(), self.doc)

        # Call migration script
        self.view()

        # Make sure a conversation has been created
        self.failUnless('plone.app.discussion:conversation' in
                        IAnnotations(self.doc))
        conversation = IConversation(self.doc)

        # Check migration
        self.assertEquals(conversation.total_comments, 1)
        self.failUnless(conversation.getComments().next())
        comment1 = conversation.values()[0]
        self.assert_(IComment.providedBy(comment1))
        self.assertEquals(comment1.Title(), 'Jim on Document 1')
        self.assertEquals(comment1.text, 'My Text')
        self.assertEquals(comment1.Creator(), 'Jim')
        self.assertEquals(comment1.creation_date,
                          datetime(2003, 3, 11, 9, 28, 6))
        self.assertEquals(comment1.modification_date,
                          datetime(2009, 7, 12, 19, 38, 7))
        self.assertEquals(
            [{'comment': comment1,     'depth': 0, 'id': long(comment1.id)},]
            , list(conversation.getThreads()))
        self.failIf(self.doc.talkback)

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

        self.assertEquals(len(talkback.getReplies()), 1)
        self.assertEquals(len(talkback_comment1.getReplies()), 1)
        self.assertEquals(len(talkback_comment1_1.getReplies()), 0)

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
        self.assertEquals(conversation.total_comments, 8)

        comment1 = conversation.values()[0]
        comment1_1 = conversation.values()[1]
        comment1_1_1 = conversation.values()[2]
        comment1_1_1_1 = conversation.values()[3]
        comment1_2 = conversation.values()[4]
        comment1_3 = conversation.values()[5]
        comment1_4 = conversation.values()[6]
        comment2 = conversation.values()[7]

        self.assertEquals(
        [{'comment': comment1,       'depth': 0, 'id': long(comment1.id)},
         {'comment': comment1_1,     'depth': 1, 'id': long(comment1_1.id)},
         {'comment': comment1_1_1,   'depth': 2, 'id': long(comment1_1_1.id)},
         {'comment': comment1_1_1_1, 'depth': 3, 'id': long(comment1_1_1_1.id)},
         {'comment': comment1_2,     'depth': 1, 'id': long(comment1_2.id)},
         {'comment': comment1_3,     'depth': 1, 'id': long(comment1_3.id)},
         {'comment': comment1_4,     'depth': 1, 'id': long(comment1_4.id)},
         {'comment': comment2,       'depth': 0, 'id': long(comment2.id)},
        ], list(conversation.getThreads()))

        talkback = self.discussion.getDiscussionFor(self.doc)
        self.assertEquals(len(talkback.getReplies()), 0)

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

        self.assertEquals(len(talkback.getReplies()), 1)
        self.assertEquals(len(talkback_comment1.getReplies()), 1)
        self.assertEquals(len(talkback_comment1_1.getReplies()), 0)

        def deny_comments(reply):
            return False

        # Call migration script
        self.view(filter_callback=deny_comments)

        # Check migration
        conversation = IConversation(self.doc)
        self.assertEquals(conversation.total_comments, 0)
        talkback = self.discussion.getDiscussionFor(self.doc)
        self.assertEquals(len(talkback.getReplies()), 0)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
