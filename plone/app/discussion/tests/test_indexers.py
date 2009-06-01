import unittest

from datetime import datetime, timedelta
from DateTime import DateTime

from zope.component import createObject

from Products.PloneTestCase.ptc import PloneTestCase
from plone.app.discussion.tests.layer import DiscussionLayer

from plone.app.discussion.interfaces import IConversation

from plone.indexer import indexer
from plone.indexer.delegate import DelegatingIndexerFactory

from zope.component import provideAdapter

from plone.app.discussion import catalog

class IndexersTest(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        # First we need to create some content.
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
        provideAdapter(catalog.comment_title, name='title')

    def test_comment_title(self):

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

        self.assertEquals(catalog.comment_title(comment)(), 'Comment 1')
        self.assert_(isinstance(catalog.comment_title, DelegatingIndexerFactory))

    def test_comment_description(self):
        # Create a 50 word comment and make sure the description returns
        # only the first 25 words

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

        # Add a comment. Note: in real life, we always create comments via the factory
        # to allow different factories to be swapped in

        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.'

        new_id = conversation.addComment(comment)

        self.assertEquals(catalog.comment_description(comment)(), 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At...')
        self.assert_(isinstance(catalog.comment_description, DelegatingIndexerFactory))

    def test_dates(self):
        # Test if created, modified, effective etc. are set correctly

        # Create a conversation. In this case we doesn't assign it to an
        # object, as we just want to check the Conversation object API.
        conversation = IConversation(self.portal.doc1)

        # Pretend that we have traversed to the comment by aq wrapping it.
        conversation = conversation.__of__(self.portal.doc1)

        # Add a comment. Note: in real life, we always create comments via the factory
        # to allow different factories to be swapped in

        comment = createObject('plone.Comment')
        comment.title = 'Comment 1'
        comment.text = 'Comment Text'
        comment.creation_date = datetime(2006, 9, 17, 14, 18, 12)
        comment.modification_date = datetime(2008, 3, 12, 7, 32, 52)

        new_id = conversation.addComment(comment)

        # Check the indexes
        self.assertEquals(catalog.created(comment)(), DateTime(2006, 9, 17, 14, 18, 12))
        self.assertEquals(catalog.modified(comment)(), DateTime(2008, 3, 12, 7, 32, 52))

    def test_searchable_text(self):
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

        self.assertEquals(catalog.comment_searchable_text(comment)(), ('Comment 1', 'Comment text'))
        self.assert_(isinstance(catalog.comment_searchable_text, DelegatingIndexerFactory))

    def test_creator(self):
        pass

    def test_title(self):
        pass

    def test_in_reply_to(self):
        pass

    def test_path(self):
        pass

    def test_review_state(self):
        pass

    def test_object_provides(self):
        pass

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)