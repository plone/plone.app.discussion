"""Comment form integration for ban management."""

from plone.app.discussion.ban import BAN_TYPE_COOLDOWN
from plone.app.discussion.ban import BAN_TYPE_PERMANENT
from plone.app.discussion.ban import can_user_comment
from plone.app.discussion.ban import get_ban_manager
from plone.app.discussion.ban import is_comment_visible
from plone.app.discussion.interfaces import _
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage


try:
    from plone.app.discussion.interfaces import IDiscussionSettings
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility
except ImportError:
    pass


def check_user_ban_before_comment(comment_form, data):
    """Check if user is banned before allowing comment submission.

    This function should be called from the comment form's handleComment method.
    Returns True if comment should be allowed, False otherwise.
    """
    context = comment_form.context
    request = comment_form.request

    # Check if ban system is enabled
    try:
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        if not getattr(settings, "ban_enabled", False):
            return True  # Ban system disabled, allow comment
    except Exception:
        return True  # If we can't check settings, allow comment

    # Get current user
    membership = getToolByName(context, "portal_membership")
    if membership.isAnonymousUser():
        return True  # Anonymous users are not subject to bans

    member = membership.getAuthenticatedMember()
    user_id = member.getId()

    # Check if user can comment (considering bans)
    if not can_user_comment(context, user_id):
        ban_manager = get_ban_manager(context)
        ban = ban_manager.get_user_ban(user_id)

        if ban and ban.is_active():
            # User is banned, show appropriate message
            if ban.ban_type == BAN_TYPE_PERMANENT:
                message = _(
                    "You have been permanently banned from commenting. Reason: ${reason}",
                    mapping={"reason": ban.reason or _("No reason provided")},
                )
            elif ban.ban_type == BAN_TYPE_COOLDOWN:
                remaining = ban.get_remaining_time()
                if remaining:
                    hours = int(remaining.total_seconds() // 3600)
                    minutes = int((remaining.total_seconds() % 3600) // 60)
                    if hours > 0:
                        time_str = _(
                            "${hours} hours and ${minutes} minutes",
                            mapping={"hours": hours, "minutes": minutes},
                        )
                    else:
                        time_str = _("${minutes} minutes", mapping={"minutes": minutes})

                    message = _(
                        "You are temporarily banned from commenting for ${time}. Reason: ${reason}",
                        mapping={
                            "time": time_str,
                            "reason": ban.reason or _("No reason provided"),
                        },
                    )
                else:
                    message = _(
                        "Your comment ban has expired. Please refresh the page."
                    )
            else:
                message = _("You are currently banned from commenting.")

            IStatusMessage(request).add(message, type="error")
            return False

    return True


def process_shadow_banned_comment(comment, context):
    """Process a comment from a shadow banned user.

    This function should be called after a comment is created to handle
    shadow ban logic.
    """
    # Get comment author
    author_id = getattr(comment, "creator", None) or getattr(
        comment, "author_username", None
    )
    if not author_id:
        return  # Can't determine author

    # Check if author is shadow banned
    if not is_comment_visible(context, author_id):
        # Comment is from shadow banned user
        # We don't need to do anything special here since visibility
        # will be handled by the catalog and views
        pass


def filter_shadow_banned_comments(comments, context):
    """Filter out comments from shadow banned users for non-authors.

    Args:
        comments: Iterable of comment objects
        context: Current context object

    Returns:
        Filtered list of comments
    """
    membership = getToolByName(context, "portal_membership")
    current_user = None

    if not membership.isAnonymousUser():
        member = membership.getAuthenticatedMember()
        current_user = member.getId()

    filtered_comments = []

    for comment in comments:
        # Get comment author
        author_id = getattr(comment, "creator", None) or getattr(
            comment, "author_username", None
        )

        if not author_id:
            # Anonymous comment or can't determine author
            filtered_comments.append(comment)
            continue

        # If current user is the comment author, always show their comments
        if current_user == author_id:
            filtered_comments.append(comment)
            continue

        # Check if comment should be visible (not from shadow banned user)
        if is_comment_visible(context, author_id):
            filtered_comments.append(comment)
        # If not visible, skip this comment (shadow banned)

    return filtered_comments


def get_ban_status_for_user(context, user_id):
    """Get ban status information for a specific user.

    Returns a dict with ban information or None if not banned.
    """
    ban_manager = get_ban_manager(context)
    ban = ban_manager.get_user_ban(user_id)

    if not ban or not ban.is_active():
        return None

    status = {
        "banned": True,
        "ban_type": ban.ban_type,
        "reason": ban.reason,
        "created_date": ban.created_date,
        "moderator_id": ban.moderator_id,
    }

    if ban.ban_type != BAN_TYPE_PERMANENT:
        status["expires_date"] = ban.expires_date
        remaining = ban.get_remaining_time()
        if remaining:
            status["remaining_seconds"] = int(remaining.total_seconds())

    return status


def add_ban_info_to_comment_data(comment_data, context):
    """Add ban information to comment data for templates.

    This can be used to show ban status in comment listings.
    """
    author_id = comment_data.get("creator") or comment_data.get("author_username")
    if not author_id:
        return comment_data

    ban_status = get_ban_status_for_user(context, author_id)
    if ban_status:
        comment_data["author_ban_status"] = ban_status

    return comment_data
