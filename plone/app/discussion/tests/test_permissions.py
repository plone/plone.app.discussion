from ..testing import PLONE_APP_DISCUSSION_INTEGRATION_TESTING
from AccessControl.PermissionRole import rolesForPermissionOn

import unittest


class PermissionsTest(unittest.TestCase):
    """Make sure the permissions are set up properly."""

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def test_permissions_site_administrator_role(self):
        # This integration test shows that the correct permissions were
        # assigned to the Site Administrator role (whether inherited from the
        # Zope application, or specified in the portal rolemap).
        self.assertTrue(
            "Site Administrator"
            not in rolesForPermissionOn("Reply to item", self.layer["portal"])
        )
