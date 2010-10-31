# -*- coding: utf-8 -*-

import unittest

from OFS.SimpleItem import SimpleItem

from zope.component import createObject
from zope.interface import implements
from zope.component import provideAdapter
from zope.annotation.interfaces import IAnnotatable, IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.annotation.attribute import AttributeAnnotations
from zope.publisher.browser import TestRequest

from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.conversation import Conversation, ANNOTATION_KEY
from plone.app.discussion.conversation import conversationAdapterFactory
from plone.app.discussion.comment import Comment
from plone.app.discussion.browser.comments import AjaxCommentLoad
from plone.app.discussion.tests.layer import DiscussionLayer

try:
    # These exist in new versions, but not in the one that comes with Zope 2.10.
    from BTrees.LOBTree import LOBTree
except ImportError: # pragma: no cover
    from BTrees.OOBTree import OOBTree as LOBTree # pragma: no cover

from Products.PloneTestCase.ptc import PloneTestCase
from Products.CMFCore.utils import getToolByName

COMMENT_COUNT = 50

class WorkflowMock(object):
    def getInfoFor(self, obj, info):
        return 'published'

class ContextMock(SimpleItem):
    implements(IAttributeAnnotatable, IAnnotatable)
    portal_workflow = WorkflowMock()


class AjaxLoadTest(unittest.TestCase):

    def setUp(self):
        context_mock = ContextMock()
        request_mock = TestRequest()
        conversation = Conversation()
        conversation._children = LOBTree()
        provideAdapter(AttributeAnnotations)
        provideAdapter(conversationAdapterFactory)
        IAnnotations(context_mock)[ANNOTATION_KEY] = conversation
        for i in range(COMMENT_COUNT):
            comment = Comment()
            comment.text = 'Comment %i text' % i
            conversation.addComment(comment)
        self.context_mock = context_mock
        self.request_mock = request_mock

    def test_ajax_full_view(self):
        view = AjaxCommentLoad(self.context_mock, self.request_mock)
        replies = view.get_replies()
        self.assertEqual(len(tuple(replies)), COMMENT_COUNT)

    def test_ajax_load_batch_view(self):
        view = AjaxCommentLoad(self.context_mock, self.request_mock)
        replies = tuple(view.get_replies(start=0, size=10))
        self.assertEqual(len(replies), 10)
        # Check that those are really the first 10 comments
        for i in range(10):
            text = replies[i]['comment'].text
            it_should_be = "Comment %i text" % i
            self.assertEqual(text, it_should_be)



class AjaxFunctionalLoadTest(PloneTestCase):
    " Functional test of ajax comment loading"
    layer = DiscussionLayer

    def afterSetUp(self):
        # First we need to create some content.
        self.loginAsPortalOwner()
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
        self.typetool = typetool
        self.portal_discussion = getToolByName(self.portal,
                                               'portal_discussion',
                                               None)
        # we publish it
        wft = getToolByName(self.portal, 'portal_workflow')
        wft.doActionFor(self.portal.doc1, 'publish')
        # and enable discussion on it
        self.portal_discussion.overrideDiscussionFor(self.portal.doc1, True)
        # Create a very long conversation with hundreds of comments
        # so that we can start a ZServer and fiddle with firebug
        conversation = IConversation(self.portal.doc1)
        for i in range(COMMENT_COUNT):
            comment = createObject('plone.Comment')
            comment.title = 'Comment %i' % i
            comment.text = 'Comment %i text' % i
            conversation.addComment(comment)

    def test_ajax_load_full_view_template(self):
        view = AjaxCommentLoad(self.portal.doc1, self.app.REQUEST)
        view.__of__(self.portal.doc1)
        comments_html = view()
        self.assertTrue('Comment 12 text' in comments_html)
        self.assertTrue('Comment 1 text' in comments_html)

    def test_ajax_load_batch_view_template(self):
        self.app.REQUEST.form = dict(start='10', size=5)
        view = AjaxCommentLoad(self.portal.doc1, self.app.REQUEST)
        view.__of__(self.portal.doc1)
        comments_html = view()
        self.assertTrue('Comment 1 text' not in comments_html)
        self.assertTrue('Comment 5 text' not in comments_html)
        self.assertTrue('Comment 12 text' in comments_html)

    def xtest_ajax_load(self):
        '''
        This is not a "real" test method.
        I'm using it to develop ajax loading of comments.
        I'll converti it to a Selenium test soon.
        This should be a starting point: https://weblion.psu.edu/svn/weblion/weblion/assessmentmanagement.core/trunk/assessmentmanagement/core/selenium/testSelenium.py

        This too: http://pastebin.com/Dnx4WSMk
        '''
        import Testing
        host, port = Testing.ZopeTestCase.utils.startZServer()
        obj_path = self.portal.doc1.virtual_url_path()
        url = "http://%s:%i/%s" % (host, port, obj_path)
        print
        print url
        import transaction
        # The next line should NOT be committed uncommented
        #transaction.commit() # I know I shouldn't do this, but this way it works

        # Fire your favourite debugger (pdb obviously),
        # open Firebug. and start coding!
        # XXX this should become a real test


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
