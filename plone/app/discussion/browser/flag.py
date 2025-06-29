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
    """

    def __call__(self):
        comment = aq_inner(self.context)
        # Increment the flag count
        if not hasattr(comment, 'flag') or comment.flag is None:
            comment.flag = 0
        comment.flag += 1
        
        # Notify that the object has been modified
        notify(ObjectModifiedEvent(comment))
        
        # Show status message
        IStatusMessage(self.request).addStatusMessage(
            _("Comment flagged as inappropriate."), type="info"
        )
        
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
