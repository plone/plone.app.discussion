"""Browser views for user ban management."""

from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Acquisition import aq_inner
from plone.app.discussion.ban import get_ban_manager
from plone.app.discussion.interfaces import _
from plone.app.discussion.interfaces import IBanUserSchema
from plone.app.discussion.interfaces import IUnbanUserSchema
from plone.app.discussion.vocabularies import BAN_TYPE_COOLDOWN
from plone.app.discussion.vocabularies import BAN_TYPE_PERMANENT
from plone.app.discussion.vocabularies import BAN_TYPE_SHADOW
from plone.z3cform.layout import wrap_form
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form


class BanManagementMixin:
    """Mixin class with common ban management functionality."""

    def _get_ban_manager(self):
        """Get ban manager for the current context."""
        return get_ban_manager(self.context)

    def _get_current_moderator_id(self):
        """Get the current user's ID as moderator."""
        membership = getToolByName(self.context, "portal_membership")
        moderator = membership.getAuthenticatedMember()
        return moderator.getId()

    def _validate_user_id(self, user_id):
        """Validate and return stripped user ID."""
        user_id = user_id.strip() if user_id else ""
        if not user_id:
            IStatusMessage(self.request).add(_("User ID is required."), type="error")
            return None
        return user_id

    def _redirect_to_ban_management(self):
        """Redirect to ban management view."""
        self.request.response.redirect(
            self.context.absolute_url() + "/@@ban-management"
        )

    def _create_ban_success_message(self, user_id, ban_type, duration=None):
        """Create appropriate success message for ban creation."""
        message_map = {
            BAN_TYPE_PERMANENT: _(
                "User ${user_id} has been permanently banned.",
                mapping={"user_id": user_id},
            ),
            BAN_TYPE_SHADOW: _(
                "User ${user_id} has been shadow banned.",
                mapping={"user_id": user_id},
            ),
            BAN_TYPE_COOLDOWN: _(
                "User ${user_id} has been banned for ${duration} hours.",
                mapping={"user_id": user_id, "duration": duration or 24},
            ),
        }
        return message_map.get(ban_type, message_map[BAN_TYPE_COOLDOWN])

    def _unban_user_with_messages(self, user_id):
        """Unban a user and show appropriate status messages."""
        user_id = self._validate_user_id(user_id)
        if not user_id:
            return False
            
        # Check if the user_id exists in the system
        membership = getToolByName(self.context, "portal_membership")
        member = membership.getMemberById(user_id)
        if not member:
            IStatusMessage(self.request).add(
                _("User ${user_id} does not exist in the system.", 
                  mapping={"user_id": user_id}),
                type="error",
            )
            return False

        moderator_id = self._get_current_moderator_id()
        ban_manager = self._get_ban_manager()
        old_ban = ban_manager.unban_user(user_id, moderator_id)

        message = (
            _("User ${user_id} has been unbanned.", mapping={"user_id": user_id})
            if old_ban
            else _("User ${user_id} was not banned.", mapping={"user_id": user_id})
        )

        IStatusMessage(self.request).add(message, type="info" if old_ban else "warning")
        return True


class UserBanForm(form.Form, BanManagementMixin):

    fields = field.Fields(IBanUserSchema)
    ignoreContext = True
    label = "Ban User"

    def updateWidgets(self):
        super().updateWidgets()

    @button.buttonAndHandler("Save")
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            return False

        user_id = data.get("user_id", "").strip()
        ban_type = data.get("ban_type", BAN_TYPE_COOLDOWN)
        reason = data.get("reason")
        reason = reason.strip() if reason else ""
        duration_hours = data.get("duration_hours")

        user_id = self._validate_user_id(user_id)
        if not user_id:
            return
            
        # Check if the user_id exists in the system
        membership = getToolByName(self.context, "portal_membership")
        member = membership.getMemberById(user_id)
        if not member:
            IStatusMessage(self.request).add(
                _("User ${user_id} does not exist in the system.", 
                  mapping={"user_id": user_id}),
                type="error",
            )
            return
            
        # Check if the user is already banned
        ban_manager = self._get_ban_manager()
        existing_ban = ban_manager.get_user_ban(user_id)
        if existing_ban and existing_ban.is_active():
            IStatusMessage(self.request).add(
                _("User ${user_id} is already banned. Unban first if you want to change the ban type.", 
                  mapping={"user_id": user_id}),
                type="error",
            )
            return

        # Get current user as moderator
        moderator_id = self._get_current_moderator_id()

        # Parse duration for temporary bans
        duration = None
        if ban_type != BAN_TYPE_PERMANENT and duration_hours:
            try:
                duration = int(duration_hours)
                if duration <= 0:
                    raise ValueError("Duration must be positive")
            except ValueError:
                IStatusMessage(self.request).add(
                    _("Invalid duration. Please enter a positive number of hours."),
                    type="error",
                )
                return

        # Create the ban
        ban_manager = self._get_ban_manager()
        try:
            ban_manager.ban_user(
                user_id=user_id,
                ban_type=ban_type,
                moderator_id=moderator_id,
                reason=reason,
                duration_hours=duration,
            )

            # Success message using mixin method
            msg = self._create_ban_success_message(user_id, ban_type, duration)
            IStatusMessage(self.request).add(msg, type="info")

        except Exception as e:
            IStatusMessage(self.request).add(
                _("Error banning user: ${error}", mapping={"error": str(e)}),
                type="error",
            )

        self._redirect_to_ban_management()

    @button.buttonAndHandler("Cancel")
    def handleCancel(self, action):
        self._redirect_to_ban_management()


class UserUnbanForm(form.Form, BanManagementMixin):
    """Form for unbanning a user."""

    fields = field.Fields(IUnbanUserSchema)
    ignoreContext = True
    label = "Unban User"

    def updateWidgets(self):
        super().updateWidgets()

    @button.buttonAndHandler("Unban")
    def handleUnban(self, action):
        data, errors = self.extractData()
        if errors:
            return False

        user_id = data.get("user_id", "")

        if self._unban_user_with_messages(user_id):
            self._redirect_to_ban_management()


class BanManagementView(BrowserView, BanManagementMixin):
    """View for managing user bans."""

    template = ViewPageTemplateFile("ban_management.pt")

    def __call__(self):
        """Process form submissions and render template."""
        if not self.can_manage_bans():
            raise Unauthorized("You do not have permission to manage bans.")

        if self.request.method == "POST":
            self.process_form()

        return self.template()

    def can_manage_bans(self):
        """Check if current user can manage bans."""
        return getSecurityManager().checkPermission(
            "Review comments", aq_inner(self.context)
        )

    def process_form(self):
        """Process ban management form submissions."""
        action = self.request.form.get("action")

        if action == "unban_user":
            self.unban_user()
        elif action == "cleanup_expired":
            self.cleanup_expired_bans()

    def unban_user(self):
        """Unban a user."""
        user_id = self.request.form.get("unban_user_id", "").strip()

        # Unban the user (validation happens in _unban_user_with_messages)
        self._unban_user_with_messages(user_id)

    def cleanup_expired_bans(self):
        """Clean up expired bans."""
        ban_manager = self._get_ban_manager()
        count = ban_manager.cleanup_expired_bans()

        IStatusMessage(self.request).add(
            _("Cleaned up ${count} expired bans.", mapping={"count": count}),
            type="info",
        )

    def get_active_bans(self):
        """Get all active bans for display."""
        ban_manager = self._get_ban_manager()
        return ban_manager.get_active_bans()

    def get_ban_type_display(self, ban_type):
        """Get display name for ban type."""
        display_map = {
            BAN_TYPE_COOLDOWN: _("Cooldown Ban"),
            BAN_TYPE_SHADOW: _("Shadow Ban"),
            BAN_TYPE_PERMANENT: _("Permanent Ban"),
        }
        return display_map.get(ban_type, ban_type)

    def format_time_remaining(self, ban):
        """Format the remaining time for a ban."""
        # Handle permanent bans
        if ban.ban_type == BAN_TYPE_PERMANENT:
            return _("Permanent")

        # Get remaining time
        remaining = ban.get_remaining_time()
        if not remaining:
            return _("Expired")

        # Format time components
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60

        # Return appropriate format based on remaining time
        if days > 0:
            return _("${days}d ${hours}h", mapping={"days": days, "hours": hours})
        elif hours > 0:
            return _(
                "${hours}h ${minutes}m", mapping={"hours": hours, "minutes": minutes}
            )
        else:
            return _("${minutes}m", mapping={"minutes": minutes})

    def get_user_display_name(self, user_id):
        """Get display name for a user."""
        if not user_id:
            return ""

        # Get member information
        membership = getToolByName(self.context, "portal_membership")
        member = membership.getMemberById(user_id)

        # If we have a valid member with a fullname, use it
        if member:
            fullname = member.getProperty("fullname", "").strip()
            if fullname:
                return f"{fullname} ({user_id})"

        return user_id


class UserBanStatusView(BrowserView, BanManagementMixin):
    """View to check if current user is banned."""

    def __call__(self):
        """Return ban status information as JSON."""
        membership = getToolByName(self.context, "portal_membership")
        member = membership.getAuthenticatedMember()

        # Default response for anonymous users or no ban
        default_response = {
            "banned": False,
            "ban_type": None,
            "can_comment": True,
            "reason": None,
            "created_date": None,
            "expires_date": None,
            "remaining_seconds": 0,
        }

        # Return default response for anonymous users
        if not member or membership.isAnonymousUser():
            return default_response

        # Get ban information
        user_id = member.getId()
        ban_manager = self._get_ban_manager()
        ban = ban_manager.get_user_ban(user_id)

        # Return default response if no active ban
        if not ban or not ban.is_active():
            return default_response

        # Build response with ban information
        result = {
            "banned": True,
            "ban_type": ban.ban_type,
            "can_comment": ban.ban_type == BAN_TYPE_SHADOW,
            "reason": ban.reason,
            "created_date": ban.created_date.isoformat() if ban.created_date else None,
            "expires_date": None,
            "remaining_seconds": 0,
        }

        # Add expiration info for temporary bans
        if ban.ban_type != BAN_TYPE_PERMANENT and ban.expires_date:
            result["expires_date"] = ban.expires_date.isoformat()
            remaining = ban.get_remaining_time()
            if remaining:
                result["remaining_seconds"] = int(remaining.total_seconds())

        return result


UserBanFormView = wrap_form(UserBanForm)
UserUnbanFormView = wrap_form(UserUnbanForm)
