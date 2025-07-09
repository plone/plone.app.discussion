"""User ban management system for plone.app.discussion"""

from datetime import datetime
from datetime import timedelta
from plone.app.discussion.interfaces import _
from plone.app.discussion.interfaces import IDiscussionSettings
from Products.CMFCore.utils import getToolByName
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface
from plone.app.discussion.vocabularies import BAN_TYPE_SHADOW
from plone.app.discussion.vocabularies import BAN_TYPE_PERMANENT


import logging


try:
    from persistent import Persistent
    from persistent.mapping import PersistentMapping
except ImportError:

    class Persistent:
        pass

    # Fallback for environments without persistent
    PersistentMapping = dict

try:
    from plone.base.utils import safe_text
except ImportError:
    # Fallback for older Plone versions
    def safe_text(text):
        if isinstance(text, bytes):
            return text.decode("utf-8")
        return str(text) if text is not None else None


try:
    from plone.registry.interfaces import IRegistry
except ImportError:

    class IRegistry:
        pass


try:
    import transaction
except ImportError:
    transaction = None

logger = logging.getLogger("plone.app.discussion.ban")

# Annotation key for storing ban data
BAN_ANNOTATION_KEY = "plone.app.discussion.bans"


class IBan(Interface):
    """Represents a user ban."""

    user_id = schema.TextLine(
        title=_("User ID"),
        description=_("The ID of the banned user"),
        required=True,
    )

    ban_type = schema.Choice(
        title=_("Ban Type"),
        vocabulary="plone.app.discussion.vocabularies.BanVocabulary",
        required=True,
    )

    created_date = schema.Datetime(
        title=_("Created Date"),
        description=_("When the ban was created"),
        required=True,
    )

    expires_date = schema.Datetime(
        title=_("Expiration Date"),
        description=_("When the ban expires (None for permanent bans)"),
        required=False,
    )

    reason = schema.TextLine(
        title=_("Reason"),
        description=_("Reason for the ban"),
        required=False,
    )

    moderator_id = schema.TextLine(
        title=_("Moderator ID"),
        description=_("ID of the moderator who created the ban"),
        required=True,
    )


@implementer(IBan)
class Ban(Persistent):
    """Implementation of a user ban."""

    def __init__(
        self,
        user_id,
        ban_type,
        moderator_id,
        reason=None,
        duration_hours=None,
        expires_date=None,
    ):
        self.user_id = safe_text(user_id)
        self.ban_type = ban_type
        self.moderator_id = safe_text(moderator_id)
        self.reason = safe_text(reason) if reason else None
        self.created_date = datetime.now()

        if ban_type == BAN_TYPE_PERMANENT:
            self.expires_date = None
        elif expires_date:
            self.expires_date = expires_date
        elif duration_hours:
            self.expires_date = self.created_date + timedelta(hours=duration_hours)
        else:
            # Use default duration from settings
            registry = getUtility(IRegistry)
            settings = registry.forInterface(IDiscussionSettings, check=False)
            default_duration = getattr(settings, "default_cooldown_duration", 24)
            self.expires_date = self.created_date + timedelta(hours=default_duration)

    def is_active(self):
        """Check if the ban is currently active."""
        if self.ban_type == BAN_TYPE_PERMANENT:
            return True

        if self.expires_date and datetime.now() > self.expires_date:
            return False

        return True

    def get_remaining_time(self):
        """Get remaining time for temporary bans."""
        if self.ban_type == BAN_TYPE_PERMANENT or not self.expires_date:
            return None

        remaining = self.expires_date - datetime.now()
        if remaining.total_seconds() <= 0:
            return None

        return remaining

    def __repr__(self):
        return f"<Ban {self.user_id} ({self.ban_type}) by {self.moderator_id}>"


class IBanManager(Interface):
    """Interface for managing user bans."""

    def ban_user(
        user_id,
        ban_type,
        moderator_id,
        reason=None,
        duration_hours=None,
        expires_date=None,
    ):
        """Ban a user with the specified parameters."""

    def unban_user(user_id, moderator_id):
        """Remove all active bans for a user."""

    def is_user_banned(user_id):
        """Check if a user is currently banned."""

    def get_user_ban(user_id):
        """Get the active ban for a user, if any."""

    def get_all_bans():
        """Get all bans (active and expired)."""

    def get_active_bans():
        """Get all currently active bans."""

    def cleanup_expired_bans():
        """Remove expired bans from storage."""


@implementer(IBanManager)
class BanManager:
    """Manages user bans using portal annotations."""

    def __init__(self, context):
        self.context = context
        self.portal = getToolByName(context, "portal_url").getPortalObject()

    def _get_ban_storage(self):
        """Get the ban storage from portal annotations."""
        annotations = IAnnotations(self.portal)
        if BAN_ANNOTATION_KEY not in annotations:
            # Initialize with a persistent mapping to ensure changes are saved
            annotations[BAN_ANNOTATION_KEY] = PersistentMapping()
        storage = annotations[BAN_ANNOTATION_KEY]

        # Ensure we have a persistent mapping even if created with regular dict
        if not isinstance(storage, PersistentMapping) and PersistentMapping != dict:
            # Convert existing dict to PersistentMapping
            new_storage = PersistentMapping()
            new_storage.update(storage)
            annotations[BAN_ANNOTATION_KEY] = new_storage
            storage = new_storage

        return storage

    def _mark_storage_changed(self, storage):
        """Mark storage as changed for ZODB persistence."""
        try:
            # Try to mark the storage as changed for persistence
            storage._p_changed = True
        except AttributeError:
            # Not a persistent object, changes won't persist across restarts
            logger.warning(
                "Ban storage is not persistent - changes may not survive server restarts"
            )

        # Attempt to commit the transaction
        if transaction:
            try:
                transaction.commit()
            except Exception as e:
                logger.error(f"Failed to commit ban transaction: {e}")

    def ban_user(
        self,
        user_id,
        ban_type,
        moderator_id,
        reason=None,
        duration_hours=None,
        expires_date=None,
    ):
        """Ban a user with the specified parameters."""
        # Remove any existing bans for this user first
        self.unban_user(user_id, moderator_id)

        ban = Ban(
            user_id=user_id,
            ban_type=ban_type,
            moderator_id=moderator_id,
            reason=reason,
            duration_hours=duration_hours,
            expires_date=expires_date,
        )

        storage = self._get_ban_storage()
        storage[user_id] = ban

        # Mark the storage as changed to ensure persistence
        self._mark_storage_changed(storage)

        logger.info(f"User {user_id} banned by {moderator_id} ({ban_type})")
        return ban

    def unban_user(self, user_id, moderator_id) -> Ban | None:
        """Remove all active bans for a user."""
        storage = self._get_ban_storage()
        if user_id in storage:
            old_ban = storage[user_id]
            del storage[user_id]

            # Mark the storage as changed to ensure persistence
            self._mark_storage_changed(storage)

            logger.info(f"User {user_id} unbanned by {moderator_id}")
            return old_ban
        return None

    def is_user_banned(self, user_id):
        """Check if a user is currently banned."""
        ban = self.get_user_ban(user_id)
        return ban is not None and ban.is_active()

    def get_user_ban(self, user_id):
        """Get the active ban for a user, if any."""
        storage = self._get_ban_storage()
        ban = storage.get(user_id)

        if ban and ban.is_active():
            return ban
        elif ban and not ban.is_active():
            # Clean up expired ban
            del storage[user_id]
            # Mark the storage as changed to ensure persistence
            self._mark_storage_changed(storage)

        return None

    def get_all_bans(self):
        """Get all bans (active and expired)."""
        storage = self._get_ban_storage()
        return list(storage.values())

    def get_active_bans(self):
        """Get all currently active bans."""
        return [ban for ban in self.get_all_bans() if ban.is_active()]

    def cleanup_expired_bans(self):
        """Remove expired bans from storage."""
        storage = self._get_ban_storage()
        expired_users = []

        for user_id, ban in storage.items():
            if not ban.is_active():
                expired_users.append(user_id)

        if expired_users:
            for user_id in expired_users:
                del storage[user_id]
                logger.info(f"Cleaned up expired ban for user {user_id}")

            # Mark the storage as changed to ensure persistence
            self._mark_storage_changed(storage)

        return len(expired_users)


def get_ban_manager(context):
    """Get a BanManager instance for the given context."""
    return BanManager(context)


def is_user_banned(context, user_id):
    """Convenience function to check if a user is banned."""
    ban_manager = get_ban_manager(context)
    return ban_manager.is_user_banned(user_id)


def get_user_ban_info(context, user_id):
    """Get ban information for a user."""
    ban_manager = get_ban_manager(context)
    return ban_manager.get_user_ban(user_id)


def can_user_comment(context, user_id):
    """Check if a user can comment (not banned or shadow banned)."""
    ban_manager = get_ban_manager(context)
    ban = ban_manager.get_user_ban(user_id)

    if not ban or not ban.is_active():
        return True

    # Shadow banned users can "comment" but comments are hidden
    if ban.ban_type == BAN_TYPE_SHADOW:
        return True

    # Cooldown and permanent bans prevent commenting
    return False


def is_comment_visible(context, user_id):
    """Check if comments from a user should be visible to others."""
    ban_manager = get_ban_manager(context)
    ban = ban_manager.get_user_ban(user_id)

    if not ban or not ban.is_active():
        return True

    # Only shadow bans hide comments
    return ban.ban_type != BAN_TYPE_SHADOW
