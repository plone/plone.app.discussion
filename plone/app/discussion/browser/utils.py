"""Utility functions for plone.app.discussion browser views."""

from plone.app.discussion import _
from zope.i18n import translate


def format_author_name_with_suffix(comment, anonymous_user_suffix, request):
    """Format author name with suffix for anonymous users.

    Returns the author name with a suffix (Guest) appended for anonymous
    comments. The suffix is translated to the current user's language.

    Args:
        comment: The comment object
        anonymous_user_suffix: The suffix message to append (e.g., _("(Guest)"))
        request: The request object for translation context

    Returns:
        str: The formatted author name
    """
    author_name = comment.author_name

    # If this is an anonymous comment (no creator), add the suffix
    if not comment.creator and author_name:
        # Translate the suffix to the current language
        translated_suffix = translate(anonymous_user_suffix, context=request)
        if not author_name.endswith(translated_suffix):
            author_name = author_name + " " + translated_suffix

    return author_name
