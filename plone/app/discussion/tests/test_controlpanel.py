import unittest

from plone.registry import Registry

from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.ptc import PloneTestCase

from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.tests.layer import DiscussionLayer


class RegistryTest(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        # Set up the registry
        self.registry = Registry()
        self.registry.register_interface(IDiscussionSettings)

    def test_discussion_in_controlpanel(self):
        # Check if discussion is in the control panel
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.failUnless('discussion' in [a.getAction(self)['id']
                            for a in self.controlpanel.listActions()])

    def test_globally_enabled(self):
        # Check globally_enabled record
        globally_enabled_record = self.registry.records['plone.app.discussion.interfaces.IDiscussionSettings.globally_enabled']

        self.failUnless('globally_enabled' in IDiscussionSettings)
        self.assertEquals(self.registry['plone.app.discussion.interfaces.IDiscussionSettings.globally_enabled'], True)

    def test_anonymous_comments(self):
        # Check anonymous_comments record
        anonymous_comments_record = self.registry.records['plone.app.discussion.interfaces.IDiscussionSettings.anonymous_comments']

        self.failUnless('anonymous_comments' in IDiscussionSettings)
        self.assertEquals(self.registry['plone.app.discussion.interfaces.IDiscussionSettings.anonymous_comments'], False)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)