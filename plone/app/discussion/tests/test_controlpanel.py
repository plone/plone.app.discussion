import unittest

from zope.component import getMultiAdapter

from plone.registry import Registry

from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.ptc import PloneTestCase

from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.tests.layer import DiscussionLayer


class RegistryTest(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        self.loginAsPortalOwner()
        # Set up the registry
        self.registry = Registry()
        self.registry.registerInterface(IDiscussionSettings)

    def test_discussion_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST), 
                               name="discussion-settings")
        view = view.__of__(self.portal)
        self.failUnless(view())

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

    def test_captcha(self):
        # Check globally_enabled record
        globally_enabled_record = self.registry.records['plone.app.discussion.interfaces.IDiscussionSettings.captcha']

        self.failUnless('captcha' in IDiscussionSettings)
        self.assertEquals(self.registry['plone.app.discussion.interfaces.IDiscussionSettings.captcha'], 'disabled')

    def test_anonymous_comments(self):
        # Check anonymous_comments record
        anonymous_comments_record = self.registry.records['plone.app.discussion.interfaces.IDiscussionSettings.anonymous_comments']

        self.failUnless('anonymous_comments' in IDiscussionSettings)
        self.assertEquals(self.registry['plone.app.discussion.interfaces.IDiscussionSettings.anonymous_comments'], False)

    def test_show_commenter_image(self):
        # Check show_commenter_image record
        show_commenter_image = self.registry.records['plone.app.discussion.interfaces.IDiscussionSettings.show_commenter_image']

        self.failUnless('show_commenter_image' in IDiscussionSettings)
        self.assertEquals(self.registry['plone.app.discussion.interfaces.IDiscussionSettings.show_commenter_image'], True)

    def test_moderator_notification_enabled(self):
        # Check show_commenter_image record
        show_commenter_image = self.registry.records['plone.app.discussion.interfaces.IDiscussionSettings.moderator_notification_enabled']

        self.failUnless('moderator_notification_enabled' in IDiscussionSettings)
        self.assertEquals(self.registry['plone.app.discussion.interfaces.IDiscussionSettings.moderator_notification_enabled'], False)

    #def test_user_notification_enabled(self):
    #    # Check show_commenter_image record
    #    show_commenter_image = self.registry.records['plone.app.discussion.interfaces.IDiscussionSettings.user_notification_enabled']
    #
    #    self.failUnless('user_notification_enabled' in IDiscussionSettings)
    #    self.assertEquals(self.registry['plone.app.discussion.interfaces.IDiscussionSettings.user_notification_enabled'], False)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)