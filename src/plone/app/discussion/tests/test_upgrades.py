from plone.app.discussion.testing import (  # noqa
    PLONE_APP_DISCUSSION_INTEGRATION_TESTING,
)
from plone.app.discussion.upgrades import move_configlet_to_content_category
from Products.CMFCore.utils import getToolByName

import unittest


class MoveConfigletToContentCategoryTest(unittest.TestCase):
    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")

    def get_configlet(self):
        for configlet in self.controlpanel.listActions():
            if configlet.getId() == "discussion":
                return configlet

    def test_configlet_in_general_is_moved(self):
        # Sites created before 5.0 have the configlet in plone-general.
        configlet = self.get_configlet()
        configlet.category = "plone-general"
        configlet.title = "Comments"

        move_configlet_to_content_category(self.portal)

        configlet = self.get_configlet()
        self.assertEqual(configlet.category, "plone-content")
        # Local changes to the configlet are kept.
        self.assertEqual(configlet.title, "Comments")

    def test_configlet_in_other_category_is_kept(self):
        self.get_configlet().category = "plone-advanced"

        move_configlet_to_content_category(self.portal)

        self.assertEqual(self.get_configlet().category, "plone-advanced")

    def test_no_configlet(self):
        self.controlpanel.unregisterConfiglet("discussion")

        move_configlet_to_content_category(self.portal)

        self.assertIsNone(self.get_configlet())
