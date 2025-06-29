from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.discussion import _
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class FlagComment(BrowserView):
    """Flag a comment as inappropriate.

    This view is called directly on the comment object:
    http://nohost/front-page/++conversation++default/1286289644723317/@@flag-comment
    
    If a user has already flagged the comment, clicking again will unflag it.
    """

    def get_user_identifier(self):
        """Get a unique identifier for the current user.
        
        Returns IP address for anonymous users and username for logged-in users.
        """
        mtool = getToolByName(self.context, "portal_membership")
        if mtool.isAnonymousUser():
            return self.request.get('REMOTE_ADDR', '')
        return mtool.getAuthenticatedMember().getId()
            
    def __call__(self):
        comment = aq_inner(self.context)
        
        # Ensure flagged_by exists as a proper persistent attribute
        if not hasattr(comment, 'flagged_by') or comment.flagged_by is None:
            # Create a new list that will be properly persisted
            comment.flagged_by = []
            
        # Get identifier for the current user
        identifier = self.get_user_identifier()
        
        # Toggle flag status only if we have a valid identifier
        if not identifier:
            return self.request.response.redirect(self.get_redirect_url())
            
        # Create a copy of the current list to ensure it's modified and persisted
        # This is important to mark the attribute as "changed" for ZODB
        current_flags = list(comment.flagged_by)
            
        # Toggle flag status
        flagged = identifier in current_flags
        if flagged:
            current_flags.remove(identifier)
            message = _("comment_unflagged", default="Comment unflagged.")
        else:
            current_flags.append(identifier)
            message = _("comment_flagged", default="Comment flagged as inappropriate.")
        
        # Assign the modified list back to ensure persistence
        comment.flagged_by = current_flags
        
        # Notify that the object has been modified
        notify(ObjectModifiedEvent(comment))
        
        # Show status message
        IStatusMessage(self.request).addStatusMessage(message, type="info")
        
        # Redirect to appropriate URL
        return self.request.response.redirect(self.get_redirect_url())
    
    def get_redirect_url(self):
        """Determine the appropriate URL to redirect to after flagging.
        
        Returns the referrer URL if valid, otherwise returns the content object URL.
        """
        comment = aq_inner(self.context)
        conversation = aq_parent(comment)
        content_object = aq_parent(conversation)
        came_from = self.request.HTTP_REFERER
        
        # Validate the referrer URL
        is_valid_referrer = (
            came_from and 
            "came_from=" not in came_from and
            getToolByName(content_object, "portal_url").isURLInPortal(came_from)
        )
        
        if not is_valid_referrer:
            return content_object.absolute_url()
            
        return came_from
