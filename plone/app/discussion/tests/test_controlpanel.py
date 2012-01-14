# -*- coding: utf-8 -*-
import unittest2 as unittest

from zope.component import getMultiAdapter
from zope.component import queryUtility

from plone.registry import Registry
from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName

from plone.app.testing import TEST_USER_ID, setRoles

from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.testing import \
    PLONE_APP_DISCUSSION_INTEGRATION_TESTING


class RegistryTest(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.registry = Registry()
        self.registry.registerInterface(IDiscussionSettings)

    def test_registry_registered(self):
        registry = queryUtility(IRegistry)
        self.assertTrue(registry.forInterface(IDiscussionSettings))

    def test_discussion_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="discussion-settings")
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_discussion_in_controlpanel(self):
        # Check if discussion is in the control panel
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue('discussion' in [a.getAction(self)['id']
                            for a in self.controlpanel.listActions()])

    def test_globally_enabled(self):
        # Check globally_enabled record
        self.assertTrue('globally_enabled' in IDiscussionSettings)
        self.assertEqual(
            self.registry['plone.app.discussion.interfaces.' +
                          'IDiscussionSettings.globally_enabled'],
            False)

    def test_anonymous_comments(self):
        # Check anonymous_comments record
        self.assertTrue('anonymous_comments' in IDiscussionSettings)
        self.assertEqual(self.registry['plone.app.discussion.interfaces.' +
            'IDiscussionSettings.anonymous_comments'], False)

    def test_moderation_enabled(self):
        # Check globally_enabled record
        self.assertTrue('moderation_enabled' in IDiscussionSettings)
        self.assertEqual(
            self.registry['plone.app.discussion.interfaces.' +
                          'IDiscussionSettings.moderation_enabled'],
            False)

    def test_text_transform(self):
        self.assertTrue('text_transform' in IDiscussionSettings)
        self.assertEqual(
            self.registry['plone.app.discussion.interfaces.' +
                          'IDiscussionSettings.text_transform'],
            'text/plain')

    def test_captcha(self):
        # Check globally_enabled record
        self.assertTrue('captcha' in IDiscussionSettings)
        self.assertEqual(self.registry['plone.app.discussion.interfaces.' +
                                        'IDiscussionSettings.captcha'],
                          'disabled')

    def test_show_commenter_image(self):
        # Check show_commenter_image record
        self.assertTrue('show_commenter_image' in IDiscussionSettings)
        self.assertEqual(self.registry['plone.app.discussion.interfaces.' +
            'IDiscussionSettings.show_commenter_image'], True)

    def test_moderator_notification_enabled(self):
        # Check show_commenter_image record
        self.assertTrue('moderator_notification_enabled' in
                        IDiscussionSettings)
        self.assertEqual(self.registry['plone.app.discussion.interfaces.' +
            'IDiscussionSettings.moderator_notification_enabled'], False)

    #def test_user_notification_enabled(self):
    #    # Check show_commenter_image record
    #    show_commenter_image = self.registry.records['plone.app.discussion.' +
    #        'interfaces.IDiscussionSettings.user_notification_enabled']
    #
    #    self.assertTrue('user_notification_enabled' in IDiscussionSettings)
    #    self.assertEqual(self.registry['plone.app.discussion.interfaces.' +
    #        'IDiscussionSettings.user_notification_enabled'], False)


class ConfigurationChangedSubscriberTest(unittest.TestCase):

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IDiscussionSettings, check=False)

    def test_moderation_enabled_in_discussion_control_panel_changed(self):
        """Make sure the 'Discussion Item' workflow is changed properly, when
           the 'comment_moderation' setting in the discussion control panel
           changes.
        """
        # By default the one_state_workflow without moderation is enabled
        self.assertEqual(('one_state_workflow',),
                          self.portal.portal_workflow.getChainForPortalType(
                              'Discussion Item'))

        # Enable moderation in the discussion control panel
        self.settings.moderation_enabled = True

        # Make sure the comment_review_workflow with moderation enabled is
        # enabled
        self.assertEqual(('comment_review_workflow',),
                          self.portal.portal_workflow.getChainForPortalType(
                              'Discussion Item'))
        # And back
        self.settings.moderation_enabled = False
        self.assertEqual(('one_state_workflow',),
                          self.portal.portal_workflow.getChainForPortalType(
                              'Discussion Item'))

    def test_change_workflow_in_types_control_panel(self):
        """Make sure the setting in the discussion control panel is changed
           accordingly, when the workflow for the 'Discussion Item' changed in
           the types control panel.
        """
        # By default, moderation is disabled
        self.settings.moderation_enabled = False

        # Enable the 'comment_review_workflow' with moderation enabled
        self.portal.portal_workflow.setChainForPortalTypes(
            ('Discussion Item',),
            ('comment_review_workflow',))

        # Make sure the moderation_enabled settings has changed
        self.settings.moderation_enabled = True

        # Enable the 'comment_review_workflow' with moderation enabled
        self.portal.portal_workflow.setChainForPortalTypes(
            ('Discussion Item',),
            ('one_state_workflow',))
        self.settings.moderation_enabled = True

        # Enable a 'custom' discussion workflow
        self.portal.portal_workflow.setChainForPortalTypes(
            ('Discussion Item',),
            ('intranet_workflow',))

        # Setting has not changed. A Custom workflow disables the
        # enable_moderation checkbox in the discussion control panel. The
        # setting itself remains unchanged.
        self.settings.moderation_enabled = True


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
