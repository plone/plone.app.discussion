# -*- coding: utf-8 -*-
import unittest

from zope.component import getMultiAdapter
from zope.component import queryUtility

from plone.registry import Registry
from plone.registry.interfaces import IRegistry

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

    def test_registry_registered(self):
        registry = queryUtility(IRegistry)
        self.failUnless(registry.forInterface(IDiscussionSettings))
            
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
        self.failUnless('globally_enabled' in IDiscussionSettings)
        self.assertEquals(
            self.registry['plone.app.discussion.interfaces.' +
                          'IDiscussionSettings.globally_enabled'], 
            True)

    def test_anonymous_comments(self):
        # Check anonymous_comments record
        self.failUnless('anonymous_comments' in IDiscussionSettings)
        self.assertEquals(self.registry['plone.app.discussion.interfaces.' +
            'IDiscussionSettings.anonymous_comments'], False)

    def test_moderation_enabled(self):
        # Check globally_enabled record
        self.failUnless('moderation_enabled' in IDiscussionSettings)
        self.assertEquals(
            self.registry['plone.app.discussion.interfaces.' +
                          'IDiscussionSettings.moderation_enabled'], 
            False)
        
    def test_text_transform(self):
        self.failUnless('text_transform' in IDiscussionSettings)
        self.assertEquals(
            self.registry['plone.app.discussion.interfaces.' +
                          'IDiscussionSettings.text_transform'],
            'text/plain')
        
    def test_captcha(self):
        # Check globally_enabled record
        self.failUnless('captcha' in IDiscussionSettings)
        self.assertEquals(self.registry['plone.app.discussion.interfaces.' +
                                        'IDiscussionSettings.captcha'],
                          'disabled')

    def test_show_commenter_image(self):
        # Check show_commenter_image record
        self.failUnless('show_commenter_image' in IDiscussionSettings)
        self.assertEquals(self.registry['plone.app.discussion.interfaces.' + 
            'IDiscussionSettings.show_commenter_image'], True)

    def test_moderator_notification_enabled(self):
        # Check show_commenter_image record
        self.failUnless('moderator_notification_enabled' in 
                        IDiscussionSettings)
        self.assertEquals(self.registry['plone.app.discussion.interfaces.' +
            'IDiscussionSettings.moderator_notification_enabled'], False)

    #def test_user_notification_enabled(self):
    #    # Check show_commenter_image record
    #    show_commenter_image = self.registry.records['plone.app.discussion.' +
    #        'interfaces.IDiscussionSettings.user_notification_enabled']
    #
    #    self.failUnless('user_notification_enabled' in IDiscussionSettings)
    #    self.assertEquals(self.registry['plone.app.discussion.interfaces.' +
    #        'IDiscussionSettings.user_notification_enabled'], False)


class ConfigurationChangedSubscriberTest(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        self.loginAsPortalOwner()
        # Set up the registry
        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IDiscussionSettings, check=False)
        
    def test_moderation_enabled_in_discussion_control_panel_changed(self):
        """Make sure the 'Discussion Item' workflow is changed properly, when 
           the 'comment_moderation' setting in the discussion control panel 
           changes.
        """
        # By default the one_state_workflow without moderation is enabled
        self.assertEquals(('one_state_workflow',),
                          self.portal.portal_workflow.getChainForPortalType(
                              'Discussion Item'))        
        
        # Enable moderation in the discussion control panel
        self.settings.moderation_enabled = True 
        
        # Make sure the comment_review_workflow with moderation enabled is
        # enabled
        self.assertEquals(('comment_review_workflow',),
                          self.portal.portal_workflow.getChainForPortalType(
                              'Discussion Item')) 
        # And back
        self.settings.moderation_enabled = False
        self.assertEquals(('one_state_workflow',),
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
