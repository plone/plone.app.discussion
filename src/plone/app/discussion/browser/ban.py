"""Browser views for user ban management."""

from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Acquisition import aq_inner
from datetime import datetime
from datetime import timedelta
from plone.app.discussion.ban import BAN_TYPE_COOLDOWN
from plone.app.discussion.ban import BAN_TYPE_PERMANENT
from plone.app.discussion.ban import BAN_TYPE_SHADOW
from plone.app.discussion.ban import get_ban_manager
from plone.app.discussion.interfaces import _
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getUtility

try:
    from plone.registry.interfaces import IRegistry
except ImportError:
    IRegistry = None


class BanManagementView(BrowserView):
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
        
        if action == "ban_user":
            self.ban_user()
        elif action == "unban_user":
            self.unban_user()
        elif action == "cleanup_expired":
            self.cleanup_expired_bans()
    
    def ban_user(self):
        """Ban a user based on form data."""
        user_id = self.request.form.get("user_id", "").strip()
        ban_type = self.request.form.get("ban_type", BAN_TYPE_COOLDOWN)
        reason = self.request.form.get("reason", "").strip()
        duration_hours = self.request.form.get("duration_hours")
        
        if not user_id:
            IStatusMessage(self.request).add(
                _("User ID is required."), type="error"
            )
            return
        
        # Get current user as moderator
        membership = getToolByName(self.context, "portal_membership")
        moderator = membership.getAuthenticatedMember()
        moderator_id = moderator.getId()
        
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
                    type="error"
                )
                return
        
        # Create the ban
        ban_manager = get_ban_manager(self.context)
        try:
            ban = ban_manager.ban_user(
                user_id=user_id,
                ban_type=ban_type,
                moderator_id=moderator_id,
                reason=reason,
                duration_hours=duration
            )
            
            # Success message
            if ban_type == BAN_TYPE_PERMANENT:
                msg = _("User ${user_id} has been permanently banned.", 
                       mapping={"user_id": user_id})
            elif ban_type == BAN_TYPE_SHADOW:
                msg = _("User ${user_id} has been shadow banned.", 
                       mapping={"user_id": user_id})
            else:  # Cooldown
                msg = _("User ${user_id} has been banned for ${duration} hours.", 
                       mapping={"user_id": user_id, "duration": duration or 24})
            
            IStatusMessage(self.request).add(msg, type="info")
            
        except Exception as e:
            IStatusMessage(self.request).add(
                _("Error banning user: ${error}", mapping={"error": str(e)}), 
                type="error"
            )
    
    def unban_user(self):
        """Unban a user."""
        user_id = self.request.form.get("unban_user_id", "").strip()
        
        if not user_id:
            IStatusMessage(self.request).add(
                _("User ID is required."), type="error"
            )
            return
        
        # Get current user as moderator
        membership = getToolByName(self.context, "portal_membership")
        moderator = membership.getAuthenticatedMember()
        moderator_id = moderator.getId()
        
        ban_manager = get_ban_manager(self.context)
        old_ban = ban_manager.unban_user(user_id, moderator_id)
        
        if old_ban:
            IStatusMessage(self.request).add(
                _("User ${user_id} has been unbanned.", 
                  mapping={"user_id": user_id}), 
                type="info"
            )
        else:
            IStatusMessage(self.request).add(
                _("User ${user_id} was not banned.", 
                  mapping={"user_id": user_id}), 
                type="warning"
            )
    
    def cleanup_expired_bans(self):
        """Clean up expired bans."""
        ban_manager = get_ban_manager(self.context)
        count = ban_manager.cleanup_expired_bans()
        
        IStatusMessage(self.request).add(
            _("Cleaned up ${count} expired bans.", mapping={"count": count}), 
            type="info"
        )
    
    def get_active_bans(self):
        """Get all active bans for display."""
        ban_manager = get_ban_manager(self.context)
        return ban_manager.get_active_bans()
    
    def get_ban_type_display(self, ban_type):
        """Get display name for ban type."""
        if ban_type == BAN_TYPE_COOLDOWN:
            return _("Cooldown Ban")
        elif ban_type == BAN_TYPE_SHADOW:
            return _("Shadow Ban")
        elif ban_type == BAN_TYPE_PERMANENT:
            return _("Permanent Ban")
        return ban_type
    
    def format_time_remaining(self, ban):
        """Format the remaining time for a ban."""
        if ban.ban_type == BAN_TYPE_PERMANENT:
            return _("Permanent")
        
        remaining = ban.get_remaining_time()
        if not remaining:
            return _("Expired")
        
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        
        if days > 0:
            return _("${days}d ${hours}h", mapping={"days": days, "hours": hours})
        elif hours > 0:
            return _("${hours}h ${minutes}m", mapping={"hours": hours, "minutes": minutes})
        else:
            return _("${minutes}m", mapping={"minutes": minutes})
    
    def get_user_display_name(self, user_id):
        """Get display name for a user."""
        membership = getToolByName(self.context, "portal_membership")
        member = membership.getMemberById(user_id)
        if member:
            fullname = member.getProperty("fullname", "")
            if fullname:
                return f"{fullname} ({user_id})"
        return user_id


class UserBanStatusView(BrowserView):
    """View to check if current user is banned."""
    
    def __call__(self):
        """Return ban status information as JSON."""
        membership = getToolByName(self.context, "portal_membership")
        member = membership.getAuthenticatedMember()
        
        if not member or membership.isAnonymousUser():
            return {"banned": False}
        
        user_id = member.getId()
        ban_manager = get_ban_manager(self.context)
        ban = ban_manager.get_user_ban(user_id)
        
        if not ban or not ban.is_active():
            return {"banned": False}
        
        result = {
            "banned": True,
            "ban_type": ban.ban_type,
            "can_comment": ban.ban_type == BAN_TYPE_SHADOW,
            "reason": ban.reason,
            "created_date": ban.created_date.isoformat() if ban.created_date else None,
        }
        
        # Add expiration info for temporary bans
        if ban.ban_type != BAN_TYPE_PERMANENT:
            remaining = ban.get_remaining_time()
            if remaining:
                result["expires_date"] = ban.expires_date.isoformat()
                result["remaining_seconds"] = int(remaining.total_seconds())
        
        return result


class BanUserFormView(BrowserView):
    """Standalone form to ban a specific user."""
    
    template = ViewPageTemplateFile("ban_user_form.pt")
    
    def __call__(self):
        """Process form and render template."""
        if not self.can_manage_bans():
            raise Unauthorized("You do not have permission to manage bans.")
        
        # Get user ID from URL or form
        self.user_id = self.request.get("user_id", "")
        
        if self.request.method == "POST":
            self.process_ban_form()
        
        return self.template()
    
    def can_manage_bans(self):
        """Check if current user can manage bans."""
        return getSecurityManager().checkPermission(
            "Review comments", aq_inner(self.context)
        )
    
    def process_ban_form(self):
        """Process the ban form submission."""
        # Similar to ban_user method in BanManagementView
        user_id = self.request.form.get("user_id", "").strip()
        ban_type = self.request.form.get("ban_type", BAN_TYPE_COOLDOWN)
        reason = self.request.form.get("reason", "").strip()
        duration_hours = self.request.form.get("duration_hours")
        
        if not user_id:
            IStatusMessage(self.request).add(
                _("User ID is required."), type="error"
            )
            return
        
        membership = getToolByName(self.context, "portal_membership")
        moderator = membership.getAuthenticatedMember()
        moderator_id = moderator.getId()
        
        duration = None
        if ban_type != BAN_TYPE_PERMANENT and duration_hours:
            try:
                duration = int(duration_hours)
                if duration <= 0:
                    raise ValueError("Duration must be positive")
            except ValueError:
                IStatusMessage(self.request).add(
                    _("Invalid duration. Please enter a positive number of hours."), 
                    type="error"
                )
                return
        
        ban_manager = get_ban_manager(self.context)
        try:
            ban_manager.ban_user(
                user_id=user_id,
                ban_type=ban_type,
                moderator_id=moderator_id,
                reason=reason,
                duration_hours=duration
            )
            
            IStatusMessage(self.request).add(
                _("User ${user_id} has been banned.", 
                  mapping={"user_id": user_id}), 
                type="info"
            )
            
            # Redirect to avoid resubmission
            self.request.response.redirect(self.context.absolute_url() + "/@@ban-management")
            
        except Exception as e:
            IStatusMessage(self.request).add(
                _("Error banning user: ${error}", mapping={"error": str(e)}), 
                type="error"
            )
    
    def get_user_info(self):
        """Get information about the user to be banned."""
        if not self.user_id:
            return None
        
        membership = getToolByName(self.context, "portal_membership")
        member = membership.getMemberById(self.user_id)
        
        if not member:
            return {"id": self.user_id, "exists": False}
        
        return {
            "id": self.user_id,
            "exists": True,
            "fullname": member.getProperty("fullname", ""),
            "email": member.getProperty("email", ""),
        }
