"""Tests for the ban management system."""

from datetime import datetime
from datetime import timedelta
from plone.app.discussion.ban import BanManager
from plone.app.discussion.ban import can_user_comment
from plone.app.discussion.ban import get_ban_manager
from plone.app.discussion.ban import is_comment_visible
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.testing import PLONE_APP_DISCUSSION_FUNCTIONAL_TESTING
from plone.app.discussion.vocabularies import BAN_TYPE_COOLDOWN
from plone.app.discussion.vocabularies import BAN_TYPE_PERMANENT
from plone.app.discussion.vocabularies import BAN_TYPE_SHADOW
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.annotation.interfaces import IAnnotations
from zope.component import queryUtility

import unittest


class TestBanManager(unittest.TestCase):
    """Test the BanManager class."""

    layer = PLONE_APP_DISCUSSION_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # Enable the ban system in registry
        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IDiscussionSettings, check=False)
        self.settings.ban_enabled = True

        # Get a ban manager
        self.ban_manager = get_ban_manager(self.portal)

    def test_ban_manager_creation(self):
        """Test creating a BanManager."""
        self.assertTrue(isinstance(self.ban_manager, BanManager))

    def test_ban_storage_initialization(self):
        """Test that the ban storage is properly initialized."""
        storage = self.ban_manager._get_ban_storage()
        self.assertTrue(hasattr(storage, "__getitem__"))
        self.assertTrue(hasattr(storage, "__setitem__"))
        self.assertTrue(hasattr(storage, "__delitem__"))

    def test_ban_user(self):
        """Test banning a user."""
        # Ban a user
        ban = self.ban_manager.ban_user(
            user_id="testuser",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            reason="Test reason",
            duration_hours=24,
        )

        # Check that the ban was created correctly
        self.assertEqual(ban.user_id, "testuser")
        self.assertEqual(ban.ban_type, BAN_TYPE_COOLDOWN)
        self.assertEqual(ban.moderator_id, "admin")
        self.assertEqual(ban.reason, "Test reason")

        # Check if the ban was stored properly
        stored_ban = self.ban_manager.get_user_ban("testuser")
        self.assertEqual(stored_ban.user_id, "testuser")
        self.assertEqual(stored_ban.ban_type, BAN_TYPE_COOLDOWN)

    def test_is_user_banned(self):
        """Test checking if a user is banned."""
        # Initially the user is not banned
        self.assertFalse(self.ban_manager.is_user_banned("testuser"))

        # Ban the user
        self.ban_manager.ban_user(
            user_id="testuser",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            duration_hours=24,
        )

        # Now the user should be banned
        self.assertTrue(self.ban_manager.is_user_banned("testuser"))

    def test_unban_user(self):
        """Test unbanning a user."""
        # Ban a user
        self.ban_manager.ban_user(
            user_id="testuser",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            duration_hours=24,
        )

        # Verify the user is banned
        self.assertTrue(self.ban_manager.is_user_banned("testuser"))

        # Unban the user
        old_ban = self.ban_manager.unban_user("testuser", "admin")

        # Check that unban returned the removed ban
        self.assertEqual(old_ban.user_id, "testuser")

        # Verify the user is no longer banned
        self.assertFalse(self.ban_manager.is_user_banned("testuser"))
        self.assertIsNone(self.ban_manager.get_user_ban("testuser"))

    def test_get_active_bans(self):
        """Test retrieving active bans."""
        # Create several bans
        self.ban_manager.ban_user(
            user_id="user1",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            duration_hours=24,
        )
        self.ban_manager.ban_user(
            user_id="user2",
            ban_type=BAN_TYPE_SHADOW,
            moderator_id="admin",
            duration_hours=48,
        )
        self.ban_manager.ban_user(
            user_id="user3",
            ban_type=BAN_TYPE_PERMANENT,
            moderator_id="admin",
        )

        # Create an expired ban
        past_date = datetime.now() - timedelta(hours=1)
        self.ban_manager.ban_user(
            user_id="expired_user",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            expires_date=past_date,
        )

        # Get active bans
        active_bans = self.ban_manager.get_active_bans()

        # There should be 3 active bans
        self.assertEqual(len(active_bans), 3)

        # Check user IDs of active bans
        active_user_ids = [ban.user_id for ban in active_bans]
        self.assertIn("user1", active_user_ids)
        self.assertIn("user2", active_user_ids)
        self.assertIn("user3", active_user_ids)
        self.assertNotIn("expired_user", active_user_ids)

    def test_cleanup_expired_bans(self):
        """Test cleaning up expired bans."""
        # Create an active ban
        self.ban_manager.ban_user(
            user_id="active_user",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            duration_hours=24,
        )

        # Create expired bans
        past_date = datetime.now() - timedelta(hours=1)
        self.ban_manager.ban_user(
            user_id="expired_user1",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            expires_date=past_date,
        )
        self.ban_manager.ban_user(
            user_id="expired_user2",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            expires_date=past_date,
        )

        # Clean up expired bans
        removed_count = self.ban_manager.cleanup_expired_bans()

        # 2 bans should have been removed
        self.assertEqual(removed_count, 2)

        # Check that expired bans were removed
        self.assertIsNone(self.ban_manager.get_user_ban("expired_user1"))
        self.assertIsNone(self.ban_manager.get_user_ban("expired_user2"))

        # Check that active ban remains
        self.assertIsNotNone(self.ban_manager.get_user_ban("active_user"))


class TestBanHelperFunctions(unittest.TestCase):
    """Test the ban helper functions."""

    layer = PLONE_APP_DISCUSSION_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # Enable the ban system in registry
        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IDiscussionSettings, check=False)
        self.settings.ban_enabled = True

        # Get a ban manager
        self.ban_manager = get_ban_manager(self.portal)

    def test_get_ban_manager(self):
        """Test getting a ban manager for a context."""
        ban_manager = get_ban_manager(self.portal)
        self.assertTrue(isinstance(ban_manager, BanManager))

    def test_is_user_banned_helper(self):
        """Test is_user_banned helper function."""
        from plone.app.discussion.ban import is_user_banned

        # Initially the user is not banned
        self.assertFalse(is_user_banned(self.portal, "testuser"))

        # Ban the user
        self.ban_manager.ban_user(
            user_id="testuser",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            duration_hours=24,
        )

        # Now the user should be banned
        self.assertTrue(is_user_banned(self.portal, "testuser"))

    def test_can_user_comment(self):
        """Test can_user_comment function."""
        # Initially, users can comment
        self.assertTrue(can_user_comment(self.portal, "regular_user"))
        self.assertTrue(can_user_comment(self.portal, "shadow_banned_user"))
        self.assertTrue(can_user_comment(self.portal, "cooldown_user"))

        # Ban users with different ban types
        self.ban_manager.ban_user(
            user_id="cooldown_user",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            duration_hours=24,
        )

        self.ban_manager.ban_user(
            user_id="shadow_banned_user",
            ban_type=BAN_TYPE_SHADOW,
            moderator_id="admin",
            duration_hours=24,
        )

        self.ban_manager.ban_user(
            user_id="permanent_user",
            ban_type=BAN_TYPE_PERMANENT,
            moderator_id="admin",
        )

        # Check if users can comment based on their ban status
        self.assertTrue(can_user_comment(self.portal, "regular_user"))  # Not banned
        self.assertTrue(
            can_user_comment(self.portal, "shadow_banned_user")
        )  # Shadow bans can comment
        self.assertFalse(
            can_user_comment(self.portal, "cooldown_user")
        )  # Cooldown bans can't comment
        self.assertFalse(
            can_user_comment(self.portal, "permanent_user")
        )  # Permanent bans can't comment

    def test_is_comment_visible(self):
        """Test is_comment_visible function."""
        # Initially, comments from all users are visible
        self.assertTrue(is_comment_visible(self.portal, "regular_user"))
        self.assertTrue(is_comment_visible(self.portal, "shadow_banned_user"))
        self.assertTrue(is_comment_visible(self.portal, "cooldown_user"))

        # Ban users with different ban types
        self.ban_manager.ban_user(
            user_id="cooldown_user",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            duration_hours=24,
        )

        self.ban_manager.ban_user(
            user_id="shadow_banned_user",
            ban_type=BAN_TYPE_SHADOW,
            moderator_id="admin",
            duration_hours=24,
        )

        self.ban_manager.ban_user(
            user_id="permanent_user",
            ban_type=BAN_TYPE_PERMANENT,
            moderator_id="admin",
        )

        # Check comment visibility based on user's ban status
        self.assertTrue(is_comment_visible(self.portal, "regular_user"))  # Not banned
        self.assertFalse(
            is_comment_visible(self.portal, "shadow_banned_user")
        )  # Shadow banned comments are hidden
        self.assertTrue(
            is_comment_visible(self.portal, "cooldown_user")
        )  # Cooldown ban comments still visible
        self.assertTrue(
            is_comment_visible(self.portal, "permanent_user")
        )  # Permanent ban comments still visible


class TestBanIntegration(unittest.TestCase):
    """Integration tests for the ban system."""

    layer = PLONE_APP_DISCUSSION_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # Enable the ban system in registry
        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IDiscussionSettings, check=False)
        self.settings.ban_enabled = True
        self.settings.default_cooldown_duration = 12  # Set default duration to 12 hours

        # Get a ban manager
        self.ban_manager = get_ban_manager(self.portal)

    def test_default_settings_from_registry(self):
        """Test that ban uses default settings from registry."""
        # Ban a user without specifying duration
        ban = self.ban_manager.ban_user(
            user_id="testuser",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
        )

        # Check that the default duration from registry was used
        time_diff = ban.expires_date - ban.created_date
        hours_diff = time_diff.total_seconds() / 3600
        self.assertAlmostEqual(hours_diff, 12, delta=0.1)

    def test_ban_persistence(self):
        """Test that bans are persisted in annotations."""
        # Ban a user
        self.ban_manager.ban_user(
            user_id="testuser",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            duration_hours=24,
        )

        # Get annotations directly and check if the ban is there
        from plone.app.discussion.ban import BAN_ANNOTATION_KEY

        annotations = IAnnotations(self.portal)
        self.assertIn(BAN_ANNOTATION_KEY, annotations)

        ban_storage = annotations[BAN_ANNOTATION_KEY]
        self.assertIn("testuser", ban_storage)
        self.assertEqual(ban_storage["testuser"].ban_type, BAN_TYPE_COOLDOWN)

    def test_shadow_ban_notification_setting(self):
        """Test the shadow ban notification setting."""
        # Set notification setting
        self.settings.shadow_ban_notification_enabled = True

        # This doesn't directly affect any behavior in the ban module
        # It's used by the UI layer to determine whether to show notifications
        # So we just test that the setting can be changed
        self.assertTrue(self.settings.shadow_ban_notification_enabled)

        self.settings.shadow_ban_notification_enabled = False
        self.assertFalse(self.settings.shadow_ban_notification_enabled)
