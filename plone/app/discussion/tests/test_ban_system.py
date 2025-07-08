"""Tests for the user ban management system."""

from datetime import datetime
from datetime import timedelta
from plone.app.discussion.ban import Ban
from plone.app.discussion.ban import BAN_TYPE_COOLDOWN
from plone.app.discussion.ban import BAN_TYPE_PERMANENT
from plone.app.discussion.ban import BAN_TYPE_SHADOW
from plone.app.discussion.ban import BanManager
from plone.app.discussion.ban import can_user_comment
from plone.app.discussion.ban import is_comment_visible
from plone.app.discussion.testing import PLONE_APP_DISCUSSION_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import unittest


class TestBanSystem(unittest.TestCase):
    """Test the user ban management system."""

    layer = PLONE_APP_DISCUSSION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # Create test content
        self.portal.invokeFactory("Document", "doc1")
        self.doc1 = self.portal.doc1

        # Enable discussion
        registry = getUtility(IRegistry)
        from plone.app.discussion.interfaces import IDiscussionSettings

        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True
        settings.ban_enabled = True

        # Enable discussion on the content
        from plone.app.discussion.interfaces import IConversation

        IConversation(self.doc1)

    def test_ban_creation(self):
        """Test creating different types of bans."""
        ban_manager = BanManager(self.doc1)

        # Test cooldown ban
        cooldown_ban = ban_manager.ban_user(
            user_id="test_user",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            reason="Testing cooldown",
            duration_hours=24,
        )

        self.assertIsInstance(cooldown_ban, Ban)
        self.assertEqual(cooldown_ban.ban_type, BAN_TYPE_COOLDOWN)
        self.assertTrue(cooldown_ban.is_active())
        self.assertIsNotNone(cooldown_ban.get_remaining_time())

        # Test shadow ban
        ban_manager.ban_user(
            user_id="shadow_user",
            ban_type=BAN_TYPE_SHADOW,
            moderator_id="admin",
            reason="Testing shadow ban",
            duration_hours=48,
        )

        shadow_ban = ban_manager.get_user_ban("shadow_user")
        self.assertEqual(shadow_ban.ban_type, BAN_TYPE_SHADOW)

        # Test permanent ban
        ban_manager.ban_user(
            user_id="permanent_user",
            ban_type=BAN_TYPE_PERMANENT,
            moderator_id="admin",
            reason="Testing permanent ban",
        )

        permanent_ban = ban_manager.get_user_ban("permanent_user")
        self.assertEqual(permanent_ban.ban_type, BAN_TYPE_PERMANENT)
        self.assertIsNone(permanent_ban.expires_date)
        self.assertIsNone(permanent_ban.get_remaining_time())

    def test_ban_behavior(self):
        """Test how different ban types affect commenting."""
        ban_manager = BanManager(self.doc1)

        # Test normal user (no ban)
        self.assertTrue(can_user_comment(self.doc1, "normal_user"))
        self.assertTrue(is_comment_visible(self.doc1, "normal_user"))

        # Test cooldown ban
        ban_manager.ban_user(
            user_id="cooldown_user",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            duration_hours=24,
        )

        self.assertFalse(can_user_comment(self.doc1, "cooldown_user"))
        self.assertTrue(is_comment_visible(self.doc1, "cooldown_user"))

        # Test shadow ban
        ban_manager.ban_user(
            user_id="shadow_user",
            ban_type=BAN_TYPE_SHADOW,
            moderator_id="admin",
            duration_hours=24,
        )

        self.assertTrue(can_user_comment(self.doc1, "shadow_user"))  # Can comment
        self.assertFalse(
            is_comment_visible(self.doc1, "shadow_user")
        )  # But not visible

        # Test permanent ban
        ban_manager.ban_user(
            user_id="permanent_user", ban_type=BAN_TYPE_PERMANENT, moderator_id="admin"
        )

        self.assertFalse(can_user_comment(self.doc1, "permanent_user"))
        self.assertTrue(is_comment_visible(self.doc1, "permanent_user"))

    def test_ban_expiration(self):
        """Test that bans expire correctly."""
        ban_manager = BanManager(self.doc1)

        # Create a ban that expires in the past
        past_time = datetime.now() - timedelta(hours=1)
        ban_manager.ban_user(
            user_id="expired_user",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            duration_hours=24,
        )

        # Manually set expiration to past
        ban = ban_manager.get_user_ban("expired_user")
        ban.expires_date = past_time

        # Check that expired ban is considered inactive
        self.assertFalse(ban.is_active())
        self.assertTrue(can_user_comment(self.doc1, "expired_user"))

    def test_ban_management(self):
        """Test ban management operations."""
        ban_manager = BanManager(self.doc1)

        # Create multiple bans
        ban_manager.ban_user("user1", BAN_TYPE_COOLDOWN, "admin", duration_hours=24)
        ban_manager.ban_user("user2", BAN_TYPE_SHADOW, "admin", duration_hours=48)
        ban_manager.ban_user("user3", BAN_TYPE_PERMANENT, "admin")

        # Test getting all bans
        all_bans = ban_manager.get_all_bans()
        self.assertEqual(len(all_bans), 3)

        # Test getting active bans
        active_bans = ban_manager.get_active_bans()
        self.assertEqual(len(active_bans), 3)

        # Test unbanning
        ban_manager.unban_user("user1", "admin")
        self.assertIsNone(ban_manager.get_user_ban("user1"))

        # Check remaining active bans
        active_bans = ban_manager.get_active_bans()
        self.assertEqual(len(active_bans), 2)

    def test_cleanup_expired_bans(self):
        """Test cleanup of expired bans."""
        ban_manager = BanManager(self.doc1)

        # Create bans with different expiration times
        past_time = datetime.now() - timedelta(hours=1)
        future_time = datetime.now() + timedelta(hours=1)

        ban_manager.ban_user("user1", BAN_TYPE_COOLDOWN, "admin", duration_hours=24)
        ban_manager.ban_user("user2", BAN_TYPE_COOLDOWN, "admin", duration_hours=24)

        # Manually set one to expired
        ban1 = ban_manager.get_user_ban("user1")
        ban1.expires_date = past_time

        # Keep one active
        ban2 = ban_manager.get_user_ban("user2")
        ban2.expires_date = future_time

        # Cleanup expired bans
        cleaned_count = ban_manager.cleanup_expired_bans()
        self.assertEqual(cleaned_count, 1)

        # Check remaining bans
        active_bans = ban_manager.get_active_bans()
        self.assertEqual(len(active_bans), 1)
        self.assertEqual(active_bans[0].user_id, "user2")

    def test_ban_persistence(self):
        """Test that bans persist across manager instances (simulating server restart)."""
        ban_manager1 = BanManager(self.doc1)

        # Create a ban
        ban_manager1.ban_user(
            user_id="persistent_user",
            ban_type=BAN_TYPE_COOLDOWN,
            moderator_id="admin",
            reason="Testing persistence",
            duration_hours=24,
        )

        # Verify ban exists
        self.assertTrue(ban_manager1.is_user_banned("persistent_user"))
        retrieved_ban = ban_manager1.get_user_ban("persistent_user")
        self.assertIsNotNone(retrieved_ban)
        self.assertEqual(retrieved_ban.user_id, "persistent_user")
        self.assertEqual(retrieved_ban.reason, "Testing persistence")

        # Create a new manager instance (simulating restart)
        ban_manager2 = BanManager(self.doc1)

        # Verify ban still exists
        self.assertTrue(ban_manager2.is_user_banned("persistent_user"))
        retrieved_ban2 = ban_manager2.get_user_ban("persistent_user")
        self.assertIsNotNone(retrieved_ban2)
        self.assertEqual(retrieved_ban2.user_id, "persistent_user")
        self.assertEqual(retrieved_ban2.reason, "Testing persistence")

        # Test that changes persist
        ban_manager2.unban_user("persistent_user", "admin")

        # Create a third manager instance
        ban_manager3 = BanManager(self.doc1)

        # Verify ban was removed
        self.assertFalse(ban_manager3.is_user_banned("persistent_user"))
        self.assertIsNone(ban_manager3.get_user_ban("persistent_user"))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
