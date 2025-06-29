from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.discussion import _
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class FlagComment(BrowserView):
    """Flag a comment as inappropriate.

    This view is called directly on the comment object:
    http://nohost/front-page/++conversation++default/1286289644723317/@@flag-comment
    
    If a user has already flagged the comment, clicking again will unflag it.
    """

    def __call__(self):
        comment = aq_inner(self.context)
        mtool = getToolByName(self.context, "portal_membership")
        
        # Initialize flagged_by as a list if it doesn't exist
        if not hasattr(comment, 'flagged_by') or comment.flagged_by is None:
            comment.flagged_by = []
            
        # Get current user
        anon = mtool.isAnonymousUser()
        if anon:
            # For anonymous users, use IP address as identifier
            identifier = self.request.get('REMOTE_ADDR', '')
        else:
            # For logged-in users, use their username
            identifier = mtool.getAuthenticatedMember().getId()
            
        # Check if this user already flagged the comment
        if identifier in comment.flagged_by:
            # User already flagged, so unflag it
            comment.flagged_by.remove(identifier)
            message = _("comment_unflagged", default="Comment unflagged.")
        else:
            # User hasn't flagged, so flag it
            comment.flagged_by.append(identifier)
            message = _("comment_flagged", default="Comment flagged as inappropriate.")
        
        # Set the flag count based on the length of flagged_by list
        comment.flag = len(comment.flagged_by)
        
        # Notify that the object has been modified
        notify(ObjectModifiedEvent(comment))
        
        # Show status message
        IStatusMessage(self.request).addStatusMessage(message, type="info")
        
        # Redirect back to the page
        conversation = aq_parent(comment)
        content_object = aq_parent(conversation)
        came_from = self.request.HTTP_REFERER
        
        # if the referrer already has a came_from in it, don't redirect back
        if (
            len(came_from) == 0
            or "came_from=" in came_from
            or not getToolByName(content_object, "portal_url").isURLInPortal(came_from)
        ):
            came_from = content_object.absolute_url()
        
        return self.request.response.redirect(came_from)
